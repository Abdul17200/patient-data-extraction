import streamlit as st
import spacy
import pandas as pd
import pdfplumber

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# App title
st.title("🩺 Patient Data Extractor")

# Upload file (txt or pdf)
uploaded_file = st.file_uploader("Upload clinical note (.txt or .pdf)", type=["txt", "pdf"])

if uploaded_file:
    # Extract text from uploaded file
    file_text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                file_text += page.extract_text() + "\n"
    else:
        file_text = uploaded_file.read().decode("utf-8")

    # Show raw text
    st.subheader("📄 Raw Extracted Text")
    st.text_area("Note Content", file_text, height=300)

    # Run spaCy
    doc = nlp(file_text)
    persons = list({ent.text for ent in doc.ents if ent.label_ == "PERSON"})
    orgs = list({ent.text for ent in doc.ents if ent.label_ == "ORG"})
    dates = list({ent.text for ent in doc.ents if ent.label_ == "DATE"})

    # Keyword matching
    disease_keywords = ["diabetes", "hypertension", "asthma", "covid", "cancer"]
    medication_keywords = ["paracetamol", "metformin", "aspirin", "ibuprofen"]

    found_diseases = list({word for word in file_text.lower().split() if word in disease_keywords})
    found_meds = list({word for word in file_text.lower().split() if word in medication_keywords})

    # Editable form
    with st.form("edit_form"):
        st.subheader("✏️ Edit Extracted Information")

        name = st.text_input("Patient Name", persons[0] if persons else "")
        org = st.text_input("Hospital / Organization", orgs[0] if orgs else "")
        visit_date = st.text_input("Visit Date", dates[0] if dates else "")
        next_visit = st.text_input("Next Visit Date", dates[1] if len(dates) > 1 else "")

        disease = st.text_input("Diagnosed Disease(s)", ", ".join(found_diseases))
        medications = st.text_input("Medications", ", ".join(found_meds))

        submitted = st.form_submit_button("Save")

        if submitted:
            st.success("✅ Data saved successfully!")
            result = {
                "Name": name,
                "Organization": org,
                "Visit Date": visit_date,
                "Next Visit": next_visit,
                "Diseases": disease,
                "Medications": medications
            }
            st.json(result)
