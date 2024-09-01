import streamlit as st
import time
import psutil
import random
import os
from PIL import Image, ImageDraw, ImageOps
from PIL.Image import Resampling
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os.path import exists

# Streamlit Page Configuration
st.set_page_config(page_title="🎈 Screen Master", layout="wide")
st.title('🎈 Screen Master')
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown('<p class="big-font">Capture and Enhance Screenshots of Streamlit Apps</p>', unsafe_allow_html=True)
st.write("Use this tool to take professional screenshots of your Streamlit applications.")

# Define Functions
def get_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument(f"--window-size={width}x{height}")
    service = Service()
    return webdriver.Chrome(service=service, options=options)

def get_screenshot(app_url):
    driver = get_driver()
    driver.get(app_url)
    time.sleep(3)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    driver.save_screenshot('screenshot.png')
    driver.quit()

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    im.putalpha(alpha)
    return im

def generate_app_image():
    bg_img = Image.open(f'background/background-{random.randint(1,100):02d}.jpeg')
    app_img = Image.open('screenshot.png')

    img = Image.new('RGB', app_img.size, color='white')
    img = add_corners(img, 24)
    img.save('rect.png')

    resized_app_img = app_img.resize((int(app_img.width * 0.95), int(app_img.height * 0.95)))
    resized_app_img = ImageOps.crop(resized_app_img, (0, 4, 0, 0))
    resized_app_img = add_corners(resized_app_img, 24)
    
    img.paste(resized_app_img, (int(resized_app_img.width * 0.025), int(resized_app_img.width * 0.035)), resized_app_img)
    img.save('app_rect.png')

    resized_img = img.resize((int(bg_img.width * 0.9), int(bg_img.height * 0.9)))
    bg_img.paste(resized_img, (int(bg_img.width * 0.05), int(bg_img.height * 0.06)), resized_img)

    if streamlit_logo:
        logo_img = Image.open('streamlit-logo.png').convert('RGBA')
        logo_img.thumbnail((logo_width, logo_width), Image.LANCZOS)  # Corrected line
        bg_img.paste(logo_img, (logo_horizontal_placement, logo_vertical_placement), logo_img)
    
    bg_img.save('final.png')
    st.image(bg_img)

# Sidebar and Input Form
with st.sidebar:
    st.header('⚙️ Settings')

    st.subheader('Image Resolution')
    width = st.slider('Width', 426, 1920, 1000)
    height = st.slider('Height', 240, 1080, 540)

    with st.expander('Streamlit Logo'):
        streamlit_logo = st.checkbox('Add Streamlit logo', value=True, key='streamlit_logo')
        logo_width = st.slider('Logo Width', 0, 500, 100, step=10)
        logo_vertical_placement = st.slider('Vertical Placement', 0, 1000, 670, step=10)
        logo_horizontal_placement = st.slider('Horizontal Placement', 0, 1800, 80, step=10)

    ram_usage = psutil.virtual_memory()[2]
    st.caption(f'RAM Usage: {ram_usage}%')

with st.form("url_form"):
    app_url = st.text_input('App URL', 'https://langchain-quickstart.streamlit.app').rstrip('/')
    app_name = app_url.replace('https://','').replace('.streamlit.app','')
    submit_button = st.form_submit_button("Capture Screenshot")

    if submit_button:
        if app_url:
            get_screenshot(app_url)

if exists('screenshot.png'):
    generate_app_image()

    with open("final.png", "rb") as file:
        st.download_button(
            label="Download Image",
            data=file,
            file_name=f"{app_name}.png",
            mime="image/png"
        )
        os.remove('screenshot.png')
        os.remove('final.png')
