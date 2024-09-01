import streamlit as st
import time
import psutil
import random
import os
from PIL import Image, ImageDraw, ImageOps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os.path import exists

# Set page config
st.set_page_config(page_title="🎈 App Screenshot")
st.title('🎈 App Screenshot')
st.warning('An app for taking a screenshot of a Streamlit app.')

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_screenshot(app_url, area):
    driver = get_driver()
    driver.get(app_url)
    time.sleep(3)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    if area:
        x, y, width, height = area
        driver.set_window_size(width, height)
        driver.execute_script(f"window.scrollTo({x}, {y});")
        screenshot = driver.get_screenshot_as_png()
        with open('screenshot.png', 'wb') as f:
            f.write(screenshot)
    else:
        driver.save_screenshot('screenshot.png')

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
    bg_random = random.randint(1, 100)
    bg_random = f'0{bg_random}' if bg_random < 10 else str(bg_random)
    bg_img = Image.open(f'background/background-{bg_random}.jpeg')
    app_img = Image.open('screenshot.png')

    w, h = app_img.width, app_img.height
    img = Image.new('RGB', (w, h), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (w + 50, h)], fill='#FFFFFF')
    img = add_corners(img, 24)
    img.save('rect.png')

    image_resize = 0.95
    new_width = int(img.width * image_resize)
    new_height = int(img.height * image_resize)
    resized_app_img = app_img.resize((new_width, new_height))
    border = (0, 4, 0, 0)
    resized_app_img = ImageOps.crop(resized_app_img, border)
    resized_app_img = add_corners(resized_app_img, 24)
    img.paste(resized_app_img, (int(resized_app_img.width * 0.025), int(resized_app_img.width * 0.035)), resized_app_img)
    img.save('app_rect.png')

    image_resize_2 = 0.9
    new_width_2 = int(bg_img.width * image_resize_2)
    new_height_2 = int(bg_img.height * image_resize_2)
    resized_img = img.resize((new_width_2, new_height_2))

    bg_img.paste(resized_img, (int(bg_img.width * 0.05), int(bg_img.width * 0.06)), resized_img)
    if streamlit_logo:
        logo_img = Image.open('streamlit-logo.png').convert('RGBA')
        logo_img.thumbnail([sys.maxsize, logo_width], Image.LANCZOS)
        bg_img.paste(logo_img, (logo_horizontal_placement, logo_vertical_placement), logo_img)
    bg_img.save('final.png')

    st.image(bg_img)

# JavaScript for area selection
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    var startX, startY, endX, endY;
    var selectionDiv = document.createElement('div');
    selectionDiv.style.position = 'absolute';
    selectionDiv.style.border = '2px dashed #ff0000';
    selectionDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
    document.body.appendChild(selectionDiv);
    
    document.addEventListener('mousedown', function(e) {
        startX = e.pageX;
        startY = e.pageY;
        selectionDiv.style.left = startX + 'px';
        selectionDiv.style.top = startY + 'px';
        selectionDiv.style.width = '0px';
        selectionDiv.style.height = '0px';
        selectionDiv.style.display = 'block';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (startX !== undefined) {
            endX = e.pageX;
            endY = e.pageY;
            selectionDiv.style.width = Math.abs(endX - startX) + 'px';
            selectionDiv.style.height = Math.abs(endY - startY) + 'px';
            selectionDiv.style.left = Math.min(endX, startX) + 'px';
            selectionDiv.style.top = Math.min(endY, startY) + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (startX !== undefined) {
            document.dispatchEvent(new CustomEvent('areaSelected', {
                detail: {
                    x: Math.min(startX, endX),
                    y: Math.min(startY, endY),
                    width: Math.abs(endX - startX),
                    height: Math.abs(endY - startY)
                }
            }));
            selectionDiv.style.display = 'none';
            startX = startY = endX = endY = undefined;
        }
    });
});
</script>
""", unsafe_allow_html=True)

# Handle area selection event
st.write('<script>document.addEventListener("areaSelected", function(e) { window.parent.postMessage(e.detail, "*"); });</script>', unsafe_allow_html=True)

# Settings
with st.sidebar:
    st.header('⚙️ Settings')
    st.subheader('Image Resolution')
    width = st.slider('Width', 426, 1920, 1000)
    height = st.slider('Height', 240, 1080, 540)
    with st.expander('Streamlit logo'):
        streamlit_logo = st.checkbox('Add Streamlit logo', value=True, key='streamlit_logo')
        logo_width = st.slider('Image width', 0, 500, 100, step=10)
        logo_vertical_placement = st.slider('Vertical placement', 0, 1000, 670, step=10)
        logo_horizontal_placement = st.slider('Horizontal placement', 0, 1800, 80, step=10)
    ram_usage = psutil.virtual_memory()[2]
    st.caption(f'RAM used (%): {ram_usage}')

# Input URL
with st.form("my_form"):
    app_url = st.text_input('App URL', 'https://langchain-quickstart.streamlit.app').rstrip('/')
    app_name = app_url.replace('https://', '').replace('.streamlit.app', '')
    
    st.write("Select area to capture:")
    area = st.text_input("Enter area as x,y,width,height (comma separated)", "")
    area = [int(a) for a in area.split(',')] if area else None
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        if app_url:
            get_screenshot(app_url, area)

file_exists = exists('screenshot.png')
if file_exists:
    generate_app_image()

    with open("final.png", "rb") as file:
        btn = st.download_button(
            label="Download image",
            data=file,
            file_name=f"{app_name}.png",
            mime="image/png"
        )
        if btn:
            os.remove('screenshot.png')
            os.remove('final.png')
