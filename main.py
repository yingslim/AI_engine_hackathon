from flask import Flask, render_template, request, jsonify
import base64
import json
import requests
from io import BytesIO
import os

import google.generativeai as genai


app = Flask(__name__)

# API Keys
API_KEY = "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"
ELEVENLABS_API_KEY = "sk_f32763bd38562304978d5ebe96c54d3a2f098e50cc238fd7"

# Set up Claude and ElevenLabs clients here
# For Claude API, you'll need to install anthropic or similar libraries
import anthropic
client = anthropic.Anthropic(api_key=API_KEY)

@app.route('/')
def index():
    return render_template('./index.html')  # We will create this HTML file


@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        # Handle file upload
        file = request.files['pdf']
        pdf_data = file.read()

        # Encode the PDF in Base64
        encoded_pdf_data =  base64.b64encode(pdf_data).decode('utf-8') # extract_text_from_pdf(pdf_data) #
        print(f"PDF Data Length: {len(encoded_pdf_data)}")  # Debug log

        # Get the instructions text from the form (ensure this is provided correctly in your form)
        instructions_text = request.form.get('instructions', 'Convert the pdf content to a conversational style speech for 2 minutes and include the main points of the document. Include jokes to make it entertaining as well. Do not add the tone of the voice or expressions in asterisks**. Goal is to make the content as fun and entertaining as possible.')

        # Debug log to confirm instructions text
        print(f"Instructions Text: {instructions_text}")

        # Send to Claude API for processing
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": encoded_pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": instructions_text    
                    }
                ]
            }]
        )
        print(f"Claude API Response: {message}")  # Debug log for Claude response

        # Get the text from Claude's response
        cleaned_text = message.content[0].text.strip()

        # Send to ElevenLabs API for text-to-speech
        url = "https://api.elevenlabs.io/v1/text-to-speech/PEEHDNaPqPa8rtKdChQc?output_format=mp3_44100_128"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": cleaned_text,
            "model_id": "eleven_multilingual_v2"
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"ElevenLabs Response Status Code: {response.status_code}")  # Debug log for ElevenLabs response
        print(f"ElevenLabs Response Content: {response.content}")  # Debug log for ElevenLabs content

        if response.status_code == 200:
            audio_file = BytesIO(response.content)
            audio_file.seek(0)

            # Generate simple subtitles
            subtitles = generate_subtitles(cleaned_text)

            # Ensure the directory exists
            if not os.path.exists('components'):
                os.makedirs('components')

            # Save the audio file
            audio_path = os.path.join('components', 'output.mp3')
            with open(audio_path, 'wb') as f:
                f.write(response.content)

            # Return audio and subtitle information
            return jsonify({
                'audio_url': f"/components/{audio_path}",
                'subtitles': subtitles
            })
        else:
            return jsonify({"success": False, "message": "Failed to generate audio from ElevenLabs"}), 500

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return jsonify({"success": False, "message": str(e)}), 500

# Helper function to generate simple subtitles (sentence-based)
def generate_subtitles(text):
    sentences = text.split('.')
    subtitles = []
    sentence_duration = 5  # Adjust based on audio length or use another method to calculate

    current_time = 0.0
    for sentence in sentences:
        if sentence.strip():
            subtitles.append({
                "start": current_time,
                "end": current_time + sentence_duration,
                "text": sentence.strip() + "."
            })
            current_time += sentence_duration

    return subtitles

if __name__ == "__main__":
    app.run(debug=True)