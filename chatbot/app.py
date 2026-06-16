import streamlit as st
from nltk.chat.util import Chat, reflections

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spice Garden | Chat",
    page_icon="🍽️",
    layout="centered",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@400;500&display=swap');

/* ── Background ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f0e0c;
    color: #f0ede8;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }

/* ── Restaurant header ── */
.restaurant-header {
    text-align: center;
    padding: 2rem 0 1rem;
    border-bottom: 1px solid #2a2825;
    margin-bottom: 1.5rem;
}
.restaurant-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #e8c97e;
    margin: 0;
    letter-spacing: 0.02em;
}
.restaurant-header p {
    font-size: 0.85rem;
    color: #6b6660;
    margin: 0.3rem 0 0;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── Chat messages ── */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.5rem 0 1.5rem;
}

.msg-row-user {
    display: flex;
    justify-content: flex-end;
}
.msg-row-bot {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 0.6rem;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e8c97e22;
    border: 1px solid #e8c97e55;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.bubble-user {
    background: #e8c97e;
    color: #0f0e0c;
    padding: 0.65rem 1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.92rem;
    font-weight: 500;
    line-height: 1.45;
}

.bubble-bot {
    background: #1e1c19;
    color: #f0ede8;
    padding: 0.65rem 1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 72%;
    font-size: 0.92rem;
    line-height: 1.45;
    border: 1px solid #2a2825;
}

/* ── Quick-reply chips ── */
.chips-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

/* ── Input area ── */
[data-testid="stChatInput"] {
    background: #1e1c19 !important;
    border: 1px solid #2a2825 !important;
    border-radius: 12px !important;
    color: #f0ede8 !important;
}

/* ── Quick-reply buttons ── */
.stButton > button {
    background: #1e1c19;
    border: 1px solid #e8c97e55;
    color: #e8c97e;
    border-radius: 20px;
    font-size: 0.82rem;
    padding: 0.35rem 0.85rem;
    transition: background 0.2s;
    font-family: 'Inter', sans-serif;
}
.stButton > button:hover {
    background: #e8c97e18;
    border-color: #e8c97e;
    color: #e8c97e;
}

/* ── Divider ── */
hr { border-color: #2a2825; }
</style>
""", unsafe_allow_html=True)

# ── Custom name-aware respond function ───────────────────────────────────────
import re

def get_response(user_input):
    """Try name patterns first (needs capture group), then fall back to Chat."""
    # "my name is X" / "i am X" / "name is X"
    name_match = re.search(
        r'(?:my name is|i am|i\'m|name is)\s+([a-zA-Z]+)', user_input, re.IGNORECASE
    )
    if name_match:
        name = name_match.group(1).capitalize()
        return f"Hello {name}! 😊 Great to meet you. How can I help you today?"
    return None  # fall through to NLTK Chat

# ── NLTK chatbot setup ────────────────────────────────────────────────────────
PAIRS = [
    # Greetings
    [r'(hi|hello|hey)(.*)',
     ["Hello! Welcome to Spice Garden 🍽️ How can I help you today?"]],

    # How are you
    [r'(how are you|how r you|how are u|hows it going|how do you do)(.*)',
     ["I'm doing great, thanks for asking! 😊 How can I help you today?",
      "All good here! Ready to take your order. What can I get you? 😄"]],

    # What is your name / who are you
    [r'(what is your name|who are you|what are you|your name)(.*)',
     ["I'm the Spice Garden virtual assistant 🤖🍽️ Here to help you with our menu, prices, and more!"]],

    # Thank you
    [r'(thank you|thanks|thank u|thx)(.*)',
     ["You're welcome! 😊 Is there anything else I can help you with?",
      "Happy to help! Let me know if you need anything else. 🍽️"]],

    # Goodbye
    [r'(bye|goodbye|see you|see ya|cya|good night)(.*)',
     ["Goodbye! 👋 Hope to see you at Spice Garden soon!",
      "Take care! Come visit us anytime. 😊"]],

    # Compliments
    [r'(good|great|awesome|nice|excellent|amazing|love it)(.*)',
     ["That's so kind of you! 😄 We always try our best. Anything else I can help with?"]],

    # Order / place order
    [r'(i want to order|place an order|can i order|order|order food)(.*)',
     ["Sure! You can visit us at our Hyderabad location or call us to place your order. 📞\nOur timings are 10 AM – 11 PM."]],

    # Offers / discounts
    [r'(offer|discount|deal|coupon|promo)(.*)',
     ["🎉 We have exciting offers running! Visit us in-store or follow us on social media for the latest deals."]],

    # Payment
    [r'(payment|pay|upi|cash|card|online payment)(.*)',
     ["💳 We accept Cash, UPI, and all major Cards. Easy and hassle-free!"]],

    # Menu
    [r'(menu|show menu|food menu)(.*)',
     ["Our menu features: 🍕 Pizza · 🍔 Burger · 🍛 Biryani\nAsk me about any item for pricing!"]],

    # Timing
    [r'(timing|opening hours|opening|when are you open)(.*)',
     ["We're open every day from 10 AM to 11 PM. Come hungry! 🕙"]],

    # Location
    [r'(where are you located|location|address|where is the restaurant)(.*)',
     ["We're located in Hyderabad. Drop by anytime! 📍"]],

    # Pizza
    [r'(pizza price|pizza|price of pizza|how much is pizza)(.*)',
     ["🍕 Pizza — ₹250\nFreshly baked with your choice of toppings."]],

    # Burger
    [r'(burger price|burger|price of burger|how much is burger)(.*)',
     ["🍔 Burger — ₹150\nJuicy patty, crisp lettuce, house sauce."]],

    # Biryani
    [r'(biryani price|biryani|price of biryani|how much is biryani)(.*)',
     ["🍛 Biryani — ₹150\nAromatic basmati, slow-cooked to perfection."]],

    # Fallback
    [r'(.*)',
     ["Thanks for reaching out! Our customer care team will contact you shortly. 😊"]],
]

@st.cache_resource
def get_chatbot():
    return Chat(PAIRS, reflections)

chatbot = get_chatbot()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "👋 Hi! I'm the Spice Garden assistant. Ask me about our menu, prices, timing, or location!"}
    ]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="restaurant-header">
    <h1>🍽️ Spice Garden</h1>
    <p>Chat with us · Hyderabad</p>
</div>
""", unsafe_allow_html=True)

# ── Quick-reply chips ─────────────────────────────────────────────────────────
QUICK_REPLIES = ["Show Menu", "Pizza Price", "Burger Price", "Biryani Price", "Timings", "Location"]

cols = st.columns(len(QUICK_REPLIES))
for i, label in enumerate(QUICK_REPLIES):
    if cols[i].button(label, key=f"qr_{label}"):
        user_text = label
        st.session_state.messages.append({"role": "user", "text": user_text})
        inp = user_text.lower()
        response = get_response(inp) or chatbot.respond(inp) or "Our customer care team will contact you shortly."
        st.session_state.messages.append({"role": "bot", "text": response})
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ── Render chat history ───────────────────────────────────────────────────────
chat_html = '<div class="chat-wrap">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f'<div class="msg-row-user"><div class="bubble-user">{msg["text"]}</div></div>'
    else:
        chat_html += f'<div class="msg-row-bot"><div class="avatar">🍽️</div><div class="bubble-bot">{msg["text"]}</div></div>'
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Type your message…"):
    st.session_state.messages.append({"role": "user", "text": user_input})
    inp = user_input.lower()
    response = get_response(inp) or chatbot.respond(inp) or "Our customer care team will contact you shortly."
    st.session_state.messages.append({"role": "bot", "text": response})
    st.rerun()