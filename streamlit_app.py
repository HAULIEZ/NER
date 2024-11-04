import streamlit as st
import requests
import pandas as pd

# Base URL of the FastAPI server
FASTAPI_URL = "http://127.0.0.1:8000"  # Adjust if running on a different host/port

# Page configuration
st.set_page_config(
    page_title="Health NER API Interface",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header section
st.title("Advanced Health NER API")
st.write("A modern, intuitive interface for extracting health-related entities like diseases, symptoms, and treatments.")

# Define function for extracting entities
def extract_entities(text):
    response = requests.post(f"{FASTAPI_URL}/extract_entities", json={"text": text})
    return response.json()

# Define function for getting common entities
def get_common_entities(top_n):
    response = requests.get(f"{FASTAPI_URL}/get_common_entities", params={"top_n": top_n})
    return response.json()

# Define function for batch extraction of entities
def batch_extract_entities(texts):
    response = requests.post(f"{FASTAPI_URL}/batch_extract_entities", json=[{"text": text} for text in texts])
    return response.json()

# Define function for category-specific extraction
def category_specific_extraction(category, text):
    response = requests.post(f"{FASTAPI_URL}/category_specific_extraction", json={"text": text}, params={"category": category})
    return response.json()

# Define function for getting entity trends
def get_entity_trends():
    response = requests.get(f"{FASTAPI_URL}/entity_trends")
    return response.json()

# Sidebar for navigation
st.sidebar.title("Explore the API")
option = st.sidebar.radio("Choose an action", [
    "Extract Entities", "Get Common Entities", "Batch Extract Entities",
    "Category Specific Extraction", "Entity Trends"
])

# Extract Entities
if option == "Extract Entities":
    st.header("Extract Entities from Text")
    text = st.text_area("Enter text to extract entities:", placeholder="Type your text here...")
    if st.button("Extract Entities"):
        if text:
            result = extract_entities(text)
            st.subheader("Extracted Entities")
            for entity in result["entities"]:
                st.markdown(f"- **Entity**: {entity['text']}, **Type**: {entity['entity']}, **Frequency**: {entity['frequency']}, **Color**: {entity['color']}")
        else:
            st.warning("Please enter text to analyze.")

# Get Common Entities
elif option == "Get Common Entities":
    st.header("Get Most Common Entities")
    top_n = st.slider("Number of top entities to retrieve:", min_value=1, max_value=20, value=5)
    if st.button("Get Common Entities"):
        result = get_common_entities(top_n)
        st.subheader("Common Entities")
        for category in result:
            st.write(f"### {category['category'].capitalize()} Entities")
            for entity in category["entities"]:
                entity_name, count = list(entity.items())[0]
                st.markdown(f"- **Entity**: {entity_name}, **Count**: {count}")

# Batch Extract Entities
elif option == "Batch Extract Entities":
    st.header("Batch Extract Entities")
    batch_texts = st.text_area("Enter multiple texts separated by new lines:", placeholder="Enter one text per line.")
    if st.button("Extract Batch Entities"):
        texts = batch_texts.strip().split("\n")
        result = batch_extract_entities(texts)
        st.subheader("Batch Extraction Results")
        for res in result:
            st.write(f"### Text: {res['text']}")
            for entity in res["entities"]:
                st.markdown(f"- **Entity**: {entity['text']}, **Type**: {entity['entity']}, **Frequency**: {entity['frequency']}, **Color**: {entity['color']}")

# Category Specific Extraction
elif option == "Category Specific Extraction":
    st.header("Category-Specific Extraction")
    category = st.selectbox("Select category:", ["DISEASE", "SYMPTOM", "TREATMENT"])
    text = st.text_area("Enter text for category-specific extraction:", placeholder="Type your text here...")
    if st.button("Extract Category-Specific Entities"):
        result = category_specific_extraction(category, text)
        st.subheader(f"Entities in Category: {category.capitalize()}")
        for entity in result["entities"]:
            st.markdown(f"- **Entity**: {entity['text']}, **Frequency**: {entity['frequency']}, **Color**: {entity['color']}")

# Entity Trends
elif option == "Entity Trends":
    st.header("View Entity Trends")
    if st.button("Show Entity Trends"):
        result = get_entity_trends()
        st.subheader("Entity Trends")
        for category, trends in result["trends"].items():
            st.write(f"### {category.capitalize()} Trends")
            df = pd.DataFrame(trends.items(), columns=["Entity", "Frequency"])
            st.table(df)

# Footer with information
st.sidebar.markdown("---")
st.sidebar.write("Developed by Group 4")
st.sidebar.write("Connect with us on [LinkedIn](https://www.linkedin.com) | [GitHub](https://github.com)")

st.sidebar.info("This tool is for educational and experimental purposes.")
