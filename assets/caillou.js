// imageUtil.js
const fs = require("fs");
const path = require("path");

// Function to convert image to Base64 URL
function imageToBase64(imagePath) {
  try {
    const imageData = fs.readFileSync(imagePath); // Read image file
    const base64Encoded = Buffer.from(imageData).toString("base64"); // Convert to base64
    const fileExtension = path.extname(imagePath).slice(1); // Get the file extension
    return `data:image/${fileExtension};base64,${base64Encoded}`; // Create Base64 URL
  } catch (error) {
    console.error("Error converting image to base64:", error);
    return null;
  }
}

// Export the function and/or the image path
const imagePath = path.join(__dirname, "caillou.png");
const image_64 = imageToBase64(imagePath);
console.log(image_64);
