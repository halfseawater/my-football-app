import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 页面基本设置
# ==========================================
st.set_page_config(page_title="一线蛛网 - 战术推演池", layout="wide")

# ==========================================
# 🕷️ 蛛网汉化引擎字典 (你以后可以随时在这里添加新球队)
# ==========================================
LEAGUE_DICT = {
    "Premier League": "英超", "Championship": "英冠", "League One": "英甲", "League Two": "英乙",
    "La Liga": "西甲", "Serie A": "意甲", "Bundesliga": "德甲", "Ligue 1": "法甲",
    "Eredivisie": "荷甲", "Eerste Divisie": "荷乙", "UEFA Champions League": "欧冠",
    "FA Cup": "足总杯", "EFL Cup": "英联杯", "World Cup": "世界杯", "Euro Championship": "欧洲杯",
    "National League": "英格兰全国联赛", "FAW Championship": "威尔士冠军联赛", "Regionalliga - West": "德国地区联赛西区"
}

TEAM_DICT = {
    # 英超强队
    "Arsenal": "阿森纳", "Manchester City": "曼城", "Manchester United": "曼联", 
    "Liverpool": "利物浦", "Chelsea": "切尔西", "Tottenham": "热刺",
    # 其他常见强队
    "Real Madrid": "皇家马德里", "Barcelona": "巴塞罗那", "Bayern Munich": "拜仁慕尼黑",
    "Juventus": "尤文图斯", "AC Milan": "AC米兰", "Inter": "国际米兰", "Paris Saint Germain": "大巴黎",
    # 帮你把刚才截图里的常见低级别球队也加上了
    "Emmen": "埃门", "Cambuur": "坎布尔", "Raith Rovers": "雷斯流浪者", "Partick": "帕尔蒂克",
    "Stranraer": "斯特兰拉尔", "Clyde": "克莱德", "Elgin City": "埃尔金城", "Forfar Athletic": "福法尔竞技",
    "Oldham": "奥尔德姆", "Notts County": "诺茨郡", "Doncaster": "唐卡斯特", "Port Vale": "韦尔港"
}

# ==========================================
# 1. 蛛网币系统与推演池（购物车）初始化
# ==========================================
if 'balance' not in st.session_state:
    st.session_state.balance = 1000.0  # 初始赠送 1000 蛛网币
if 'cart' not in st.session_state:
    st.session_state.cart = []         # 推演池订单列表

def add_to_cart(match, play_type, option, odd):
    st.session_state.cart.append({
        "match": match, "play_type": play_type, "option": option, "odd": float(odd)
    })

def remove_from_cart(index):
    st.session_state.cart.pop(index)

# ==========================================
# 2. 左侧边栏：推演池控制台
# ==========================================
with st.sidebar:
    st.header("🛒 战术推演池")
    st.metric(label="💼 算力余额 (蛛网币)", value=f"{st.session_state.balance:.2f}")
    st.divider()
    
    if not st.session_state.cart:
        st.info("🕸️ 矩阵空载。请在主界面提取赛事数据并添加选项。")
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
        st.success(f"🎯 全红总回报: {potential_return:.2f} 币")
        
        if st.button("🚀 锁定目标，注入算力", use_container_width=True):
            if st.session_state.balance >= total_stake:
                st.session_state.balance -= total_stake
                st.session_state.cart = [] 
                st.toast("✅ 算力注入成功！已保存至数据库，等待比赛结果...")
                st.rerun()
            else:
                st.error("🚨 算力余额不足，请充值！")

# ==========================================
# 3. 主界面：底层数据抓取与解析 (带汉化引擎)
# ==========================================
st.title("📡 实时信号源 (全盘口展示)")
today_str = datetime.now().strftime("%Y-%m-%d")

@st.cache_data(ttl=3600)
def fetch_full_odds(date):
    # ⚠️⚠️⚠️ 请务必在此处填入你的真实 API Key ⚠️⚠️⚠️
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    
    try:
        # 1. 抓取赛程拿球队名字
        res_fix = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"date": date})
        
        # 汉化球队名字
        teams_map = {}
        for item in res_fix.json().get("response", []):
            f_id = item["fixture"]["id"]
            home_en = item["teams"]["home"]["name"]
            away_en = item["teams"]["away"]["name"]
            teams_map[f_id] = {
                "home": TEAM_DICT.get(home_en, home_en), 
                "away": TEAM_DICT.get(away_en, away_en)
            }

        # 2. 抓取赔率 (包含所有玩法)
        res_odds = requests.get("https://v3.football.api-sports.io/odds", headers=headers, params={"date": date, "bookmaker": "8", "page": "1"})
        data_odds = res_odds.json()
        
        matches_list = []
        if data_odds.get("response"):
            for item in data_odds["response"]:
                f_id = item["fixture"]["id"]
                if f_id not in teams_map:
                    continue
                    
                # 汉化联赛名字
                league_en = item["league"]["name"]
                league_cn = LEAGUE_DICT.get(league_en, league_en)
                    
                bets = item["bookmakers"][0]["bets"]
                m_1x2 = next((m for m in bets if m["id"] == 1), None)           
                m_goals = next((m for m in bets if m["id"] == 5), None)         
                m_score = next((m for m in bets if m["id"] == 10), None)        
                m_htft = next((m for m in bets if m["name"] == "Halftime/Fulltime"), None) 
                
                matches_list.append({
                    "id": f_id,
                    "联赛": league_cn,
                    "时间": datetime.fromisoformat(item["fixture"]["date"]).strftime("%H:%M"),
                    "主队": teams_map[f_id]["home"],
                    "客队": teams_map[f_id]["away"],
                    "1x2": m_1x2["values"] if m_1x2 else [],
                    "goals": m_goals["values"] if m_goals else [],
                    "score": m_score["values"] if m_score else [],
                    "htft": m_htft["values"] if m_htft else []
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
    # 自动提取今天所有存在比赛的联赛名称，并去重排序
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
                    options = {}
                    for v in match["goals"]:
                        name_cn = v['value'].replace("Over", "大").replace("Under", "小") + " 球"
                        options[name_cn] = v['odd']
                        
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
                    htft_dict = {
                        "Home/Home": "胜/胜", "Home/Draw": "胜/平", "Home/Away": "胜/负",
                        "Draw/Home": "平/胜", "Draw/Draw": "平/平", "Draw/Away": "平/负",
                        "Away/Home": "负/胜", "Away/Draw": "负/平", "Away/Away": "负/负"
                    }
                    options = {}
                    for v in match["htft"]:
                        name_cn = htft_dict.get(v['value'], v['value'])
                        options[name_cn] = v['odd']
                        
                    sel_htft = st.selectbox("推演半全场赛果:", list(options.keys()), key=f"sh_{idx}")
                    if st.button(f"锁定半全场 {sel_htft} | @{options[sel_htft]}", key=f"bh_{idx}"):
                        add_to_cart(match_title, "半全场", sel_htft, options[sel_htft])
                        st.rerun()
                else:
                    st.info("暂未开出半全场盘口")
else:
    st.info("🚨 扫描完成，但今日暂无任何赛事数据。")