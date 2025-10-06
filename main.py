import functions_framework
from googleapiclient.discovery import build
from google.auth import default
import json
import os
from google.cloud import storage
from googleapiclient.http import MediaIoBaseDownload
import io
import requests

@functions_framework.http
def stream_drive_to_gcs(request):
    """
    Cloud Run Function to stream Google Drive files to Google Cloud Storage.
    
    Request JSON:
    {
        "file_id": "your-google-drive-file-id",
        "gcs_destination_path": "videos/output.mp4"  # optional
    }
    
    Environment Variables:
    - GCS_BUCKET_NAME: Target GCS bucket name
    """
    try:
        storage_client = storage.Client()
        CHUNK_SIZE = 100 * 1024 * 1024  # 100MB chunks
        BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'n8n-test-bucket-for-video')

        credentials, project = default()
        drive_service = build('drive', 'v3', credentials=credentials)
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
        
        # Get file metadata from Google Drive (including Shared Drives)
        file_info = drive_service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,size,createdTime,modifiedTime,webViewLink,webContentLink,parents',
            supportsAllDrives=True  # This enables access to Shared Drive files
        ).execute()
        
        file_name = file_info.get('name', 'unknown')
        mime_type = file_info.get('mimeType', '')
        file_size = int(file_info.get('size', 0))

        if not mime_type.startswith('video/'):
            return {'error': f'Invalid mime type: {mime_type}'}, 400

        gcs_path = request_json.get('gcs_destination_path', f'raw/{file_name}')
        request_download = drive_service.files().get_media(fileId=file_id)


        # Stream Drive file directly to GCS using proper resumable upload
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        blob.content_type = mime_type
        

        # Get upload URL
        upload_url = blob.create_resumable_upload_session(content_type=mime_type)
        
        # Stream chunks from Drive to GCS
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_download, chunksize=CHUNK_SIZE)
        
        done = False
        uploaded_bytes = 0
        
        while not done:
            # Download chunk from Drive
            status, done = downloader.next_chunk()
            
            # Get the chunk data
            chunk_data = fh.getvalue()
            chunk_size = len(chunk_data)
            
            if chunk_size > 0:
                # Upload this chunk to GCS using resumable upload
                headers = {
                    'Content-Length': str(chunk_size),
                    'Content-Range': f'bytes {uploaded_bytes}-{uploaded_bytes + chunk_size - 1}/{file_size}'
                }
                
                response = requests.put(
                    upload_url,
                    data=chunk_data,
                    headers=headers
                )
                
                if response.status_code not in [200, 201, 308]:
                    raise Exception(f"Upload failed: {response.status_code} {response.text}")
                
                uploaded_bytes += chunk_size
                
                if status:
                    progress = int(status.progress() * 100)
                    print(f'Stream progress: {progress}% ({uploaded_bytes}/{file_size} bytes)')
            
            # Clear buffer for next chunk
            fh.seek(0)
            fh.truncate(0)
        
        gcs_uri = f'gs://{BUCKET_NAME}/{gcs_path}'
        print(f'File streamed to: {gcs_uri}')
        
        # Format the response
        response = {
            'success': True,
            'gcs_uri': gcs_uri,
            'gcs_path': gcs_path,
            'file': {
                'id': file_info.get('id'),
                'name': file_info.get('name'),
                'mimeType': file_info.get('mimeType'),
                'size': file_info.get('size'),
                'createdTime': file_info.get('createdTime'),
                'modifiedTime': file_info.get('modifiedTime'),
                'webViewLink': file_info.get('webViewLink'),
                'webContentLink': file_info.get('webContentLink'),
                'parents': file_info.get('parents', [])
            }
        }
        
        return response, 200
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to get file from Google Drive'
        }, 500

