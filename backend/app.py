import os
import io
import cv2
import numpy as np
from flask import Flask, request, jsonify
from google.cloud import vision
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Initialize Google Cloud Vision client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
vision_client = vision.ImageAnnotatorClient()

def preprocess_image(image_bytes):
    """Enhance image quality for better OCR results"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Preprocessing pipeline
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    _, threshold = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.imencode('.jpg', threshold)[1].tobytes()

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """Handle image upload and OCR processing"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        image_file = request.files['image']
        image_bytes = image_file.read()
        processed_image = preprocess_image(image_bytes)
        
        # Perform OCR
        image = vision.Image(content=processed_image)
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        return jsonify({
            "text": texts[0].description if texts else "",
            "confidence": response.full_text_annotation.pages[0].confidence
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
