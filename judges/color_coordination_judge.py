import openai
import base64
import os 
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def get_prompt(theme):
    prompt = (
        f"Based on the theme: {theme},\n"
        "Are the colors in this outfit complementary or harmonious?\n"
        "Do the color choices enhance the overall aesthetic appeal of the outfit?\n"
        "Is there a balance between bright and neutral tones in this design?\n"
        "Is there a color that better suits the mood and theme?\n"
        "In the context of the theme, do you think the skin tone matches with the color and style of the clothes?\n"
        "Please provide the feedback (no need to repeat questions) and the rating in the following format:\n"
        "Feedback: [Your detailed feedback here]\n"
        "Rating: [Your rating here]"
    )
    return prompt
    
def evaluate_outfit(image_url, theme):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are a fashion judge for the Roblox game 'Dress To Impress.' Provide detailed, objective feedback and a numerical rating on a scale from 1 to 10 based on the given questions."},
            {"role": "user", "content": [{"type": "text", "text": get_prompt(theme)}, {"type": "image_url", "image_url": {"url": image_url}}]}
        ],
        max_tokens=200  
    )

    feedback = response['choices'][0]['message']['content'].strip()

    try:
        feedback_part, score_part = feedback.rsplit("Rating:", 1)
        score = int(score_part.split('/')[0])  
    except (ValueError, IndexError):
        # default to a score of 0 if fail
        feedback_part = feedback
        score = 0

    return feedback_part.strip(), score

image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'caillou.png')
base64_url = image_to_base64(image_path)
#print(get_prompt("Disney Princess"))
print(evaluate_outfit(base64_url, "caillou"))

