
import streamlit as st
import datetime
import random

# --- Basic setup ---
st.set_page_config(page_title="Daily Sparks", page_icon="✨", layout="centered")
st.title("✨ Daily Sparks")
st.subheader("A 2-minute daily ritual to grow into the person you want to be.")

# --- Session state setup ---
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
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = None

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
    mode = st.radio("When would you like to reflect?", ["Day Planning", "Reflection"])
    if st.button("Start Daily Sparks"):
        st.session_state.trait = trait
        st.session_state.mode = mode
        st.session_state.step = 'spark'
        st.session_state.current_prompt = random.choice(prompts[trait])

# --- Spark view ---
elif st.session_state.step == 'spark':
    st.success(f"Today's focus: **{st.session_state.trait}**")
    prompt = st.session_state.current_prompt
    st.markdown(f"### 🌟 Spark Prompt:
**{prompt}**")
    st.markdown("---")

    # Progress bar
    total_needed = 10
    completed = len(st.session_state.entries)
    progress = min(completed / total_needed, 1.0)
    st.progress(progress, text=f"{completed}/{total_needed} reflections completed")

    # Response section
    if not st.session_state.writing_unlocked:
        mood = st.radio("How did this make you feel?", ["😊", "😐", "😢", "💪"])
        if st.button("Log reflection"):
            st.session_state.entries.append({
                "date": str(datetime.date.today()),
                "trait": st.session_state.trait,
                "mode": st.session_state.mode,
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
                "mode": st.session_state.mode,
                "prompt": prompt,
                "response": response,
                "written": True
            })
            st.success("Reflection saved! Keep growing ✨")

    st.markdown("---")
    st.info(f"You've completed {completed} reflection(s).")
    if not st.session_state.writing_unlocked:
        st.caption(f"Writing unlocks after 3 reflections. {3 - completed} to go!")
    else:
        st.caption("Writing unlocked ✅")

    # Reflection report after 10 entries
    if completed >= 10:
        st.markdown("## 🧠 Reflection Report")
        most_common_trait = st.session_state.trait
        most_common_mode = max(set([e['mode'] for e in st.session_state.entries]), key=[e['mode'] for e in st.session_state.entries].count)
        all_responses = [e['response'] for e in st.session_state.entries if not e['written']]
        if all_responses:
            most_common_mood = max(set(all_responses), key=all_responses.count)
            st.markdown(f"**Most common mood:** {most_common_mood}")
        st.markdown(f"**Reflection mode:** {most_common_mode}")
        st.markdown(f"**Growth trait focus:** {most_common_trait}")
