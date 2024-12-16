from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import asyncio
from app.analyze_video import analyze_video
from app.analyze_video import analyze_audio
from moviepy.editor import VideoFileClip
from deepgram import Deepgram
import openai
from app.config import OPENAI_API_KEY
from app.config import DEEPGRAM_API_KEY


upload_blueprint = Blueprint('upload', __name__)

deepgram = Deepgram(DEEPGRAM_API_KEY)
openai.api_key = OPENAI_API_KEY

# Function to check allowed file types
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename, {'mp4', 'mp3', 'wav'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        
        # Ensure the 'uploads' directory exists
        os.makedirs('uploads', exist_ok=True)
        
        # Save the file
        file.save(file_path)

        try:
            if(file.filename.endswith('.mp4')):
                mp3_path = convert_mp4_to_mp3(file_path)
                transcription = asyncio.run(transcribe_audio(mp3_path))
                sentiment = generate_sentiment(transcription)
                analysis_result = analyze_video(file_path)
                analysis_result['sentiment'] = sentiment
                print("The result received", analysis_result)
                return jsonify(analysis_result)
            # Transcribe audio using Deepgram
            # transcription = asyncio.run(transcribe_audio(file_path))
            transcription, audio_issues = asyncio.run(analyze_audio(file_path))
            formatted_issues = format_issues(audio_issues)

            summary = generate_summary(transcription)
            sentiment = generate_sentiment(transcription)
            response = {
                'issues' : formatted_issues,
                'summary' : summary,
                'sentiment' : sentiment
            }
            print("Result for audio file:", response)
            return jsonify(response)
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return jsonify({'error': 'Error transcribing audio'}), 500

    return jsonify({'error': 'File type not allowed'}), 400

# Function to transcribe audio using Deepgram
async def transcribe_audio(file_path):
    try:
        file_extension = file_path.rsplit('.', 1)[1].lower()
        mimetypes = {
            'mp3' : 'audio/mpeg',
            'wav' : 'audio/wav',
        }
        mimetype = mimetypes.get(file_extension)

        if not mimetype:
            raise ValueError(f"Unsupported file type: {file_extension}")
        source = {
            'buffer' : open(file_path, 'rb'),
            'mimetype' : mimetype
        }
        transcription_options = {
            'punctuate'  : True,
            'paragraphs' : True,
        }

        response = await deepgram.transcription.prerecorded(source, transcription_options)
        transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript']
        return transcript
    except Exception as e:
        print(f"Error with Deepgram transcription: {e}")
        raise

def convert_mp4_to_mp3(mp4_path):
    try:
        video = VideoFileClip(mp4_path)
        mp3_path = mp4_path.rsplit('.', 1)[0]+".mp3"
        video.audio.write_audiofile(mp3_path)
        print(f"Converted MP4 to MP3: {mp3_path}")
        return mp3_path
    except Exception as e:
        print(f"Error converting the video file: {e}")
        raise


def generate_summary(transcription):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role" : "user",
                    "content" : f"Summarize the following text: \"{transcription}\""
                },
            ]
        )
        summary = response['choices'][0]['message']['content']
        print(f"Summary: {summary}")
        return summary
    except Exception as e:
        print("Error generating summary:", e)
        raise


def generate_sentiment(transcription):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Analyze the overall sentiment of the following text in one word only. "
                        f"Do not provide any explanation. Respond with a single word like happy, sad, angry, excited, neutral, etc. "
                        f"The text is: \"{transcription}\""
                    ),
                },
            ]
        )
        # Extract the content and ensure it's a single word
        sentiment = response['choices'][0]['message']['content'].strip()
        
        # Post-process: Validate and reduce to a single word
        sentiment = sentiment.split()[0].lower()  # Ensure it's one word and lowercase for consistency
        print(f"Sentiment: {sentiment}")
        return sentiment
    except Exception as e:
        print("Error generating sentiment:", e)
        raise

def format_issues(issues):
    formatted_issues = []
    for issue in issues:
        formatted_issues.append(f"{issue['issue'].capitalize()} at {issue['timestamp']}")
    return formatted_issues