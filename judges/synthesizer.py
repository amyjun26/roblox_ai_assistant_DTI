import openai
from accuracy_theme_judge import evaluate_outfit as accuracy_evaluate_outfit
from color_coordination_judge import evaluate_outfit as color_coordination_evaluate_outfit
from creativity_judge import evaluate_outfit as creativity_judge_evaluate_outfit
from technical_fashion_judge import evaluate_outfit as technical_fashion_evaluate_outfit
import os
import base64

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


#judges_feedback from the output from the other LLM judges
def synthesize_feedback(image_url, theme):
    """
    This function synthesizes feedback from multiple LLM judges, scaling the weight of their feedback 
    based on their credibility score.
    
    Parameters:
    feedback_dict (dictionary): key is name of judge, value is 0.25 (fixed credibility for demo)
    image_url: (string) image url
    theme: (string) theme name
    
    Returns:
    str: Synthesized feedback based on the most credible judges.
    """

    #TODO: Synthesize all of the feedback from Creativity Judge, Technical Fashion Sense Judge, Accuracy Theme Judge, and Color Coordination Theme Judge. When synthesizing feedback, give 1-2 paragraphs in total.
    # WE USE OLD WEIGHTS HERE
    # When summarizing, weigh the feedback from each judges proportion to the following values:

    # Creativity Judge: rating of <int>/10, credibility score is <int>
    # Technical Fashion Sense Judge: rating of <int>/10, credibility score is <int>
    # Accuracy Theme Judge: rating of <int>/10, credibility score is <int>
    # Color Coordination Theme Judge: rating of <int>/10, credibility score is <int>

    # Finally, to obtain a following rating, weigh each judge’s individual rating by their credibility score to obtain a final rating out of 10.
    # Return the text output and the rating itself.    

    c_feedback, c_score = creativity_judge_evaluate_outfit(image_url, theme)
    t_feedback, t_score = technical_fashion_evaluate_outfit(image_url, theme)
    a_feedback, a_score = accuracy_evaluate_outfit(image_url, theme)
    color_feedback, color_score = color_coordination_evaluate_outfit(image_url, theme)
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

    return final_judgement

#Testing

image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'caillou.png')
base64_url = image_to_base64(image_path)
print("FINAL FEEDBACK\n")
print("-----------------------------------\n")
print(synthesize_feedback(base64_url, "brat"))


