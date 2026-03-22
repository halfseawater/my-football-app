import streamlit as st
import pandas as pd
import datetime

# ================= 1. 系统与状态初始化 =================
st.set_page_config(page_title="一线蛛网 - 高阶推演矩阵", page_icon="🕸️", layout="wide")

if 'balance' not in st.session_state:
    st.session_state.balance = 10000
if 'bet_history' not in st.session_state:
    st.session_state.bet_history = []
if 'bet_slip' not in st.session_state:
    st.session_state.bet_slip = []

# ================= 2. 核心赛事数据库 (扩充版) =================
# 内置了丰富的模拟真实赛事和完整赔率体系
matches = {
    "ENG_01": {
        "name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 曼彻斯特城 VS 阿森纳",
        "markets": {
            "胜平负": {"主胜": 1.85, "平局": 3.60, "客胜": 4.20},
            "总进球": {"0-1球": 4.50, "2-3球": 2.10, "4球+": 2.40},
            "比分": {"1:0": 8.00, "2:1": 7.50, "1:1": 7.00, "0:1": 12.00, "2:2": 15.00},
            "半全场": {"胜胜": 2.80, "平胜": 4.50, "平平": 5.50, "负负": 6.50}
        }
    },
    "ENG_02": {
        "name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 利物浦 VS 曼彻斯特联",
        "markets": {
            "胜平负": {"主胜": 1.65, "平局": 4.20, "客胜": 4.80},
            "总进球": {"0-1球": 5.00, "2-3球": 2.05, "4球+": 2.15},
            "比分": {"2:0": 8.50, "3:1": 11.00, "1:1": 8.50, "1:2": 15.00},
            "半全场": {"胜胜": 2.40, "平胜": 4.80, "负负": 8.00}
        }
    },
    "SPA_01": {
        "name": "🇪🇸 皇家马德里 VS 巴塞罗那",
        "markets": {
            "胜平负": {"主胜": 2.25, "平局": 3.50, "客胜": 2.90},
            "总进球": {"0-1球": 4.20, "2-3球": 2.00, "4球+": 2.50},
            "比分": {"2:1": 8.50, "1:1": 6.50, "1:2": 10.00, "2:2": 11.00},
            "半全场": {"胜胜": 3.50, "平胜": 5.50, "平负": 6.50, "负负": 4.50}
        }
    },
    "SPA_02": {
        "name": "🇪🇸 马德里竞技 VS 塞维利亚",
        "markets": {
            "胜平负": {"主胜": 1.55, "平局": 3.80, "客胜": 6.50},
            "总进球": {"0-1球": 2.80, "2-3球": 1.95, "4球+": 3.50},
            "比分": {"1:0": 6.00, "2:0": 6.50, "0:0": 9.00, "0:1": 15.00},
            "半全场": {"胜胜": 2.30, "平胜": 4.20, "平平": 5.50}
        }
    },
    "ITA_01": {
        "name": "🇮🇹 国际米兰 VS 尤文图斯",
        "markets": {
            "胜平负": {"主胜": 2.10, "平局": 3.20, "客胜": 3.60},
            "总进球": {"0-1球": 2.90, "2-3球": 1.95, "4球+": 3.80},
            "比分": {"1:0": 6.50, "1:1": 6.00, "0:0": 8.00, "0:1": 9.50},
            "半全场": {"胜胜": 3.40, "平胜": 5.00, "平平": 4.50, "负负": 6.00}
        }
    },
    "ITA_02": {
        "name": "🇮🇹 AC米兰 VS 那不勒斯",
        "markets": {
            "胜平负": {"主胜": 2.50, "平局": 3.30, "客胜": 2.75},
            "总进球": {"0-1球": 3.40, "2-3球": 1.95, "4球+": 3.10},
            "比分": {"1:1": 6.00, "2:1": 9.00, "1:2": 9.50},
            "半全场": {"胜胜": 4.00, "平平": 5.00, "负负": 4.50}
        }
    },
    "GER_01": {
        "name": "🇩🇪 拜仁慕尼黑 VS 多特蒙德",
        "markets": {
            "胜平负": {"主胜": 1.45, "平局": 5.00, "客胜": 6.00},
            "总进球": {"0-1球": 6.50, "2-3球": 2.30, "4球+": 1.70},
            "比分": {"3:1": 9.50, "2:0": 8.50, "2:2": 13.00, "1:2": 18.00},
            "半全场": {"胜胜": 2.00, "平胜": 4.50, "负胜": 18.00}
        }
    },
    "FRA_01": {
        "name": "🇫🇷 巴黎圣日耳曼 VS 马赛",
        "markets": {
            "胜平负": {"主胜": 1.35, "平局": 5.50, "客胜": 7.50},
            "总进球": {"0-1球": 6.00, "2-3球": 2.20, "4球+": 1.80},
            "比分": {"2:0": 7.50, "3:0": 9.00, "1:1": 11.00},
            "半全场": {"胜胜": 1.85, "平胜": 4.20, "平平": 8.50}
        }
    }
}

# ================= 3. 主界面：前端控制台 =================
st.markdown("<h1 style='text-align: center; color: #00FF41;'>🕸️「一线蛛网」全维推演终端 V3.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A9A9A9;'>已接入全球超算赛事节点 | 支持多维盘口 | 深度串关逻辑</p>", unsafe_allow_html=True)
st.divider()

col_main, col_sidebar = st.columns([7, 3])

with col_main:
    st.subheader("📡 全球实时信号源")
    
    for match_id, match_data in matches.items():
        with st.expander(f"🔥 {match_data['name']}", expanded=False): # 默认折叠，节省空间
            tabs = st.tabs(list(match_data["markets"].keys()))
            
            for i, market_name in enumerate(match_data["markets"].keys()):
                with tabs[i]:
                    options = match_data["markets"][market_name]
                    cols = st.columns(len(options))
                    for col, (option_name, odds) in zip(cols, options.items()):
                        if col.button(f"{option_name}\n\n@{odds}", key=f"{match_id}_{market_name}_{option_name}", use_container_width=True):
                            slip_item = {
                                "match_id": match_id,
                                "match_name": match_data['name'],
                                "market": market_name,
                                "option": option_name,
                                "odds": odds
                            }
                            if slip_item not in st.session_state.bet_slip:
                                st.session_state.bet_slip.append(slip_item)
                                st.rerun()

with col_sidebar:
    st.markdown("### 🛒 战术推演池")
    st.metric("💼 剩余蛛网币", st.session_state.balance)
    
    if not st.session_state.bet_slip:
        st.info("尚未锁定目标。请从左侧信号源提取数据。")
    else:
        for idx, item in enumerate(st.session_state.bet_slip):
            st.markdown(f"**{item['match_name']}**")
            st.caption(f"{item['market']} - {item['option']} (@{item['odds']})")
            if st.button("❌ 移除", key=f"remove_{idx}"):
                st.session_state.bet_slip.pop(idx)
                st.rerun()
            st.divider()

        slip_len = len(st.session_state.bet_slip)
        unique_matches = len(set([item['match_id'] for item in st.session_state.bet_slip]))
        
        mode = st.radio("选择战术模式:", ["单关拆分执行", f"极限串关 ({unique_matches}串1)"])
        bet_amount = st.number_input("注入蛛网币 (单笔):", min_value=10, step=10, value=100)
        
        total_odds = 0
        if "串关" in mode and unique_matches > 1:
            total_odds = 1.0
            for item in st.session_state.bet_slip:
                total_odds *= item['odds']
            st.success(f"⚡ 综合赔率引爆: @{total_odds:.2f}")
            st.info(f"💰 预计最高回报: {int(bet_amount * total_odds)} 蛛网币")
        elif "串关" in mode and unique_matches <= 1:
            st.warning("⚠️ 串关指令失败：至少需要选择两场独立赛事！")
        else:
            st.info(f"单关模式：将执行 {slip_len} 笔独立推演，共需 {bet_amount * slip_len} 蛛网币")

        if st.button("🚀 锁定目标，注入算力", type="primary", use_container_width=True):
            required_balance = bet_amount * slip_len if "单关" in mode else bet_amount
            
            if st.session_state.balance < required_balance:
                st.error("⚠️ 蛛网币余额枯竭！")
            elif "串关" in mode and unique_matches <= 1:
                 st.error("⚠️ 战术配置错误：场次不足。")
            else:
                st.session_state.balance -= required_balance
                record = {
                    "时间": datetime.datetime.now().strftime("%H:%M:%S"),
                    "类型": mode,
                    "推演内容": " | ".join([f"{i['match_name']}({i['option']})" for i in st.session_state.bet_slip]),
                    "总投入": required_balance,
                    "综合赔率": f"@{total_odds:.2f}" if "串关" in mode else "独立计算",
                    "状态": "⏳ 数据链演算中..."
                }
                st.session_state.bet_history.append(record)
                st.session_state.bet_slip = [] 
                st.success("指令已成功写入区块链！")
                st.rerun()

# ================= 4. 底部：推演记录档案 =================
st.divider()
st.subheader("📜 核心推演档案库")
if st.session_state.bet_history:
    st.dataframe(pd.DataFrame(st.session_state.bet_history[::-1]), use_container_width=True, hide_index=True)
else:
    st.caption("档案库当前为空。")