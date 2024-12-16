import requests
import json
from app.config import DEEPGRAM_API_KEY

def process_with_deepgram(audio_path):
    # Deepgram API endpoint for transcription
    url = "https://api.deepgram.com/v1/listen?access_token=" + DEEPGRAM_API_KEY

    # Open the audio file
    with open(audio_path, 'rb') as audio_file:
        headers = {
            'Authorization': f'Bearer {DEEPGRAM_API_KEY}',
            'Content-Type': 'audio/wav'  # Assuming the audio file is in WAV format
        }
        response = requests.post(url, headers=headers, data=audio_file)

    if response.status_code == 200:
        # Parse the JSON response from Deepgram
        result = response.json()
        # Extract the transcription from the result
        transcription = result['results']['channels'][0]['alternatives'][0]['transcript']
        return transcription
    else:
        print(f"Deepgram API Error: {response.status_code} - {response.text}")
        return None
