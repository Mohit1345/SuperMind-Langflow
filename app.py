import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

load_dotenv()
# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = os.environ.get("LANGFLOW_ID") 
FLOW_ID = os.environ.get("FLOW_ID") 
APPLICATION_TOKEN = os.environ.get("APPLICATION_TOKEN")  # Replace with your actual token
TWEAKS = {
    "ChatInput-zqJHc": {},
    "AzureOpenAIModel-wSMfJ": {},
    "ChatOutput-UFwns": {},
    "Prompt-L08F8": {},
    "Prompt-yPXwF": {},
    "AstraDBToolComponent-dCiii": {},
    "Agent-TGf7G": {}
}

# Function to call the API
def run_flow(message, endpoint, output_type="chat", input_type="chat", tweaks=None, application_token=None):
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"} if application_token else None

    if tweaks:
        payload["tweaks"] = tweaks

    response = requests.post(api_url, json=payload, headers=headers)
    try:
        result = response.json()
        # Safely access the deeply nested 'text'
        text = result.get('outputs', [])
        if text:
            text = text[-1].get('outputs', [])
            if text:
                text = text[-1].get('results', {}).get('message', {}).get('data', {}).get('text', 'Default text if not found')
        return text
    except (KeyError, IndexError, TypeError) as e:
        # Handle error, such as logging or returning a fallback value
        return 'Error retrieving data'


# Streamlit UI
st.title("LangFlow API Interaction & Analytics Dashboard")
st.markdown("This app provides two functionalities: interacting with the LangFlow API and creating an analytical dashboard from a CSV file.")

# Tabs for the two functionalities
tabs = st.tabs(["LangFlow API Interaction", "Analytics Dashboard"])

# Tab 1: LangFlow API Interaction
with tabs[0]:
    st.header("LangFlow API Interaction")

    # User inputs
    message = st.text_input("Message", "Type your message here...")
    endpoint = st.text_input("Endpoint", FLOW_ID)
    output_type = st.selectbox("Output Type", ["chat", "json"])
    input_type = st.selectbox("Input Type", ["chat", "json"])
    application_token = st.text_input("Application Token", APPLICATION_TOKEN, type="password")
    tweaks = st.text_area("Tweaks (JSON)", json.dumps(TWEAKS, indent=2))

    # Run API call on button click
    if st.button("Send Request"):
        try:
            tweaks_dict = json.loads(tweaks)
            response = run_flow(
                message=message,
                endpoint=endpoint,
                output_type=output_type,
                input_type=input_type,
                tweaks=tweaks_dict,
                application_token=application_token
            )
            print(response)
            st.success("Request sent successfully!")
            # st.json(response)
            st.write(response)
        except json.JSONDecodeError:
            st.error("Invalid tweaks JSON format.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Tab 2: Analytics Dashboard
with tabs[1]:
    st.header("Analytics Dashboard")

    # File upload
    # uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    uploaded_file = "arijitsingh_instagram_posts.csv"

    if uploaded_file is not None:
        # Load the data
        data = pd.read_csv(uploaded_file)

        # Validate required columns
        required_columns = ["post_id", "post_type", "likes", "comments", "timestamp", "caption"]
        if all(col in data.columns for col in required_columns):

            # Show raw data
            st.subheader("Raw Data")
            st.dataframe(data)

            # Pie chart: Distribution of post types
            st.subheader("Post Type Distribution")
            pie_chart = px.pie(data, names="post_type", title="Post Type Distribution", hole=0.4)
            st.plotly_chart(pie_chart)

            # Bar chart: Top performing posts by likes
            st.subheader("Top Performing Posts by Likes")
            top_likes = data.sort_values(by="likes", ascending=False).head(10)
            bar_chart = px.bar(top_likes, x="post_id", y="likes", color="post_type", title="Top Posts by Likes")
            st.plotly_chart(bar_chart)

            # Line chart: Likes over time
            st.subheader("Likes Over Time")
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            data = data.sort_values("timestamp")
            line_chart = px.line(data, x="timestamp", y="likes", title="Likes Over Time", markers=True)
            st.plotly_chart(line_chart)

            # Tabular insights
            st.subheader("Summary Insights")
            st.markdown(f"- **Total Posts**: {data.shape[0]}")
            st.markdown(f"- **Total Likes**: {data['likes'].sum()}")
            st.markdown(f"- **Total Comments**: {data['comments'].sum()}")

            # Additional insights
            best_post = data.loc[data['likes'].idxmax()]
            st.markdown(f"- **Best Performing Post**: {best_post['caption']} ({best_post['likes']} likes)")

        else:
            st.error("The uploaded CSV file must contain the required columns: post_id, post_type, likes, comments, timestamp, caption.")
    else:
        st.info("Please upload a CSV file to view the analytics dashboard.")
