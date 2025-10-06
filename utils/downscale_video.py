import tempfile
from flask import Blueprint, request, jsonify
import ffmpeg
from utils.file_transfer import stream_drive_to_gcs
from google.cloud import storage


def downscale_video(gcs_input_url, gcs_output_url):
    scale = 0.5
    if not gcs_input_url or not gcs_output_url:
        raise ValueError("gcs_input_url and gcs_output_url are required")

    try:
        storage_client = storage.Client()
        input_bucket, input_path = parse_gcs_url(gcs_input_url)
        output_bucket, output_path = parse_gcs_url(gcs_output_url)

        in_bucket = storage_client.bucket(input_bucket)
        out_bucket = storage_client.bucket(output_bucket)

        with tempfile.NamedTemporaryFile(
            suffix=".mp4"
        ) as in_tmp, tempfile.NamedTemporaryFile(suffix=".mp4") as out_tmp:
            in_bucket.blob(input_path).download_to_filename(in_tmp.name)

            (
                ffmpeg.input(in_tmp.name)
                .output(
                    out_tmp.name,
                    vf=f"scale=iw*{scale}:ih*{scale}",
                    vcodec="libx264",
                    crf=28,
                    preset="fast",
                    acodec="aac",
                    audio_bitrate="128k",
                )
                .overwrite_output()
                .run(quiet=True)
            )

        out_bucket.blob(output_path).upload_from_filename(out_tmp.name)

        input_blob = storage_client.bucket(input_bucket).blob(input_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_gcs_url(url: str):
    if not url.startswith("gs://"):
        raise ValueError("URL must start with gs://")
    parts = url[5:].split("/", 1)
    return parts[0], parts[1]
