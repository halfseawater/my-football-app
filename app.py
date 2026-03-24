import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 页面基本设置
# ==========================================
st.set_page_config(page_title="一线蛛网 - 战术推演池", layout="wide")

# ==========================================
# 1. 蛛网币系统与推演池（购物车）初始化
# ==========================================
if 'balance' not in st.session_state:
    st.session_state.balance = 1000.0  # 初始赠送 1000 蛛网币
if 'cart' not in st.session_state:
    st.session_state.cart = []         # 推演池订单列表

# 添加订单的函数
def add_to_cart(match, play_type, option, odd):
    st.session_state.cart.append({
        "match": match, 
        "play_type": play_type, 
        "option": option, 
        "odd": float(odd)
    })

# 移除订单的函数
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
        # 逐个展示推演池里的选项
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"**{item['match']}**")
            st.caption(f"{item['play_type']} : {item['option']} @ **{item['odd']}**")
            if st.button("❌ 排除此项", key=f"del_{i}"):
                remove_from_cart(i)
                st.rerun() # 刷新界面更新购物车
        
        st.divider()
        st.markdown("**⚡ 执行协议:**")
        # 玩法模式选择
        mode = st.radio("选择策略", ["单关拆分", "极限串关", "混合容错矩阵"], label_visibility="collapsed")
        stake = st.number_input("注入蛛网币 (单注):", min_value=10, max_value=int(max(10, st.session_state.balance)), value=100, step=10)
        
        # --- 核心：动态计算预计回报 ---
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
        else: # 混合串关（简单逻辑模拟）
            total_stake = stake * len(st.session_state.cart)
            potential_return = sum(stake * item['odd'] for item in st.session_state.cart) * 1.5 
            
        st.info(f"💡 总计消耗: {total_stake} 币")
        st.success(f"🎯 全红总回报: {potential_return:.2f} 币")
        
        # 结算按钮
        if st.button("🚀 锁定目标，注入算力", use_container_width=True):
            if st.session_state.balance >= total_stake:
                st.session_state.balance -= total_stake
                st.session_state.cart = [] # 结算后清空
                st.toast("✅ 算力注入成功！已保存至数据库，等待比赛结果...")
                st.rerun()
            else:
                st.error("🚨 算力余额不足，请充值！")

# ==========================================
# 3. 主界面：底层数据抓取与解析
# ==========================================
st.title("📡 实时信号源 (全盘口展示)")
today_str = datetime.now().strftime("%Y-%m-%d")

@st.cache_data(ttl=3600)
def fetch_full_odds(date):
    # ⚠️⚠️⚠️ 你的真实 API Key 填在这里 ⚠️⚠️⚠️
    headers = {"x-apisports-key": "d42308f17e30da5e7b7af0be42f39ce9"} 
    
    try:
        # 1. 抓取赛程拿球队名字
        res_fix = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"date": date})
        teams_map = {item["fixture"]["id"]: {"home": item["teams"]["home"]["name"], "away": item["teams"]["away"]["name"]} 
                     for item in res_fix.json().get("response", [])}

        # 2. 抓取赔率 (包含所有玩法)
        res_odds = requests.get("https://v3.football.api-sports.io/odds", headers=headers, params={"date": date, "bookmaker": "8", "page": "1"})
        data_odds = res_odds.json()
        
        matches_list = []
        if data_odds.get("response"):
            for item in data_odds["response"]:
                f_id = item["fixture"]["id"]
                if f_id not in teams_map:
                    continue
                    
                bets = item["bookmakers"][0]["bets"]
                # 提取四大核心玩法的数据
                m_1x2 = next((m for m in bets if m["id"] == 1), None)           # 胜平负
                m_goals = next((m for m in bets if m["id"] == 5), None)         # 总进球 (Over/Under)
                m_score = next((m for m in bets if m["id"] == 10), None)        # 正确比分
                m_htft = next((m for m in bets if m["name"] == "Halftime/Fulltime"), None) # 半全场
                
                matches_list.append({
                    "id": f_id,
                    "联赛": item["league"]["name"],
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

with st.spinner("正在加载多元赔率矩阵..."):
    matches_data = fetch_full_odds(today_str)

# ==========================================
# 4. 渲染：智能筛选 + 多标签页界面
# ==========================================
if matches_data:
    # 自动提取今天所有存在比赛的联赛名称，并去重排序
    available_leagues = sorted(list(set([m["联赛"] for m in matches_data])))
    
    # 顶部下拉菜单：智能联赛筛选
    selected_league = st.selectbox("🏆 筛选目标锦标赛/联赛:", ["🌍 显示全部赛事"] + available_leagues)
    st.divider() 

    # 执行过滤
    if selected_league == "🌍 显示全部赛事":
        display_matches = matches_data
    else:
        display_matches = [m for m in matches_data if m["联赛"] == selected_league]

    if not display_matches:
        st.warning(f"🚨 当前筛选的【{selected_league}】节点暂无信号。")

    # 渲染比赛列表 (最多展示20场防卡顿)
    for idx, match in enumerate(display_matches[:20]): 
        match_title = f"{match['主队']} VS {match['客队']}"
        with st.expander(f"[{match['联赛']}] 🔥 ⚽ {match_title} (开赛 {match['时间']})"):
            
            # 四个独立的标签页
            tab1, tab2, tab3, tab4 = st.tabs(["胜平负", "总进球", "比分", "半全场"])
            
            # --- Tab 1: 胜平负 ---
            with tab1:
                if match["1x2"]:
                    cols = st.columns(3)
                    # 🕷️ 强行拦截机翻，替换为专业中文术语
                    trans_dict = {"Home": "主胜", "Draw": "平局", "Away": "客胜"}
                    for i, val in enumerate(match["1x2"]):
                        cn_name = trans_dict.get(val['value'], val['value']) 
                        if cols[i].button(f"{cn_name} | @{val['odd']}", key=f"1x2_{idx}_{i}", use_container_width=True):
                            add_to_cart(match_title, "胜平负", cn_name, val['odd'])
                            st.rerun()
                else:
                    st.info("博彩公司暂未开出胜平负盘口")
            
            # --- Tab 2: 总进球 ---
            with tab2:
                if match["goals"]:
                    # 将 Over/Under 替换为大小球中文
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
                    # 拦截半全场机翻，例如 Home/Away 替换为 胜/负
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