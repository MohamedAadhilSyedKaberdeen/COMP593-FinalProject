'''
COMP 593 - Final Project
Authors (Group Assignment):
Sivaneshwar Tamilmaran Latha
Mohamed Aadhil Syed Kaberdeen

Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests

APOD_API_URL = 'https://api.nasa.gov/planetary/apod'
API_KEY = '9SCEQj2qU22MxgcH4FP6ERyucjXJnfmYMtI40va8'

def main():
    # TODO: Add code to test the functions in this module
    apod_date = get_apod_info("1995-06-16")
    print(apod_date)

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    # TODO: Complete the function body
    # Hint: The APOD API uses query string parameters: https://requests.readthedocs.io/en/latest/user/quickstart/#passing-parameters-in-urls
    # Hint: Set the 'thumbs' parameter to True so the info returned for video APODs will include URL of the video thumbnail image 
    get_params = {'api_key': API_KEY,
                  'date': apod_date,
                  'thumbs': True
    }

    resp_msg = requests.get(APOD_API_URL, params=get_params)
    
    if resp_msg.status_code == requests.codes.ok:
        return resp_msg.json() 
    return None      

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    # TODO: Complete the function body
    # Hint: The APOD info dictionary includes a key named 'media_type' that indicates whether the APOD is an image or video
    
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict('hdurl')
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict['thumbnail_url']
    return None

if __name__ == '__main__':
    main()