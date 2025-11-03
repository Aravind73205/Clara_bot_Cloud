#import content
import random
import streamlit as st
import google.generativeai as genai


#page config
st.set_page_config(
    page_title="MediBot - Your Health Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

#api key load
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)

except KeyError:
    st.stop()

#prompt for clara
clara_prompt = f"""You are Mrs.Clara, an experienced AI powered family doctor, Your goal is to understand patient issues and support them.

Key Notes:
 Do not prescribe drugs or specific treatments beyond basic first aid
 If user Asked to generate Images(eg: show the image of how that allergy looks like), refuse politely.
 Flag sensitive topics (eg: if "suicide", "self-harm", "abuse", "violence", etc.), "Escalate: Advise immediate professional help."
 At the end of the chat:
  Summarize the coversation in 3-5 bullet points. 
  Ask: "Did this help? (Yes/No)" and suggest next steps.

 You are not a replacement for inperson care, always guide toward professional consulting when needed.
"""

#model init
model_name = "gemini-2.5-flash"
model = genai.GenerativeModel(
    model_name=model_name,
    system_instruction=clara_prompt
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.chat_session.history.append({
        "role": "model",
        "parts": [{"text": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?"}]
    })

def extract_message_data(message):
    if isinstance(message, dict):
        role = message.get("role")
        content = message.get("parts", [{}])[0].get("text", "[Content Error]")

    else:
        role = message.role
        content = message.parts[0].text if message.parts and message.parts[0].text else "[Reply loading...]"
    
    display_role = "assistant" if role == "model" else role
    return display_role, content

#custom response
def style_response(text):
    starters = ["Hmm", "Okay", "Alright,"]
    emojis = ["💊","👍","😊"]

    if random.random() < 0.2:
        text = random.choice(starters) + " " + text

    if random.random() < 0.4:
        text += " " + random.choice(emojis)

    return text

st.markdown("## 👩🏻‍⚕️ **Clara** | Smart Health Assistant")

# Chat container
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_session.history:
        role, content = extract_message_data(message)
        if content:
            with st.chat_message(role):
                st.markdown(content if role == "user" else style_response(content))

#input content
user_input = st.chat_input(placeholder="Ask Clara... 💬")
if user_input:
    st.session_state.chat_session.history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    # to get reply from gemini
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        try:
            with st.spinner("Checking with Clara..."):
                response = st.session_state.chat_session.send_message(
                    user_input,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7
                    ),
                ) 
            ai_reply = response.text     
            typing_placeholder.markdown(style_response(response.text))          

        except Exception as e:
            st.error("Something went wrong") 

#sidebar for guidance
with st.sidebar:

    st.markdown("---")
    st.markdown("### 🔹 **Quick Tips**")

    st.markdown("""
    - **Describe your symptoms** ( severity, duration, etc...)
    - **Ask about health tips** (Healthy Snacks, Fatfree Foods..)
    - **Need urgent help?** 🚨 Contact Professional!
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ **Note**")

    st.markdown("""
    -  I’m your **Smart health Assistant, not a certified doctor**, consult a professional for serious concerns🌱
    """)
    

    st.markdown("---")
    st.markdown("♊️ *Powered by Google's Gemini*")
    
    #clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_session = model.start_chat(
            history=[]
        )
        st.session_state.chat_session.history.append({
            "role": "model",
            "parts": [{"text": "Hi! I'm Clara, your AI health companion 😇. How are you feeling today?"}]
        })