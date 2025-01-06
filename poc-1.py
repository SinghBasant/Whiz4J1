import streamlit as st
import openai
# Set up OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]
# Function to generate a response from OpenAI
def get_openai_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=200,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"
# Streamlit app
st.title("WhizBot - Talk2Me:sunglasses:")
st.write("Powered by Whizlabs R&D Squad")
# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
# User input
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submitted = st.form_submit_button("Submit")
# Handle user input
if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response = get_openai_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**WhizBot:** {message['content']}")
