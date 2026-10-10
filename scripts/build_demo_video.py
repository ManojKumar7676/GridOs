import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import shutil

def build_demo_video():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ref_path = 'C:/Users/paddu/Downloads/Untitled video-10_9_2026, 7_32\u202fPM.mp4'
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    work_dir = os.path.join(project_root, "showcase", "assets", "video_build")
    os.makedirs(work_dir, exist_ok=True)
    
    print("=== Step 1: Extracting full audio from reference video ===")
    audio_full = os.path.join(work_dir, "full_audio.m4a").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-i", ref_path,
        "-vn", "-c:a", "copy", audio_full
    ], check=True)
    print("Audio extracted successfully!")
    
    print("\n=== Step 2: Extracting Part 1 video stream (00:00 to 03:20 = 200s) ===")
    part1_mp4 = os.path.join(work_dir, "part1_200s.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-ss", "0", "-t", "200", "-i", ref_path,
        "-an", "-c:v", "copy", part1_mp4
    ], check=True)
    print("Part 1 video extracted successfully!")
    
    print("\n=== Step 3: Preparing High-Res Visual Assets for Part 2 (3:20 - 4:00) ===")
    scada_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab2_scada.png").replace("\\", "/")
    radar_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab3_radar.png").replace("\\", "/")
    disp_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab4_analytics.png").replace("\\", "/")
    
    # Path to frame 185s
    eval_orig_path = os.path.join(project_root, "showcase", "assets", "ref_inspection", "part1_samples", "frame_185s.jpg")
    if not os.path.exists(eval_orig_path):
        # fallback extract if needed
        subprocess.run([ffmpeg_exe, "-y", "-ss", "185", "-i", ref_path, "-vframes", "1", "-q:v", "2", eval_orig_path], check=True)
        
    eval_orig = Image.open(eval_orig_path).convert("RGBA")
    eval_orig = eval_orig.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # Semi-transparent bottom banner
    banner = Image.new("RGBA", (1920, 130), (11, 17, 32, 235))
    eval_orig.paste(banner, (0, 950), banner)
    
    draw = ImageDraw.Draw(eval_orig)
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except:
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((60, 965), "GridOS™ Core Architecture Team: ManojKumar P (Lead) • B Iniyavan • Nishi Verma • Pasupulati Siva Puja", fill=(248, 250, 252), font=font_bold)
    draw.text((60, 1005), "Open-Source Codebase, Automated Benchmark Suite & SCADA UI:  github.com/ManojKumar7676/GridOs", fill=(56, 189, 248), font=font_sub)
    
    outro_img = os.path.join(work_dir, "slide_outro_clean.png").replace("\\", "/")
    eval_orig.convert("RGB").save(outro_img, quality=95)
    print("Outro slide created!")
    
    print("\n=== Step 4: Generating smooth animated 1080p clips for Part 2 ===")
    clip1_mp4 = os.path.join(work_dir, "clip1_scada.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", scada_img,
        "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", "10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", clip1_mp4
    ], check=True)
    
    clip2_mp4 = os.path.join(work_dir, "clip2_radar.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", radar_img,
        "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d=300:x='iw/2-(iw/zoom/2)+10':y='ih/2-(ih/zoom/2)+10':s=1920x1080:fps=30",
        "-t", "10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", clip2_mp4
    ], check=True)
    
    clip3_mp4 = os.path.join(work_dir, "clip3_disp.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", disp_img,
        "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", "10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", clip3_mp4
    ], check=True)
    
    clip4_mp4 = os.path.join(work_dir, "clip4_outro.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", outro_img,
        "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0003,1.04)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", "10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", clip4_mp4
    ], check=True)
    print("All 4 clips generated!")
    
    print("\n=== Step 5: Concatenating Part 2 (40s) ===")
    concat_list = os.path.join(work_dir, "part2_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{clip1_mp4}'\n")
        f.write(f"file '{clip2_mp4}'\n")
        f.write(f"file '{clip3_mp4}'\n")
        f.write(f"file '{clip4_mp4}'\n")
        
    part2_mp4 = os.path.join(work_dir, "part2_40s.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", part2_mp4
    ], check=True)
    print("Part 2 combined!")
    
    print("\n=== Step 6: Concatenating Full Video (Part 1 + Part 2 = 240s) with Audio ===")
    full_list = os.path.join(work_dir, "full_video_list.txt")
    with open(full_list, "w", encoding="utf-8") as f:
        f.write(f"file '{part1_mp4}'\n")
        f.write(f"file '{part2_mp4}'\n")
        
    combined_video = os.path.join(work_dir, "full_video_noaudio.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", full_list,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", combined_video
    ], check=True)
    
    final_output_repo = os.path.join(project_root, "showcase", "media", "GridOS_Demo_Video.mp4").replace("\\", "/")
    final_output_dl = "C:/Users/paddu/Downloads/GridOS_Demo_Video.mp4"
    
    subprocess.run([
        ffmpeg_exe, "-y", "-i", combined_video, "-i", audio_full,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        final_output_repo
    ], check=True)
    
    shutil.copy2(final_output_repo, final_output_dl)
    
    print("\n=======================================================")
    print(f"🎉 FINAL DEMO VIDEO CREATED SUCCESSFULLY!")
    print(f"1. Repo Path:      {final_output_repo} ({os.path.getsize(final_output_repo)/(1024*1024):.2f} MB)")
    print(f"2. Downloads Path: {final_output_dl} ({os.path.getsize(final_output_dl)/(1024*1024):.2f} MB)")
    print("=======================================================")

if __name__ == "__main__":
    build_demo_video()
