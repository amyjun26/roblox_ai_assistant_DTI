package main

import (
	"bytes"
	"fmt"
	"image/jpeg"
	"os"
	"time"

	"github.com/kbinani/screenshot"
)

func main() {
	msg_chan := make(chan string)

	frame := 0
	for {
		// Time process
		start := time.Now()

		// Get screenshot of display
		img, err := screenshot.CaptureDisplay(0)
		if err != nil {
			panic(err)
		}

		// Save to filesystem for testing
		var img_buf bytes.Buffer
		err = jpeg.Encode(&img_buf, img, nil)
		if err != nil {
			panic(err)
		}

		err = os.WriteFile(fmt.Sprintf("frame_%d.jpg", frame), img_buf.Bytes(), 0644)
		if err != nil {
			panic(err)
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
