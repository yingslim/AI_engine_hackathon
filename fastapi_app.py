import base64
import json
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from io import BytesIO
import anthropic

app = FastAPI()

# Set up your Claude API key
API_KEY = "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"
client = anthropic.Anthropic(api_key=API_KEY)

# ElevenLabs API key
ELEVENLABS_API_KEY = "sk_f32763bd38562304978d5ebe96c54d3a2f098e50cc238fd7"  # Replace with your actual API key

@app.post("/process_pdf")
async def process_pdf(pdf: UploadFile = File(...)):
    try:
        # Read the uploaded PDF file
        pdf_data = await pdf.read()

        # Encode the PDF in Base64
        encoded_pdf_data = base64.b64encode(pdf_data).decode("utf-8")

        # Step 1: Send the PDF to Claude for processing
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
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
                            "text": "Convert the pdf content to a conversational style speech for 2 minutes and include the main points of the document. I am using Peter Griffin as the speaker, so make it align with his character without losing the main findings of the content. Include jokes to make it entertaining as well. Do not add the tone of the voice or expressions in asterisks**."
                        }
                    ]
                }
            ]
        )

        # Step 2: Get the processed text from Claude
        cleaned_text = message.content[0].text.replace("\'", "").strip()

        # Step 3: Send the processed text to ElevenLabs for text-to-speech
        url = "https://api.elevenlabs.io/v1/text-to-speech/595KJIE4EJo8CDdtxwud?output_format=mp3_44100_128"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": cleaned_text,
            "model_id": "eleven_multilingual_v2"
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Step 4: Check if ElevenLabs request is successful
        if response.status_code == 200:
            # Return the audio file as a response
            audio_file = BytesIO(response.content)
            audio_file.seek(0)
            return FileResponse(audio_file, media_type="audio/mpeg", filename="output.mp3")
        else:
            return {"success": False, "message": "Failed to generate audio from ElevenLabs"}

    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
