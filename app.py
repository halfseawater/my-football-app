import streamlit as st
import pandas as pd
import datetime
import itertools
import math

# ================= 1. 系统与状态初始化 =================
st.set_page_config(page_title="一线蛛网 - 矩阵接入", page_icon="🕸️")

st.markdown("""
<style>
    div[data-testid="stButton"] button { border-radius: 8px; font-weight: bold; transition: all 0.3s ease; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .streamlit-expanderHeader { font-size: 1.1rem; font-weight: 600; color: #00FF41 !important; }
</style>
""", unsafe_allow_html=True)

# --- 模拟数据库初始化 ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {} 

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'bet_slip' not in st.session_state:
    st.session_state.bet_slip = []

# ================= 2. 赛事数据库 (扩充版) =================
matches = {
    "ENG_01": {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 曼城 VS 阿森纳", "markets": {"胜平负": {"主胜": 1.85, "平局": 3.60, "客胜": 4.20}, "总进球": {"0-1球": 4.50, "2-3球": 2.10, "4球+": 2.40}, "比分": {"1:0": 8.00, "2:1": 7.50, "1:1": 7.00, "0:1": 12.00, "2:2": 15.00}, "半全场": {"胜胜": 2.80, "平胜": 4.50, "平平": 5.50, "负负": 6.50}}},
    "ENG_02": {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 利物浦 VS 曼联", "markets": {"胜平负": {"主胜": 1.65, "平局": 4.20, "客胜": 4.80}, "总进球": {"0-1球": 5.00, "2-3球": 2.05, "4球+": 2.15}, "比分": {"2:0": 8.50, "3:1": 11.00, "1:1": 8.50, "1:2": 15.00}, "半全场": {"胜胜": 2.40, "平胜": 4.80, "负负": 8.00}}},
    "ENG_03": {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 切尔西 VS 阿森纳", "markets": {"胜平负": {"主胜": 2.80, "平局": 3.40, "客胜": 2.45}, "总进球": {"0-1球": 3.60, "2-3球": 1.95, "4球+": 3.20}, "比分": {"1:1": 6.50, "1:2": 8.50, "0:2": 12.00}, "半全场": {"平负": 5.50, "负负": 3.80, "胜胜": 4.50}}},
    "ENG_04": {"name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 托特纳姆热刺 VS 曼城", "markets": {"胜平负": {"主胜": 4.50, "平局": 4.10, "客胜": 1.68}, "总进球": {"0-1球": 5.50, "2-3球": 2.10, "4球+": 2.05}, "比分": {"1:2": 7.50, "0:2": 8.50, "1:3": 11.00}, "半全场": {"负负": 2.40, "平负": 4.60, "平平": 6.50}}},
    "SPA_01": {"name": "🇪🇸 皇马 VS 巴萨", "markets": {"胜平负": {"主胜": 2.25, "平局": 3.50, "客胜": 2.90}, "总进球": {"0-1球": 4.20, "2-3球": 2.00, "4球+": 2.50}, "比分": {"2:1": 8.50, "1:1": 6.50, "1:2": 10.00, "2:2": 11.00}, "半全场": {"胜胜": 3.50, "平胜": 5.50, "平负": 6.50, "负负": 4.50}}},
    "SPA_02": {"name": "🇪🇸 马竞 VS 塞维利亚", "markets": {"胜平负": {"主胜": 1.55, "平局": 3.80, "客胜": 6.50}, "总进球": {"0-1球": 2.80, "2-3球": 1.95, "4球+": 3.50}, "比分": {"1:0": 6.00, "2:0": 6.50, "0:0": 9.00}, "半全场": {"胜胜": 2.30, "平胜": 4.20, "平平": 5.50}}},
    "ITA_01": {"name": "🇮🇹 国米 VS 尤文图斯", "markets": {"胜平负": {"主胜": 2.10, "平局": 3.20, "客胜": 3.60}, "总进球": {"0-1球": 2.90, "2-3球": 1.95, "4球+": 3.80}, "比分": {"1:0": 6.50, "1:1": 6.00, "0:0": 8.00}, "半全场": {"胜胜": 3.40, "平胜": 5.00, "平平": 4.50}}},
    "ITA_02": {"name": "🇮🇹 AC米兰 VS 罗马", "markets": {"胜平负": {"主胜": 1.95, "平局": 3.40, "客胜": 3.90}, "总进球": {"0-1球": 3.10, "2-3球": 1.95, "4球+": 3.50}, "比分": {"1:0": 6.50, "2:1": 8.00, "1:1": 6.50}, "半全场": {"胜胜": 3.00, "平胜": 4.80, "平平": 5.00}}},
    "GER_01": {"name": "🇩🇪 拜仁 VS 多特蒙德", "markets": {"胜平负": {"主胜": 1.45, "平局": 5.00, "客胜": 6.00}, "总进球": {"0-1球": 6.50, "2-3球": 2.30, "4球+": 1.70}, "比分": {"3:1": 9.50, "2:0": 8.50, "2:2": 13.00}, "半全场": {"胜胜": 2.00, "平胜": 4.50, "负胜": 18.00}}},
    "FRA_01": {"name": "🇫🇷 巴黎圣日耳曼 VS 马赛", "markets": {"胜平负": {"主胜": 1.40, "平局": 5.20, "客胜": 7.00}, "总进球": {"0-1球": 5.80, "2-3球": 2.15, "4球+": 1.85}, "比分": {"2:0": 7.50, "3:0": 9.00, "1:1": 10.00}, "半全场": {"胜胜": 1.90, "平胜": 4.40, "平平": 7.50}}},
    "UCL_01": {"name": "🌟 [欧冠] 拜仁慕尼黑 VS 皇家马德里", "markets": {"胜平负": {"主胜": 2.45, "平局": 3.60, "客胜": 2.65}, "总进球": {"0-1球": 4.80, "2-3球": 2.05, "4球+": 2.20}, "比分": {"2:1": 8.50, "1:2": 9.00, "2:2": 10.00}, "半全场": {"胜胜": 3.80, "负负": 4.20, "平平": 6.00}}}
}

# ================= 3. 登录与注册网关 =================
def login_page():
    st.markdown("<h2 style='text-align: center; color: #00FF41;'>🕸️ 一线蛛网 · 身份验证终端</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>请验证您的身份以接入推演矩阵</p>", unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔑 矩阵登录", "📝 申请新许可 (送1000币)"])

    with tab1:
        st.subheader("接入已有账户")
        login_user = st.text_input("终端代号 (用户名)", key="login_user")
        login_pwd = st.text_input("访问密钥 (密码)", type="password", key="login_pwd")
        if st.button("🚀 验证并接入", use_container_width=True):
            if login_user in st.session_state.users_db and st.session_state.users_db[login_user]['pwd'] == login_pwd:
                st.session_state.current_user = login_user
                st.success("身份验证通过。正在为您连接节点...")
                st.rerun()
            else:
                st.error("⚠️ 权限拒绝：代号或密钥错误，或该特工不存在。")

    with tab2:
        st.subheader("注册新特工")
        reg_user = st.text_input("设置终端代号", key="reg_user")
        reg_pwd = st.text_input("设置访问密钥", type="password", key="reg_pwd")
        reg_pwd2 = st.text_input("确认访问密钥", type="password", key="reg_pwd2")
        
        if st.button("⚡ 申请接入权限", use_container_width=True):
            if not reg_user or not reg_pwd:
                st.warning("⚠️ 必填信息缺失。")
            elif reg_pwd != reg_pwd2:
                st.error("⚠️ 两次输入的密钥不匹配。")
            elif reg_user in st.session_state.users_db:
                st.error("⚠️ 该终端代号已被占用，请更换。")
            else:
                st.session_state.users_db[reg_user] = {"pwd": reg_pwd, "balance": 1000, "history": []}
                st.success(f"✅ 注册成功！系统已为您自动注入 1000 初始蛛网币。请前往登录。")

# ================= 4. 主系统 =================
def main_app():
    user = st.session_state.current_user
    user_balance = st.session_state.users_db[user]['balance']
    user_history = st.session_state.users_db[user]['history']

    st.markdown(f"<h3 style='text-align: center; color: #00FF41;'>🕸️ 欢迎回归, 特工 {user}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("🚪 断开连接 (退出)"):
            st.session_state.current_user = None
            st.session_state.bet_slip = []
            st.rerun()

    st.divider()

    st.markdown("### 📡 实时信号源")
    for match_id, match_data in matches.items():
        with st.expander(f"🔥 {match_data['name']}", expanded=False):
            tabs = st.tabs(list(match_data["markets"].keys()))
            for i, market_name in enumerate(match_data["markets"].keys()):
                with tabs[i]:
                    options = match_data["markets"][market_name]
                    options_items = list(options.items())
                    cols_per_row = 3
                    for row_start in range(0, len(options_items), cols_per_row):
                        row_items = options_items[row_start:row_start + cols_per_row]
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if j < len(row_items):
                                option_name, odds = row_items[j]
                                btn_label = f"{option_name} | @{odds}"
                                with cols[j]:
                                    if st.button(btn_label, key=f"{match_id}_{market_name}_{option_name}", use_container_width=True):
                                        slip_item = {"match_id": match_id, "match_name": match_data['name'], "market": market_name, "option": option_name, "odds": odds}
                                        if slip_item not in st.session_state.bet_slip:
                                            st.session_state.bet_slip.append(slip_item)
                                            st.rerun()

    # --- 侧边栏：加入混合过关逻辑 ---
    with st.sidebar:
        st.markdown("## 🛒 战术推演池")
        st.metric("💼 算力余额 (蛛网币)", user_balance)
        st.divider()
        
        if not st.session_state.bet_slip:
            st.info("🕸️ 矩阵空载。请在主界面提取赛事数据。")
        else:
            for idx, item in enumerate(st.session_state.bet_slip):
                st.markdown(f"**{item['match_name']}**")
                st.markdown(f"`{item['market']}`: {item['option']} 🎯 **@{item['odds']}**")
                if st.button("❌ 排除此项", key=f"remove_{idx}", use_container_width=True):
                    st.session_state.bet_slip.pop(idx)
                    st.rerun()
                st.markdown("---")

            slip_len = len(st.session_state.bet_slip)
            unique_matches = len(set([item['match_id'] for item in st.session_state.bet_slip]))
            
            # 协议中加入混合容错
            mode = st.radio("⚡ 执行协议:", ["单关拆分", f"极限串关 ({unique_matches}串1)", "混合容错矩阵"])
            bet_amount = st.number_input("注入蛛网币 (单注):", min_value=10, step=10, value=100)
            
            total_odds = 0
            required_balance = 0
            expected_return = 0
            
            # --- 1. 极限串关 ---
            if mode == f"极限串关 ({unique_matches}串1)":
                if unique_matches > 1:
                    total_odds = 1.0
                    for item in st.session_state.bet_slip:
                        total_odds *= item['odds']
                    required_balance = bet_amount
                    expected_return = required_balance * total_odds
                    st.success(f"🔥 串关裂变: @{total_odds:.2f}")
                    st.warning(f"💰 预计总回报: {int(expected_return)} 币\n\n(🎯 最高净利: +{int(expected_return - required_balance)})")
                else:
                    st.error("⚠️ 协议驳回：极限串关至少需要两场独立赛事！")
                    required_balance = 0 
            
            # --- 2. 混合容错矩阵 (M串N) ---
            elif mode == "混合容错矩阵":
                if unique_matches < 3:
                    st.error("⚠️ 混合容错协议至少需要锁定 3 场独立赛事！")
                    required_balance = 0
                else:
                    k = st.slider("选择矩阵降维 (例如4选3):", min_value=2, max_value=unique_matches-1, value=2)
                    
                    # 生成不冲突的排列组合
                    valid_combos = []
                    for combo in itertools.combinations(st.session_state.bet_slip, k):
                        if len(set([item['match_id'] for item in combo])) == k:
                            valid_combos.append(combo)
                    
                    num_bets = len(valid_combos)
                    if num_bets == 0:
                        st.error("⚠️ 冲突：同场赛事过多，无法生成交叉矩阵。")
                        required_balance = 0
                    else:
                        required_balance = num_bets * bet_amount
                        # math.prod 计算单个组合的赔率乘积
                        max_return = sum([math.prod([item['odds'] for item in c]) * bet_amount for c in valid_combos])
                        
                        st.info(f"💡 协议已裂变为 {num_bets} 组 {k}串1\n共耗 {required_balance} 币")
                        st.warning(f"💰 全红总回报: {int(max_return)} 币\n\n(🎯 最高净利: +{int(max_return - required_balance)})")

            # --- 3. 单关拆分 ---
            else:
                required_balance = bet_amount * slip_len
                expected_return = sum([bet_amount * item['odds'] for item in st.session_state.bet_slip])
                st.info(f"💡 单关模式：总计消耗 {required_balance} 币")
                st.warning(f"💰 全红总回报: {int(expected_return)} 币\n\n(🎯 最高净利: +{int(expected_return - required_balance)})")

            # 统一结算网关
            if st.button("🚀 锁定目标，注入算力", type="primary", use_container_width=True):
                if required_balance == 0:
                     st.error("⚠️ 战术配置不合规。")
                elif user_balance < required_balance:
                    st.error("⚠️ 算力枯竭！无法执行。")
                else:
                    st.session_state.users_db[user]['balance'] -= required_balance
                    
                    # 根据模式生成更酷的档案记录
                    if "混合容错" in mode:
                        detail = f"{unique_matches}场组合为 {len(valid_combos)}个 {st.session_state.bet_slip[0]['match_name'][:3]}等..."
                    else:
                        detail = " + ".join([f"{i['match_name']}({i['option']})" for i in st.session_state.bet_slip])
                        
                    record = {
                        "时间": datetime.datetime.now().strftime("%H:%M:%S"),
                        "类型": mode,
                        "推演内容": detail,
                        "投入": required_balance,
                        "综合赔率": f"最高 @{int(max_return/required_balance)}倍" if "混合容错" in mode else (f"@{total_odds:.2f}" if "串关" in mode else "-"),
                        "状态": "演算中..."
                    }
                    st.session_state.users_db[user]['history'].append(record)
                    st.session_state.bet_slip = [] 
                    st.success("✅ 指令已写入区块链！")
                    st.rerun()

    # --- 底部记录 ---
    if user_history:
        st.divider()
        st.subheader("📜 链上档案库")
        st.dataframe(pd.DataFrame(user_history[::-1]), use_container_width=True, hide_index=True)

# ================= 5. 路由控制 =================
if st.session_state.current_user is None:
    login_page()
else:
    main_app()