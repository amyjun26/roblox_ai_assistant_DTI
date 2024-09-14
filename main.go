package main

import (
	"fmt"
	"image"
	"time"

	"github.com/vova616/screenshot"
)

func main() {
	start := time.Now()

	img, _ := screenshot.CaptureScreen()
	_ = image.Image(img)

	fmt.Printf("Time to capture screenshot: %v\n", time.Since(start))
}
