import streamlit as st
import base64
from google import genai

st.set_page_config(
    page_title="BioLens AI",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 BioLens AI")
st.subheader("AI-Powered Biological Identification Assistant")

st.write(
    "Upload an image of an animal, bird, plant, or microorganism "
    "to receive an AI-assisted biological analysis."
)

st.info(
    "BioLens AI provides AI-assisted identification. "
    "Important scientific identifications should be verified."
)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    client = None

organism_type = st.selectbox(
    "Select organism type",
    ["Animal / Bird", "Plant", "Microorganism"]
)

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)

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
