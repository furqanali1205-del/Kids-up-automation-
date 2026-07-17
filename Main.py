import streamlit as st
import os
import json
import time
import glob
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

# --- Safe Dynamic Import for MoviePy ---
try:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
except ImportError:
    try:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
    except ImportError:
        st.error("⚠️ Requirements mein 'moviepy==1.0.3' check karein.")

# --- Edge-TTS Import ---
try:
    import edge_tts
except ImportError:
    st.error("⚠️ 'edge-tts' library missing hai.")

# Google API client for public/data fetch
from googleapiclient.discovery import build

# --- Page Config ---
st.set_page_config(page_title="YouTube Automation Studio", page_icon="🎬", layout="centered")

# --- Custom Premium CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    h1, h2, h3, p { color: #1e293b !important; }
    div[data-baseweb="input"] { background-color: white !important; border-radius: 8px !important; }
    
    .stButton>button { 
        background-color: #8b5cf6 !important; 
        color: white !important; 
        border-radius: 30px !important; 
        width: 100% !important; 
        height: 52px !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(139, 92, 246, 0.3);
    }
    
    .shogo-header {
        background-color: white;
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        border: 1px solid #f1f5f9;
    }
    
    .stat-card {
        background-color: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .stat-num { font-size: 28px; font-weight: 800; margin-bottom: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Simple Settings ---
if "api_key" not in st.session_state: st.session_state.api_key = st.secrets.get("YOUTUBE_API_KEY", "")
if "channel_id" not in st.session_state: st.session_state.channel_id = st.secrets.get("YOUTUBE_CHANNEL_ID", "")
if "channel_name" not in st.session_state: st.session_state.channel_name = "My Channel"

# --- Simple Public Client Builder ---
def get_youtube_client():
    if not st.session_state.api_key:
        return None
    try:
        return build('youtube', 'v3', developerKey=st.session_state.api_key)
    except Exception:
        return None

# --- Stats Fetcher via API Key ---
def fetch_channel_stats(youtube, channel_id):
    if not channel_id: return None
    try:
        request = youtube.channels().list(part="statistics,snippet", id=channel_id)
        response = request.execute()
        if "items" in response:
            item = response["items"][0]
            stats = item["statistics"]
            st.session_state.channel_name = item["snippet"]["title"]
            return {
                "views": stats.get("viewCount", "0"),
                "subs": stats.get("subscriberCount", "0"),
                "videos": stats.get("videoCount", "0")
            }
    except Exception:
        pass
    return None

# --- Gemini AI Script Generator ---
def generate_ai_content(format_type="short"):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Generate a 4-scene nursery rhyme script for kids, optimized for YouTube {format_type}. Response as JSON with keys: 'title', 'description', 'tags', 'scenes' (list with 'text', 'bg_color', 'character_action'). No markdown backticks."
    
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        raw_text = r.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(raw_text.replace("```json", "").replace("```", "").strip())
    except Exception:
        return {
            "title": "Five Little Monkeys Jumping On The Bed",
            "description": "Fun kids animation. #nurseryrhymes",
            "tags": "kids songs, nursery rhymes",
            "scenes": [
                {"text": "Five little monkeys jumping on the bed!", "bg_color": "#ff6b6b", "character_action": "jumping"},
                {"text": "One fell off and bumped his head!", "bg_color": "#4ecdc4", "character_action": "crying"},
                {"text": "Mama called the doctor and the doctor said,", "bg_color": "#ffe66d", "character_action": "laughing"},
                {"text": "No more monkeys jumping on the bed!", "bg_color": "#1a535c", "character_action": "dancing"}
            ]
        }

# --- Edge-TTS Engine ---
async def generate_edge_voice(text, output_path):
    try:
        communicate = edge_tts.Communicate(text, "en-US-AnaNeural", rate="+10%")
        await communicate.save(output_path)
    except Exception:
        with open(output_path, "wb") as f: f.write(b"")

# --- Video Rendering Framework ---
def compile_professional_video(content_data, is_short=True, progress_bar=None):
    clips = []
    size = (1080, 1920) if is_short else (1920, 1080)
    
    for i, scene in enumerate(content_data["scenes"]):
        if progress_bar: progress_bar.progress((i + 1) / len(content_data["scenes"]), text=f"Processing Scene {i+1}...")
        img = Image.new("RGB", size, color=scene["bg_color"])
        draw = ImageDraw.Draw(img)
        cx, cy = size[0] // 2, size[1] // 2
        
        draw.ellipse([cx-160, cy-160, cx+160, cy+160], fill="#ffde59", outline="#ff914d", width=12)
        draw.ellipse([cx-80, cy-60, cx-40, cy-20], fill="black")
        draw.ellipse([cx+40, cy-60, cx+80, cy-20], fill="black")
        if scene.get("character_action") == "crying":
            draw.arc([cx-60, cy+60, cx+60, cy+120], start=180, end=360, fill="black", width=10)
        else:
            draw.arc([cx-60, cy+40, cx+60, cy+100], start=0, end=180, fill="black", width=10)
            
        frame_path = f"p_frame_{i}.png"
        img.save(frame_path)
        
        audio_path = f"p_voice_{i}.mp3"
        asyncio.run(generate_edge_voice(scene["text"], audio_path))
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.6 if audio_clip.duration > 0 else 3.0
            img_clip = ImageClip(frame_path)
            video_clip = img_clip.with_duration(duration).with_audio(audio_clip) if hasattr(img_clip, "with_duration") else img_clip.set_duration(duration).set_audio(audio_clip)
        except Exception:
            img_clip = ImageClip(frame_path)
            video_clip = img_clip.with_duration(3.0) if hasattr(img_clip, "with_duration") else img_clip.set_duration(3.0)
        
        clips.append(video_clip)
        
    try:
        final_video = concatenate_videoclips(clips, method="compose")
        output_filename = "automated_output.mp4"
        final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
        return output_filename
    except Exception:
        return None
    finally:
        for f in glob.glob("p_frame_*.png") + glob.glob("p_voice_*.mp3"):
            try: os.remove(f)
            except: pass

# --- BRAND HEADER ---
st.markdown("""
    <div class="shogo-header">
        <div style="background-color: #ef4444; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
            <span style="color: white; font-size: 22px; font-weight: bold;">▶</span>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: #8b5cf6 !important;">YouTube Automation Studio</h2>
            <p style="margin: 0; font-size: 12px; color: #64748b;">Easiest Key & ID Method</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab_dashboard, tab_research, tab_scripts, tab_voice, tab_videos, tab_schedule, tab_channel = st.tabs([
    "📊 Dashboard", "🔍 Research", "📄 Scripts", "🎙️ Voiceovers", "🎬 Videos", "📅 Scheduled", "⚙️ Add Channel"
])

youtube_client = get_youtube_client()
real_views, real_subs, real_vids = "0", "0", "0"

if youtube_client and st.session_state.channel_id:
    api_stats = fetch_channel_stats(youtube_client, st.session_state.channel_id)
    if api_stats:
        real_views = f"{int(api_stats['views']):,}"
        real_subs = f"{int(api_stats['subs']):,}"
        real_vids = api_stats['videos']

# ==================== TAB 1: DASHBOARD ====================
with tab_dashboard:
    if not youtube_client or not st.session_state.channel_id:
        st.warning("⚠️ **Channel Config Missing!** Go to '⚙️ Add Channel' to link using your API Key and Channel ID.")
    else:
        st.success(f"🎉 **Connected to:** {st.session_state.channel_name}")

    st.markdown("""
        <div style="background-color: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <span style="font-weight: bold; font-size: 18px; color: #6d28d9;">🤖 YouTube AutoPilot</span>
    """, unsafe_allow_html=True)
    
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        video_format = st.selectbox("📹 Format Select", ["Shorts (Portrait)", "Long Video (Landscape)"])
    with col_ap2:
        target_country = st.selectbox("🌍 Target Country", ["US", "UK", "CA", "PK"])
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("▶ Run Full Pipeline Now"):
        if not st.session_state.api_key:
            st.error("❌ Link your Channel using your API Key first.")
        else:
            status_container = st.empty()
            progress_bar = st.progress(0, text="Initializing Pipeline...")
            
            status_container.info("🤖 Generating Script with Gemini AI...")
            is_short = video_format == "Shorts (Portrait)"
            ai_data = generate_ai_content("short" if is_short else "long")
            st.write(f"✨ **Title:** {ai_data['title']}")
            
            status_container.info("🎬 Creating Video & Audio via Edge-TTS...")
            video_file = compile_professional_video(ai_data, is_short=is_short, progress_bar=progress_bar)
            
            if video_file and os.path.exists(video_file):
                progress_bar.progress(1.0, text="Completed!")
                status_container.success("🎉 **Video Ready!** (Automated rendering finished successfully).")
                st.video(video_file)
            else:
                status_container.error("❌ Video build failed.")

    st.write("---")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f'<div class="stat-card" style="border-left: 5px solid #ef4444;"><div class="stat-num" style="color: #ef4444;">{real_vids}</div><p style="color: #64748b; margin: 0; font-size: 14px;">Total Videos</p></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<div class="stat-card" style="border-left: 5px solid #10b981;"><div class="stat-num" style="color: #10b981;">{real_subs}</div><p style="color: #64748b; margin: 0; font-size: 14px;">Total Subscribers</p></div>', unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f'<div class="stat-card" style="border-left: 5px solid #3b82f6;"><div class="stat-num" style="color: #3b82f6;">{real_views}</div><p style="color: #64748b; margin: 0; font-size: 14px;">Total Views</p></div>', unsafe_allow_html=True)

# ==================== TAB 7: CHANNEL MANAGEMENT (OLD SIMPLE WAY) ====================
with tab_channel:
    st.subheader("⚙️ Add Channel (Easiest Way)")
    st.write("Apna data fill karein aur channel ko bina kisi token jhanjhat ke direct sync karein:")
    
    in_key = st.text_input("🔑 Enter YouTube API Key:", value=st.session_state.api_key, type="password")
    in_id = st.text_input("🆔 Enter Channel ID:", value=st.session_state.channel_id, placeholder="UCxxxxxxxxxxxxxxxxx")
    in_name = st.text_input("📛 Enter Channel Name (Optional):", value=st.session_state.channel_name)
    
    if st.button("🔄 Sync & Save Channel"):
        if not in_key or not in_id:
            st.error("API Key aur Channel ID dono daalna zaroori hai!")
        else:
            st.session_state.api_key = in_key
            st.session_state.channel_id = in_id
            st.session_state.channel_name = in_name
            st.success("🎉 Channel credentials saved! Dashboard check karein.")
            time.sleep(1)
            st.rerun()
