from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import google.generativeai as genai
import json
import re

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

API_KEY = 'AIzaSyCaUiFv6X4DuUx2Lk84_Pg1-j27NymfDHc'  # Replace this with your actual API key
genai.configure(api_key=API_KEY)

@app.route('/')
def home():
    return "Welcome to the Vurbalize API using GeminiAI!"

@app.route('/generate-poem', methods=['POST'])
def generate_poem():
    data = request.get_json()
    prompt = data.get('prompt', 'Write a poem about the beauty of nature.')

    try:
        # Generate the poem
        response = genai.generate_text(model="models/text-bison-001", prompt=prompt)
        poem = response.result if hasattr(response, 'result') else response.candidates[0]

        # Emotion analysis prompt
        analysis_prompt = (
            f"Analyze the following poem and provide a list of emotions detected along with their percentages.(provide it in form of JSON in double inverted commas) "
            f"Format the result as a JSON array of objects with 'label' and 'percentage' properties. Here is the poem: "
            f"{poem}"
        )
        print("Emotion Analysis Prompt:", analysis_prompt)

        analysis_response = genai.generate_text(model="models/text-bison-001", prompt=analysis_prompt)
        emotions_raw = analysis_response.result if hasattr(analysis_response, 'result') else analysis_response.candidates[0]

        # Sanitize and handle response
        print("Raw Emotion Analysis Response:", repr(emotions_raw))
        emotions_raw = sanitize_json_response(emotions_raw)

        # Handle response
        emotions = parse_emotions(emotions_raw)
        formatted_poem = f"<h2>Generated Poem</h2><p style='font-style: italic;'>{poem}</p>"

        return jsonify({"text": formatted_poem, "emotions": emotions})

    except Exception as e:
        print("Error in /generate-poem:", str(e))
        return jsonify({"error": str(e)}), 500

def sanitize_json_response(raw_response):
    # Remove code block markers and extra newlines
    cleaned_response = re.sub(r'^```json|```$', '', raw_response).strip()
    # Remove extra newlines or spaces
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    return cleaned_response

def parse_emotions(emotions_raw):
    print("Parsing Emotion Analysis Response:", repr(emotions_raw))
    try:
        # Ensure the cleaned string starts with '[' or '{' to be valid JSON
        if emotions_raw.startswith('{') or emotions_raw.startswith('['):
            emotions = json.loads(emotions_raw)
        else:
            raise ValueError("Invalid JSON format")

    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing error: {e}")
        emotions = []  # Default to empty list in case of error
    

    print("Detected Emotions:", emotions)
    return emotions

@socketio.on('stream_text')
def handle_text_stream(data):
    prompt = data.get('prompt', '')

    if not prompt:
        emit('error', {'error': 'No prompt provided'})
        return

    try:
        # Generate the poem
        response = genai.generate_text(model="models/text-bison-001", prompt=prompt)
        poem = response.result if hasattr(response, 'result') else response.candidates[0]

        # Emotion analysis prompt
        analysis_prompt = (
            f"Analyze the following poem and provide a list of emotions detected along with their percentages. "
            f"Format the result as a JSON array of objects with 'label' and 'percentage' properties. Here is the poem: "
            f"{poem}"
        )
        print("Emotion Analysis Prompt:", analysis_prompt)

        analysis_response = genai.generate_text(model="models/text-bison-001", prompt=analysis_prompt)
        emotions_raw = analysis_response.result if hasattr(analysis_response, 'result') else analysis_response.candidates[0]

        print("Raw Emotion Analysis Response:", repr(emotions_raw))
        emotions_raw = sanitize_json_response(emotions_raw)

        # Handle response
        emotions = parse_emotions(emotions_raw)

        # Stream the poem text line by line
        lines = poem.split('\n')
        for line in lines:
            emit('text_stream', {'text': line})

        # Emit emotion analysis
        emit('emotion_analysis', {'emotions': emotions})

    except Exception as e:
        print("Error in WebSocket:", str(e))
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)
