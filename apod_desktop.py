"""
Academic Integrity Statement – COMP593 Final Project

This script is my own original work and complies with the academic integrity policies of Fleming College.
Any external resources (e.g., NASA APOD API, public documentation, or tutorial references) have been cited where appropriate.
No AI tools (such as ChatGPT, GitHub Copilot, etc.) were used in generating the code content.
I understand that submitting code copied from others without attribution is a violation of academic honesty.

Student Name: Mohamed Aadhil Syed Kaberdeen
Student ID: 10330868
Date: April 17

APOD Desktop – Downloads NASA's Astronomy Picture of the Day for a given date and sets it as wallpaper.
Usage (CLI): python apod_desktop.py [YYYY-MM-DD]
"""
from datetime import date
import os
import sys
import hashlib
import sqlite3
import re

import apod_api
import image_lib

# Full paths for image cache directory and database file
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, "images")
image_cache_db = os.path.join(image_cache_dir, "image_cache.db")
print(f"Image cache directory: {image_cache_dir}")
print(f"Image cache DB: {image_cache_db}")

def main():
    """Main function to handle CLI invocation."""
    # Get the APOD date from command line or use today if not provided
    apod_date = get_apod_date()
    # Initialize the cache (create folder and database if not already present)
    init_apod_cache()
    # Fetch the APOD image and info for the given date, add it to cache
    apod_id = add_apod_to_cache(apod_date)
    # If successfully obtained (apod_id != 0), set it as desktop background
    if apod_id != 0:
        apod_info = get_apod_info(apod_id)
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Parses and validates the APOD date from the command-line arguments.
    
    Returns:
        datetime.date: The APOD date to use.
    Exits the program with an error message if the date is invalid or out of range.
    """
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        # No date provided, default to today’s date
        date_str = date.today().isoformat()
    try:
        apod_date = date.fromisoformat(date_str)
    except ValueError:
        print("Error: Invalid date format; please use YYYY-MM-DD.")
        sys.exit(1)
    # Enforce valid APOD date range
    if apod_date < date(1995, 6, 16):
        print("Error: APOD date must be on or after 1995-06-16 (the first APOD).")
        sys.exit(1)
    if apod_date > date.today():
        print("Error: APOD date cannot be in the future.")
        sys.exit(1)
    return apod_date

def init_apod_cache():
    """Initializes the image cache directory and database.
    
    Creates the 'images' folder and the SQLite database (with table) if they don’t exist.
    """
    # Create cache directory if not present
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image cache directory created.")
    # Connect to the database (this will create the file if it doesn't exist)
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    # Create the table for storing APOD info if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS apod_images (
        id INTEGER PRIMARY KEY,
        title TEXT,
        explanation TEXT,
        file_path TEXT,
        sha256 TEXT
    );
    """
    cur.execute(create_table_sql)
    conn.commit()
    conn.close()

def add_apod_to_cache(apod_date):
    """Downloads the APOD for the given date (if not already cached) and stores it in the cache.
    
    Returns:
        int: The database ID of the APOD record (or 0 if the download failed).
    """
    print(f"APOD date: {apod_date.isoformat()}")
    # Get APOD metadata from NASA
    apod_info = apod_api.get_apod_info(apod_date)
    if apod_info is None:
        print(f"Getting {apod_date.isoformat()} APOD information from NASA...failure")
        return 0
    else:
        print(f"Getting {apod_date.isoformat()} APOD information from NASA...success")
    print(f"APOD title: {apod_info['title']}")
    # Determine the image URL (HD image if it's a picture, or thumbnail if it's a video)
    if apod_info.get('media_type') == 'image':
        image_url = apod_info.get('hdurl')
    else:
        image_url = apod_info.get('thumbnail_url')
    print(f"APOD URL: {image_url}")
    # Download image data
    image_data = image_lib.download_image(image_url)
    if image_data is None:
        # Download failed (message already printed in download_image)
        return 0
    # Compute SHA-256 hash of the image to check for duplicates
    image_hash = hashlib.sha256(image_data).hexdigest()
    print(f"APOD SHA-256: {image_hash}")
    # Check if this image (by hash) is already in our database (cache)
    existing_id = get_apod_id_from_db(image_hash)
    if existing_id != 0:
        print("APOD image is already in cache.")
        return existing_id  # Return the existing record's ID
    # If not cached, proceed to save it
    print("APOD image is not already in cache.")
    image_title = apod_info['title']
    # Determine a safe file path for the image
    file_path = determine_apod_file_path(image_title, image_url)
    print(f"APOD file path: {file_path}")
    # Save the image file to disk
    saved = image_lib.save_image_file(image_data, file_path)
    if not saved:
        return 0  # Stop if we couldn't save the image
    # Store APOD metadata in the database
    apod_id = add_apod_to_db(image_title, apod_info['explanation'], file_path, image_hash)
    if apod_id != 0:
        print("Adding APOD to image cache DB...success")
    return apod_id

def add_apod_to_db(title, explanation, file_path, sha256_hash):
    """Adds a new APOD record to the SQLite database.
    
    Args:
        title (str): Title of the APOD image.
        explanation (str): Explanation text of the APOD.
        file_path (str): File path where the image is saved.
        sha256_hash (str): SHA-256 hash of the image bytes.
    Returns:
        int: The ID of the inserted database record, or 0 if there was an error.
    """
    try:
        conn = sqlite3.connect(image_cache_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO apod_images (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)",
            (title, explanation, file_path, sha256_hash)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0

def get_apod_id_from_db(image_hash):
    """Checks if an image with the given SHA-256 hash is already in the cache database.
    
    Returns:
        int: The ID of the existing record if found, or 0 if not found.
    """
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    cur.execute("SELECT id FROM apod_images WHERE sha256 = ?", (image_hash,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return 0

def determine_apod_file_path(title, image_url):
    """Generates a safe file path (in the cache directory) for the APOD image.
    
    Replaces non-alphanumeric characters in the title with underscores and appends the image file extension.
    """
    safe_title = re.sub(r'\W+', '_', title.strip())  # Remove any special chars from title
    ext = os.path.splitext(image_url)[1]  # Use the original image's extension (e.g., .jpg or .png)
    return os.path.join(image_cache_dir, f"{safe_title}{ext}")

def get_apod_info(image_id):
    """Retrieves APOD information by ID from the cache database.
    
    Returns:
        dict: A dictionary with 'title', 'explanation', 'file_path' for the given image ID, or {} if not found.
    """
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    cur.execute("SELECT title, explanation, file_path FROM apod_images WHERE id = ?", (image_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"title": row[0], "explanation": row[1], "file_path": row[2]}
    else:
        return {}

def get_all_apod_titles():
    """Returns a list of all APOD titles stored in the cache database."""
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    cur.execute("SELECT title FROM apod_images")
    rows = cur.fetchall()
    conn.close()
    titles = [row[0] for row in rows]
    return titles

def get_apod_id_by_title(title):
    """Finds the database ID of an APOD by its title.
    
    Returns:
        int: The ID if found, or 0 if no match.
    """
    conn = sqlite3.connect(image_cache_db)
    cur = conn.cursor()
    cur.execute("SELECT id FROM apod_images WHERE title = ?", (title,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

if __name__ == "__main__":
    main()
