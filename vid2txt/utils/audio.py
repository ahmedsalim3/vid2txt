from pathlib import Path
import ffmpeg

def extract_audio(video_path, force=False):
    """
    Extract audio from a video file using ffmpeg.
    The audio is saved as a WAV file with the following properties:
    - PCM 16-bit encoding
    - Mono channel
    - 16 kHz sample rate
    """
    video_path = Path(video_path)
    output_audio = video_path.with_name(f"{video_path.stem}.audio.wav")
    
    if output_audio.exists() and not force:
        return output_audio
    
    stream = ffmpeg.input(str(video_path))
    stream = ffmpeg.output(
        stream,
        str(output_audio),
        ar=16000,
        ac=1,
        acodec='pcm_s16le',
    )
    
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
    
    return output_audio


if __name__ == "__main__":
    video_path = "example/assemblyai.mp4"
    audio_path = extract_audio(video_path)
    print(audio_path)
