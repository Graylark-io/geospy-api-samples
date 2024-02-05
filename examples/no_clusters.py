import requests
import base64

# Configuration
ENDPOINT_URL = "YOUR_END_POINT"  # API endpoint
API_KEY = "YOUR_API_KEY"  # Securely fetched or stored
def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def predict_location_with_clustering(image_path, anti_cluster=True, top_k=5):
    """Send an image to the GeoSpy AI API with clustering enabled."""
    api_url = ENDPOINT_URL  # Replace with the actual API URL
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "image": encode_image(image_path),
        "key ": API_KEY,  # Replace with your actual API key
        "anti_cluster": anti_cluster,
        "top_k": top_k
    }
    
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        print("Prediction with clustering successful:", response.json())
    else:
        print("Failed to predict location with clustering:", response.text)

if __name__ == "__main__":
    image_path = "sample_images/bar.jpg"  # Replace with your image path
    predict_location_with_clustering(image_path)
