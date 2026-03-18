import streamlit as st
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()
from modules.recommender import get_recommendations
from modules.color_detector import get_dominant_color

st.set_page_config(page_title="AI Wardrobe Assistant")

st.title("👔 Personal AI Wardrobe Assistant")

st.write("Upload a garment photo to get matching recommendations.")

# Upload image
uploaded_file = st.file_uploader(
    "Upload garment image",
    type=["jpg", "png", "jpeg","heic"]
)

# Select garment type
garment_type = st.selectbox(
    "Select garment type",
    ["shirt", "trouser"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Selected Garment", width='stretch')

if st.button("Analyze Outfit"):

    if image is None:
        st.warning("Please capture or upload an image.")

    else:
        detected_color = get_dominant_color(image)
        st.write(f"Detected Color: {detected_color}")

        recommendations = get_recommendations(
            detected_color,
            garment_type
        )

        st.subheader("Recommendations")

        for rec in recommendations:
            st.markdown(f"### {rec['category']}")
            st.write(f"**Suggested Color:** {rec['color']}")
            st.write(f"**Confidence:** {rec['confidence']}%")
            st.write(rec["reason"])
            st.divider()