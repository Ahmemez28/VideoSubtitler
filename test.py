import moviepy.editor as mp
from moviepy.video.tools.drawing import color_split

# Create a white background clip
background = mp.ColorClip(size=(1920, 1080), color=(255, 255, 255), duration=1)

# Define the text properties
text = "test"
fontsize_fg = 120  # Font size for foreground text (white)
fontsize_bg = 120  # Font size for background text (black)
font = "Arial-Bold"

# Create the background text clip (black text, larger fontsize)
bg_text_clip = mp.TextClip(text, fontsize=fontsize_bg, color='black', font=font,stroke_color='black',stroke_width=15)
bg_text_clip = bg_text_clip.set_position(('center', 'center')).set_duration(1)

# Create the foreground text clip (white text)
fg_text_clip = mp.TextClip(text, fontsize=fontsize_fg, color='white', font=font)
fg_text_clip = fg_text_clip.set_position(('center', 'center')).set_duration(1)

# Composite the text clips onto the background
final_clip = mp.CompositeVideoClip([background, bg_text_clip, fg_text_clip])

# Write the final video to a file
final_clip.write_videofile("test_video.mp4", fps=24, codec='libx264')
