import openai
from accuracy_theme_judge import evaluate_outfit as accuracy_evaluate_outfit
from color_coordination_judge import evaluate_outfit as color_coordination_evaluate_outfit
from creativity_judge import evaluate_outfit as creativity_judge_evaluate_outfit
from technical_fashion_judge import evaluate_outfit as technical_fashion_evaluate_outfit

openai.api_key = "sk-r_IF9spJBilKfacYvlYpiY9cgttmGFqqNg5G9qDE1DT3BlbkFJmkGNsgIfqLIS31B95LQ4_xBoj6kDABCrUZ4ktKuWkA"

# def adjust_credibility(rating):
#         """
#         Adjusts the credibility based on a logarithmic scaling of the rating from 1 to 10.
#         Ratings closer to 1 will have a much lower scaling factor, while ratings closer to 10
#         will have a much higher scaling factor.
#         """
#         # Logarithmic scaling of rating between 1 and 10. 
#         return 1 + (math.log(rating + 1) / math.log(11))


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

    synthesizer_prompt = (
    "Synthesize all of the feedback from Creativity Judge, Technical Fashion Sense Judge, Accuracy Theme Judge, "
    "and Color Coordination Theme Judge. When synthesizing feedback, give 1-2 paragraphs in total. When summarizing, "
    "weigh the feedback from each judges proportion to the following values:\n"
    "Creativity Judge: rating of {creativity_rating}/10, credibility score is {creativity_credibility}\n"
    "Technical Fashion Sense Judge: rating of {tech_fashion_rating}/10, credibility score is {tech_fashion_credibility}\n"
    "Accuracy Theme Judge: rating of {accuracy_theme_rating}/10, credibility score is {accuracy_theme_credibility}\n"
    "Color Coordination Theme Judge: rating of {color_coordination_rating}/10, credibility score is {color_coordination_credibility}\n" +
    
    "Here is the feedback from the Creativity Judge: " + creativity_judge_evaluate_outfit(image_url, theme) + "\n" +
    "Here is the feedback from the Technical Fashion Sense Judge: " + technical_fashion_evaluate_outfit(image_url, theme) + "\n" +
    "Here is the feedback from the Accuracy Theme Judge: " + accuracy_evaluate_outfit(image_url, theme) + "\n" +
    "Here is the feedback from the Color Coordination Theme Judge: " + color_coordination_evaluate_outfit(image_url, theme) + "\n" +

    "Finally, to obtain a following rating, weigh each judge’s individual rating by their credibility score to obtain a final rating out of 10. Return this at the end."
)

    creativity_rating = feedback_dict["creativity_judge"]
    tech_fashion_rating = feedback_dict["technical_fashion_sense_judge"]
    accuracy_theme_rating = feedback_dict["accuracy_theme_judge"]
    color_coordination_rating = feedback_dict["color_coordination_theme_judge"]

    
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

    synthesized_judgement = openai.Completion.create(
    engine="text-davinci-003",  # You can change this to any model, such as gpt-3.5-turbo
    prompt=formatted_synthesizer_prompt,
    max_tokens=100
)
    print("FINAL JUDGEMENT: \n" + synthesized_output)

    return synthesized_output

#Testing

image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'snow_white.jpg')
base64_url = image_to_base64(image_path)
print(synthesize_feedback(base64_url, "Disney Princess"))


