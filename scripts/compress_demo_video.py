import imageio_ffmpeg
import subprocess
import os
import shutil

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
src_video = os.path.abspath("showcase/media/GridOS_Demo_Video.mp4")
temp_compressed = os.path.abspath("showcase/media/GridOS_Demo_Video_compressed.mp4")

dest_repo = os.path.abspath("showcase/media/GridOS_Demo_Video.mp4")
dest_dl = os.path.abspath("C:/Users/paddu/Downloads/GridOS_Demo_Video.mp4")

print(f"Source video size: {os.path.getsize(src_video)/(1024*1024):.2f} MB")
print("Target: Under 50 MB (approx 44 MB, 1080p, H.264, 1400 kbps video + 128 kbps audio)...")

cmd = [
    ffmpeg_exe, "-y",
    "-i", src_video,
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-b:v", "1400k",
    "-maxrate", "1600k",
    "-bufsize", "2800k",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-movflags", "+faststart",
    temp_compressed
]

subprocess.run(cmd, check=True)

size_mb = os.path.getsize(temp_compressed) / (1024 * 1024)
print(f"Compressed video size: {size_mb:.2f} MB")

if size_mb <= 50.0:
    # Overwrite destination files
    shutil.move(temp_compressed, dest_repo)
    shutil.copy2(dest_repo, dest_dl)
    print("Successfully replaced repo and downloads files!")
    print(f"Final Repo:      {dest_repo} ({os.path.getsize(dest_repo)/(1024*1024):.2f} MB)")
    print(f"Final Downloads: {dest_dl} ({os.path.getsize(dest_dl)/(1024*1024):.2f} MB)")
else:
    print("Warning: size is greater than 50 MB, further tuning required.")
