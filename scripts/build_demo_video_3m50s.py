import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import shutil

def build_demo_video_3m50s():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ref_path = 'C:/Users/paddu/Downloads/Untitled video-10_9_2026, 7_32\u202fPM.mp4'
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    work_dir = os.path.join(project_root, "showcase", "assets", "video_build_3m50s")
    os.makedirs(work_dir, exist_ok=True)
    
    TARGET_TOTAL_SEC = 230.0  # Exactly 3 minutes 50 seconds
    ORIG_TOTAL_SEC = 240.0
    SPEED_FACTOR = ORIG_TOTAL_SEC / TARGET_TOTAL_SEC  # ~1.043478
    
    PART1_ORIG_SEC = 200.0  # Scenes 1-10 (00:00 - 03:20)
    PART1_TARGET_SEC = PART1_ORIG_SEC / SPEED_FACTOR  # ~191.667s
    PART2_TARGET_SEC = TARGET_TOTAL_SEC - PART1_TARGET_SEC  # ~38.333s
    CLIP_DURATION = PART2_TARGET_SEC / 4.0  # ~9.5833s each
    
    print(f"=== Video Timing Configuration (3m 50s Target) ===")
    print(f"Total Target Duration: {TARGET_TOTAL_SEC:.2f}s (3m 50s)")
    print(f"Audio Tempo Factor:    {SPEED_FACTOR:.6f}")
    print(f"Part 1 Video Duration: {PART1_TARGET_SEC:.2f}s")
    print(f"Part 2 Video Duration: {PART2_TARGET_SEC:.2f}s (4 clips @ {CLIP_DURATION:.2f}s each)")
    print("===================================================")
    
    # Step 1: Process and speed up audio
    print("\n--- Step 1: Generating 230.0s Stereo Audio ---")
    audio_out = os.path.join(work_dir, "audio_230s.m4a").replace("\\", "/")
    if not os.path.exists(audio_out):
        subprocess.run([
            ffmpeg_exe, "-y", "-i", ref_path,
            "-vn", "-filter:a", f"atempo={SPEED_FACTOR:.8f}",
            "-c:a", "aac", "-b:a", "128k", "-ac", "2",
            audio_out
        ], check=True)
    print("Audio ready!")
    
    # Step 2: Extract & speed up Part 1 Video
    print("\n--- Step 2: Generating Part 1 Video Stream ---")
    part1_out = os.path.join(work_dir, "part1_video.mp4").replace("\\", "/")
    if not os.path.exists(part1_out):
        subprocess.run([
            ffmpeg_exe, "-y", "-ss", "0", "-t", str(PART1_ORIG_SEC), "-i", ref_path,
            "-an", "-vf", f"setpts={1.0/SPEED_FACTOR:.8f}*PTS,scale=1920:1080,fps=30",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            part1_out
        ], check=True)
    print("Part 1 video ready!")
    
    # Step 3: Prepare Outro Slide for Part 2
    print("\n--- Step 3: Preparing Part 2 Visual Assets ---")
    scada_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab2_scada.png").replace("\\", "/")
    radar_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab3_radar.png").replace("\\", "/")
    disp_img = os.path.join(project_root, "showcase", "assets", "screenshots", "screenshot_tab4_analytics.png").replace("\\", "/")
    
    # Frame for outro
    eval_orig_path = os.path.join(work_dir, "frame_185s.jpg").replace("\\", "/")
    if not os.path.exists(eval_orig_path):
        subprocess.run([ffmpeg_exe, "-y", "-ss", "185", "-i", ref_path, "-frames:v", "1", "-update", "1", "-q:v", "2", eval_orig_path], check=True)
        
    eval_orig = Image.open(eval_orig_path).convert("RGBA")
    eval_orig = eval_orig.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # Banner overlay
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
    
    # Step 4: Generate 4 animated clips for Part 2
    print("\n--- Step 4: Generating 4 Animated Clips for Part 2 ---")
    clip_frames = int(CLIP_DURATION * 30)
    
    clip1_mp4 = os.path.join(work_dir, "clip1_scada.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", scada_img,
        "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d={clip_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", f"{CLIP_DURATION:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", clip1_mp4
    ], check=True)
    
    clip2_mp4 = os.path.join(work_dir, "clip2_radar.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", radar_img,
        "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d={clip_frames}:x='iw/2-(iw/zoom/2)+10':y='ih/2-(ih/zoom/2)+10':s=1920x1080:fps=30",
        "-t", f"{CLIP_DURATION:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", clip2_mp4
    ], check=True)
    
    clip3_mp4 = os.path.join(work_dir, "clip3_disp.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", disp_img,
        "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0005,1.06)':d={clip_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", f"{CLIP_DURATION:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", clip3_mp4
    ], check=True)
    
    clip4_mp4 = os.path.join(work_dir, "clip4_outro.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-loop", "1", "-i", outro_img,
        "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0003,1.04)':d={clip_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
        "-t", f"{CLIP_DURATION:.4f}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", clip4_mp4
    ], check=True)
    
    # Step 5: Combine Part 2
    print("\n--- Step 5: Combining Part 2 ---")
    concat_list = os.path.join(work_dir, "part2_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{clip1_mp4}'\n")
        f.write(f"file '{clip2_mp4}'\n")
        f.write(f"file '{clip3_mp4}'\n")
        f.write(f"file '{clip4_mp4}'\n")
        
    part2_out = os.path.join(work_dir, "part2_video.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", part2_out
    ], check=True)
    
    # Step 6: Concatenate Part 1 + Part 2
    print("\n--- Step 6: Combining Part 1 and Part 2 Video ---")
    full_list = os.path.join(work_dir, "full_video_list.txt")
    with open(full_list, "w", encoding="utf-8") as f:
        f.write(f"file '{part1_out}'\n")
        f.write(f"file '{part2_out}'\n")
        
    combined_video = os.path.join(work_dir, "full_video_noaudio.mp4").replace("\\", "/")
    subprocess.run([
        ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", full_list,
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", combined_video
    ], check=True)
    
    # Step 7: Final Mux with Audio & Web Compression (<50MB)
    print("\n--- Step 7: Final Muxing & Encoding to <50MB ---")
    final_output_repo = os.path.join(project_root, "showcase", "media", "GridOS_Demo_Video.mp4").replace("\\", "/")
    final_output_dl = "C:/Users/paddu/Downloads/GridOS_Demo_Video.mp4"
    
    subprocess.run([
        ffmpeg_exe, "-y", "-i", combined_video, "-i", audio_out,
        "-c:v", "libx264", "-preset", "veryfast",
        "-b:v", "1450k", "-maxrate", "1650k", "-bufsize", "2900k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "-shortest",
        final_output_repo
    ], check=True)
    
    shutil.copy2(final_output_repo, final_output_dl)
    
    size_mb = os.path.getsize(final_output_repo) / (1024 * 1024)
    print("\n=======================================================", flush=True)
    print("SUCCESS: 3m 50s DEMO VIDEO CREATED!", flush=True)
    print(f"• Repo Path:      {final_output_repo} ({size_mb:.2f} MB)", flush=True)
    print(f"• Downloads Path: {final_output_dl} ({size_mb:.2f} MB)", flush=True)
    print("=======================================================", flush=True)

if __name__ == "__main__":
    build_demo_video_3m50s()
