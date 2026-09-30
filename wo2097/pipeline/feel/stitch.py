"""Encode each film segment (out/film/<seg>/%05d.png) and join them in name order -> out/feel_flythrough_1080p30.mp4."""
import os, subprocess
H = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(H, 'out', 'film')
segs = sorted(d for d in os.listdir(F) if os.path.isdir(os.path.join(F, d)))
for d in segs:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(F, d, '%05d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-r', '30', os.path.join(F, d + '.mp4')], check=True)
open(os.path.join(F, 'list.txt'), 'w').write(''.join("file '%s.mp4'\n" % d for d in segs))
out = os.path.join(H, 'out', 'feel_flythrough_1080p30.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(F, 'list.txt'), '-c', 'copy', out], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,r_frame_rate:format=duration', '-of', 'compact', out],
                     capture_output=True, text=True).stdout)
