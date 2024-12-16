from moviepy import VideoFileClip

def process_video_to_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    video.audio.write_audiofile(audio_path)
    return audio_path
