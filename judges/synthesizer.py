from collections import defaultdict
import math


def adjust_credibility(rating):
        """
        Adjusts the credibility based on a logarithmic scaling of the rating from 1 to 10.
        Ratings closer to 1 will have a much lower scaling factor, while ratings closer to 10
        will have a much higher scaling factor.
        """
        # Logarithmic scaling of rating between 1 and 10. 
        return 1 + (math.log(rating + 1) / math.log(11))  # Log base is 11 for better distribution


#judges_feedback from the output from the other LLM judges
def synthesize_feedback_and_scale_credibility(judges_feedback, feedback_dict):
    """
    This function synthesizes feedback from multiple LLM judges, scaling the weight of their feedback 
    based on their credibility score.
    
    Parameters:
    judges_feedback (list): A list of tuples, where each tuple consists of:
                            - feedback (str): The feedback given by the judge.
                            - rating (float): The judge's credibility score between 1 and 10.
    
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
    "Color Coordination Theme Judge: rating of {color_coordination_rating}/10, credibility score is {color_coordination_credibility}\n"
    "Finally, to obtain a following rating, weigh each judge’s individual rating by their credibility score to obtain a final rating out of 10."
)
    
    #hardcode for demo
    creativity_credibility = feedback_dict["creativity_judge"][0]
    tech_fashion_credibility = feedback_dict["technical_fashion_sense_judge"][0]
    accuracy_theme_credibility = feedback_dict["accuracy_theme_judge"][0]
    color_coordination_credibility = feedback_dict["color_coordination_theme_judge"][0]

    creativity_rating = feedback_dict["creativity_judge"][1]
    tech_fashion_rating = feedback_dict["technical_fashion_sense_judge"][1]
    accuracy_theme_rating = feedback_dict["accuracy_theme_judge"][1]
    color_coordination_rating = feedback_dict["color_coordination_theme_judge"][1]

    
    formatted_synthesizer_prompt = synthesizer_prompt.format(
    creativity_rating=creativity_rating,
    creativity_credibility=creativity_credibility,
    tech_fashion_rating=tech_fashion_rating,
    tech_fashion_credibility=tech_fashion_credibility,
    accuracy_theme_rating=accuracy_theme_rating,
    accuracy_theme_credibility=accuracy_theme_credibility,
    color_coordination_rating=color_coordination_rating,
    color_coordination_credibility=color_coordination_credibility
)


    synthesized_judgement = openai.Completion.create(
    engine="text-davinci-003",  # You can change this to any model, such as gpt-3.5-turbo
    prompt=formatted_synthesizer_prompt,
    max_tokens=100
)
    print("FINAL JUDGEMENT: \n" + synthesized_output)

    feedback = input("Input ground-truth feedback about the outfit. Be detailed.")


    #TODO: Call to OpenAI API to check, for every LLM judge,
    #is this feedback at odds with the LLM's feedback? Does it align? How or how not? 
    #Rate it out of 10, and return only the number.

    for llm_judge in feedback_dict:
        eval_prompt = ("Is the feedback with this LLM judge at odds "
                       "with the user-defined ground truth? How or how not? Return only a number from 1-10, "
                       "where 1 means the LLM judge totally was at odds with the feedback, or 10, if it was spot on.")
         
        old_cred = feedback_dict[llm_judge][0]
        new_cred = adjust_credibility(old_cred)
        feedback_dict["creativity_judge"] = (new_cred, new_)

    return synthesized


# Test

# Dictionary to store weighted feedbacks
 # TODO: set to default credibility level

feedback_dict = {
    "creativity_judge": (0.25, 8),
    "technical_fashion_sense_judge": (0.25, 6),
    "accuracy_theme_judge": (0.25, 8),
    "color_coordination_theme_judge": (0.25, 9)
}
    
synthesized_output = synthesize_feedback_and_scale_credibility(judges_feedback, feedback_dict)
print(synthesized_output)
