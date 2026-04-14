import streamlit as st
import os
from dotenv import load_dotenv

from xai_sdk import Client
from xai_sdk.chat import system, user
from xai_sdk.tools import x_search, web_search

load_dotenv()

# ====================== PAGE SETUP ======================
st.set_page_config(
    page_title="X Client Insights Agent",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 X Client Insights Agent")
st.caption("Real-time brand + competitor analysis powered by Grok + X search")

# ====================== CONNECT TO GROK USING SECRETS ======================
if "xai_client" not in st.session_state:
    try:
        # First try Streamlit Secrets (for deployed app)
        api_key = st.secrets["XAI_API_KEY"]
    except:
        # Fallback to environment variable (for local testing)
        api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        st.error("❌ xAI API Key not found. Please add it in Streamlit Secrets.")
        st.stop()

    try:
        st.session_state.xai_client = Client(api_key=api_key.strip())
        st.success("✅ Connected to Grok!")
    except Exception as e:
        st.error(f"❌ Failed to connect to Grok: {e}")
        st.stop()

client = st.session_state.xai_client

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are an expert X (Twitter) Client Partner AI assistant specialized in competitive intelligence.
Always use x_search for real-time X data.
Be concise, professional, and give actionable advice for client meetings.
"""

# ====================== CHAT HISTORY ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ====================== USER INPUT ======================
if prompt := st.chat_input("Analyze a client or brand (e.g. Nike competitors, Starbucks campaign)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            chat = client.chat.create(
                model="grok-4.20-reasoning",
                tools=[x_search(), web_search()],
            )

            chat.append(system(SYSTEM_PROMPT))
            chat.append(user(
                f"Query: {prompt}\n\n"
                "Structure your response exactly like this:\n"
                "1. CLIENT / BRAND SUMMARY\n"
                "2. COMPETITOR INSIGHTS (top 2-3 competitors + side-by-side comparison)\n"
                "3. 3 READY-TO-POST X IDEAS (<280 chars each, differentiated from competitors)\n"
                "4. STRATEGIC RECOMMENDATIONS (how to outperform competitors)"
            ))

            for _, chunk in chat.stream():
                if chunk.content:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
