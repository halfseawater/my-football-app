import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# ==========================================
# 🎨 视觉引擎：【矩阵流 + 动态蛛网】开机动画
# ==========================================
def run_opening_animation():
    if 'animation_played' not in st.session_state:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
            
            .opening-container {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: #0a0a0a;
                display: flex; justify-content: center; align-items: center;
                z-index: 99999;
                overflow: hidden;
            }

            /* 背景动态蛛网画布 */
            #spider-canvas {
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100%;
                opacity: 0.4;
            }

            .main-title {
                position: relative;
                font-family: 'Orbitron', sans-serif;
                font-size: 72px;
                color: #00ff41;
                text-transform: uppercase;
                letter-spacing: 12px;
                z-index: 100;
                animation: gather 2.5s ease-out forwards;
                text-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
            }

            /* 碎块聚拢动画 */
            @keyframes gather {
                0% { opacity: 0; transform: scale(1.5); filter: blur(10px); letter-spacing: 40px; }
                20% { opacity: 0.5; filter: blur(5px); }
                100% { opacity: 1; transform: scale(1); filter: blur(0); letter-spacing: 12px; }
            }

            /* 扫描线效果 */
            .scanline {
                width: 100%;
                height: 2px;
                background: rgba(0, 255, 65, 0.1);
                position: absolute;
                top: 0;
                z-index: 101;
                animation: scan 3s linear infinite;
            }
            @keyframes scan {
                0% { top: 0; }
                100% { top: 100%; }
            }
            </style>
            
            <div class="opening-container" id="opening">
                <canvas id="spider-canvas"></canvas>
                <div class="scanline"></div>
                <div class="main-title">蛛网方盒</div>
            </div>
            
            <script>
            // 动态蛛网逻辑
            const canvas = document.getElementById('spider-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            let particles = [];
            const count = 80;

            class Particle {
                constructor() {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.vx = (Math.random() - 0.5) * 1.5;
                    this.vy = (Math.random() - 0.5) * 1.5;
                }
                update() {
                    this.x += this.vx;
                    this.y += this.vy;
                    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
                }
            }

            for (let i = 0; i < count; i++) particles.push(new Particle());

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.strokeStyle = '#00ff41';
                ctx.lineWidth = 0.5;

                for (let i = 0; i < particles.length; i++) {
                    particles[i].update();
                    for (let j = i + 1; j < particles.length; j++) {
                        const dist = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
                        if (dist < 150) {
                            ctx.beginPath();
                            ctx.moveTo(particles[i].x, particles[i].y);
                            ctx.lineTo(particles[j].x, particles[j].y);
                            ctx.globalAlpha = 1 - dist / 150;
                            ctx.stroke();
                        }
                    }
                }
                requestAnimationFrame(animate);
            }
            animate();

            // 3秒后移除动画
            setTimeout(() => {
                document.getElementById('opening').style.opacity = '0';
                setTimeout(() => { document.getElementById('opening').style.display = 'none'; }, 500);
            }, 3000);
            </script>
        """, unsafe_allow_html=True)
        time.sleep(3.5)
        st.session_state.animation_played = True
        st.rerun()

# --- 动画启动 ---
run_opening_animation()

# ==========================================
# 🔐 零级协议：多用户隔离数据库 (保持功能)
# ==========================================
st.set_page_config(page_title="蛛网方盒", layout="wide", page_icon="🕸️")

if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "养虎人": {
            "pwd": "888888", "balance": 10000.0, "orders": [], 
            "stats": {"total_bets": 0, "won_bets": 0, "total_staked": 0.0, "total_returned": 0.0}
        }
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 登录界面配色升级 ---
if not st.session_state.logged_in:
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 10px 20px; color: #00ff41; }
        .stButton>button { background-color: #00ff41; color: black; border: none; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: Orbitron, sans-serif; color: #00ff41;'>🕸️ WEB-BOX // 矩阵接入</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.divider()
        tab_login, tab_reg = st.tabs(["🔐 密钥接入", "🆔 申请特工权限"])
        with tab_login:
            login_user = st.text_input("特工代号", key="login_user")
            login_pwd = st.text_input("安全密钥", type="password", key="login_pwd")
            if st.button("⚡ 执行接入程序", use_container_width=True):
                if login_user in st.session_state.user_db and st.session_state.user_db[login_user]["pwd"] == login_pwd:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.rerun() 
                else:
                    st.error("🚨 身份校验失败！")
        with tab_reg:
            reg_user = st.text_input("设定代号", key="reg_user")
            reg_pwd = st.text_input("设定密钥", type="password", key="reg_pwd")
            if st.button("📝 写入底层协议", use_container_width=True):
                if reg_user in st.session_state.user_db:
                    st.warning("🚨 代号已被占用！")
                elif reg_user and reg_pwd:
                    st.session_state.user_db[reg_user] = {
                        "pwd": reg_pwd, "balance": 1000.0, "orders": [],
                        "stats": {"total_bets": 0, "won_bets": 0, "total_staked": 0.0, "total_returned": 0.0}
                    }
                    st.success("✅ 注册成功！")
    st.stop() 

# ---------------------------------------------------------
# 后续数据逻辑（fetch_full_odds, smart_translate 等）保持之前代码一致即可
# ---------------------------------------------------------
user_data = st.session_state.user_db[st.session_state.current_user]

@st.cache_data(ttl=86400)
def smart_translate(text):
    if not text: return ""
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except: return text

@st.cache_data(ttl=3600)
def fetch_full_odds(date):
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    try:
        res_fix = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"date": date})
        t_map = {i["fixture"]["id"]: {"h": smart_translate(i["teams"]["home"]["name"]), "a": smart_translate(i["teams"]["away"]["name"])} 
                 for i in res_fix.json().get("response", [])}
        res_odds = requests.get("https://v3.football.api-sports.io/odds", headers=headers, params={"date": date, "bookmaker": "8", "page": "1"})
        
        m_list = []
        for i in res_odds.json().get("response", []):
            fid = i["fixture"]["id"]
            if fid not in t_map: continue
            bets = i["bookmakers"][0]["bets"]
            m_list.append({
                "id": fid, "联赛": smart_translate(i["league"]["name"]),
                "时间": datetime.fromisoformat(i["fixture"]["date"]).strftime("%H:%M"),
                "主队": t_map[fid]["h"], "客队": t_map[fid]["a"],
                "1x2": next((m["values"] for m in bets if m["id"] == 1), []),
                "goals": next((m["values"] for m in bets if m["id"] == 5), []),
                "score": next((m["values"] for m in bets if m["id"] == 10), [])
            })
        return m_list
    except: return []

# --- 侧边栏与主界面（配色同步） ---
with st.sidebar:
    st.markdown(f"### 🕵️ 特工 {st.session_state.current_user}")
    st.metric("💼 算力余额", f"{user_data['balance']:.2f}", delta_color="normal")
    if st.button("🚪 销毁会话", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.animation_played = False
        st.rerun()

st.title("📡 实时信号源")
data = fetch_full_odds(datetime.now().strftime("%Y-%m-%d"))
if data:
    for idx, m in enumerate(data[:20]):
        with st.expander(f"[{m['联赛']}] {m['主队']} vs {m['客队']} ({m['时间']})"):
            # 此处省略具体按钮逻辑，参考之前完整版即可
            st.write("点击赔率进入推演池...")