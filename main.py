import moviepy.editor as mp
import whisper
import os
from moviepy.config import change_settings
from dotenv import load_dotenv
import textwrap

load_dotenv()

image_magick_path = os.getenv('IMAGEMAGICK_BINARY')
change_settings({"IMAGEMAGICK_BINARY": image_magick_path})

def list_videos(directory):
    return [f for f in os.listdir(directory) if f.endswith('.mp4')]

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

def generate_subtitles(audio_path, subtitle_path, words_per_segment=4):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    
    with open(subtitle_path, 'w') as f:
        for segment in result['segments']:
            start = segment['start']
            end = segment['end']
            text = segment['text'].replace('\n', ' ')
            words = text.split()
            
            # Split text into smaller segments
            wrapped_lines = textwrap.wrap(text, width=words_per_segment * 10)
            segment_duration = (end - start) / len(wrapped_lines)
            
            for i, line in enumerate(wrapped_lines):
                segment_start = start + i * segment_duration
                segment_end = segment_start + segment_duration
                f.write(f"{segment_start:.3f} --> {segment_end:.3f}\n{line}\n\n")

def add_subtitles(video_path, subtitle_path, output_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    subs = []
    with open(subtitle_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 3):
            start = float(lines[i].split()[0])
            end = float(lines[i].split()[2])
            text = lines[i+1].strip()
            subs.append(mp.TextClip(text, fontsize=40, color='white', bg_color='black').set_position(('center', 'center')).set_duration(end - start).set_start(start))

    final_video = mp.CompositeVideoClip([video] + subs)
    final_video = final_video.set_audio(audio)
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

def main():
    input_directory = "InputVideo"
    output_directory = "Output"

    videos = list_videos(input_directory)
    if not videos:
        print("No videos found in the InputVideo directory.")
        return
    
    print("Choose a video to add subtitles to:")
    for i, video in enumerate(videos):
        print(f"[{i}] {video}")

    choice = int(input("Enter the index of the video: "))
    if choice < 0 or choice >= len(videos):
        print("Invalid choice.")
        return
    
    video_path = os.path.join(input_directory, videos[choice])
    video_title, video_ext = os.path.splitext(videos[choice])
    output_title = video_title + "wSubtitles"
    output_path = os.path.join(output_directory, output_title + video_ext)

    index = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_directory, f"{output_title}_{index}{video_ext}")
        index += 1
    
    audio_path = "temp_audio.wav"
    subtitle_path = "temp_subs.srt"
    
    extract_audio(video_path, audio_path)
    generate_subtitles(audio_path, subtitle_path, words_per_segment=4)
    add_subtitles(video_path, subtitle_path, output_path)
    
    os.remove(audio_path)
    os.remove(subtitle_path)

if __name__ == "__main__":
    main()
