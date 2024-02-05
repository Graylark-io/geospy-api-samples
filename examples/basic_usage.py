import aiohttp
import asyncio
import base64
import logging
from aiohttp import ClientTimeout

# Configuration
ENDPOINT_URL = "YOUR_END_POINT"  # API endpoint
API_KEY = "YOUR_API_KEY"  # Securely fetched or stored
IMAGE_PATH = "sample_images/bar.jpg"  # Replace with the path to your image file

# Logger configuration for simple debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom timeout for aiohttp session
custom_timeout = ClientTimeout(total=60)  # 60 seconds timeout for API requests

async def encode_image_to_base64(path_to_image: str) -> str:
    """
    Encodes an image file to a base64 string.
    
    Args:
        path_to_image (str): The file path to the image to be encoded.
    
    Returns:
        str: The base64 encoded string of the image.
    """
    with open(path_to_image, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def send_request(session, image_base64: str) -> None:
    """
    Sends an asynchronous request to the GeoSpy AI API with the encoded image and API key in the payload.
    
    Args:
        session (ClientSession): The aiohttp session used to send the request.
        image_base64 (str): The base64 encoded string of the image.
    """
    payload = {
        "image": image_base64,
        "key": API_KEY,  # API key included in the payload as specified
        # Add additional parameters here as needed
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        async with session.post(ENDPOINT_URL, json=payload, headers=headers, timeout=custom_timeout) as response:
            if response.status == 200:
                result = await response.json()
                logging.info(f"Success: {result}")
            else:
                logging.error(f"Failed with status code: {response.status}, Message: {await response.text()}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

async def main():
    """
    Main function to encode the image and send the request.
    """
    image_base64 = await encode_image_to_base64(IMAGE_PATH)
    async with aiohttp.ClientSession() as session:
        await send_request(session, image_base64)
    
# Run the main function
asyncio.run(main())
# Expected output:
#

