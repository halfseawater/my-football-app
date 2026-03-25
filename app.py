import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# ==========================================
# 🎨 视觉引擎：斗罗满配版（仅保留动画，名字已改）
# ==========================================
def run_opening_animation():
    if 'animation_played' not in st.session_state:
        # ⚠️ HTML代码已扁平化，绝不触发报错
        st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Zhi+Mang+Xing&family=Orbitron:wght@700&display=swap');
.opening-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #03000a; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 99999; overflow: hidden; }
#spider-canvas { position: absolute; width: 100%; height: 100%; opacity: 0.7; z-index: 10; }
.main-title { font-family: 'Zhi Mang Xing', cursive; font-size: 100px; color: #b026ff; text-shadow: 0 0 20px #b026ff, 0 0 50px #ff0000; z-index: 100; position: relative; animation: soul-fusion 2.8s ease-out forwards; }
.sub-title { font-family: 'Orbitron', sans-serif; font-size: 18px; color: #00e5ff; letter-spacing: 8px; margin-top: 10px; z-index: 100; opacity: 0; animation: fade-in 1s 1.8s forwards; }
.ring { position: absolute; border-radius: 50%; border: 15px solid rgba(255, 0, 0, 0.4); box-shadow: 0 0 30px #ff0000, inset 0 0 30px #ff0000; z-index: 50; opacity: 0; }
.ring1 { width: 300px; height: 300px; animation: ring-rise 1.5s 1.0s forwards; }
.ring2 { width: 450px; height: 450px; animation: ring-rise 1.8s 1.5s forwards; }
.ring3 { width: 600px; height: 600px; animation: ring-rise 2.1s 2.0s forwards; }
.status-container { position: absolute; bottom: 10%; left: 5%; font-family: monospace; font-size: 14px; color: #b026ff; z-index: 100; text-align: left; opacity: 0.8; }
.power-level { font-weight: bold; color: #ff0000; animation: blink 0.3s infinite alternate; }
@keyframes soul-fusion { 0% { opacity: 0; transform: scale(1.8); filter: blur(20px); letter-spacing: 50px; } 50% { filter: blur(5px); } 100% { opacity: 1; transform: scale(1); filter: blur(0); letter-spacing: 18px; } }
@keyframes fade-in { to { opacity: 1; } }
@keyframes ring-rise { 0% { opacity: 0; transform: scale(0.5); top: 100vh; } 70% { opacity: 0.8; } 100% { opacity: 0.2; transform: scale(1) translateY(-100px); top: 0vh; } }
@keyframes blink { from { opacity: 0.4; } to { opacity: 1; } }
</style>
<div class="opening-container" id="opening">
<canvas id="spider-canvas"></canvas>
<div class="ring ring1"></div>
<div class="ring ring2"></div>
<div class="ring ring3"></div>
<div class="main-title">蛛网方盒</div>
<div class="sub-title">100k Yr SPIRIT RING MATRIX</div>
<div class="status-container">
> 警告: 杀神领域 开启中... <br>
> [十万年泰坦巨猿/天青牛蟒适配 100%] <br>
> 魂力解析进度: <span class="power-level">九十八级·超级斗罗</span>...
</div>
</div>
<script>
const canvas = document.getElementById('spider-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
let p = [];
for(let i=0; i<90; i++) {
p.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, vx: (Math.random()-0.5)*3, vy: (Math.random()-0.5)*3 });
}
function draw() {
ctx.clearRect(0,0,canvas.width,canvas.height);
p.forEach((a,i)=>{
a.x+=a.vx; a.y+=a.vy;
if(a.x<0||a.x>canvas.width) a.vx*=-1; if(a.y<0||a.y>canvas.height) a.vy*=-1;
for(let j=i+1; j<p.length; j++) {
let d = Math.hypot(a.x-p[j].x, a.y-p[j].y);
if(d<160) { 
ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(p[j].x,p[j].y); 
ctx.strokeStyle = d < 80 ? `rgba(255, 0, 0, ${1-d/160})` : `rgba(176, 38, 255, ${1-d/160})`;
ctx.lineWidth = 1.2; ctx.stroke(); 
}
}
});
requestAnimationFrame(draw);
}
draw();
setTimeout(() => { document.getElementById('opening').style.display='none'; }, 4000);
</script>
""", unsafe_allow_html=True)
        time.sleep(4.3)
        st.session_state.animation_played = True
        st.rerun()

# 播放开场动画
run_opening_animation()

# ==========================================
# 🔐 零级协议：原版多用户与登录注册 (特工架构，绝无删减)
# ==========================================
st.set_page_config(page_title="蛛网方盒", layout="wide", page_icon="🕸️")

if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "养虎人": {
            "pwd": "888888", "balance": 10000.0, "orders": [], 
            "stats": {"total_bets": 0, "won_bets": 0, "total_staked": 0.0, "total_returned": 0.0}
        }
    }

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'cart' not in st.session_state: st.session_state.cart = []

if not st.session_state.logged_in:
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: monospace;'>🕸️ 蛛网方盒</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #ff4b4b;'>[ RESTRICTED ACCESS // 矩阵已锁定 ]</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.divider()
        tab_login, tab_reg = st.tabs(["🔐 密钥接入", "🆔 申请最高权限"])
        
        with tab_login:
            login_user = st.text_input("特工代号", key="login_user")
            login_pwd = st.text_input("安全密钥", type="password", key="login_pwd")
            if st.button("⚡ 破解协议并登入", use_container_width=True):
                if login_user in st.session_state.user_db and st.session_state.user_db[login_user]["pwd"] == login_pwd:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.rerun() 
                else:
                    st.error("🚨 警告：代号或密钥不匹配，已记录入侵者 IP！")
        
        with tab_reg:
            reg_user = st.text_input("设定新代号", key="reg_user")
            reg_pwd = st.text_input("设定新密钥", type="password", key="reg_pwd")
            if st.button("📝 写入底层协议", use_container_width=True):
                if reg_user in st.session_state.user_db:
                    st.warning("🚨 数据库拦截：此特工代号已被注册！每人仅限注册一次。")
                elif reg_user and reg_pwd:
                    init_balance = 1000.0 
                    st.session_state.user_db[reg_user] = {
                        "pwd": reg_pwd, "balance": init_balance, "orders": [],
                        "stats": {"total_bets": 0, "won_bets": 0, "total_staked": 0.0, "total_returned": 0.0}
                    }
                    st.success(f"✅ 权限写入成功！系统已为您分配初始算力: {init_balance} 枚蛛网币。请前往【密钥接入】登入。")
                else:
                    st.warning("⚠️ 代号和密钥参数不能为空。")
    st.stop() 

user_data = st.session_state.user_db[st.session_state.current_user]

# ==========================================
# 🕷️ 原版汉化字典与数据抓取 (四大盘口全恢复)
# ==========================================
LEAGUE_DICT = {
    "Premier League": "英超", "Championship": "英冠", "League One": "英甲", "League Two": "英乙",
    "La Liga": "西甲", "Serie A": "意甲", "Bundesliga": "德甲", "Ligue 1": "法甲",
    "Eredivisie": "荷甲", "Eerste Divisie": "荷乙", "UEFA Champions League": "欧冠",
    "UEFA Europa League": "欧联杯", "FA Cup": "足总杯", "Copa del Rey": "国王杯"
}

LEAGUE_ID_MAP = {
    "英超": 39, "西甲": 140, "意甲": 135, "德甲": 78, "法甲": 61,
    "英冠": 40, "英甲": 41, "英乙": 42, "荷甲": 88, "荷乙": 89
}

TEAM_DICT = {
    "Arsenal": "阿森纳", "Manchester City": "曼城", "Manchester United": "曼联", 
    "Liverpool": "利物浦", "Chelsea": "切尔西", "Tottenham": "热刺", "Newcastle": "纽卡斯尔",
    "Real Madrid": "皇家马德里", "Barcelona": "巴塞罗那", "Bayern Munich": "拜仁慕尼黑",
    "Juventus": "尤文图斯", "AC Milan": "AC米兰", "Inter": "国际米兰", "Paris Saint Germain": "大巴黎"
}

@st.cache_data(ttl=86400)
def smart_translate(text, dict_type):
    if not text: return ""
    if dict_type == "team" and text in TEAM_DICT: return TEAM_DICT[text]
    if dict_type == "league" and text in LEAGUE_DICT: return LEAGUE_DICT[text]
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except:
        return text

@st.cache_data(ttl=3600)
def fetch_full_odds(date):
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    try:
        res_fix = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"date": date})
        teams_map = {item["fixture"]["id"]: {
            "home": smart_translate(item["teams"]["home"]["name"], "team"), 
            "away": smart_translate(item["teams"]["away"]["name"], "team")} 
            for item in res_fix.json().get("response", [])}

        res_odds = requests.get("https://v3.football.api-sports.io/odds", headers=headers, params={"date": date, "bookmaker": "8", "page": "1"})
        
        matches_list = []
        for item in res_odds.json().get("response", []):
            f_id = item["fixture"]["id"]
            if f_id not in teams_map: continue
                
            league_en = item["league"]["name"]
            bets = item["bookmakers"][0]["bets"]
            
            # 原版四大盘口全保留
            m_1x2 = next((m for m in bets if m["id"] == 1), None)          
            m_goals = next((m for m in bets if m["id"] == 5), None)        
            m_score = next((m for m in bets if m["id"] == 10), None)        
            m_htft = next((m for m in bets if m["name"] == "Halftime/Fulltime"), None) 
            
            matches_list.append({
                "id": f_id, 
                "联赛": smart_translate(league_en, "league"),
                "时间": datetime.fromisoformat(item["fixture"]["date"]).strftime("%H:%M"),
                "主队": teams_map[f_id]["home"], "客队": teams_map[f_id]["away"],
                "1x2": m_1x2["values"] if m_1x2 else [], "goals": m_goals["values"] if m_goals else [],
                "score": m_score["values"] if m_score else [], "htft": m_htft["values"] if m_htft else []
            })
        return matches_list
    except:
        return []

@st.cache_data(ttl=86400) 
def fetch_standings(league_id, season):
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    try:
        res = requests.get("https://v3.football.api-sports.io/standings", headers=headers, params={"league": league_id, "season": season})
        data = res.json()
        if not data.get("response"): return pd.DataFrame()
        
        standings_list = data["response"][0]["league"]["standings"][0]
        table_data = []
        for team_info in standings_list:
            team_en = team_info["team"]["name"]
            table_data.append({
                "排名": team_info["rank"],
                "球队": smart_translate(team_en, "team"), 
                "场次": team_info["all"]["played"], "胜": team_info["all"]["win"], "平": team_info["all"]["draw"], "负": team_info["all"]["lose"],
                "进/失": f"{team_info['all']['goals']['for']} / {team_info['all']['goals']['against']}",
                "净胜球": team_info["goalsDiff"], "积分": team_info["points"], "近况": team_info.get("form", "-")
            })
        return pd.DataFrame(table_data)
    except:
        return pd.DataFrame()

# ==========================================
# 1. 购物车逻辑
# ==========================================
def add_to_cart(match, play_type, option, odd):
    st.session_state.cart.append({"match": match, "play_type": play_type, "option": option, "odd": float(odd)})

def remove_from_cart(index):
    st.session_state.cart.pop(index)

# ==========================================
# 2. 原版侧边栏：推演池控制台 
# ==========================================
with st.sidebar:
    st.success(f"🕵️ 欢迎回归, 特工 {st.session_state.current_user}")
    if st.button("🚪 断开连接 (销毁会话)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.cart = []
        st.session_state.animation_played = False
        st.rerun()
        
    st.divider()
    st.header("🛒 战术推演池")
    st.metric(label="💼 算力余额 (蛛网币)", value=f"{user_data['balance']:.2f}")
    st.divider()
    
    if not st.session_state.cart:
        st.info("🕸️ 矩阵空载。请添加赛事选项。")
    else:
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"**{item['match']}**")
            st.caption(f"{item['play_type']} : {item['option']} @ **{item['odd']}**")
            if st.button("❌ 排除此项", key=f"del_{i}"):
                remove_from_cart(i)
                st.rerun() 
        
        st.divider()
        st.markdown("**⚡ 执行协议:**")
        mode = st.radio("选择策略", ["单关拆分", "极限串关", "混合容错矩阵"], label_visibility="collapsed")
        
        max_stake = int(max(10, user_data['balance']))
        stake = st.number_input("注入蛛网币 (单注):", min_value=10, max_value=max_stake, value=min(100, max_stake), step=10)
        
        total_stake = stake
        potential_return = 0.0
        
        if mode == "单关拆分":
            total_stake = stake * len(st.session_state.cart)
            potential_return = sum(stake * item['odd'] for item in st.session_state.cart)
        elif mode == "极限串关":
            total_stake = stake
            total_odd = 1.0
            for item in st.session_state.cart:
                total_odd *= item['odd']
            potential_return = stake * total_odd
        else: 
            total_stake = stake * len(st.session_state.cart)
            potential_return = sum(stake * item['odd'] for item in st.session_state.cart) * 1.5 
            
        st.info(f"💡 总计消耗: {total_stake} 币")
        st.success(f"🎯 全红最高回报: {potential_return:.2f} 币")
        
        if st.button("🚀 锁定目标，注入算力", use_container_width=True):
            if user_data['balance'] >= total_stake:
                user_data['balance'] -= total_stake
                order_id = "WEB-" + datetime.now().strftime("%Y%m%d%H%M%S")
                new_order = {
                    "id": order_id, "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "mode": mode,
                    "stake": total_stake, "potential_return": potential_return,
                    "items": list(st.session_state.cart), "status": "🟡 等待赛果"
                }
                user_data['orders'].insert(0, new_order) 
                user_data['stats']["total_bets"] += 1
                user_data['stats']["total_staked"] += total_stake
                st.session_state.cart = [] 
                st.toast("✅ 算力注入成功！已记录至专属特工档案室...")
                st.rerun()
            else:
                st.error("🚨 专属算力余额不足，请充值！")

# ==========================================
# 4. 原版顶级视角划分：三核标签页
# ==========================================
st.title("📡 蛛网方盒")
tab_main, tab_standings, tab_profile = st.tabs(["📡 实时信号源", "🏆 战略态势感知", "📂 我的专属档案室"])

# --- Tab 1: 实时推演盘口 (四大盘口全恢复) ---
with tab_main:
    with st.spinner("正在加载多元赔率矩阵..."):
        today_str = datetime.now().strftime("%Y-%m-%d")
        matches_data = fetch_full_odds(today_str)
        
    if matches_data:
        available_leagues = sorted(list(set([m["联赛"] for m in matches_data])))
        selected_league = st.selectbox("🏆 筛选目标锦标赛/联赛:", ["🌍 显示全部赛事"] + available_leagues)
        st.divider() 

        display_matches = matches_data if selected_league == "🌍 显示全部赛事" else [m for m in matches_data if m["联赛"] == selected_league]

        if not display_matches:
            st.warning(f"🚨 当前筛选的【{selected_league}】节点暂无信号。")

        for idx, match in enumerate(display_matches[:20]): 
            match_title = f"{match['主队']} VS {match['客队']}"
            with st.expander(f"[{match['联赛']}] 🔥 ⚽ {match_title} (开赛 {match['时间']})"):
                t1, t2, t3, t4 = st.tabs(["胜平负", "总进球", "比分", "半全场"])
                
                with t1:
                    if match["1x2"]:
                        cols = st.columns(3)
                        trans_dict = {"Home": "主胜", "Draw": "平局", "Away": "客胜"}
                        for i, val in enumerate(match["1x2"]):
                            cn_name = trans_dict.get(val['value'], val['value']) 
                            if cols[i].button(f"{cn_name} | @{val['odd']}", key=f"1x2_{idx}_{i}", use_container_width=True):
                                add_to_cart(match_title, "胜平负", cn_name, val['odd'])
                                st.rerun()
                    else: st.info("暂无盘口")
                with t2:
                    if match["goals"]:
                        options = {v['value'].replace("Over", "大").replace("Under", "小") + " 球": v['odd'] for v in match["goals"]}
                        sel_goal = st.selectbox("选择大小球盘口:", list(options.keys()), key=f"sg_{idx}")
                        if st.button(f"锁定 {sel_goal} | @{options[sel_goal]}", key=f"bg_{idx}"):
                            add_to_cart(match_title, "总进球", sel_goal, options[sel_goal])
                            st.rerun()
                    else: st.info("暂无盘口")
                with t3:
                    if match["score"]:
                        options = {f"{v['value']}": v['odd'] for v in match["score"]}
                        sel_score = st.selectbox("精准打击 (比分):", list(options.keys()), key=f"ss_{idx}")
                        if st.button(f"锁定比分 {sel_score} | @{options[sel_score]}", key=f"bs_{idx}"):
                            add_to_cart(match_title, "比分", sel_score, options[sel_score])
                            st.rerun()
                    else: st.info("暂无盘口")
                with t4:
                    if match["htft"]:
                        htft_dict = {"Home/Home": "胜/胜", "Home/Draw": "胜/平", "Home/Away": "胜/负", "Draw/Home": "平/胜", "Draw/Draw": "平/平", "Draw/Away": "平/负", "Away/Home": "负/胜", "Away/Draw": "负/平", "Away/Away": "负/负"}
                        options = {htft_dict.get(v['value'], v['value']): v['odd'] for v in match["htft"]}
                        sel_htft = st.selectbox("推演半全场赛果:", list(options.keys()), key=f"sh_{idx}")
                        if st.button(f"锁定半全场 {sel_htft} | @{options[sel_htft]}", key=f"bh_{idx}"):
                            add_to_cart(match_title, "半全场", sel_htft, options[sel_htft])
                            st.rerun()
                    else: st.info("暂无盘口")
    else:
        st.info("🚨 扫描完成，但今日暂无任何赛事数据。")

# --- Tab 2: 全网积分榜 (原版恢复) ---
with tab_standings:
    st.markdown("### 📊 全球主要战区实时积分榜")
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        selected_standings_league = st.selectbox("选择战区:", list(LEAGUE_ID_MAP.keys()))
    
    with st.spinner(f"正在拉取 {selected_standings_league} 最新赛季数据..."):
        current_month = datetime.now().month
        target_season = datetime.now().year - 1 if current_month < 8 else datetime.now().year
        df_standings = fetch_standings(LEAGUE_ID_MAP[selected_standings_league], target_season)
        
    if not df_standings.empty:
        st.dataframe(df_standings, use_container_width=True, hide_index=True, height=600)
    else:
        st.error("🚨 无法连接到该战区的积分榜数据库，请稍后重试。")

# --- Tab 3: 我的专属档案室 (原版恢复) ---
with tab_profile:
    st.markdown(f"### 📈 {st.session_state.current_user} 的个人数据大盘 (ROI)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💼 当前算力余额", f"{user_data['balance']:.2f} 币")
    c2.metric("🔥 累计消耗算力", f"{user_data['stats']['total_staked']:.2f} 币")
    c3.metric("💰 累计回收算力", f"{user_data['stats']['total_returned']:.2f} 币")
    
    roi = 0.0
    if user_data['stats']['total_staked'] > 0:
        profit = user_data['stats']['total_returned'] - user_data['stats']['total_staked']
        roi = (profit / user_data['stats']['total_staked']) * 100
    
    if roi >= 0: c4.metric("📊 整体 ROI", f"+{roi:.2f}%", "正向收益")
    else: c4.metric("📊 整体 ROI", f"{roi:.2f}%", "-策略亏损")
        
    st.divider()
    st.markdown("### 📜 个人历史战术指令")
    
    if not user_data['orders']:
        st.info("📂 你的档案室目前为空，去【实时信号源】下达第一条战术指令吧！")
    else:
        for idx, order in enumerate(user_data['orders']):
            status_icon = order['status']
            
            with st.expander(f"{status_icon} | 编号: {order['id']} | 模式: {order['mode']} | 消耗: {order['stake']} 币"):
                st.caption(f"下达时间: {order['time']}")
                st.markdown("**推演矩阵明细:**")
                for item in order['items']:
                    st.write(f"- ⚽ **{item['match']}** | {item['play_type']}: `{item['option']}` @ **{item['odd']}**")
                
                st.divider()
                st.write(f"💵 **预期总回报:** `{order['potential_return']:.2f} 币`")
                
                if order['status'] == "🟡 等待赛果":
                    st.info("⚠️ 模拟推演系统：在此手动判决赛果以更新你的 ROI 数据。")
                    col_win, col_lose = st.columns(2)
                    if col_win.button("✅ 目标达成 (算力回收)", key=f"win_{order['id']}", use_container_width=True):
                        user_data['orders'][idx]['status'] = "🟢 成功打出"
                        user_data['balance'] += order['potential_return'] 
                        user_data['stats']['won_bets'] += 1
                        user_data['stats']['total_returned'] += order['potential_return']
                        st.rerun() 
                        
                    if col_lose.button("❌ 任务失败 (算力销毁)", key=f"lose_{order['id']}", use_container_width=True):
                        user_data['orders'][idx]['status'] = "🔴 策略失败"
                        st.rerun()