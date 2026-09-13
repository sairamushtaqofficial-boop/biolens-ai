import streamlit as st
import base64
from google import genai

st.set_page_config(
    page_title="BioLens AI",
    page_icon="🔬",
    layout="wide"
)

# -----------------------------
# Custom UI styling
# -----------------------------
st.markdown("""
<style>
.main-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0;
}
.subtitle {
    font-size: 1.15rem;
    margin-top: 0.2rem;
    margin-bottom: 1.5rem;
}
.category-card {
    padding: 1rem;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1rem;
}
.category-icon {
    font-size: 2rem;
}
.upload-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1rem;
}
.footer-note {
    text-align: center;
    margin-top: 2rem;
    opacity: 0.7;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Gemini client
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    client = None

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="main-title">🔬 BioLens AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Biological Identification Assistant</div>',
    unsafe_allow_html=True
)

st.write(
    "Explore animals, birds, plants, and microorganisms from a single image "
    "using AI-assisted biological analysis."
)

st.info(
    "🔎 BioLens AI provides AI-assisted identification. "
    "Important scientific identifications should be independently verified."
)

# -----------------------------
# Categories
# -----------------------------
st.markdown("### 🧬 What do you want to identify?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """<div class="category-card">
        <div class="category-icon">🐦</div>
        <b>Animals & Birds</b><br>
        <small>Species and biological information</small>
        </div>""",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """<div class="category-card">
        <div class="category-icon">🌱</div>
        <b>Plants</b><br>
        <small>Identification and botanical information</small>
        </div>""",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """<div class="category-card">
        <div class="category-icon">🔬</div>
        <b>Microorganisms</b><br>
        <small>Morphology and possible identification</small>
        </div>""",
        unsafe_allow_html=True
    )

organism_type = st.selectbox(
    "Choose analysis category",
    ["Animal / Bird", "Plant", "Microorganism"]
)

# -----------------------------
# Image upload
# -----------------------------
st.markdown(
    '<div class="upload-title">📷 Upload your image</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Supported formats: JPG, JPEG, PNG, WEBP",
    type=["jpg", "jpeg", "png", "webp"]
)

# -----------------------------
# Prompt creation
# -----------------------------
def build_prompt(category):
    if category == "Animal / Bird":
        return """
You are BioLens AI, a biological identification assistant.

Analyze the uploaded image of an animal or bird.

Give the most likely identification based on visible evidence.

Use these sections:

## Identification
Common name:
Scientific name:
Confidence:

## Classification
Kingdom:
Phylum:
Class:
Order:
Family:
Genus:
Species:

## Biology
Physical characteristics:
Habitat:
Geographic distribution:
Diet:
Ecological role:

## Similar Species
Mention up to two similar species if relevant.

## Interesting Fact
Give one short interesting fact.

IMPORTANT:
If the image is unclear, explicitly say so.
Do not claim certainty when the evidence is insufficient.
"""

    if category == "Plant":
        return """
You are BioLens AI, a biological identification assistant.

Analyze the uploaded image of a plant.

Give the most likely identification based on visible evidence.

Use these sections:

## Identification
Common name:
Scientific name:
Confidence:

## Classification
Kingdom:
Phylum/Division:
Class:
Order:
Family:
Genus:
Species:

## Botany
Visible characteristics:
Habitat:
Geographic distribution:
Ecological role:
Common uses, if reliably known:

## Similar Species
Mention up to two similar species if relevant.

IMPORTANT:
Do not claim an exact species when the image does not provide enough evidence.
Do not make unsupported medical or edible-use claims.
"""

    return """
You are BioLens AI, a microbiology image analysis assistant.

Analyze the uploaded microorganism or microscopy image.

IMPORTANT:
Morphology alone usually cannot establish a definitive species identification.
Do not pretend that an exact species has been confirmed.

Use these sections:

## Observed Morphology
Cell shape:
Cell arrangement:
Visible staining characteristics:
Other visible features:

## Likely Identification
Likely group:
Possible organism(s):
Confidence:

## Microbiology
Relevant biological characteristics:
Possible habitat or source:

## Confirmation
Suggest appropriate laboratory tests or observations
that could help confirm the identification.

## Scientific Limitation
Clearly explain what cannot be confirmed from this image alone.
"""

# -----------------------------
# Analysis
# -----------------------------
if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded image",
        use_container_width=True
    )

    if st.button("🔍 Analyze Organism", type="primary"):
        if client is None:
            st.error(
                "Gemini API key is not configured. "
                "Add GEMINI_API_KEY to Streamlit Secrets."
            )
            st.stop()

        try:
            with st.spinner("Analyzing image..."):
                image_bytes = uploaded_file.getvalue()
                image_data = base64.b64encode(image_bytes).decode("utf-8")
                mime_type = uploaded_file.type
                prompt = build_prompt(organism_type)

                # Same working Interactions API format tested in Colab
                response = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=[
                        {
                            "type": "image",
                            "data": image_data,
                            "mime_type": mime_type
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                )

                result = response.output_text

                if result:
                    st.success("Analysis complete!")
                    st.markdown("## 🧬 Biological Analysis")
                    st.markdown(result)
                    st.caption(
                        "AI-generated analysis. Verify important "
                        "scientific identifications independently."
                    )
                else:
                    st.error(
                        "The AI returned an empty response. "
                        "Please try another image."
                    )

        except Exception as e:
            st.error("The image could not be analyzed.")
            st.exception(e)

st.markdown(
    '<div class="footer-note">BioLens AI • AI-assisted biological exploration</div>',
    unsafe_allow_html=True
)
