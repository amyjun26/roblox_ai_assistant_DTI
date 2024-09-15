package main

import (
	"bytes"
	"context"
	_ "embed"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"image"
	"image/jpeg"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/corona10/goimagehash"
	"github.com/davecgh/go-spew/spew"
	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
	"github.com/kbinani/screenshot"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

// Define all our prompts
//
//go:embed prompts/get_caption_prompt.txt
var GET_CAPTION_PROMPT string

//go:embed prompts/get_judge_opinion_prompt.txt
var GET_JUDGE_OPINION_PROMPT string

//go:embed prompts/ocr_prompt.txt
var OCR_PROMPT string

const HEART_OFFSET_X float32 = 162.5
const HEART_OFFSET_Y float32 = 171.1

const HEART_START_X int = 239
const HEART_START_Y int = 331
const HEART_IMG_W int = 20
const HEART_IMG_H int = 20

const CLOTHING_START_X int = 176
const CLOTHING_START_Y int = 194
const CLOTHING_IMG_W int = 143
const CLOTHING_IMG_H int = 154

const X_IMG_ACCEPTABLE_HASH_DIFF int = 20

const THEME_OFFSET_X int = 395
const THEME_OFFSET_Y int = 89
const THEME_OFFSET_W int = 696
const THEME_OFFSET_H int = 57

const STAR_COUNT_OFFSET_X int = 82
const STAR_COUNT_OFFSET_Y int = 830
const STAR_COUNT_OFFSET_W int = 141
const STAR_COUNT_OFFSET_H int = 43

const END_ROUND_HEADER_OFFSET_X int = 456
const END_ROUND_HEADER_OFFSET_Y int = 90
const END_ROUND_HEADER_OFFSET_W int = 615
const END_ROUND_HEADER_OFFSET_H int = 97

type DTIData struct {
	ClothingItems []string `json:"clothing_items"`
	Theme         string   `json:"theme"`
	JudgeOpinion  string   `json:"judge_opinion"`
	NumPlayers    int      `json:"num_players"`
	NumStars      float32  `json:"avg_rating"`
	Complete      bool     `json:"complete"`
}

var last_dti_data DTIData = DTIData{}
var websocket_con *websocket.Conn = nil
var last_star_count int = 0

func main() {
	// Load .env
	err := godotenv.Load()
	if err != nil {
		panic(err)
	}

	r := mux.NewRouter()

	r.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {

	})

	var upgrader = websocket.Upgrader{} // use default options
	r.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		ws, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			fmt.Printf("Upgrade error: %v\n", err)
			return
		}
		defer ws.Close()

		for {
			_, message, err := ws.ReadMessage()
			if err != nil {
				fmt.Printf("Read error: %v\n", err)
				return
			}

			fmt.Printf("Recv: %v\n", message)

			// err = ws.WriteMessage(mt, message)
			// if err != nil {
			// 	log.Println("write:", err)
			// 	break
			// }
		}
	})

	// For all static files that didn't match any other handlers
	r.PathPrefix("/").Handler(http.FileServer(http.Dir("frontend/dress-to-impress-interface/build")))

	// Run all our tasks
	var wg sync.WaitGroup
	wg.Add(2)
	go main_loop()
	go http.ListenAndServe(fmt.Sprintf(":%v", 8080), r)
	wg.Wait()
}

func determine_number_of_clothing_items(x_img_hash *goimagehash.ImageHash, display_screenshot *image.RGBA) int {
	num := 0
	for x := 0; x < 5; x++ {
		for y := 0; y < 4; y++ {
			x_img := int(float32(HEART_START_X) + HEART_OFFSET_X*float32(x))
			y_img := int(float32(HEART_START_Y) + HEART_OFFSET_Y*float32(y))
			subimg := display_screenshot.SubImage(image.Rect(x_img, y_img, x_img+HEART_IMG_W, y_img+HEART_IMG_H))

			// Hash of subimage
			subimg_hash, err := goimagehash.DifferenceHash(subimg)
			if err != nil {
				panic(err)
			}

			// Distance from X image
			x_img_dist, _ := subimg_hash.Distance(x_img_hash)

			// if difference is acceptable this is an X image, thus this is a clothing item
			if x_img_dist < X_IMG_ACCEPTABLE_HASH_DIFF {
				num += 1
			}
		}
	}

	return num
}

func get_dti_data(client *openai.Client, x_img_hash *goimagehash.ImageHash, display_screenshot *image.RGBA) DTIData {
	// Extract theme image
	theme_subimg := display_screenshot.SubImage(image.Rect(THEME_OFFSET_X, THEME_OFFSET_Y, THEME_OFFSET_X+THEME_OFFSET_W, THEME_OFFSET_Y+THEME_OFFSET_H))

	// Create image buf from theme image
	var theme_img_buf bytes.Buffer
	err := jpeg.Encode(&theme_img_buf, theme_subimg, nil)
	if err != nil {
		panic(err)
	}

	// Use chatgpt to do OCR, Tesseract does a poor job
	chat_completion_theme, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{
		Messages: openai.F([]openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(OCR_PROMPT),
			openai.UserMessageParts(openai.ImagePart(fmt.Sprintf("data:image/jpeg;base64,%s", base64.StdEncoding.EncodeToString(theme_img_buf.Bytes())))),
		}),
		Model: openai.F(openai.ChatModelGPT4o),
	})
	if err != nil {
		panic(err)
	}

	dti_data := DTIData{}
	dti_data.ClothingItems = []string{}

	// Extract the theme
	theme_output := chat_completion_theme.Choices[0].Message.Content
	if strings.Contains(theme_output, "THE_TEXT:") && strings.Contains(theme_output, "Theme:") {
		theme := theme_output[strings.Index(theme_output, "Theme:")+len("Theme: "):]
		dti_data.Theme = theme
	}

	for x := 0; x < 5; x++ {
		for y := 0; y < 4; y++ {
			x_img := int(float32(HEART_START_X) + HEART_OFFSET_X*float32(x))
			y_img := int(float32(HEART_START_Y) + HEART_OFFSET_Y*float32(y))
			subimg := display_screenshot.SubImage(image.Rect(x_img, y_img, x_img+HEART_IMG_W, y_img+HEART_IMG_H))

			// Hash of subimage
			subimg_hash, err := goimagehash.DifferenceHash(subimg)
			if err != nil {
				panic(err)
			}

			// Distance from X image
			x_img_dist, _ := subimg_hash.Distance(x_img_hash)

			// if difference is acceptable this is an X image, thus this is a clothing item
			if x_img_dist < X_IMG_ACCEPTABLE_HASH_DIFF {
				x_clothing_img := int(float32(CLOTHING_START_X) + HEART_OFFSET_X*float32(x))
				y_clothing_img := int(float32(CLOTHING_START_Y) + HEART_OFFSET_Y*float32(y))
				clothing_subimg := display_screenshot.SubImage(image.Rect(x_clothing_img, y_clothing_img, x_clothing_img+CLOTHING_IMG_W, y_clothing_img+CLOTHING_IMG_H))

				// Create image buf
				var img_buf bytes.Buffer
				err = jpeg.Encode(&img_buf, clothing_subimg, nil)
				if err != nil {
					panic(err)
				}

				// Convert image to base64 string
				// Get caption
				chat_completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{
					Messages: openai.F([]openai.ChatCompletionMessageParamUnion{
						openai.UserMessage(GET_CAPTION_PROMPT),
						openai.UserMessageParts(openai.ImagePart(fmt.Sprintf("data:image/jpeg;base64,%s", base64.StdEncoding.EncodeToString(img_buf.Bytes())))),
					}),
					Model: openai.F(openai.ChatModelGPT4o),
				})
				if err != nil {
					panic(err)
				}

				dti_data.ClothingItems = append(dti_data.ClothingItems, chat_completion.Choices[0].Message.Content)
			}
		}
	}

	// Get judge opinion of our outfit
	judge_chat_completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{
		Messages: openai.F([]openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(fmt.Sprintf(GET_JUDGE_OPINION_PROMPT, strings.Join(dti_data.ClothingItems, "\n"), dti_data.Theme)),
		}),
		Model: openai.F(openai.ChatModelGPT4o),
	})
	if err != nil {
		panic(err)
	}

	dti_data.JudgeOpinion = judge_chat_completion.Choices[0].Message.Content

	return dti_data
}

func change_star_count(client *openai.Client, display_screenshot *image.RGBA) {
	subimg := display_screenshot.SubImage(image.Rect(STAR_COUNT_OFFSET_X, STAR_COUNT_OFFSET_Y, STAR_COUNT_OFFSET_X+STAR_COUNT_OFFSET_W, STAR_COUNT_OFFSET_Y+STAR_COUNT_OFFSET_H))

	// Create image buf
	var img_buf bytes.Buffer
	err := jpeg.Encode(&img_buf, subimg, nil)
	if err != nil {
		panic(err)
	}

	// Convert image to base64 string
	// Get star count
	chat_completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{
		Messages: openai.F([]openai.ChatCompletionMessageParamUnion{
			openai.UserMessage(OCR_PROMPT),
			openai.UserMessageParts(openai.ImagePart(fmt.Sprintf("data:image/jpeg;base64,%s", base64.StdEncoding.EncodeToString(img_buf.Bytes())))),
		}),
		Model: openai.F(openai.ChatModelGPT4o),
	})
	if err != nil {
		panic(err)
	}

	// Proceed only if star count correct
	chat_output := chat_completion.Choices[0].Message.Content
	if strings.Contains(chat_output, "THE_TEXT:") {
		star_count, err := strconv.Atoi(chat_completion.Choices[0].Message.Content)
		if err == nil {
			if star_count != last_star_count && last_star_count != 0 {
				// Determine number of stars obtained
				star_diff := star_count - last_star_count
				last_star_count = star_count
				last_dti_data.NumStars = float32(star_diff)

				// Signal we are done
				last_dti_data.Complete = true

				// Send payload
				send_dti_payload()
			} else if last_star_count == 0 {
				last_star_count = star_count
			}
		}
	}
}

// Voting complete!

// First up are
// Next up is
// Wooohoo! Look how gorgeous
// We head over to
// And last but not least
// Voting complete!

func send_dti_payload() {
	spew.Dump(last_dti_data)

	// Send to client
	if websocket_con != nil {
		dti_data_payload, err := json.Marshal(last_dti_data)
		if err != nil {
			panic(err)
		}

		// Send as JSON
		err = websocket_con.WriteMessage(websocket.TextMessage, dti_data_payload)
		if err != nil {
			panic(err)
		}
	}
}

func main_loop() {
	msg_chan := make(chan string)

	// X image hashing
	x_img_file, err := os.Open("assets/x.jpg")
	if err != nil {
		panic(err)
	}
	defer x_img_file.Close()
	x_img, err := jpeg.Decode(x_img_file)
	if err != nil {
		panic(err)
	}
	x_img_hash, err := goimagehash.DifferenceHash(x_img)
	if err != nil {
		panic(err)
	}

	client := openai.NewClient(
		option.WithAPIKey(os.Getenv("OPENAI_KEY")),
	)

	frame := 0
	last_recorded_number_of_clothing_items := -1
	for {
		// Time process
		start := time.Now()

		// Get screenshot of display
		img, err := screenshot.CaptureDisplay(0)
		if err != nil {
			panic(err)
		}

		// Debug save
		var img_buf bytes.Buffer
		err = jpeg.Encode(&img_buf, img, nil)
		if err != nil {
			panic(err)
		}
		os.WriteFile(fmt.Sprintf("test_frame_%d.jpg", frame), img_buf.Bytes(), 0644)

		// Only run computationally expensive task if we have to
		recorded_number_of_clothing_items := determine_number_of_clothing_items(x_img_hash, img)
		if recorded_number_of_clothing_items != 0 && recorded_number_of_clothing_items != last_recorded_number_of_clothing_items {
			last_recorded_number_of_clothing_items = recorded_number_of_clothing_items

			// Get data
			dti_data := get_dti_data(client, x_img_hash, img)

			spew.Dump(dti_data)

			last_dti_data = dti_data

			send_dti_payload()
		}

		// Attempt to change star count
		change_star_count(client, img)

		fmt.Printf("Time to take screenshot: %v\n", time.Since(start))

		time.Sleep(time.Millisecond * 3000)

		frame += 1

		select {
		case msg := <-msg_chan:
			fmt.Printf("Terminating with message: %s\n", msg)
		default:
		}
	}
}
