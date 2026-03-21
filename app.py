import streamlit as st
import requests

st.set_page_config(page_title="足球竞猜混合过关", page_icon="⚽")
st.title("⚽ 足球混合过关计算器 (完全体)")
st.write("数据来源：实时抓取全网最新赔率 🕵️‍♀️")
st.divider()

# ==========================================
# 🌟 1. 抓取与清洗核心 (加入了总进球数 ttg)
# ==========================================
url = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry?channel=c&poolCode=hhad,had"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

try:
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    match_list = data.get('value', {}).get('matchInfoList', [])
except:
    match_list = []

formatted_matches = []
for m in match_list:
    # 提取胜平负
    odds_had = m.get('had', {})
    odds_hhad = m.get('hhad', {})
    win_odd = odds_had.get('h', odds_hhad.get('h', '0'))
    draw_odd = odds_had.get('d', odds_hhad.get('d', '0'))
    lose_odd = odds_had.get('a', odds_hhad.get('a', '0'))
    
    # 🌟 刀妹魔法：提取总进球数 (ttg) 赔率
    odds_ttg = m.get('ttg', {})
    goals_dict = {}
    for i in range(8): # 0到7+球
        key = f"s{i}"
        label = f"{i}球" if i < 7 else "7+球"
        goals_dict[label] = float(odds_ttg.get(key, '0'))

    # 只有当胜平负和进球数全部没开盘时，才判定为彻底死盘丢弃
    if win_odd == '0' and draw_odd == '0' and odds_ttg.get('s0', '0') == '0':
        continue
        
    formatted_matches.append({
        "id": m.get('matchNumStr', '未知'),
        "league": m.get('leagueName', '未知赛事'),
        "home": m.get('homeTeamAllName', '主队'),
        "away": m.get('awayTeamAllName', '客队'),
        "win": float(win_odd) if win_odd else 0.0,
        "draw": float(draw_odd) if draw_odd else 0.0,
        "lose": float(lose_odd) if lose_odd else 0.0,
        "goals": goals_dict
    })

# ==========================================
# 🌟 2. 界面展示 (Tabs 多玩法)
# ==========================================
selected_odds = {}
st.subheader(f"📋 今日可买赛事 (共 {len(formatted_matches)} 场)")

if not formatted_matches:
    st.warning("🌙 刀妹夜间播报：当前时段比赛已全部停售，请明天上午再来抓取最新鲜的比赛哦！")

for index, match in enumerate(formatted_matches[:15]):
    st.write(f"**{match['id']} {match['league']}** | 🏠 **{match['home']}** VS **{match['away']}** ✈️")
    
    unique_id = f"{match['id']}_{index}"
    
    # 画出两个标签页
    tab1, tab2 = st.tabs(["⚔️ 胜平负", "⚽ 总进球数"])
    
    choice_spf = "不选"
    choice_goal = "不选"
    
    with tab1:
        w_text = f"主胜 ({match['win']})" if match['win'] != 0 else "主胜 (停售)"
        d_text = f"平局 ({match['draw']})" if match['draw'] != 0 else "平局 (停售)"
        l_text = f"客胜 ({match['lose']})" if match['lose'] != 0 else "客胜 (停售)"
        
        choice_spf = st.radio("胜平负选项：", ["不选", w_text, d_text, l_text], horizontal=True, key=f"spf_{unique_id}")
    
    with tab2:
        goal_options = ["不选"]
        for g_label, g_odd in match['goals'].items():
            if g_odd != 0:
                goal_options.append(f"{g_label} ({g_odd})")
            else:
                goal_options.append(f"{g_label} (停售)")
        
        choice_goal = st.selectbox("总进球数选项：", goal_options, key=f"goal_{unique_id}")

    # 判断用户选了啥，把赔率存进收银台
    if choice_spf != "不选" and "停售" not in choice_spf:
        if "主胜" in choice_spf: selected_odds[unique_id] = match['win']
        elif "平局" in choice_spf: selected_odds[unique_id] = match['draw']
        elif "客胜" in choice_spf: selected_odds[unique_id] = match['lose']
    elif choice_goal != "不选" and "停售" not in choice_goal:
        # 提取括号里的赔率数字，比如 "3球 (3.60)" 提取出 3.60
        odd_value = float(choice_goal.split("(")[1].split(")")[0])
        selected_odds[unique_id] = odd_value
        
    st.divider()

# ==========================================
# 🌟 3. 结账区
# ==========================================
st.subheader("💰 结账区")
bet_amount = st.number_input("请输入投注金额 (元):", min_value=2, value=10, step=2)
match_count = len(selected_odds)

if match_count < 2:
    st.warning("⚠️ 混合过关至少需要选择 2 场【未停售】的比赛哦！")
else:
    total_odds = 1.0
    for odd in selected_odds.values():
        total_odds = total_odds * odd 
    max_return = total_odds * bet_amount
    
    st.success(f"🔥 你的方案：{match_count} 串 1 (支持胜平负与进球数混搭)")
    col1, col2 = st.columns(2)
    with col1: st.metric(label="混合总赔率", value=f"{total_odds:.2f}")
    with col2: st.metric(label="理论最高奖金 (元)", value=f"{max_return:.2f}")