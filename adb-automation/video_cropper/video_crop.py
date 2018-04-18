from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
ffmpeg_extract_subclip("video1.mp4", 45*60+49, 2860, targetname="test.mp4")