import subprocess
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def apply_lut_to_video(input_video_path: str, lut_path: str, output_video_path: str, crf: int = 23):
    """
    Applies a 3D LUT to a video file using FFmpeg, copying the original audio track.

    Args:
        input_video_path (str): Path to the source video file.
        lut_path (str): Path to the .cube LUT file.
        output_video_path (str): Path to save the processed video file.
        crf (int): Constant Rate Factor for H.264 encoding (0-51). Lower is better quality. Defaults to 23.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    sanitized_lut_path = lut_path.replace('\\', '/')
    
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', input_video_path,
        '-vf', f"lut3d=file='{sanitized_lut_path}':interp=tetrahedral",
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-pix_fmt', 'yuv420p',  # For maximum player compatibility
        '-c:a', 'copy',          # Copy audio stream without re-encoding
        output_video_path
    ]

    logger.info(f"Processing video: {input_video_path} with LUT: {lut_path}")
    logger.info(f"Executing command: {' '.join(command)}")

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        logger.info(f"Video processing successful! Saved to: {output_video_path}")
        return True
    except FileNotFoundError:
        logger.error("Error: 'ffmpeg' command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred during FFmpeg execution for {input_video_path}.")
        logger.error(f"Error message:\n{e.stderr}")
        return False

def apply_lut_to_image(input_image_path: str, lut_path: str, output_image_path: str, quality: int = 2):
    """
    Applies a 3D LUT to a single image file using FFmpeg.

    Args:
        input_image_path (str): Path to the source image file.
        lut_path (str): Path to the .cube LUT file.
        output_image_path (str): Path to save the processed image file.
        quality (int): Quality for JPEG output (1-31). Lower is better quality. Defaults to 2.

    Returns:
        bool: True if successful, False otherwise.
    """
    sanitized_lut_path = lut_path.replace('\\', '/')
    
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', input_image_path,
        '-vf', f"lut3d=file='{sanitized_lut_path}':interp=tetrahedral",
        '-q:v', str(quality),  # Set output quality
        output_image_path
    ]

    logger.info(f"Processing image: {input_image_path} with LUT: {lut_path}")
    logger.info(f"Executing command: {' '.join(command)}")

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Image processing successful! Saved to: {output_image_path}")
        return True
    except FileNotFoundError:
        logger.error("Error: 'ffmpeg' command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred during FFmpeg execution for {input_image_path}.")
        logger.error(f"Error message:\n{e.stderr}")
        return False
