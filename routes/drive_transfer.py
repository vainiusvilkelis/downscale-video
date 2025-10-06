from flask import Blueprint, request, jsonify
from utils.file_transfer import stream_drive_to_gcs

drive_bp = Blueprint("drive", __name__)

@drive_bp.route("/transfer", methods=["POST"])
def transfer():
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'file_id' in request_json:
        file_id = request_json['file_id']
        gcs_destination_path = request_json.get('gcs_destination_path')
    elif request_args and 'file_id' in request_args:
        file_id = request_args['file_id']
        gcs_destination_path = request_args.get('gcs_destination_path')
    else:
        return {
            'error': 'Missing file_id parameter',
            'usage': 'Send POST with {"file_id": "your-file-id", "gcs_destination_path": "optional/path.mp4"}'
        }, 400
        
    try:
        stream_drive_to_gcs(file_id, gcs_destination_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
