import subprocess
import os
import argparse

# --- Core Processing Functions (merged from your notebooks) ---

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
    # Sanitize LUT path for FFmpeg filter syntax compatibility
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

    print("--- Processing video, this may take a while... ---")
    print(f"Executing command: {' '.join(command)}")
    print("--------------------------------------------------")

    try:
        subprocess.run(
            command,
            check=True,          # Raise CalledProcessError if FFmpeg returns a non-zero exit code
            capture_output=True, # Capture stdout and stderr
            text=True,           # Decode stdout/stderr as text
            encoding='utf-8'
        )
        print(f"✅ Video processing successful! Saved to: {output_video_path}")
        return True
    except FileNotFoundError:
        print("❌ Error: 'ffmpeg' command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print("❌ An error occurred during FFmpeg execution.")
        print(f"Error message:\n{e.stderr}")
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
    # Sanitize LUT path for FFmpeg filter syntax compatibility
    sanitized_lut_path = lut_path.replace('\\', '/')
    
    command = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', input_image_path,
        '-vf', f"lut3d=file='{sanitized_lut_path}':interp=tetrahedral",
        '-q:v', str(quality),  # Set output quality
        output_image_path
    ]

    print("--- Processing image ---")
    print(f"Executing command: {' '.join(command)}")
    print("------------------------")

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Image processing successful! Saved to: {output_image_path}")
        return True
    except FileNotFoundError:
        print("❌ Error: 'ffmpeg' command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print("❌ An error occurred during FFmpeg execution.")
        print(f"Error message:\n{e.stderr}")
        return False

# --- Main Program and Command-Line Interface ---

def main():
    """
    Main execution function to parse command-line arguments and dispatch tasks.
    """
    parser = argparse.ArgumentParser(
        description="A command-line tool to apply 3D LUTs to videos and images using FFmpeg.",
        formatter_class=argparse.RawTextHelpFormatter # Preserve newlines in help text
    )
    parser.add_argument(
        '-i', '--input', 
        type=str, 
        required=True, 
        help="Path to the input video or image file."
    )
    parser.add_argument(
        '-l', '--lut', 
        type=str, 
        required=True, 
        help="Path to the .cube LUT file to apply."
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        help="Path for the output file.\nIf not specified, '_lut' will be added to the original filename."
    )
    parser.add_argument(
        '--crf', 
        type=int, 
        default=23, 
        help="[Video Only] The CRF quality parameter for H.264 (0-51). Lower is better. Default: 23."
    )
    parser.add_argument(
        '-q', '--quality', 
        type=int, 
        default=2, 
        help="[Image Only] The quality parameter for JPEG (1-31). Lower is better. Default: 2."
    )
    
    args = parser.parse_args()

    # --- File validation ---
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found at '{args.input}'")
        return
    if not os.path.exists(args.lut):
        print(f"❌ Error: LUT file not found at '{args.lut}'")
        return

    # --- Auto-generate output path if not provided ---
    output_path = args.output
    if not output_path:
        base, ext = os.path.splitext(args.input)
        output_path = f"{base}_lut{ext}"

    # --- Determine file type and dispatch to the correct function ---
    _, extension = os.path.splitext(args.input.lower())
    
    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']

    if extension in VIDEO_EXTENSIONS:
        apply_lut_to_video(args.input, args.lut, output_path, args.crf)
    elif extension in IMAGE_EXTENSIONS:
        apply_lut_to_image(args.input, args.lut, output_path, args.quality)
    else:
        print(f"❌ Error: Unsupported file type '{extension}'.")
        print("Supported video formats:", VIDEO_EXTENSIONS)
        print("Supported image formats:", IMAGE_EXTENSIONS)

if __name__ == "__main__":
    main()