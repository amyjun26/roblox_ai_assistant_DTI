package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"fmt"
	"image"
	"image/jpeg"
	"os"
	"time"

	"github.com/corona10/goimagehash"
	"github.com/joho/godotenv"
	"github.com/kbinani/screenshot"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

func main() {
	/*
		items, _ := ioutil.ReadDir("output")
		for _, item := range items {
			if !item.IsDir() {
				f, err := os.Open(fmt.Sprintf("output/%s", item.Name()))
				if err != nil {
					panic(err)
				}
				defer f.Close()

				img, err := jpeg.Decode(f)
				if err != nil {
					panic(err)
				}

				analyzer := smartcrop.NewAnalyzer(nfnt.NewDefaultResizer())
				smart_rect, _ := analyzer.FindBestCrop(img, 60, 60)

				subimg := img.(interface {
					SubImage(r image.Rectangle) image.Image
				}).SubImage(smart_rect)

				// Save to filesystem for testing
				var img_buf bytes.Buffer
				err = jpeg.Encode(&img_buf, subimg, nil)
				if err != nil {
					panic(err)
				}

				err = os.WriteFile(fmt.Sprintf("output_2/%s", item.Name()), img_buf.Bytes(), 0644)
				if err != nil {
					panic(err)
				}
			}
		}
	*/

	main_loop()
}

func main_loop() {
	// Load .env
	err := godotenv.Load()
	if err != nil {
		panic(err)
	}

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
	for {
		// Time process
		start := time.Now()

		// Get screenshot of display
		img, err := screenshot.CaptureDisplay(0)
		if err != nil {
			panic(err)
		}

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

		for x := 0; x < 5; x++ {
			for y := 0; y < 4; y++ {
				x_img := int(float32(HEART_START_X) + HEART_OFFSET_X*float32(x))
				y_img := int(float32(HEART_START_Y) + HEART_OFFSET_Y*float32(y))
				subimg := img.SubImage(image.Rect(x_img, y_img, x_img+HEART_IMG_W, y_img+HEART_IMG_H))

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
					clothing_subimg := img.SubImage(image.Rect(x_clothing_img, y_clothing_img, x_clothing_img+CLOTHING_IMG_W, y_clothing_img+CLOTHING_IMG_H))

					// Create image buf
					var img_buf bytes.Buffer
					err = jpeg.Encode(&img_buf, clothing_subimg, nil)
					if err != nil {
						panic(err)
					}

					// Convert to base64 string
					// Get caption
					chat_completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{
						Messages: openai.F([]openai.ChatCompletionMessageParamUnion{
							openai.UserMessage("Describe the clothing item you see in the center of the image as succinctly as possible, only describe the clothing and print no more tokens: The clothing item in the center of the image is a"),
							openai.UserMessageParts(openai.ImagePart(fmt.Sprintf("data:image/jpeg;base64,%s", base64.StdEncoding.EncodeToString(img_buf.Bytes())))),
						}),
						Model: openai.F(openai.ChatModelGPT4o),
					})
					if err != nil {
						panic(err)
					}

					fmt.Printf("Caption: %s\n", chat_completion.Choices[0].Message.Content)
				}
			}
		}

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
