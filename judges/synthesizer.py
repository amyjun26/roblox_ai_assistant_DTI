import openai
from .accuracy_theme_judge import evaluate_outfit as accuracy_evaluate_outfit
from .color_coordination_judge import evaluate_outfit as color_coordination_evaluate_outfit
from .creativity_judge import evaluate_outfit as creativity_judge_evaluate_outfit
from .technical_fashion_judge import evaluate_outfit as technical_fashion_evaluate_outfit
import os
import base64
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

def image_to_base64(image_source):
    try:
        if image_source.startswith('http://') or image_source.startswith('https://'):
            # Fetch the image from the URL
            response = requests.get(image_source)
            response.raise_for_status()  # Check for HTTP errors
            image_data = response.content
        else:
            # Handle local file path
            if not os.path.isfile(image_source):
                raise FileNotFoundError(f"The local file {image_source} does not exist.")
            with open(image_source, "rb") as image_file:
                image_data = image_file.read()

        # Convert the image data to base64 string
        base64_encoded = base64.b64encode(image_data).decode('utf-8')

        # Determine the file extension from the URL or file path
        file_extension = image_source.split('.')[-1].split('?')[0]  # Split and handle URL parameters or file extensions
        base64_url = f"data:image/{file_extension};base64,{base64_encoded}"

        return base64_url
    
    except requests.RequestException as e:
        print(f"Error fetching the image from URL: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Error with the local file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


#judges_feedback from the output from the other LLM judges
def synthesize_feedback(image_url, theme):
    print("in synthesize_feedback() now!\n")
    # print(f"Image URL: {image_url}")
    # print(f"Theme: {theme}")

    b_img = image_to_base64(image_url)
    #print(f"the b64 image link is {b_img}\n")
    print("got b64 url now tryna get scores")
    c_feedback, c_score = creativity_judge_evaluate_outfit(b_img, theme)
    t_feedback, t_score = technical_fashion_evaluate_outfit(b_img, theme)
    a_feedback, a_score = accuracy_evaluate_outfit(b_img, theme)
    color_feedback, color_score = color_coordination_evaluate_outfit(b_img, theme)
    print(f"calculatinggg scores are: {c_score}, {t_score}, {a_score}, {color_score}")
    avg_score = (c_score + t_score + a_score + color_score) / 4.0

    synthesizer_prompt = (
    "Synthesize all of the feedback from Creativity Judge, Technical Fashion Sense Judge, Accuracy Theme Judge,\n"
    "and Color Coordination Theme Judge. When synthesizing feedback, give 1-2 paragraphs in total. Give a brief overview to the user that they were weighed based on four different criteria.\n"
    )
    user_prompt = ( 
        f"Here is the feedback from the Creativity Judge: {c_feedback}\n"
        f"Here is the feedback from the Technical Fashion Sense Judge: {t_feedback}\n"
        f"Here is the feedback from the Accuracy Theme Judge: {a_feedback}\n"
        f"Here is the feedback from the Color Coordination Theme Judge: {color_feedback}\n"
        f"And here is the average score: {avg_score}\n"
    )

    synthesized_output = openai.ChatCompletion.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": [{"type": "text", "text": synthesizer_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
        ],
        max_tokens=400  
    )
    final_judgement = synthesized_output['choices'][0]['message']['content']

    #print("FINAL JUDGEMENT: \n" + final_judgement)
    print("average score is: ")
    print(avg_score)
    return (final_judgement, str(avg_score))

#Testing

# image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'caillou.png')
# base64_url = image_to_base64(image_path)
# print("FINAL FEEDBACK\n")
# print("-----------------------------------\n")
# print(synthesize_feedback(base64_url, "brat"))


