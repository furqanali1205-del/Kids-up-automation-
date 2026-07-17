import streamlit as st
import os
import json
import time
import glob
import asyncio
import requests
from googleapiclient.discovery import build

# --- MoviePy Imports ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
except ImportError:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

# --- Edge-TTS ---
import edge_tts

st.set_page_config(page_title="Dynamic Kids Automation Studio", page_icon="🎬", layout="centered")

# --- Dark Slate Premium UI ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3, p, label { color: #f8fafc !important; }
    div[data-baseweb="input"], div[data-baseweb="select"] { background-color: #1e293b !important; color: white !important; border-radius: 10px !important; }
    .stButton>button { 
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important; 
        color: white !important; border-radius: 12px !important; height: 50px !important; font-weight: bold !important; border: none !important;
    }
    .stat-card {
        background-color: #1e293b; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #334155;
    }
    .stat-num { font-size: 32px; font-weight: 800; color: #38bdf8; }
    </style>
""", unsafe_allow_html=True)

# --- State Management ---
if "api_key" not in st.session_state: st.session_state.api_key = st.secrets.get("YOUTUBE_API_KEY", "")
if "channel_id" not in st.session_state: st.session_state.channel_id = "UCuILBGteDysGVKVMaPPnjxg"
if "channel_name" not in st.session_state: st.session_state.channel_name = "kids Up"

def get_youtube_client():
    if not st.session_state.api_key: return None
    try: return build('youtube', 'v3', developerKey=st.session_state.api_key)
    except: return None

def fetch_channel_stats(youtube, channel_id):
    if not channel_id: return None
    try:
        request = youtube.channels().list(part="statistics,snippet", id=channel_id)
        response = request.execute()
        if "items" in response:
            item = response["items"][0]
            st.session_state.channel_name = item["snippet"]["title"]
            stats = item["statistics"]
            return {
                "views": stats.get("viewCount", "0"),
                "subs": stats.get("subscriberCount", "0"),
                "videos": stats.get("videoCount", "0")
            }
    except: pass
    return {"views": "0", "subs": "0", "videos": "0"}

# --- AI Dynamic Script Generator ---
def generate_dynamic_script(format_type="Shorts"):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = (
        f"Generate a unique and catchy 4-scene nursery rhyme or simple kids story optimized for YouTube {format_type}. "
        "Every time generate a different random theme (like animals, space, sea life, numbers, or trains). "
        "Response must be strictly in raw JSON format (no markdown backticks or extra words) with this structure: "
        '{"title": "Rhyme Title", "scenes": ["Scene 1 narrated line", "Scene 2 narrated line", "Scene 3 narrated line", "Scene 4 narrated line"]}'
    )
    
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"}, timeout=10)
        raw_text = r.json()['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = raw_text.replace("```json", "").replace("
