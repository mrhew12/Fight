import requests
import time
import os

# --- Configuration ---
# In a real application, this would be the public URL of your API Gateway.
API_BASE_URL = "https://api.spriteshift.ai/v1"
# API keys should be handled securely, e.g., via environment variables.
API_KEY = os.environ.get("SPRITESHIFT_API_KEY", "your_api_key_here")

# --- API Client Functions ---

def submit_job(image_path: str) -> str | None:
    """
    Submits a new character animation job to the API.

    Args:
        image_path: The local path to the character image file.

    Returns:
        The job_id if successful, otherwise None.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # In a real implementation, the API would likely provide a pre-signed URL
    # for a direct S3 upload. For this example, we send the file directly.
    files = {"image": (os.path.basename(image_path), open(image_path, "rb"), "image/png")}

    print(f"Submitting job for image: {image_path}...")
    try:
        response = requests.post(f"{API_BASE_URL}/jobs", headers=headers, files=files)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"Successfully submitted job. Job ID: {job_id}")
        return job_id

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def poll_job_status(job_id: str, timeout_seconds: int = 300) -> dict | None:
    """
    Polls the status of a job until it's completed or times out.

    Args:
        job_id: The ID of the job to check.
        timeout_seconds: The maximum time to wait for the job to complete.

    Returns:
        The final job status data if completed, otherwise None.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        print(f"Checking status for job {job_id}...")
        try:
            response = requests.get(f"{API_BASE_URL}/jobs/{job_id}", headers=headers)
            response.raise_for_status()

            job_data = response.json()
            status = job_data.get("status")
            print(f"Current status: {status}")

            if status in ["completed", "failed"]:
                print("Job finished.")
                return job_data

            time.sleep(10)  # Wait for 10 seconds before polling again

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking status: {e}")
            return None

    print("Job polling timed out.")
    return None

# --- Main Execution ---

if __name__ == "__main__":
    # Create a dummy image file for the example to work.
    if not os.path.exists("dummy_character.png"):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save("dummy_character.png")

    print("--- SpriteShift AI API Example ---")

    # 1. Submit a new job
    job_id = submit_job("dummy_character.png")

    # 2. If submission was successful, poll for the result
    if job_id:
        final_status = poll_job_status(job_id)
        if final_status and final_status.get("status") == "completed":
            print("\n--- Job Complete! ---")
            print(f"Results for job {job_id}:")
            # In a real scenario, you would download the assets from these URLs.
            print(f"Sprite Sheet URL: {final_status.get('results', {}).get('sprite_sheet_url')}")
            print(f"Metadata URL: {final_status.get('results', {}).get('metadata_url')}")

    # Clean up the dummy file
    os.remove("dummy_character.png")
