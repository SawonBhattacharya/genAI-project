# react_sql_agent_ui.py
import streamlit as st
from react_agent import agent_executor  # import from your main agent file

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Sales Data Assistant", page_icon="📊", layout="centered")

st.title("📊 Sales Data Assistant")
st.markdown("Ask questions about **sales, products, channels, cities, or quantities** and get business insights instantly.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Input box for new query
if user_query := st.chat_input("💬 Ask me about sales data..."):
    # Add user query to history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your query... ⏳"):
            try:
                response = agent_executor.invoke({"input": user_query})
                answer = response["output"]
            except Exception as e:
                answer = f"⚠️ Error: {e}"
            st.markdown(answer)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})
