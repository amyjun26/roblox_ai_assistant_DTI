from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

# Endpoint to run each judge's script and return their results
@app.route('/api/judges_responses', methods=['GET'])
def get_judges_responses():
    responses = []

    try:
        # Run each judge's Python file using subprocess and capture their output
        color_response = subprocess.check_output(['python', 'color-coordination-judge.py']).decode('utf-8')
        creativity_response = subprocess.check_output(['python', 'creativity-judge.py']).decode('utf-8')
        technical_response = subprocess.check_output(['python', 'technical-fashion-judge.py']).decode('utf-8')
        theme_response = subprocess.check_output(['python', 'accuracy_theme_judge.py']).decode('utf-8')

        # Collect responses from all the judges
        responses.append({"judge": "Color Judge", "feedback": color_response})
        responses.append({"judge": "Creativity Judge", "feedback": creativity_response})
        responses.append({"judge": "Technical Fashion Judge", "feedback": technical_response})
        responses.append({"judge": "Theme Accuracy Judge", "feedback": theme_response})

    except subprocess.CalledProcessError as e:
        # Handle script execution errors
        responses.append({"error": f"Error executing judge scripts: {str(e)}"})

    # Return as JSON
    return jsonify(responses)

if __name__ == "__main__":
    app.run(debug=True)
