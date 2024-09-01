import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="🎈 App Screenshot")
st.title('🎈 App Screenshot with Area Selection')

# Inject JavaScript into the Streamlit app
st.components.v1.html(
    """
    <button onclick="captureArea()">Select and Capture Area</button>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js"></script>
    <script>
        function captureArea() {
            html2canvas(document.body).then(function(canvas) {
                var imgData = canvas.toDataURL('image/png');
                var img = new Image();
                img.src = imgData;
                document.body.appendChild(img);
            });
        }
    </script>
    """, height=600
)

# A simple file uploader to demonstrate saving the selected image
uploaded_file = st.file_uploader("Upload the selected image (for testing purposes)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Save the image if needed
    image.save("captured_area.png")
    st.success("Image saved as 'captured_area.png'")
