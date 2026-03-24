import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 页面基本设置 (名称已升级为 蛛网方盒)
# ==========================================
st.set_page_config(page_title="蛛网方盒 - 核心枢纽", layout="wide")

# ==========================================
# 🔐 零级协议：身份验证系统 (拦截闸门)
# ==========================================
# 初始化用户数据库 (临时存在浏览器缓存中)
if 'users' not in st.session_state:
    st.session_state.users = {"养虎人": "888888"}  # 默认给你留了一个超级管理员后门
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# 如果未登录，展示高逼格的拦截界面，并阻止后续代码运行
if not st.session_state.logged_in:
    # 模拟终端居中排版
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: monospace;'>🕸️ 蛛网方盒 (WEB-BOX)</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #ff4b4b;'>[ RESTRICTED ACCESS // 矩阵枢纽已锁定 ]</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.divider()
        tab_login, tab_reg = st.tabs(["🔐 密钥接入", "🆔 申请最高权限"])
        
        with tab_login:
            login_user = st.text_input("特工代号", key="login_user")
            login_pwd = st.text_input("安全密钥", type="password", key="login_pwd")
            if st.button("⚡ 破解协议并登入", use_container_width=True):
                if login_user in st.session_state.users and st.session_state.users[login_user] == login_pwd:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.rerun() # 瞬间刷新，进入主界面
                else:
                    st.error("🚨 警告：代号或密钥不匹配，已记录入侵者 IP！")
        
        with tab_reg:
            reg_user = st.text_input("设定新代号", key="reg_user")
            reg_pwd = st.text_input("设定新密钥", type="password", key="reg_pwd")
            if st.button("📝 写入底层协议", use_container_width=True):
                if reg_user in st.session_state.users:
                    st.warning("🚨 数据库提示：此代号已被其他特工占用！")
                elif reg_user and reg_pwd:
                    st.session_state.users[reg_user] = reg_pwd
                    st.success("✅ 权限写入成功！请切换至【密钥接入】进行首次登入。")
                else:
                    st.warning("⚠️ 代号和密钥参数不能为空。")
    # st.stop() 是一堵叹息之墙，未登录前，下面的所有代码都不会被执行
    st.stop() 

# ==========================================
# 🕷️ 蛛网汉化引擎字典
# ==========================================
LEAGUE_DICT = {
    "Premier League": "英超", "Championship": "英冠", "League One": "英甲", "League Two": "英乙",
    "La Liga": "西甲", "Serie A": "意甲", "Bundesliga": "德甲", "Ligue 1": "法甲",
    "Eredivisie": "荷甲", "Eerste Divisie": "荷乙", "UEFA Champions League": "欧冠",
    "FA Cup": "足总杯", "EFL Cup": "英联杯", "World Cup": "世界杯", "Euro Championship": "欧洲杯"
}

TEAM_DICT = {
    "Arsenal": "阿森纳", "Manchester City": "曼城", "Manchester United": "曼联", 
    "Liverpool": "利物浦", "Chelsea": "切尔西", "Tottenham": "热刺",
    "Real Madrid": "皇家马德里", "Barcelona": "巴塞罗那", "Bayern Munich": "拜仁慕尼黑",
    "Juventus": "尤文图斯", "AC Milan": "AC米兰", "Inter": "国际米兰", "Paris Saint Germain": "大巴黎"
}

# ==========================================
# 1. 蛛网币系统初始化
# ==========================================
if 'balance' not in st.session_state:
    st.session_state.balance = 1000.0  
if 'cart' not in st.session_state:
    st.session_state.cart = []         

def add_to_cart(match, play_type, option, odd):
    st.session_state.cart.append({"match": match, "play_type": play_type, "option": option, "odd": float(odd)})

def remove_from_cart(index):
    st.session_state.cart.pop(index)

# ==========================================
# 2. 左侧边栏：推演池控制台 (增加了断开连接按钮)
# ==========================================
with st.sidebar:
    st.success(f"🕵️ 欢迎回归, 特工 {st.session_state.current_user}")
    # 断开连接按钮
    if st.button("🚪 断开连接 (销毁当前会话)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.cart = [] # 退出时清空购物车
        st.rerun()
        
    st.divider()
    st.header("🛒 战术推演池")
    st.metric(label="💼 算力余额 (蛛网币)", value=f"{st.session_state.balance:.2f}")
    st.divider()
    
    if not st.session_state.cart:
        st.info("🕸️ 矩阵空载。请在右侧提取赛事数据并添加选项。")
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
        stake = st.number_input("注入蛛网币 (单注):", min_value=10, max_value=int(max(10, st.session_state.balance)), value=100, step=10)
        
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
            if st.session_state.balance >= total_stake:
                st.session_state.balance -= total_stake
                st.session_state.cart = [] 
                st.toast("✅ 算力注入成功！指令已发送至数据中心...")
                st.rerun()
            else:
                st.error("🚨 算力余额不足，请充值！")

# ==========================================
# 3. 主界面：底层数据抓取与解析
# ==========================================
st.title("📡 蛛网方盒 - 核心枢纽")
today_str = datetime.now().strftime("%Y-%m-%d")

@st.cache_data(ttl=3600)
def fetch_full_odds(date):
    # ⚠️⚠️⚠️ 填入你的真实 API Key ⚠️⚠️⚠️
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    
    try:
        res_fix = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"date": date})
        teams_map = {}
        for item in res_fix.json().get("response", []):
            f_id = item["fixture"]["id"]
            home_en = item["teams"]["home"]["name"]
            away_en = item["teams"]["away"]["name"]
            teams_map[f_id] = {
                "home": TEAM_DICT.get(home_en, home_en), 
                "away": TEAM_DICT.get(away_en, away_en)
            }

        res_odds = requests.get("https://v3.football.api-sports.io/odds", headers=headers, params={"date": date, "bookmaker": "8", "page": "1"})
        data_odds = res_odds.json()
        
        matches_list = []
        if data_odds.get("response"):
            for item in data_odds["response"]:
                f_id = item["fixture"]["id"]
                if f_id not in teams_map:
                    continue
                    
                league_en = item["league"]["name"]
                league_cn = LEAGUE_DICT.get(league_en, league_en)
                    
                bets = item["bookmakers"][0]["bets"]
                m_1x2 = next((m for m in bets if m["id"] == 1), None)           
                m_goals = next((m for m in bets if m["id"] == 5), None)         
                m_score = next((m for m in bets if m["id"] == 10), None)        
                m_htft = next((m for m in bets if m["name"] == "Halftime/Fulltime"), None) 
                
                matches_list.append({
                    "id": f_id, "联赛": league_cn,
                    "时间": datetime.fromisoformat(item["fixture"]["date"]).strftime("%H:%M"),
                    "主队": teams_map[f_id]["home"], "客队": teams_map[f_id]["away"],
                    "1x2": m_1x2["values"] if m_1x2 else [], "goals": m_goals["values"] if m_goals else [],
                    "score": m_score["values"] if m_score else [], "htft": m_htft["values"] if m_htft else []
                })
        return matches_list
    except Exception as e:
        st.error(f"信号源异常: {e}")
        return []

with st.spinner("正在加载多元赔率矩阵与中文汉化包..."):
    matches_data = fetch_full_odds(today_str)

# ==========================================
# 4. 渲染：智能筛选 + 多标签页界面
# ==========================================
if matches_data:
    available_leagues = sorted(list(set([m["联赛"] for m in matches_data])))
    selected_league = st.selectbox("🏆 筛选目标锦标赛/联赛:", ["🌍 显示全部赛事"] + available_leagues)
    st.divider() 

    if selected_league == "🌍 显示全部赛事":
        display_matches = matches_data
    else:
        display_matches = [m for m in matches_data if m["联赛"] == selected_league]

    if not display_matches:
        st.warning(f"🚨 当前筛选的【{selected_league}】节点暂无信号。")

    for idx, match in enumerate(display_matches[:20]): 
        match_title = f"{match['主队']} VS {match['客队']}"
        with st.expander(f"[{match['联赛']}] 🔥 ⚽ {match_title} (开赛 {match['时间']})"):
            
            tab1, tab2, tab3, tab4 = st.tabs(["胜平负", "总进球", "比分", "半全场"])
            
            # --- Tab 1: 胜平负 ---
            with tab1:
                if match["1x2"]:
                    cols = st.columns(3)
                    trans_dict = {"Home": "主胜", "Draw": "平局", "Away": "客胜"}
                    for i, val in enumerate(match["1x2"]):
                        cn_name = trans_dict.get(val['value'], val['value']) 
                        if cols[i].button(f"{cn_name} | @{val['odd']}", key=f"1x2_{idx}_{i}", use_container_width=True):
                            add_to_cart(match_title, "胜平负", cn_name, val['odd'])
                            st.rerun()
                else:
                    st.info("暂未开出胜平负盘口")
            
            # --- Tab 2: 总进球 ---
            with tab2:
                if match["goals"]:
                    options = {v['value'].replace("Over", "大").replace("Under", "小") + " 球": v['odd'] for v in match["goals"]}
                    sel_goal = st.selectbox("选择大小球盘口:", list(options.keys()), key=f"sg_{idx}")
                    if st.button(f"锁定 {sel_goal} | @{options[sel_goal]}", key=f"bg_{idx}"):
                        add_to_cart(match_title, "总进球", sel_goal, options[sel_goal])
                        st.rerun()
                else:
                    st.info("暂未开出总进球盘口")
            
            # --- Tab 3: 比分 ---
            with tab3:
                if match["score"]:
                    options = {f"{v['value']}": v['odd'] for v in match["score"]}
                    sel_score = st.selectbox("精准打击 (比分):", list(options.keys()), key=f"ss_{idx}")
                    if st.button(f"锁定比分 {sel_score} | @{options[sel_score]}", key=f"bs_{idx}"):
                        add_to_cart(match_title, "比分", sel_score, options[sel_score])
                        st.rerun()
                else:
                    st.info("暂未开出比分盘口")

            # --- Tab 4: 半全场 ---
            with tab4:
                if match["htft"]:
                    htft_dict = {"Home/Home": "胜/胜", "Home/Draw": "胜/平", "Home/Away": "胜/负", "Draw/Home": "平/胜", "Draw/Draw": "平/平", "Draw/Away": "平/负", "Away/Home": "负/胜", "Away/Draw": "负/平", "Away/Away": "负/负"}
                    options = {htft_dict.get(v['value'], v['value']): v['odd'] for v in match["htft"]}
                    sel_htft = st.selectbox("推演半全场赛果:", list(options.keys()), key=f"sh_{idx}")
                    if st.button(f"锁定半全场 {sel_htft} | @{options[sel_htft]}", key=f"bh_{idx}"):
                        add_to_cart(match_title, "半全场", sel_htft, options[sel_htft])
                        st.rerun()
                else:
                    st.info("暂未开出半全场盘口")
else:
    st.info("🚨 扫描完成，但今日暂无任何赛事数据。")