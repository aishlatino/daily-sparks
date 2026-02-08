from __future__ import annotations

import calendar
import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

# ---------- Configuration ----------
st.set_page_config(page_title="Daily Parsha", page_icon="📖", layout="wide")

DATA_PATH = Path("daily_entries.json")
SUBSCRIBERS_PATH = Path("subscribers.json")

PALETTE = {
    "bg": "#f8f6f1",
    "text": "#1f1f1f",
    "muted": "#66645f",
    "border": "#d8d4cc",
    "accent": "#7a6e5f",
    "card": "#fbfaf7",
}

ABOUT_TEXT = """
Daily Parsha is a daily Torah learning program focused on continuity.
Each day presents that day's learning with written commentary and recorded or live teaching.
This is a multi-year project built for steady participation, one day at a time.
""".strip()

ORIENTATION_TEXT = (
    "This is a daily Torah learning program. Every day we study that day’s Torah reading—"
    "word by word, with explanation and depth. You can join on any day."
    " The learning continues every day."
)


def default_entries() -> Dict[str, Dict[str, Any]]:
    today = dt.date.today()
    entries: Dict[str, Dict[str, Any]] = {}
    for offset in (-1, 0, 1):
        target = today + dt.timedelta(days=offset)
        key = target.isoformat()
        entries[key] = {
            "date": key,
            "hebrew_date": f"{target.day} Tevet 5786",
            "parsha": "Vayigash",
            "aliyah": f"Aliyah {((target.day % 7) or 7)}",
            "cycle_label": f"Day {200 + offset + 1}",
            "teacher": "Rabbi Levi Cohen",
            "live_time": "19:30",
            "live_active": offset == 0,
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "written": (
                "## Opening\n"
                "Torah learning begins with attention.\n\n"
                "> Every day carries its own gate of understanding.\n\n"
                "### Hebrew Text\n"
                "<div dir='rtl'>וַיְהִי מִקֵּץ שְׁנָתַיִם יָמִים...</div>\n\n"
                "### Notes\n"
                "1. Rashi on the opening verse.\n"
                "2. See Midrash Rabbah for a parallel reading."
            ),
            "published": True,
            "locked": True,
        }
    return entries


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_entries() -> Dict[str, Dict[str, Any]]:
    entries = load_json(DATA_PATH, default_entries())
    if not DATA_PATH.exists():
        save_json(DATA_PATH, entries)
    return entries


def load_subscribers() -> List[str]:
    subs = load_json(SUBSCRIBERS_PATH, [])
    if not SUBSCRIBERS_PATH.exists():
        save_json(SUBSCRIBERS_PATH, subs)
    return subs


def nav_css() -> None:
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {PALETTE['bg']}; color: {PALETTE['text']}; }}
          .main-title {{ font-size: 2.35rem; margin-bottom: .2rem; letter-spacing: -0.02em; }}
          .subtitle {{ color: {PALETTE['muted']}; font-size: 1rem; max-width: 900px; }}
          .bar {{ border: 1px solid {PALETTE['border']}; background: {PALETTE['card']}; padding: .8rem 1rem; border-radius: 6px; margin: 1rem 0; }}
          .orientation {{ border: 1px solid {PALETTE['border']}; background: {PALETTE['card']}; padding: .9rem 1rem; border-radius: 6px; }}
          .metadata {{ color: {PALETTE['muted']}; font-size: .95rem; }}
          .content-box {{ border-top: 1px solid {PALETTE['border']}; padding-top: 1rem; margin-top: 1rem; }}
          a {{ text-decoration: none; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sorted_dates(entries: Dict[str, Dict[str, Any]]) -> List[str]:
    return sorted(entries.keys())


def get_today_key(entries: Dict[str, Dict[str, Any]]) -> str | None:
    today = dt.date.today().isoformat()
    if today in entries:
        return today
    keys = sorted_dates(entries)
    return keys[-1] if keys else None


def read_route() -> str:
    params = st.query_params
    page = params.get("page", "today")
    if isinstance(page, list):
        page = page[0]
    return str(page)


def set_route(page: str, day: str | None = None) -> None:
    st.query_params.clear()
    st.query_params["page"] = page
    if day:
        st.query_params["day"] = day


def top_nav() -> None:
    left, right = st.columns([5, 1])
    with left:
        st.markdown("<div class='main-title'>Daily Parsha</div>", unsafe_allow_html=True)
        nav = st.columns(4)
        if nav[0].button("Today", use_container_width=True):
            set_route("today")
            st.rerun()
        if nav[1].button("Archive", use_container_width=True):
            set_route("archive")
            st.rerun()
        if nav[2].button("Live", use_container_width=True):
            set_route("live")
            st.rerun()
        if nav[3].button("About", use_container_width=True):
            set_route("about")
            st.rerun()
    with right:
        if st.button("Subscribe", use_container_width=True, type="secondary"):
            set_route("subscribe")
            st.rerun()


def live_bar(today_entry: Dict[str, Any]) -> None:
    if today_entry.get("live_active"):
        st.markdown(
            f"<div class='bar'><strong>Live now</strong> · {today_entry['teacher']} · "
            f"Started {today_entry['live_time']} — <a href='?page=live'>Join class</a></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='bar'>Next live class: {today_entry['live_time']} (local time)</div>",
            unsafe_allow_html=True,
        )


def render_home(entries: Dict[str, Dict[str, Any]]) -> None:
    today_key = get_today_key(entries)
    if not today_key:
        st.warning("No entries yet.")
        return
    entry = entries[today_key]
    st.markdown(f"### {entry['hebrew_date']} · {entry['date']}")
    st.markdown(f"## {entry['parsha']} — {entry['aliyah']}")
    cta = st.columns(3)
    if cta[0].button("Read Today", use_container_width=True):
        set_route("day", today_key)
        st.rerun()
    if cta[1].button("Watch Today", use_container_width=True):
        set_route("day", today_key)
        st.rerun()
    if cta[2].button("Listen", use_container_width=True):
        set_route("day", today_key)
        st.rerun()
    st.markdown(f"<p class='subtitle'>{ORIENTATION_TEXT}</p>", unsafe_allow_html=True)
    live_bar(entry)


def day_nav(entries: Dict[str, Dict[str, Any]], key: str) -> None:
    keys = sorted_dates(entries)
    idx = keys.index(key)
    prev_key = keys[idx - 1] if idx > 0 else None
    next_key = keys[idx + 1] if idx < len(keys) - 1 else None
    left, mid, right = st.columns(3)
    with left:
        if prev_key and st.button("← Previous Day", use_container_width=True):
            set_route("day", prev_key)
            st.rerun()
    with mid:
        if st.button("Today", use_container_width=True):
            set_route("today")
            st.rerun()
    with right:
        if next_key and st.button("Next Day →", use_container_width=True):
            set_route("day", next_key)
            st.rerun()


def render_day(entries: Dict[str, Dict[str, Any]]) -> None:
    key = st.query_params.get("day", get_today_key(entries))
    if isinstance(key, list):
        key = key[0]
    if key not in entries:
        st.error("Day not found.")
        return
    entry = entries[key]
    st.markdown(f"## {entry['hebrew_date']} · {entry['date']}")
    st.markdown(f"### {entry['parsha']} — {entry['aliyah']}")
    st.caption(entry["cycle_label"])

    st.markdown(
        "<div class='orientation'><strong>First time here?</strong><br/>"
        "You’re learning today’s Torah portion. No preparation needed—just start here.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='content-box'></div>", unsafe_allow_html=True)
    st.markdown(entry["written"], unsafe_allow_html=True)

    st.markdown("### Video / Audio")
    status = "Live" if entry.get("live_active") else "Recorded"
    st.markdown(f"<div class='metadata'>{status} · Teacher: {entry['teacher']}</div>", unsafe_allow_html=True)
    st.components.v1.iframe(entry["video_url"], height=360)
    st.audio(entry["audio_url"])

    day_nav(entries, key)


def render_archive(entries: Dict[str, Dict[str, Any]]) -> None:
    st.header("Archive")
    year = st.selectbox("Year", sorted({dt.date.fromisoformat(k).year for k in entries}, reverse=True))
    month = st.selectbox("Month", list(range(1, 13)), format_func=lambda m: calendar.month_name[m])

    st.subheader("Calendar View")
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].write(" ")
                continue
            key = dt.date(year, month, day_num).isoformat()
            if key in entries:
                if cols[i].button(str(day_num), key=f"cal-{key}", use_container_width=True):
                    set_route("day", key)
                    st.rerun()
            else:
                cols[i].markdown(f"<span class='metadata'>{day_num}</span>", unsafe_allow_html=True)

    st.subheader("Parsha View")
    by_parsha: Dict[str, List[Dict[str, Any]]] = {}
    for item in entries.values():
        by_parsha.setdefault(item["parsha"], []).append(item)
    for parsha, items in sorted(by_parsha.items()):
        with st.expander(parsha):
            for item in sorted(items, key=lambda it: it["date"]):
                if st.button(f"{item['date']} · {item['aliyah']}", key=f"p-{item['date']}"):
                    set_route("day", item["date"])
                    st.rerun()


def render_live(entries: Dict[str, Dict[str, Any]]) -> None:
    today_key = get_today_key(entries)
    if not today_key:
        return
    item = entries[today_key]
    st.header("Live Learning")
    st.markdown("Daily class times: Sunday–Thursday 19:30 · Friday 11:00")
    st.markdown(f"Teacher: {item['teacher']}")
    st.markdown("Format: Daily Parsha with close reading and practical explanation.")
    st.components.v1.iframe(item["video_url"], height=400)
    st.markdown("Optional in-person classes: Jerusalem 20:30, New York 20:00")


def render_about() -> None:
    st.header("About")
    st.write(ABOUT_TEXT)


def render_subscribe() -> None:
    st.header("Subscribe")
    st.write("Receive each day’s learning by email.")
    with st.form("subscribe_form"):
        email = st.text_input("Email")
        submitted = st.form_submit_button("Subscribe")
    if submitted:
        subscribers = load_subscribers()
        if email and email not in subscribers:
            subscribers.append(email)
            save_json(SUBSCRIBERS_PATH, subscribers)
            st.success("Subscribed.")
        else:
            st.info("Already subscribed or invalid email.")


def render_admin(entries: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    with st.expander("Admin: Daily Entry Management"):
        st.caption("Create, schedule, publish, and lock daily entries.")
        with st.form("new_entry"):
            date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))
            hebrew_date = st.text_input("Hebrew Date", value="1 Shevat 5786")
            parsha = st.text_input("Parsha", value="Bo")
            aliyah = st.text_input("Aliyah", value="Aliyah 1")
            cycle_label = st.text_input("Cycle Label", value="Day 201")
            teacher = st.text_input("Teacher", value="Rabbi Levi Cohen")
            live_time = st.text_input("Live Time", value="19:30")
            video_url = st.text_input("Video Embed URL", value="https://www.youtube.com/embed/dQw4w9WgXcQ")
            audio_url = st.text_input("Audio URL", value="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
            written = st.text_area("Written Content (Markdown + optional RTL HTML)", height=180)
            publish = st.checkbox("Publish now", value=True)
            lock = st.checkbox("Lock on publish", value=True)
            submit = st.form_submit_button("Create / Overwrite")

        if submit:
            key = date.isoformat()
            existing = entries.get(key)
            if existing and existing.get("locked") and not st.session_state.get("override_lock", False):
                st.error("Entry is locked. Enable explicit override and submit again.")
            else:
                entries[key] = {
                    "date": key,
                    "hebrew_date": hebrew_date,
                    "parsha": parsha,
                    "aliyah": aliyah,
                    "cycle_label": cycle_label,
                    "teacher": teacher,
                    "live_time": live_time,
                    "live_active": False,
                    "video_url": video_url,
                    "audio_url": audio_url,
                    "written": written or "No written content yet.",
                    "published": publish,
                    "locked": lock,
                }
                save_json(DATA_PATH, entries)
                st.success(f"Saved entry for {key}.")

        st.checkbox("Explicit override for locked entries", key="override_lock")
    return entries


# ---------- App ----------
nav_css()
entries_state = copy.deepcopy(load_entries())
top_nav()
entries_state = render_admin(entries_state)

route = read_route()
if route == "today":
    render_home(entries_state)
elif route == "day":
    render_day(entries_state)
elif route == "archive":
    render_archive(entries_state)
elif route == "live":
    render_live(entries_state)
elif route == "about":
    render_about()
elif route == "subscribe":
    render_subscribe()
else:
    render_home(entries_state)
