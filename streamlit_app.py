
import streamlit as st
import datetime
import random

# --- Basic setup ---
st.set_page_config(page_title="Daily Sparks", page_icon="✨", layout="centered")

st.title("✨ Daily Sparks")
st.subheader("A 2-minute daily ritual to grow into the person you want to be.")

# --- Session state ---
if 'step' not in st.session_state:
    st.session_state.step = 'onboarding'
if 'trait' not in st.session_state:
    st.session_state.trait = None
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'entries' not in st.session_state:
    st.session_state.entries = []
if 'writing_unlocked' not in st.session_state:
    st.session_state.writing_unlocked = False

# --- Prompts database ---
prompts = {
    "Gratitude": [
        "What’s one small thing you appreciated today but usually overlook?",
        "Who made your life easier this week — and have you thanked them?",
        "What challenge are you grateful for — even if it was uncomfortable?",
    ],
    "Courage": [
        "What did you do today that took effort or boldness?",
        "Is there something you avoided out of fear?",
        "What would ‘the brave version of you’ do tomorrow?",
    ],
    "Humility": [
        "Did you listen more than you spoke today?",
        "When were you wrong and learned from it?",
        "Who around you deserves more credit than they get?",
    ],
    "Compassion": [
        "Who might be struggling silently right now — and how can you support them?",
        "What’s one way you showed kindness today, even in a small moment?",
        "Where can you soften your judgment of someone?",
    ],
    "Self-Discipline": [
        "Where did you follow through on something difficult today?",
        "When were you tempted to quit, but didn’t?",
        "What’s one decision you made today that your future self will thank you for?",
    ]
}

# --- Onboarding ---
if st.session_state.step == 'onboarding':
    st.markdown("#### Who do you want to become?")
    trait = st.selectbox("Choose a growth trait:", list(prompts.keys()))
    mode = st.radio("When would you like to reflect?", ["Morning", "Night"])
    if st.button("Start Daily Sparks"):
        st.session_state.trait = trait
        st.session_state.mode = mode
        st.session_state.step = 'spark'

# --- Spark view ---
elif st.session_state.step == 'spark':
    st.success(f"Today's focus: **{st.session_state.trait}**")
    prompt = random.choice(prompts[st.session_state.trait])
st.markdown(f"### 🌟 Spark Prompt:\n**{prompt}**")
st.markdown("---")
    if not st.session_state.writing_unlocked:
        mood = st.radio("How did this make you feel?", ["😊", "😐", "😢", "💪"])
        if st.button("Log reflection"):
            st.session_state.entries.append({
                "date": str(datetime.date.today()),
                "trait": st.session_state.trait,
                "prompt": prompt,
                "response": mood,
                "written": False
            })
            if len(st.session_state.entries) >= 3:
                st.session_state.writing_unlocked = True
            st.success("Reflection saved! See you tomorrow ✨")
    else:
        response = st.text_area("Write your reflection (1–2 sentences):", height=100)
        if st.button("Submit"):
            st.session_state.entries.append({
                "date": str(datetime.date.today()),
                "trait": st.session_state.trait,
                "prompt": prompt,
                "response": response,
                "written": True
            })
            st.success("Reflection saved! Keep growing ✨")

    st.markdown("---")
    st.info(f"You've completed {len(st.session_state.entries)} reflection(s).")
    if not st.session_state.writing_unlocked:
        st.caption(f"Writing unlocks after 3 reflections. {3 - len(st.session_state.entries)} to go!")
    else:
        st.caption("Writing unlocked ✅")

