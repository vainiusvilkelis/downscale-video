#!/usr/bin/env python3
"""
Test script for video downscaling functionality
"""

import os
import sys
from utils.downscale_video import downscale_video

def test_downscale():
    """Test the video downscaling function"""
    
    # Example usage
    input_video = "input_video.mp4"  # Replace with your input video path
    
    if not os.path.exists(input_video):
        print(f"Error: Input video file '{input_video}' not found.")
        print("Please provide a valid video file path.")
        return False
    
    try:
        print(f"Downscaling video: {input_video}")
        output_path = downscale_video(input_video)
        print(f"Downscaled video saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error downscaling video: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use command line argument as input video path
        input_video = sys.argv[1]
        if os.path.exists(input_video):
            try:
                output_path = downscale_video(input_video)
                print(f"Success! Downscaled video saved to: {output_path}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Error: File '{input_video}' not found.")
    else:
        print("Usage: python test_downscale.py <input_video_path>")
        print("Example: python test_downscale.py my_video.mp4")
