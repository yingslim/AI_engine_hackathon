from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

FASTAPI_URL = "http://127.0.0.1:8000/process_pdf"  # Update if your FastAPI backend is hosted elsewhere

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify({"success": False, "message": "No PDF file part"})
    
    pdf_file = request.files['pdf']
    voice_id = request.form.get('voice_id', 'default_voice')  # Example: Get voice id (you can adjust this as needed)
    
    if pdf_file.filename == '':
        return jsonify({"success": False, "message": "No selected file"})
    
    # Send the PDF to your FastAPI backend
    files = {'pdf': (pdf_file.filename, pdf_file.stream, pdf_file.content_type)}
    response = requests.post(FASTAPI_URL, files=files, data={'voice_id': voice_id})
    
    if response.status_code == 200:
        # Process the response from FastAPI (return audio URL and subtitles)
        result = response.json()
        audio_url = result.get('audio_url')
        subtitles = result.get('subtitles')
        audio_duration = result.get('audio_duration')
        return render_template('index.html', audio_url=audio_url, subtitles=subtitles, audio_duration=audio_duration)
    else:
        return jsonify({"success": False, "message": "Error from backend"})

if __name__ == '__main__':
    app.run(debug=True)
