import streamlit as st
import requests
import pandas as pd
import json
import base64
import matplotlib.pyplot as plt

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
st.title(" Advanced Health NER API")
st.write("A modern, intuitive interface for extracting health-related entities like diseases, symptoms, and treatments.")

# Helper function to fetch data
def extract_entities(text):
    response = requests.post(f"{FASTAPI_URL}/extract_entities", json={"text": text})
    return response.json()

def get_common_entities(top_n):
    response = requests.get(f"{FASTAPI_URL}/get_common_entities", params={"top_n": top_n})
    return response.json()

def batch_extract_entities(texts):
    response = requests.post(f"{FASTAPI_URL}/batch_extract_entities", json=[{"text": text} for text in texts])
    return response.json()

def get_entity_trends():
    response = requests.get(f"{FASTAPI_URL}/entity_trends")
    return response.json()

# Sidebar navigation
st.sidebar.title(" Explore the API")
option = st.sidebar.radio("Choose an action", [
    "Extract Entities 🧬", "Get Common Entities 📊", "Batch Extract Entities 📋", "Entity Trends 📈"
])

# Feature: Interactive Visualization for Common Entities
if option == "Get Common Entities 📊":
    st.header("📊 Most Common Entities")
    top_n = st.slider("Number of top entities to retrieve:", min_value=1, max_value=20, value=5)
    if st.button("Get Common Entities"):
        result = get_common_entities(top_n)
        st.subheader("Common Entities")
        
        # Display as a bar chart
        for category in result:
            entity_names = [list(entity.keys())[0] for entity in category["entities"]]
            entity_counts = [list(entity.values())[0] for entity in category["entities"]]
            
            fig, ax = plt.subplots()
            ax.barh(entity_names, entity_counts, color="skyblue")
            ax.set_xlabel("Frequency")
            ax.set_title(f"{category['category'].capitalize()} Entities")
            st.pyplot(fig)

# Feature: Highlighted Entity Display for Extracted Entities
elif option == "Extract Entities 🧬":
    st.header("🧬 Extract Entities from Text")
    text = st.text_area("Enter text to extract entities:", placeholder="Type your text here...")
    if st.button("Extract Entities"):
        if text:
            result = extract_entities(text)
            st.subheader("Extracted Entities")

            # Display text with highlighted entities
            highlighted_text = text
            for entity in result["entities"]:
                color = entity["color"]
                highlighted_text = highlighted_text.replace(
                    entity["text"], f":{color}[{entity['text']}]"
                )
            
            st.markdown(f"**Highlighted Text:** {highlighted_text}")

            # Display entity details
            for entity in result["entities"]:
                st.markdown(f"- **Entity**: {entity['text']}, **Type**: {entity['entity']}, **Frequency**: {entity['frequency']}, **Color**: {entity['color']}")
        else:
            st.warning("Please enter text to analyze.")

# Feature: File Upload for Batch Entity Extraction
elif option == "Batch Extract Entities 📋":
    st.header("📋 Batch Extract Entities")
    uploaded_file = st.file_uploader("Upload a text file with each text on a new line:", type="txt")
    if uploaded_file is not None:
        # Read file content
        file_content = uploaded_file.read().decode("utf-8").splitlines()
        if st.button("Extract Batch Entities"):
            result = batch_extract_entities(file_content)
            st.subheader("Batch Extraction Results")
            
            # Display each result
            for res in result:
                st.write(f"### Text: {res['text']}")
                for entity in res["entities"]:
                    st.markdown(f"- **Entity**: {entity['text']}, **Type**: {entity['entity']}, **Frequency**: {entity['frequency']}, **Color**: {entity['color']}")

# Feature: Entity Trends Visualization
elif option == "Entity Trends 📈":
    st.header("📈 View Entity Trends")
    if st.button("Show Entity Trends"):
        result = get_entity_trends()
        st.subheader("Entity Trends")
        for category, trends in result["trends"].items():
            st.write(f"### {category.capitalize()} Trends")
            
            # Display trends as a table
            df = pd.DataFrame(trends.items(), columns=["Entity", "Frequency"])
            st.table(df)

            # Bar chart for trends
            fig, ax = plt.subplots()
            ax.barh(df["Entity"], df["Frequency"], color="lightcoral")
            ax.set_title(f"{category.capitalize()} Trends")
            st.pyplot(fig)

# Feature: Export Results as CSV
def export_as_csv(data, filename="export.csv"):
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    b64 = base64.b64encode(csv_data.encode()).decode()  # strings <-> bytes conversions
    link = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return link

# Example usage:
# st.markdown(export_as_csv(result["entities"], "entities_export.csv"), unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Developed by [Your Name](https://yourwebsite.com)")
st.sidebar.write("Connect with us on [LinkedIn](https://www.linkedin.com) | [GitHub](https://github.com)")

st.sidebar.info("💡 This tool is for educational and experimental purposes.")
