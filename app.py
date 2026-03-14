import streamlit as st
from PIL import Image
from modules.recommender import get_recommendations

st.set_page_config(page_title="AI Wardrobe Assistant")

st.title("👔 Personal AI Wardrobe Assistant")

st.write("Upload a garment photo to get matching recommendations.")

# Upload image
uploaded_file = st.file_uploader(
    "Upload garment image",
    type=["jpg", "png", "jpeg"]
)

# Select garment type
garment_type = st.selectbox(
    "Select garment type",
    ["shirt", "trouser"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Garment", use_column_width=True)

if st.button("Analyze Outfit"):

    if uploaded_file is None:
        st.warning("Please upload an image.")
    else:

        # TEMPORARY placeholder color
        detected_color = "black"

        recommendations = get_recommendations(
            detected_color,
            garment_type
        )

        st.subheader("Recommendations")

        for rec in recommendations:

            st.markdown(f"### {rec['category']}")
            st.write(f"**Suggested Color:** {rec['color']}")
            st.write(f"**Confidence:** {rec['confidence']}%")
            st.write(rec['reason'])

            st.divider()