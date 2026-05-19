import subprocess


def convert_video_resolution(source='', resolution='480'):
    target = f"{source[:-4]}_{resolution}.mp4"
    cmd = f'ffmpeg -i "{source}" -s hd{resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd)