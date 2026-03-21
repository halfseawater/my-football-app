import streamlit as st

st.set_page_config(page_title="我的足球竞猜", page_icon="⚽")
st.title("⚽ 足球竞猜混合过关计算器")
st.divider()

# ==========================================
# 🌟 1. 数据大升级：为每场比赛加入“总进球”赔率字典
# ==========================================
matches = [
    {
        "id": "周六001", "home": "皇家马德里", "away": "巴塞罗那",
        "spf": {"主胜": 2.10, "平局": 3.40, "客胜": 2.80},
        "goals": {"0球": 15.0, "1球": 6.25, "2球": 3.90, "3球": 3.60, "4球": 4.70}
    },
    {
        "id": "周六002", "home": "曼城", "away": "阿森纳",
        "spf": {"主胜": 1.85, "平局": 3.60, "客胜": 3.20},
        "goals": {"0球": 12.0, "1球": 5.50, "2球": 4.10, "3球": 3.80, "4球": 5.20}
    }
]

selected_odds = {}

st.subheader("📋 今日比赛列表")

# ==========================================
# 🌟 2. 界面大升级：加入 Tabs 标签页切换
# ==========================================
for match in matches:
    st.write(f"**{match['id']}** | 🏠 {match['home']} VS {match['away']} ✈️")
    
    # 刀妹魔法：画出两个可以点击切换的标签页！
    tab1, tab2 = st.tabs(["⚔️ 胜平负", "⚽ 总进球数"])
    
    # 在第一个标签页里放“胜平负”
    with tab1:
        # 把字典里的赔率动态拼接成文字，比如 "主胜 (2.1)"
        spf_options = ["不选"] + [f"{k} ({v})" for k, v in match["spf"].items()]
        choice_spf = st.radio("请选择胜平负：", spf_options, horizontal=True, key=f"{match['id']}_spf")
        
    # 在第二个标签页里放“总进球数”
    with tab2:
        goal_options = ["不选"] + [f"{k} ({v})" for k, v in match["goals"].items()]
        # 因为进球数选项比较多，用 selectbox (下拉菜单) 会让页面更整洁
        choice_goals = st.selectbox("请选择总进球数：", goal_options, key=f"{match['id']}_goals")

    # ==========================================
    # 🌟 3. 逻辑升级：判断用户到底选了哪个玩法
    # ==========================================
    # （刀妹设定的简单规则：如果同一个比赛你两边都选了，优先算胜平负）
    if choice_spf != "不选":
        for k, v in match["spf"].items():
            if k in choice_spf:
                selected_odds[match['id']] = v
    elif choice_goals != "不选":
        for k, v in match["goals"].items():
            if k in choice_goals:
                selected_odds[match['id']] = v
                
    st.divider()

# ==========================================
# 4. 结账区（核心计算逻辑完全不用变！）
# ==========================================
st.subheader("💰 结账区")

bet_amount = st.number_input("请输入投注金额 (元):", min_value=2, value=10, step=2)
match_count = len(selected_odds)

if match_count < 2:
    st.warning("⚠️ 混合过关至少需要选择 2 场比赛哦！请继续在上方选择。")
else:
    total_odds = 1.0
    for odd in selected_odds.values():
        total_odds = total_odds * odd 
        
    max_return = total_odds * bet_amount
    
    st.success(f"🔥 你当前的选择是：{match_count} 串 1")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="混合总赔率", value=f"{total_odds:.2f}")
    with col2:
        st.metric(label="理论最高奖金 (元)", value=f"{max_return:.2f}")
        
    if st.button("确认提交方案"):
        st.balloons() 
        st.info("✅ 方案已记录！刀妹祝你好运！（注：本项目仅为编程模拟测试）")