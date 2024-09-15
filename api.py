from flask import Flask, request, jsonify
from judges.synthesizer import synthesize_feedback
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        # Get data from the request
        data = request.json
        image_url = data.get('image_url')
        theme = data.get('theme')
        #print("preparing to call synthesize...")
        # Call the function from synthesizer.py
        feedback, avg_score = synthesize_feedback(image_url, theme)
        print("this is the score:")
        print(avg_score)
        # Return the result as JSON
        return jsonify({"feedback": feedback, "avg_score": avg_score})
        #return jsonify({"feedback": "heyyyyy"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
