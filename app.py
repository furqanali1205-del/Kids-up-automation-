import streamlit as st
import time
import requests

# Light/White Clean Shogo.ai Style Page Setup
st.set_page_config(page_title="YouTube Automation Studio", page_icon="🎬", layout="centered")

# Custom CSS styling for exact white UI match, tabs, and nice layout
st.markdown("""
    <style>
    /* Clean white background and slate fonts */
    .main { background-color: #f8f9fa; color: #1e293b; }
    h1, h2, h3, p { color: #1e293b !important; }
    
    /* Clean white input fields */
    div[data-baseweb="input"] { background-color: white !important; border-radius: 8px !important; }
    
    /* Purple Accent Buttons matching your screenshot */
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
    
    /* Brand Header Box */
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
    
    /* Analytics Cards Grid */
    .stat-card {
        background-color: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .stat-num { font-size: 28px; font-weight: 800; margin-bottom: 2px; }
    
    /* Pipeline Step Box */
    .pipe-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
    .pipe-icon { font-size: 24px; margin-bottom: 8px; }
    .pipe-num { font-size: 22px; font-weight: 700; color: #0f172a; }
    .pipe-label { font-size: 13px; color: #64748b; }
    
    /* Blue Connection Box */
    .connection-box {
        background-color: white;
        border: 2px solid #3b82f6;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TOP BRAND HEADER BAR ---
st.markdown("""
    <div class="shogo-header">
        <div style="background-color: #ef4444; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
            <span style="color: white; font-size: 22px; font-weight: bold;">▶</span>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: #8b5cf6 !important;">YouTube Automation Studio</h2>
            <p style="margin: 0; font-size: 12px; color: #64748b;">Kids Entertainment Content Factory</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab_dashboard, tab_research, tab_scripts, tab_voice, tab_videos, tab_schedule, tab_channel = st.tabs([
    "📊 Dashboard", "🔍 Research", "📄 Scripts", "🎙️ Voiceovers", "🎬 Videos", "📅 Scheduled", "⚙️ Add Channel"
])

# ==================== TAB 1: DASHBOARD ====================
with tab_dashboard:
    
    # --- AUTOPILOT SETTINGS ---
    st.markdown("""
        <div style="background-color: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span style="font-weight: bold; font-size: 18px; color: #6d28d9;">🤖 YouTube AutoPilot</span>
                <span style="background-color: #bbf7d0; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">● Active</span>
            </div>
    """, unsafe_allow_html=True)
    
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        # Option for more than 3 shorts
        daily_shorts = st.selectbox("📱 Daily Shorts", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], index=2) # Default is 3
        target_country = st.selectbox("🌍 Target Country", ["US", "UK", "CA", "PK"], index=0)
    with col_ap2:
        # Option for more than 2 long videos
        daily_long = st.selectbox("🎬 Daily Long Videos", [1, 2, 3, 4, 5], index=1) # Default is 2
        autopilot_toggle = st.toggle("AutoPilot Active State", value=True, label_visibility="collapsed")
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- PIPELINE ENGINE TRIGGER ---
    if st.button("▶ Run Full Pipeline Now"):
        with st.status("Initializing Auto-Automation Engines...", expanded=True) as status:
            st.write("🔍 Running Trend Research for Kids Niche...")
            time.sleep(1.5)
            
            st.write("📝 Writing Funny & Engaging Nursery Rhyme Script (Gemini AI)...")
            # In the future, real API call will execute here
            time.sleep(1.5)
            
            st.write("🎙️ Adding character dialogues & background funny sound effects...")
            time.sleep(1.5)
            
            st.write("🎨 Generating 100% Free, Watermark-Free high quality frames...")
            # We fetch free assets or generate clean vectors here
            time.sleep(2)
            
            st.write("🚀 Running SEO Engine (Auto-generating High CTR Title, Tags & Description)...")
            time.sleep(1)
            
            st.write("📤 Uploading & Scheduling directly to your connected YouTube Channel...")
            time.sleep(1.5)
            
            status.update(label="Full Pipeline Executed & Scheduled Successfully!", state="complete")
        st.success("🎉 Process Completed! Video is now queued and ready without watermarks.")

    st.write("---")
    
    # --- METRICS GRAPHICS ---
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown('<div class="stat-card" style="border-left: 5px solid #ef4444;"><div class="stat-num" style="color: #ef4444;">4</div><p style="color: #64748b; margin: 0; font-size: 14px;">Total Videos</p></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="stat-card" style="border-left: 5px solid #10b981;"><div class="stat-num" style="color: #10b981;">6</div><p style="color: #64748b; margin: 0; font-size: 14px;">Trending Topics</p></div>', unsafe_allow_html=True)
    with col_stat2:
        st.markdown('<div class="stat-card" style="border-left: 5px solid #3b82f6;"><div class="stat-num" style="color: #3b82f6;">6.3M</div><p style="color: #64748b; margin: 0; font-size: 14px;">Total Views</p></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="stat-card" style="border-left: 5px solid #8b5cf6;"><div class="stat-num" style="color: #8b5cf6;">1/4</div><p style="color: #64748b; margin: 0; font-size: 14px;">Uploaded</p></div>', unsafe_allow_html=True)

    st.write("---")
    
    # --- PIPELINE STEPS STATUS GRID ---
    st.subheader("⚡ Automation Pipeline Steps")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown('<div class="pipe-card"><div class="pipe-icon">🔍</div><div class="pipe-num">6</div><div class="pipe-label">Research</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="pipe-card"><div class="pipe-icon">🎤</div><div class="pipe-num">4</div><div class="pipe-label">Voiceovers</div></div>', unsafe_allow_html=True)
    with col_p2:
        st.markdown('<div class="pipe-card"><div class="pipe-icon">📝</div><div class="pipe-num">4</div><div class="pipe-label">Scripts</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="pipe-card"><div class="pipe-icon">🎬</div><div class="pipe-num">4</div><div class="pipe-label">Videos</div></div>', unsafe_allow_html=True)

# ==================== ADDITIONAL DETAILED TABS ====================
with tab_research:
    st.subheader("🔍 Active Trend Monitor")
    st.info("Current Hot Topic: 'Lullaby Collection' - Growing by +9.7%")
    
with tab_scripts:
    st.subheader("📝 Live Script & SEO tags generator")
    st.text_input("Current Generated Title:", "Five Little Monkeys Jumping On The Bed (Engaging & Funny Remake)")
    st.text_area("Screenplay Dialogues", "Monkey 1: 'Oops! I fell down!'\nMama: 'No more monkeys jumping on the bed!'")
    st.text_area("Keywords / Tags", "kids songs, nursery rhymes, funny monkey song, coco melon style, baby cartoons")

with tab_voice:
    st.subheader("🎙️ Dialect & Audio Settings")
    st.selectbox("Narrator Voice Profile", ["Cute Baby (Funny)", "Friendly Uncle", "Anime Character"])
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

with tab_videos:
    st.subheader("🎬 Video Render Status (Watermark Free)")
    st.write("✅ Video 1: ABC Song Remix (Render Completed)")
    st.write("⏳ Video 2: Colors Adventure (Compiling Scenes...)")

with tab_schedule:
    st.subheader("📅 Auto Upload Log")
    st.success("Ready for Auto-Upload: Kids Fun TV - Upload Schedule: Today, 3:00 PM")

# ==================== TAB 7: ADD CHANNEL (Exact UI Matching Screenshot) ====================
with tab_channel:
    st.markdown("""
        <div class="connection-box">
            <h3 style="color: #2563eb !important; margin-top:0;">➕ Naya Channel Add Karo</h3>
    """, unsafe_allow_html=True)
    
    channel_name_input = st.text_input("Channel Name *", value="Kids Up")
    channel_id_input = st.text_input("YouTube Channel ID (Optional)", placeholder="e.g., UCxxxxxxxxxxxxxxxxxxxx")
    st.caption("YouTube → About → Share → Copy Channel ID. Ye optional hai, baad mein daal sakte ho.")
    
    api_key_input = st.text_input("🔑 YouTube Data API v3 Key *", type="password", placeholder="AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    st.warning("⚠️ Google Cloud Console se API key. Ye key server pe safely store hogi.")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Channel Save Karo"):
            st.success(f"Channel '{channel_name_input}' Successfully Saved!")
    with col_btn2:
        st.button("Cancel")
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # API Setup Guide
    st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;">
            <h4 style="margin-top:0; color: #0f172a;">⚙️ YouTube API Setup Guide</h4>
            <p style="font-size: 14px; color: #475569;"><b>1️⃣ Google Cloud Console:</b> console.cloud.google.com pe jao. Naya project banao ya existing mein YouTube Data API v3 enable karo.</p>
        </div>
    """, unsafe_allow_html=True)
