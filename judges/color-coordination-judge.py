import openai

def evaluate_outfit(image_url, theme):
    prompt = (f"You are a fashion judge for the Roblox game 'Dress To Impress.' Based on the theme {theme} and following guiding questions, provide detailed, objective feedback along with a specific numerical rating out of 10, where 10 is the best.\n"
              f"Guiding Questions:\n"
              f"1. Are the colors in this outfit complementary or harmonious?\n"
              f"2. Do the color choices enhance the overall aesthetic appeal of the outfit?\n"
              f"3. Is there a balance between bright and neutral tones in this design?\n"
              f"4. Is there a color that better suits the mood and theme?\n"
              f"5. “In the context of the theme, evaluate how the skin tone matches with the color and style of the clothes?\n"
              f"Image URL: {image_url}\n\n"
              f"Please provide the feedback and the rating in the following format:\n"
              f"Feedback: [Your detailed feedback here]\n"
              f"Rating: [Your rating out of 10]")

    response = openai.Completion.create(
        engine="text-davinci-003",  # which model to use???
        prompt=prompt,
        max_tokens=150
    )

    result_text = response.choices[0].text.strip()
    
    # Extract feedback and rating
    try:
        feedback, rating = result_text.split('Rating:')
        feedback = feedback.strip().replace('Feedback:', '').strip()
        rating = rating.strip()
        # Ensure rating is an integer
        rating = int(rating) if rating.isdigit() else None
    except ValueError:
        feedback = result_text
        rating = None

    return feedback, rating

