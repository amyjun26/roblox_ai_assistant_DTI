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
def synthesize_feedback(feedback_dict, image_url, theme):
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

    creativity_rating = feedback_dict["creativity_judge"]
    tech_fashion_rating = feedback_dict["technical_fashion_sense_judge"]
    accuracy_theme_rating = feedback_dict["accuracy_theme_judge"]
    color_coordination_rating = feedback_dict["color_coordination_theme_judge"]

    synthesizer_prompt = (
    "Synthesize all of the feedback from Creativity Judge, Technical Fashion Sense Judge, Accuracy Theme Judge,\n"
    "and Color Coordination Theme Judge. When synthesizing feedback, give 1-2 paragraphs in total. When summarizing,\n"
    "weigh the feedback from each judges proportion to the following values:\n"
    f"Here is the feedback from the Creativity Judge: {creativity_judge_evaluate_outfit(image_url, theme)}\n"
    f"Here is the feedback from the Technical Fashion Sense Judge: {technical_fashion_evaluate_outfit(image_url, theme)}\n"
    f"Here is the feedback from the Accuracy Theme Judge: {accuracy_evaluate_outfit(image_url, theme)}\n"
    f"Here is the feedback from the Color Coordination Theme Judge: {color_coordination_evaluate_outfit(image_url, theme)}\n"
    "Finally, to obtain a following rating, weigh each judge’s individual rating by their credibility score to obtain a final rating out of 10. Return this at the end.\n"
)

    
    formatted_synthesizer_prompt = synthesizer_prompt.format(
    creativity_rating=creativity_rating,
    creativity_credibility=0.25,
    tech_fashion_rating=tech_fashion_rating,
    tech_fashion_credibility=0.25,
    accuracy_theme_rating=accuracy_theme_rating,
    accuracy_theme_credibility=0.25,
    color_coordination_rating=color_coordination_rating,
    color_coordination_credibility=0.25
)

    synthesized_output = openai.ChatCompletion.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are compiling information from various judges judging outfits on Roblox's hit game, Dress to Impress."},
            {"role": "user", "content": [{"type": "text", "text": formatted_synthesizer_prompt}]}
        ],
        max_tokens=200  
    )
    final_judgement = synthesized_output['choices'][0]['message']['content']

    #print("FINAL JUDGEMENT: \n" + final_judgement)

    return final_judgement

#Testing

d = dict()
d["creativity_judge"] = 0.25
d["technical_fashion_sense_judge"] = 0.25
d["accuracy_theme_judge"] = 0.25
d["color_coordination_theme_judge"] = 0.25
image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'caillou.png')
base64_url = image_to_base64(image_path)
print(synthesize_feedback(d, base64_url, "brat"))


