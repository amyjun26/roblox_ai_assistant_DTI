from flask import Flask, request, jsonify
import importlib
import os
import base64

app = Flask(__name__)

JUDGES = ['accuracy', 'color', 'creativity', 'technical']
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Read the image file in binary mode
        image_data = image_file.read()

        # Convert binary data to base64 string
        base64_encoded = base64.b64encode(image_data).decode('utf-8')

        # Create a Base64 URL
        file_extension = image_path.split('.')[-1]
        base64_url = f"data:image/{file_extension};base64,{base64_encoded}"

    return base64_url

# Endpoint to run each judge's script and return their results
@app.route('/evaluate', methods=['GET'])
def get_judges_responses():
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'caillou.png')
    image_url = image_to_base64(image_path)
    theme = "brat"
    responses = []

    for judge_name in JUDGES:
        judge_module = importlib.import_module(f'judges.{judge_name}')
        result = judge_module.evaluate_outfit(image_url, theme)
        responses.append(result)

    return responses

if __name__ == "__main__":
    app.run(debug=True)
