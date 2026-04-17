import streamlit as st
import os

from xai_sdk import Client
from xai_sdk.chat import system, user
from xai_sdk.tools import x_search, web_search

st.set_page_config(
    page_title="X Client Insights Agent",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 X Client Insights Agent")
st.caption("Real-time brand + competitor intelligence with X Ads recommendations")

# ====================== GROK CLIENT ======================
if "xai_client" not in st.session_state:
    try:
        api_key = st.secrets["XAI_API_KEY"]
        st.session_state.xai_client = Client(api_key=api_key.strip())
        st.success("✅ Connected to Grok")
    except:
        st.error("❌ xAI API Key not found in Secrets.")
        st.stop()

client = st.session_state.xai_client

# ====================== UPGRADED SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are an expert X (Twitter) Client Partner AI assistant specialized in competitive intelligence and X advertising strategy.

Use real-time x_search data.

Structure your response **exactly** like this:

1. CLIENT / BRAND SUMMARY
   • Key trends, overall sentiment, notable posts

2. COMPETITOR INSIGHTS
   • Include the client itself + top 2-3 direct competitors
   • Present a clean Markdown table with these columns:
     Brand | Handle | Followers | Activity Volume | Sentiment | Avg. Engagement | Top Content Type

3. 3 READY-TO-POST X IDEAS
   • Each idea must be under 280 characters
   • Make them highly engaging and differentiated from competitors
   • For each idea, recommend the best X Ads product to amplify it 
     (Promoted Posts, Video Ads, X Amplify, Trend Takeover, Carousel Ads, etc.)

4. STRATEGIC RECOMMENDATIONS
   • 2-3 high-impact strategies to outperform competitors
   • Recommend specific X Ads products to sell or run 
     (X Amplify, Video Ads, Trend Takeover, Promoted Trends, Ads Manager campaigns, etc.)
"""

# ====================== CHAT HISTORY ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ====================== USER INPUT ======================
if prompt := st.chat_input("Analyze a client or brand (e.g. Nike competitors, Huawei Pura X Max launch)"):
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
            chat.append(user(f"Analyze recent X activity for: {prompt}"))

            for _, chunk in chat.stream():
                if chunk.content:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

# ====================== UTILITY ======================
if st.button("🔄 Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
