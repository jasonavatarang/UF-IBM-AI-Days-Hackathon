from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

app = Flask(__name__)
CORS(app)
load_dotenv()

IBM_API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

@app.route('/get-disaster-info', methods=['POST'])
def get_disaster_info():
    data = request.json
    user_input = data.get("message", "")
    lat = data.get("lat")
    lon = data.get("lon")

    # Extract location and disaster keywords from the user input
    keywords = user_input.split()  # Simplified; for complex extraction, use NLP
    location_keyword = None
    disaster_keyword = None

    for word in keywords:
        if word.lower() in ["hurricane", "flood", "earthquake", "wildfire"]:  # Example disaster types
            disaster_keyword = word.lower()
        elif not lat and not lon:  # Assume location if coordinates not provided
            location_keyword = word

    # Use geolocation API to get coordinates if location name is provided
    if location_keyword and not (lat and lon):
        location = geolocator.geocode(location_keyword)
        if location:
            lat, lon = location.latitude, location.longitude

    if not lat or not lon:
        return jsonify({"error": "Location data is required"}), 400

    # Build a search query using the location and disaster type
    search_query = f"{location_keyword} {disaster_keyword} news"
    google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(google_search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract top headlines from Google search results
    results = []
    for item in soup.find_all('h3'):
        if item.text:
            results.append(item.text)
        if len(results) >= 5:  # Limit to top 5 results
            break

    if results:
        return jsonify({"success": True, "data": results}), 200
    else:
        return jsonify({"success": False, "message": "No data found"}), 404


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
