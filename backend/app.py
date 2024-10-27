from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
CORS(app)
load_dotenv()

IBM_API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")

def get_auth_token(api_key):
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    response = requests.post(auth_url, headers=headers, data=data, verify=False)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get authentication token")

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    base64_image = base64.b64encode(uploaded_file.read()).decode()
    return jsonify({"image_base64": base64_image}), 200

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    access_token = get_auth_token(IBM_API_KEY)
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
    
    body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": user_input}]}],
        "project_id": PROJECT_ID,
        "model_id": "meta-llama/llama-3-2-90b-vision-instruct",
        "decoding_method": "greedy",
        "repetition_penalty": 1,
        "max_tokens": 900
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        response_content = response.json()['choices'][0]['message']['content']
        return jsonify({"reply": response_content}), 200
    else:
        return jsonify({"error": "Failed to process request"}), 500

if __name__ == "__main__":
    app.run(debug=True)
