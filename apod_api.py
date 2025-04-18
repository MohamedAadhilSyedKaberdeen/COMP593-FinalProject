"""
Library for interacting with NASA's Astronomy Picture of the Day (APOD) API.
"""
import requests

APOD_API_URL = "https://api.nasa.gov/planetary/apod"
API_KEY = "iaVRDrtMurc9vEDQmUAnrb45FJW8VoXTB7rPm2YU"  # Use your API key here

def main():
    """Run a simple test of the APOD API functions."""
    # Example: fetch APOD info for the first available APOD date
    info = get_apod_info("1995-06-16")
    print("APOD title for 1995-06-16:", info.get("title") if info else "Failed to fetch")
    # Example: get image URL from that info
    if info:
        url = get_apod_image_url(info)
        print("Image URL for 1995-06-16:", url)

def get_apod_info(apod_date):
    """Gets the APOD information for a specified date from NASA's API.
    
    Args:
        apod_date (date or str): APOD date (YYYY-MM-DD format string or date object)
    
    Returns:
        dict: Dictionary of APOD data (title, explanation, URL, etc.) if successful, or None if failed.
    """
    # Prepare request parameters, including API key and date
    params = {
        "api_key": API_KEY,
        "date": str(apod_date),
        "thumbs": True  # Request thumbnail URL if the APOD is a video
    }
    # Send GET request to the APOD API
    response = requests.get(APOD_API_URL, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()  # Successful response returns a dict of APOD info
    else:
        return None  # API request failed (e.g., invalid date or network issue)

def get_apod_image_url(apod_info):
    """Determines the URL of the APOD image from the APOD info dictionary.
    
    If the APOD media type is an image, returns the HD image URL.
    If it's a video, returns the thumbnail image URL (so we have an image to display).
    
    Args:
        apod_info (dict): APOD information dictionary (from get_apod_info).
    
    Returns:
        str: URL of an image (HD image or video thumbnail) corresponding to the APOD.
    """
    if apod_info is None:
        return None
    if apod_info.get("media_type") == "image":
        return apod_info.get("hdurl")
    elif apod_info.get("media_type") == "video":
        return apod_info.get("thumbnail_url")
    else:
        return None

if __name__ == "__main__":
    main()
