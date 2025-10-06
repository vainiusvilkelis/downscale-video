# Video Downscaling with FFmpeg

This module provides functionality to downscale videos to 1/4 resolution using FFmpeg.

## Features

- Downscale videos to 1/4 resolution (0.5x width and height)
- Maintains aspect ratio
- Preserves audio track
- Uses H.264 video codec and AAC audio codec
- Automatic temporary file management
- Comprehensive error handling and logging

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure FFmpeg is installed on your system:
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html

## Usage

### Basic Usage

```python
from utils.downscale_video import downscale_video

# Downscale a video file
output_path = downscale_video("input_video.mp4")
print(f"Downscaled video saved to: {output_path}")
```

### With Custom Output Path

```python
output_path = downscale_video("input_video.mp4", "output_video.mp4")
```

### With Custom Scale Factor

```python
# Downscale to 1/2 resolution instead of 1/4
output_path = downscale_video("input_video.mp4", scale_factor=0.707)  # sqrt(0.5)
```

### Testing

Run the test script:
```bash
python test_downscale.py your_video.mp4
```

## API Functions

### `downscale_video(input_path, output_path=None, scale_factor=0.5)`

Downscales a video file using FFmpeg.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str, optional): Path for output video file. If None, creates temp file
- `scale_factor` (float): Scale factor for resolution (0.5 = 1/4 resolution)

**Returns:**
- `str`: Path to the downscaled video file

**Raises:**
- `ValueError`: If no video stream found in input file
- `RuntimeError`: If FFmpeg processing fails

### `downscale_video_from_drive(file_id, gcs_destination_path)`

Downloads video from Google Drive, downscales it, and uploads to GCS.

**Parameters:**
- `file_id` (str): Google Drive file ID
- `gcs_destination_path` (str): GCS destination path for the downscaled video

**Returns:**
- `tuple`: (response_dict, status_code)

## Technical Details

- **Resolution**: Reduces video to 1/4 resolution (0.5x width and height)
- **Codec**: Uses H.264 for video and AAC for audio
- **Quality**: Uses CRF 23 for good quality/size balance
- **Preset**: Uses 'medium' preset for balanced encoding speed
- **Dimensions**: Automatically ensures even dimensions (required for most codecs)

## Error Handling

The module includes comprehensive error handling for:
- Missing input files
- Invalid video streams
- FFmpeg processing errors
- File I/O errors
- Temporary file cleanup

All errors are logged with appropriate detail levels.
