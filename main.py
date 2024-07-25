import moviepy.editor as mp
import whisper
import os
import sys
from moviepy.config import change_settings
from dotenv import load_dotenv

load_dotenv()

# Load and print the path to verify it's being read correctly
image_magick_path = os.getenv('IMAGEMAGICK_BINARY')
if image_magick_path is None:
    print("Error: IMAGEMAGICK_BINARY environment variable not set.")
else:
    print(f"ImageMagick path: {image_magick_path}")

change_settings({"IMAGEMAGICK_BINARY": image_magick_path})

def list_videos(directory):
    return [f for f in os.listdir(directory) if f.endswith('.mp4')]

def extract_audio(video_path, audio_path):
    try:
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path)
    except Exception as e:
        print(f"Error extracting audio: {e}")
        sys.exit(1)

def generate_subtitles(audio_path, subtitle_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        with open(subtitle_path, 'w') as f:
            for segment in result['segments']:
                start = segment['start']
                end = segment['end']
                print(f"Segment: {start} - {end}")

                words = segment['words']
                
                for i, word in enumerate(words):
                    word_start = word['start']
                    word_end = word['end']
                    text = word['word']
                    print(f"Word: {text}, Start: {word_start}, End: {word_end}")
                    f.write(f"{word_start:.3f} --> {word_end:.3f}\n{text.strip()}\n\n")
    except Exception as e:
        print(f"Error generating subtitles: {e}")
        sys.exit(1)

def add_subtitles(video_path, subtitle_path, output_path, font="Arial"):
    try:
        video = mp.VideoFileClip(video_path)
        print(f"Original video size: {video.size}")
        
        # Resizing the video for TikTok format (1080x1920)
        resized_video = video.resize(height=1920)
        resized_video = resized_video.crop(x_center=resized_video.w/2, y_center=resized_video.h/2, width=1080, height=1920)
        
        print(f"Resized video size: {resized_video.size}")
        
        audio = video.audio
        subs = []
        with open(subtitle_path, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 3):
                start = float(lines[i].split()[0])
                end = float(lines[i].split()[2])
                text = lines[i+1].strip()
                subs.append(mp.TextClip(text, fontsize=60, color='white', stroke_color='black', stroke_width=3, font=font).set_position(('center', 'center')).set_duration(end - start).set_start(start))

        final_video = mp.CompositeVideoClip([resized_video] + subs)
        final_video = final_video.set_audio(audio)

        print(f"Writing video to {output_path}")
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        print(f"Video written to {output_path}")
    except Exception as e:
        print(f"Error adding subtitles or writing video: {e}")
        sys.exit(1)

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
    generate_subtitles(audio_path, subtitle_path)
    add_subtitles(video_path, subtitle_path, output_path, font="Arial")  # Change "Arial" to your desired font
    
    print("Cleaning up temporary files...")
    try:
        os.remove(audio_path)
        os.remove(subtitle_path)
        print("Cleanup complete.")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
