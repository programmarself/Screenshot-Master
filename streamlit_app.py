import streamlit as st
import time
import psutil
import os
from PIL import Image, ImageDraw, ImageOps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os.path import exists

# Streamlit Page Configuration
st.set_page_config(page_title="Screenshot Master", layout="wide")
st.title(' Screenshot Master')
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
    app_img = Image.open('screenshot.png')

    # Create a blank white image
    img = Image.new('RGB', app_img.size, color='white')
    img = add_corners(img, 24)
    img.save('rect.png')

    # Resize and crop the app image
    resized_app_img = app_img.resize((int(app_img.width * 0.95), int(app_img.height * 0.95)))
    resized_app_img = ImageOps.crop(resized_app_img, (0, 4, 0, 0))
    resized_app_img = add_corners(resized_app_img, 24)
    
    img.paste(resized_app_img, (int(resized_app_img.width * 0.025), int(resized_app_img.width * 0.035)), resized_app_img)
    img.save('app_rect.png')

    # Add Streamlit logo if selected
    if streamlit_logo:
        logo_img = Image.open('streamlit-logo.png').convert('RGBA')
        logo_img.thumbnail((logo_width, logo_width), Image.LANCZOS)
        logo_position = (img.width - logo_img.width - 10, img.height - logo_img.height - 10)
        img.paste(logo_img, logo_position, logo_img)
    
    img.save('final.png')
    st.image(img)

# Sidebar and Input Form
with st.sidebar:
    st.header('⚙️ Settings')

    st.subheader('Image Resolution')
    width = st.slider('Width', 426, 1920, 1000)
    height = st.slider('Height', 240, 1080, 540)

    with st.expander('Streamlit Logo'):
        streamlit_logo = st.checkbox('Add Streamlit logo', value=True, key='streamlit_logo')
        logo_width = st.slider('Logo Width', 0, 500, 100, step=10)

    ram_usage = psutil.virtual_memory()[2]
    st.caption(f'RAM Usage: {ram_usage}%')

with st.form("url_form"):
    app_url = st.text_input('App URL', 'https://flowcv.me/ikm').rstrip('/')
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

# Footer
st.markdown("""
    <div class="footer">
        Developed By: Irfan Ullah Khan<br>
        <a href="https://flowcv.me/ikm">https://flowcv.me/ikm</a><br>
        Developed For: Essential Generative AI Training<br>
        Conducted By: PAK ANGELS, iCodeGuru, ASPIRE PAKISTAN
    </div>
""", unsafe_allow_html=True)