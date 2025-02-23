import streamlit as st
import requests
import re

# ---------------------------
# Streamlit Page Configuration
# ---------------------------
st.set_page_config(page_title="Founders Podcast GPT", page_icon="F", layout="centered")

# ---------------
# Custom CSS (Dark)
# ---------------
custom_css = """
<style>
/* Overall background */
body {
    background-color: #0E1117 !important;
    color: #E1E1E1 !important;
}

/* Remove Streamlit default top padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* Chat message bubbles */
.chat-bubble {
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    line-height: 1.4;
}

.user-bubble {
    background-color: #2C2F33;
    text-align: left;
    color: #FFFFFF;
}

.assistant-bubble {
    background-color: #23272A;
    text-align: left;
    color: #FFFFFF;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background-color: #1f1f1f;
}
::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 4px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------
# Page Title and Description
# ---------------------------
st.write("")
st.header("Founders Podcast GPT")
st.write("Ask me anything.")

# ---------------------------------
# Initialize Session State for Chat
# ---------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = (
        []
    )  # Each item: {"role": "user"/"assistant", "content": ..., "analysis": ..., "sources": ...}


# ----------------------------------------
# Helper Function to Query Your FastAPI API
# ----------------------------------------
def query_backend(user_input: str):
    """
    Sends the user_input to your FastAPI backend /query endpoint.
    The backend is expected to return a JSON dict like:
      {
         "sources": [...],
         "context_analysis": "...",
         "response": "..."
      }
    """
    try:
        url = "http://localhost:8000/query"
        payload = {"query": user_input}
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return {"sources": [], "response": f"Error: {str(e)}"}


# ---------------------------
# Display All Chat Messages
# ---------------------------
def display_chat():
    """
    Renders all messages stored in session_state as chat bubbles.
    For assistant messages, we also show expanders for context analysis + sources if present.
    """
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # User bubble
            st.markdown(
                f'<div class="chat-bubble user-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Assistant bubble
            st.markdown(
                f'<div class="chat-bubble assistant-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            # If there's context analysis, show it in an expander
            analysis_text = msg.get("analysis", "")
            if analysis_text:
                with st.expander("Show context analysis"):
                    st.markdown(analysis_text)

            # If there are sources, show them in another expander
            sources = msg.get("sources", [])
            if sources:
                with st.expander("Sources"):
                    for src in sources:
                        st.markdown(f"- {src}")


# ---------------------------
# Main Chatbot Functionality
# ---------------------------
def main():
    display_chat()

    # Use Streamlit's new chat_input widget (requires Streamlit >= 1.22).
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Add the user's message to the session
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Query the backend
        backend_result = query_backend(user_input)

        # The raw text that possibly includes <context_analysis> and <response>
        analysis_text = backend_result.get("context_analysis", "")
        final_answer = backend_result.get("response", "")
        # The list of sources (if any)
        sources = backend_result.get("sources", [])

        # Store the assistant's message in session_state
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_answer,  # visible bubble
                "analysis": analysis_text,  # hidden in expander
                "sources": sources,  # hidden in expander
            }
        )

        # Immediately update the UI
        st.rerun()


if __name__ == "__main__":
    main()
