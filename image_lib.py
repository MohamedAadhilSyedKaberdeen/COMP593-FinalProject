"""
Library of utility functions for downloading and saving images, and setting the desktop wallpaper.
"""

import requests
import ctypes
import os
from PIL import Image  # pip install pillow

def main():
    """Test the image library functions with a sample image."""
    test_url = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg"
    img_data = download_image(test_url)
    if img_data:
        save_image_file(img_data, "test_image.jpg")
        set_desktop_background_image("test_image.jpg")

def download_image(image_url):
    """Downloads an image from the given URL (but does not save it to disk).
    
    Args:
        image_url (str): URL of the image to download.
    Returns:
        bytes: Binary image data if successful, or None if the download failed.
    """
    print(f"Downloading image from {image_url}...", end="")
    try:
        resp = requests.get(image_url)
        if resp.status_code == requests.codes.ok:
            print("success")
            return resp.content  # Return the raw image bytes
        else:
            print("failure")
            print(f"Response code: {resp.status_code} ({resp.reason})")
            return None
    except Exception as e:
        print("failure")
        print(f"Error: {e}")
        return None

def save_image_file(image_data, image_path):
    """Saves the given image data to a file on disk.
    
    Args:
        image_data (bytes): The binary image data to save.
        image_path (str): Destination file path (including filename).
    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        print(f"Saving image file as {image_path}...", end="")
        with open(image_path, "wb") as file:
            file.write(image_data)
        print("success")
        return True
    except Exception as e:
        print("failure")
        print(f"Error: {e}")
        return False

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image (Windows OS only).
    
    Converts the image to BMP format and then sets it as wallpaper.
    """
    print(f"Setting desktop to {image_path}...", end="")
    try:
        bmp_path = os.path.splitext(image_path)[0] + ".bmp"
        img = Image.open(image_path)
        img.save(bmp_path, "BMP")

        SPI_SETDESKWALLPAPER = 20
        result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, bmp_path, 3)
        if result:
            print("success")
            return True
        else:
            print("failure")
            return False
    except Exception as e:
        print("failure")
        print(f"Error: {e}")
        return False

def scale_image(image_size, max_size=(800, 600)):
    """Calculates a resized (width, height) for an image to fit within max_size while maintaining aspect ratio.
    
    Args:
        image_size (tuple): Original image dimensions as (width, height).
        max_size (tuple): Maximum allowed size (width, height).
    Returns:
        tuple: New (width, height) that fits within max_size.
    """
    original_width, original_height = image_size
    max_width, max_height = max_size
    scale_ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    return (new_width, new_height)

if __name__ == "__main__":
    main()
