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

st.set_page_config(page_title="Premium YouTube Automation Studio", page_icon="🎬", layout="centered")

# --- Dark Slate Premium UI ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3, p, label { color: #f8fafc !important; }
    div[data-baseweb="input"] { background-color: #1e293b !important; color: white !important; border-radius: 10px !important; }
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

# --- Download Background Music ---
def download_bg_music():
    bg_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # Safe royalty-free kids instrumental stream
    bg_path = "bg_music.mp3"
    if not os.path.exists(bg_path):
        r = requests.get(bg_url)
        with open(bg_path, "wb") as f: f.write(r.content)
    return bg_path

# --- High Quality Templates instead of Ugly Emoji ---
def download_kids_template(index):
    # Free standard cartoon templates for kids background
    urls = [
        "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=1080&q=80",
        "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1080&q=80",
        "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1080&q=80",
        "https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=1080&q=80"
    ]
    path = f"template_{index}.jpg"
    try:
        r = requests.get(urls[index % len(urls)])
        with open(path, "wb") as f: f.write(r.content)
    except:
        # Fallback
        from PIL import Image
        img = Image.new("RGB", (1080, 1920), color="#4f46e5")
        img.save(path)
    return path

async def generate_voice(text, path):
    communicate = edge_tts.Communicate(text, "en-US-AnaNeural", rate="+5%")
    await communicate.save(path)

def build_premium_video(progress_bar):
    # Fixed high quality template scripts for kids rhymes
    scenes_data = [
        "Welcome to the magical world of fun and learning!",
        "Five little birds sitting on a tree, singing sweet songs for you and me.",
        "Let us count them together one by one.",
        "Don't forget to like and subscribe for more amazing adventures!"
    ]
    
    clips = []
    bg_music_path = download_bg_music()
    
    for i, text in enumerate(scenes_data):
        progress_bar.progress((i+1)/6, text=f"Rendering Scene {i+1} with HD Template...")
        img_path = download_kids_template(i)
        v_path = f"v_{i}.mp3"
        asyncio.run(generate_voice(text, v_path))
        
        audio_clip = AudioFileClip(v_path)
        img_clip = ImageClip(img_path).set_duration(audio_clip.duration + 0.5)
        video_clip = img_clip.set_audio(audio_clip)
        clips.append(video_clip)
        
    progress_bar.progress(5/6, text="Mixing Background Music Track...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Mix Background Music at 15% Volume so voice is clear
    bg_audio = AudioFileClip(bg_music_path).set_duration(final_video.duration).volumex(0.15)
    mixed_audio = CompositeAudioClip([final_video.audio, bg_audio])
    final_video = final_video.set_audio(mixed_audio)
    
    out_file = "premium_kids_short.mp4"
    final_video.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup logs
    for f in glob.glob("v_*.mp3") + glob.glob("template_*.jpg"):
        try: os.remove(f)
        except: pass
        
    return out_file

# --- UI Layout ---
st.title("🎬 Premium Kids Automation Studio")
st.write(f"Connected Channel ID: `{st.session_state.channel_id}`")

youtube_client = get_youtube_client()
stats = fetch_channel_stats(youtube_client, st.session_state.channel_id) if youtube_client else {"views": "0", "subs": "0", "videos": "0"}

# --- Correct Stats Injection ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["videos"]}</div><p>Real Videos</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["subs"]}</div><p>Subscribers</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["views"]}</div><p>Total Views</p></div>', unsafe_allow_html=True)

st.write("---")

if st.button("🔥 Generate Premium Video with Music & Song"):
    p_bar = st.progress(0, text="Starting engine...")
    output = build_premium_video(p_bar)
    p_bar.progress(1.0, text="Done!")
    st.success("🎉 Video created with high-quality background music mix!")
    st.video(output)

# --- Configuration Tab ---
st.write("---")
with st.expander("⚙️ Re-configure Channel Credentials"):
    in_key = st.text_input("YouTube API Key:", value=st.session_state.api_key, type="password")
    if st.button("Save Settings"):
        st.session_state.api_key = in_key
        st.rerun()
