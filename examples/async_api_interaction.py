import aiohttp
import asyncio
import time
import base64
import logging
from aiohttp import ClientTimeout, ClientError

# Configuration
ENDPOINT_URL = "YOUR_END_POINT"  # API endpoint
API_KEY = "YOUR_API_KEY"  # Securely fetched or stored
CONCURRENT_REQUESTS = 300  # Max number of concurrent requests
TOTAL_REQUESTS = 100  # Total number of requests to send
REQUEST_INTERVAL = 0.01  # Time in seconds between launching each request to avoid rate limit
MAX_RETRIES = 5  # Max retry attempts for each request
RETRY_BACKOFF = 2  # Exponential backoff factor for retries
TIMEOUT_SECONDS = 30  # Timeout for each API request

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set a custom timeout for aiohttp session
custom_timeout = ClientTimeout(total=TIMEOUT_SECONDS)

# Headers for the HTTP request
headers = {
    'Content-Type': 'application/json',
}

async def encode_image_to_base64(path_to_image: str) -> str:
    """Encode image file to base64 string."""
    with open(path_to_image, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def send_request(session, image_base64: str, request_number: int) -> dict:
    """Send a single request to the API with exponential backoff retry logic."""
    payload = {
        "inputs": {"image": image_base64},
        "key": API_KEY,  # API key included in the payload
        "use_classification": False,
        "top_k": 5,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.post(ENDPOINT_URL, headers=headers, json=payload, timeout=custom_timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"Request {request_number}: Success")
                    print(result)
                    return result
                else:
                    logging.error(f"Request {request_number}: Failed with status {response.status}")
                    return {"error": f"HTTP error {response.status}"}
        except (ClientError, asyncio.TimeoutError) as e:
            logging.error(f"Request {request_number}: Attempt {attempt} failed with error: {e}")
            if attempt < MAX_RETRIES:
                sleep_time = RETRY_BACKOFF ** attempt
                logging.info(f"Retrying in {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)
            else:
                logging.error(f"Request {request_number}: Max retries reached.")
                return {"error": "Max retries reached"}

async def main():
    # Load and encode the image outside the request loop to avoid repetition
    print("Welcome to the GeoSpy AI API!")
    path_to_image = 'sample_images/bar.jpg'  # Replace with the actual image path
    print(f"Encoding image: {path_to_image}")
    image_base64 = await encode_image_to_base64(path_to_image)


    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            if len(tasks) >= CONCURRENT_REQUESTS:
                # Wait for some tasks to complete before adding more
                _ = await asyncio.gather(*tasks[:CONCURRENT_REQUESTS])
                tasks = tasks[CONCURRENT_REQUESTS:]
            task = asyncio.ensure_future(send_request(session, image_base64, i + 1))
            tasks.append(task)
            await asyncio.sleep(REQUEST_INTERVAL)  # Respect API rate limits

        responses = await asyncio.gather(*tasks)
        logging.info(f"Received {len(responses)} responses")
        # Further processing of responses can be done here

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    logging.info(f"Execution time: {end_time - start_time} seconds")
