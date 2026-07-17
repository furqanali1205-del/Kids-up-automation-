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

# Force clear local cache to prevent wrong channel values leaking
@st.cache_data(ttl=1)
def fetch_channel_stats_live(api_key, channel_id):
    if not api_key or not channel_id:
        return {"views": "0", "subs": "0", "videos": "0"}
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(part="statistics,snippet", id=channel_id)
        response = request.execute()
        if "items" in response and len(response["items"]) > 0:
            item = response["items"][0]
            stats = item["statistics"]
            return {
                "views": stats.get("viewCount", "0"),
                "subs": stats.get("subscriberCount", "0"),
                "videos": stats.get("videoCount", "0")
            }
    except:
        pass
    return {"views": "0", "subs": "0", "videos": "0"}

# --- AI Dynamic Script Generator ---
def generate_dynamic_script(format_type="Shorts"):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"Generate a unique and catchy 4-scene nursery rhyme or simple kids story optimized for YouTube {format_type}. Every time generate a different random theme like animals, space, sea life, numbers, or trains. Response must be strictly in raw JSON format with no markdown backticks with this structure: {{\x22title\x22: \x22Rhyme Title\x22, \x22scenes\x22: [\x22Scene 1 narrated line\x22, \x22Scene 2 narrated line\x22, \x22Scene 3 narrated line\x22, \x22Scene 4 narrated line\x22]}}"
    
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"}, timeout=10)
        raw_text = r.json()['candidates'][0]['content']['parts'][0]['text']
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except:
        t = int(time.time()) % 3
        themes = [
            {"title": f"The Jolly Little Train {t}", "scenes": ["Choo choo goes the happy train!", "Rolling down the track again.", "Red and blue and bright and green.", "Prettiest train you have ever seen!"]},
            {"title": f"Five Little Fishes {t}", "scenes": ["Five little fishes swimming in the sea.", "Happy and wild, swimming so free.", "One blew a bubble and swam away.", "Four little fishes left to play."]},
            {"title": f"Dancing Stars {t}", "scenes": ["Look at the stars up in the sky.", "Winking at us from way up high.", "Shining bright like a diamond glow.", "Lighting up the world below!"]}
        ]
        return themes[t]

# --- Download Background Music ---
def download_bg_music():
    bg_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    bg_path = "bg_music.mp3"
    if not os.path.exists(bg_path):
        r = requests.get(bg_url)
        with open(bg_path, "wb") as f: f.write(r.content)
    return bg_path

# --- High Quality Templates ---
def download_kids_template(index):
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
        from PIL import Image
        img = Image.new("RGB", (1080, 1920), color="#4f46e5")
        img.save(path)
    return path

async def generate_voice(text, path):
    communicate = edge_tts.Communicate(text, "en-US-AnaNeural", rate="+5%")
    await communicate.save(path)

def set_clip_duration(clip, duration):
    if hasattr(clip, "with_duration"): return clip.with_duration(duration)
    return clip.set_duration(duration)

def change_clip_volume(clip, volume_factor):
    if hasattr(clip, "with_volume_factor"): return clip.with_volume_factor(volume_factor)
    elif hasattr(clip, "volumex"): return clip.volumex(volume_factor)
    return clip

def build_premium_video(script_data, video_mode, progress_bar):
    clips = []
    bg_music_path = download_bg_music()
    resolution = (1080, 1920) if video_mode == "Shorts (9:16)" else (1920, 1080)
    
    for i, text in enumerate(script_data["scenes"]):
        progress_bar.progress((i+1)/6, text=f"Processing Scene {i+1}...")
        img_path = download_kids_template(i)
        v_path = f"v_{i}.mp3"
        asyncio.run(generate_voice(text, v_path))
        
        audio_clip = AudioFileClip(v_path)
        img_clip = ImageClip(img_path)
        
        if hasattr(img_clip, "resize"):
            img_clip = img_clip.resize(newsize=resolution)
            
        target_dur = audio_clip.duration + 0.5
        img_clip = set_clip_duration(img_clip, target_dur)
        
        video_clip = img_clip.set_audio(audio_clip)
        clips.append(video_clip)
        
    progress_bar.progress(5/6, text="Mixing Audio Tracks...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    bg_audio = AudioFileClip(bg_music_path)
    bg_audio = set_clip_duration(bg_audio, final_video.duration)
    bg_audio = change_clip_volume(bg_audio, 0.12)
    
    mixed_audio = CompositeAudioClip([final_video.audio, bg_audio])
    final_video = final_video.set_audio(mixed_audio)
    
    out_file = "final_output_video.mp4"
    final_video.write_videofile(out_file, fps=24, codec="libx264", audio_codec="aac")
    
    for f in glob.glob("v_*.mp3") + glob.glob("template_*.jpg"):
        try: os.remove(f)
        except: pass
        
    return out_file

# --- UI MAIN LAYOUT ---
st.title("🎬 Kids AutoPilot Video Studio")

tab_dashboard, tab_settings = st.tabs(["🚀 Video Pipeline", "⚙️ Channel Configuration"])

# Live fresh metrics extraction (No memory/leaks)
stats = fetch_channel_stats_live(st.session_state.api_key, st.session_state.channel_id)

with tab_dashboard:
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["videos"]}</div><p>Videos</p></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["subs"]}</div><p>Subscribers</p></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats["views"]}</div><p>Total Views</p></div>', unsafe_allow_html=True)
    
    st.write("---")
    video_mode = st.radio("📹 Choose Video Format:", ["Shorts (9:16)", "Long Video (16:9)"], horizontal=True)
    
    if st.button("🔥 Generate Brand New Custom Video"):
        p_bar = st.progress(0, text="Fetching fresh script...")
        script_data = generate_dynamic_script(video_mode)
        st.info(f"✨ **Theme:** {script_data['title']}")
        
        output = build_premium_video(script_data, video_mode, p_bar)
        p_bar.progress(1.0, text="Completed!")
        st.success("🎉 Video Mixed and Rendered Successfully!")
        st.video(output)

with tab_settings:
    st.subheader("🔗 Channel Linker Settings")
    in_key = st.text_input("YouTube API Key:", value=st.session_state.api_key, type="password")
    in_id = st.text_input("YouTube Channel ID:", value=st.session_state.channel_id)
    
    if st.button("Save & Sync Settings"):
        st.session_state.api_key = in_key
        st.session_state.channel_id = in_id
        # Hard reset Streamlit local storage cache
        st.cache_data.clear()
        st.success("Cache cleared and Settings Sync Completed!")
        time.sleep(0.5)
        st.rerun()
