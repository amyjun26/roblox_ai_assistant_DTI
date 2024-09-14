import openai
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def evaluate_outfit(image_url, theme):
    prompt = (f"You are a fashion judge for the Roblox game 'Dress To Impress.' Based on the theme {theme} and following guiding questions, provide detailed, objective feedback along with a specific numerical rating out of 10, where 10 is the best.\n"
              f"Guiding Questions:\n"
              f"1. Does this outfit feature unique and innovative design elements?\n"
              f"2. How does the outfit push boundaries or experiment with fashion norms?\n"
              f"3. How different is this outfit from the theme?\n"
              f"4. Can you suggest an outfit piece that still fits within the theme, but also spices up the outfit a bit more in a creative way to elevate its themed style?\n\n"
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

