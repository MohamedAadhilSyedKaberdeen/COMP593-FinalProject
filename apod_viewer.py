import os
import requests
import ctypes
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import date
import io

# === CONFIGURATION ===
API_KEY = 'DEMO_KEY'  # Replace with your own key if you have one
APOD_API_URL = 'https://api.nasa.gov/planetary/apod'
IMAGE_CACHE_DIR = 'apod_images'

# Create image cache directory if not exist
if not os.path.exists(IMAGE_CACHE_DIR):
    os.makedirs(IMAGE_CACHE_DIR)

# === FUNCTIONS ===

def get_apod_data(apod_date):
    params = {
        'api_key': API_KEY,
        'date': apod_date
    }
    response = requests.get(APOD_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('media_type') == 'image':
            return data
    return None

def download_apod_image(apod_data):
    image_url = apod_data['hdurl'] if 'hdurl' in apod_data else apod_data['url']
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        filename = f"{apod_data['date']}.jpg"
        path = os.path.join(IMAGE_CACHE_DIR, filename)
        with open(path, 'wb') as f:
            f.write(image_response.content)
        return path
    return None

def update_cached_list():
    files = [f for f in os.listdir(IMAGE_CACHE_DIR) if f.endswith('.jpg')]
    cached_images_cb['values'] = files

def show_image(path):
    img = Image.open(path)
    img.thumbnail((800, 800))
    tk_img = ImageTk.PhotoImage(img)
    image_label.config(image=tk_img)
    image_label.image = tk_img

def handle_download():
    apod_date = date_entry.get()
    apod_data = get_apod_data(apod_date)
    if not apod_data:
        messagebox.showerror("Error", "Could not retrieve APOD data.")
        return
    image_path = download_apod_image(apod_data)
    if image_path:
        show_image(image_path)
        update_cached_list()
        cached_images_cb.set(os.path.basename(image_path))
    else:
        messagebox.showerror("Error", "Could not download image.")

def handle_cached_select(event):
    selected_file = cached_images_cb.get()
    if selected_file:
        path = os.path.join(IMAGE_CACHE_DIR, selected_file)
        show_image(path)

def set_as_desktop():
    selected_file = cached_images_cb.get()
    if not selected_file:
        return
    path = os.path.abspath(os.path.join(IMAGE_CACHE_DIR, selected_file))
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)

# === GUI SETUP ===
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.geometry('900x700')

# === IMAGE PREVIEW AREA ===
image_label = Label(root)
image_label.pack(pady=10)

# === CONTROLS FRAME ===
controls_frame = Frame(root)
controls_frame.pack(fill=X, padx=10, pady=5)

# Left side: Cached images
left_frame = Frame(controls_frame)
left_frame.pack(side=LEFT, expand=True, fill=X)

Label(left_frame, text="View Cached Image").pack(anchor='w')
cached_images_cb = ttk.Combobox(left_frame, state='readonly')
cached_images_cb.pack(fill=X)
cached_images_cb.bind("<<ComboboxSelected>>", handle_cached_select)

set_btn = Button(left_frame, text="Set as Desktop", command=set_as_desktop)
set_btn.pack(pady=5)

# Right side: Download new image
right_frame = Frame(controls_frame)
right_frame.pack(side=RIGHT, expand=True, fill=X)

Label(right_frame, text="Get More Images").pack(anchor='w')
date_entry = ttk.Entry(right_frame)
date_entry.pack(fill=X)
date_entry.insert(0, str(date.today()))

download_btn = Button(right_frame, text="Download Image", command=handle_download)
download_btn.pack(pady=5)

# Initial population of cached images
update_cached_list()

# Start GUI loop
root.mainloop()