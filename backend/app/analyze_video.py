import os
import cv2
import asyncio
from moviepy.editor import VideoFileClip
from transformers import pipeline
from ultralytics import YOLO
import openai
from deepgram import Deepgram
from app.config import DEEPGRAM_API_KEY, OPENAI_API_KEY

# Initialize Deepgram and Models
deepgram = Deepgram(DEEPGRAM_API_KEY)
bert_model = pipeline("text-classification", model="unitary/toxic-bert")  # BERT for hate speech detection
yolo_model = YOLO("yolov8n.pt")  # YOLO for violent imagery detection (lightweight model)
openai.api_key = OPENAI_API_KEY

def analyze_video(file_path):
    try:
        # Step 1: Extract audio from video
        audio_path = extract_audio_from_video(file_path)

        # Step 2: Analyze audio
        paragraph, audio_issues = asyncio.run(analyze_audio(audio_path))

        # Step 3: Analyze video
        video_issues = analyze_video_frames(file_path)

        # Step 4: Combine issues and generate response
        issues_list = create_issues_list(audio_issues, video_issues)
        summary = generate_summary(paragraph)
        sentiment = generate_sentiment(paragraph)

        return {
            "issues": issues_list,  # Combined issues as per the requirement
            "summary": summary,      # Full summary text
            "sentiment": sentiment,
        }

    except Exception as e:
        print(f"Error analyzing video: {e}")
        return {"error": "Error analyzing video"}

# Step 1: Extract audio from video
def extract_audio_from_video(video_path):
    try:
        video = VideoFileClip(video_path)
        audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
        video.audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        raise

# Step 2: Analyze audio
async def analyze_audio(audio_path):
    try:
        # Transcribe audio
        transcription, paragraph = await transcribe_audio(audio_path)
        print("In Analyze audio", transcription, paragraph)

        # Detect issues in transcription
        audio_issues = detect_audio_issues(transcription)

        return paragraph, audio_issues
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        raise

async def transcribe_audio(file_path):
    try:
        source = {
            'buffer': open(file_path, 'rb'),
            'mimetype': 'audio/mpeg'
        }
        options = {
            'punctuate': True,
            'paragraphs': True,
            'timestamps': True
        }
        response = await deepgram.transcription.prerecorded(source, options)
        transcript = response['results']['channels'][0]['alternatives'][0]['words']
        paragraph = " ".join([word['word'] for word in transcript])
        return transcript, paragraph  # List of words with timestamps
    except Exception as e:
        print(f"Error with Deepgram transcription: {e}")
        raise

def detect_audio_issues(transcription):
    issues = []
    pause_threshold = 2.0  # Seconds
    disallowed_categories = ["toxic", "hate", "violence", "threat"]  # Categories to flag
    last_word_end = 0

    # Detect long pauses
    for word in transcription:
        start_time = word['start']
        end_time = word['end']

        if start_time - last_word_end > pause_threshold:
            issues.append({
                "issue": "Long pause",
                "timestamp": format_time(start_time)
            })

        last_word_end = end_time

    # Combine words into sentences for classification
    sentences = group_words_into_sentences(transcription)
    for sentence, start_time in sentences:
        result = bert_model(sentence)[0]  # Use BERT model for classification
        print("Bert Model Response", result)
        if result['label'].lower() in disallowed_categories and result['score'] > 0:  # Confidence threshold
            issues.append({
                "issue": "Hate speech detected",
                "timestamp": format_time(start_time)
            })
    print("In  detect audio issues" ,issues)
    return issues

def group_words_into_sentences(transcription):
    """Group words into sentences with start time."""
    sentences = []
    current_sentence = []
    start_time = None

    for word in transcription:
        if start_time is None:
            start_time = word['start']
        current_sentence.append(word['word'])

        # Group into sentences based on punctuation or max words
        if word['word'].endswith(('.', '!', '?')) or len(current_sentence) >= 15:
            sentences.append((' '.join(current_sentence), start_time))
            current_sentence = []
            start_time = None

    if current_sentence:  # Add remaining sentence
        sentences.append((' '.join(current_sentence), start_time))

    return sentences

# Step 3: Analyze video frames
def analyze_video_frames(video_path):
    issues = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return issues

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Default to 30 FPS if FPS is invalid
    frame_skip = fps  # Analyze one frame per second

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Total Frames: {total_frames}, FPS: {fps}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Skip frames to process only one per second
        if frame_count % frame_skip == 0:
            timestamp = frame_count / fps
            if is_frame_violent(frame):
                issues.append({
                    "issue": "Violent imagery detected",
                    "timestamp": format_time(timestamp)
                })

        frame_count += 1
    print("Inside analyze video frames", issues)

    cap.release()
    return issues

def is_frame_violent(frame):
    # Perform inference
    results = yolo_model(frame, conf=0.4)  # YOLO inference on the frame
    detections = results[0].boxes  # Updated structure for YOLO's results
    
    # Check each detection
    for detection in detections:
        class_id = int(detection.cls)  # Get the class ID
        class_name = yolo_model.names[class_id]  # Map class ID to class name
        print("Yolo Class found is: ", class_name)
        if class_name in ["knife", "gun", "blood"]:  # Violent objects to flag
            return True
    return False

# Step 4: Combine issues into a single list
def create_issues_list(audio_issues, video_issues):
    issues_list = []
    print("In list creation", audio_issues, video_issues)

    # Add audio issues to the list
    for issue in audio_issues:
        issues_list.append(f"{issue['issue']} detected at {issue['timestamp']} ")

    # Add video issues to the list
    for issue in video_issues:
        issues_list.append(f"{issue['issue']} detected at {issue['timestamp']} ")

    return issues_list

# Updated Summary Generator
def generate_summary(transcription):
    try:
        # Generate a text summary of the transcription (using OpenAI or another summarization method)
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
        print("In summary", transcription, summary)
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
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
        print("In sentiment generation", transcription, sentiment)
        # Post-process: Validate and reduce to a single word
        sentiment = sentiment.split()[0].lower()  # Ensure it's one word and lowercase for consistency
        print(f"Sentiment: {sentiment}")
        return sentiment
    except Exception as e:
        print("Error generating sentiment:", e)
        raise

# Helper function to format timestamps
def format_time(seconds):
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"
