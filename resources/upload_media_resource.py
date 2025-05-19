from flask import request
from flask_restful import Resource
import cloudinary
import cloudinary.uploader
import os

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

class ImageUploadResource(Resource):
    def post(self):
        if 'image' not in request.files:
            return {'error': 'No image part in request'}, 400

        image_file = request.files['image']

        if image_file.filename == '':
            return {'error': 'No image selected'}, 400

        try:
            upload_result = cloudinary.uploader.upload(image_file)
            return {
                'message': 'Image uploaded successfully',
                'url': upload_result['secure_url']
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500
