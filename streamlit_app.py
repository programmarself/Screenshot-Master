import streamlit as st

# Add JavaScript for area selection
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
