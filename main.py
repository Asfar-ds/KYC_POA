import streamlit as st
from pypdf import PdfReader
from groq import Groq
from prompt import POA_PROMPT
from PIL import Image
import pytesseract

# Initialize Groq client using Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])



# If using Windows, set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("📄 AI Proof of Address Verifier")

st.write("Upload a **PDF or Image document** to verify Proof of Address.")

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["pdf", "png", "jpg", "jpeg"]
)

user_address = st.text_input("Enter your address to match with the document")

text = ""

if uploaded_file and user_address:

    file_type = uploaded_file.type

    st.info("Extracting text from document...")

    # -------- PDF Processing --------
    if file_type == "application/pdf":

        reader = PdfReader(uploaded_file)

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    # -------- Image Processing --------
    else:

        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document")

        text = pytesseract.image_to_string(image)

    st.success("Text extracted!")

    with st.expander("View Extracted Text"):
        st.write(text)

    if st.button("Verify Proof of Address"):

        with st.spinner("Analyzing document..."):

            prompt = f"""
{POA_PROMPT}

USER PROVIDED ADDRESS:
{user_address}

DOCUMENT TEXT:
{text}

Analyze the document strictly according to the above rules.
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            result = response.choices[0].message.content

        st.subheader("Verification Result")

        st.code(result)