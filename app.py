import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd

# ==========================================
# 💾 双核心数据库引擎 (用户库 + 赛果库)
# ==========================================
DB_FILE = "spider_users.json"
RES_FILE = "spider_results.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # 🌟 初始化时加入 last_sign_in 字段
    return {"养虎人": {"pwd": "888", "balance": 999999.0, "orders": [], "redeemed": [], "last_sign_in": ""}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_results():
    if os.path.exists(RES_FILE):
        try:
            with open(RES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_results(data):
    with open(RES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 🛠️ 掌柜每日控制台 (开售赛事区)
# ==========================================
TODAYS_MATCHES = [
    {
        "id": "M001", "league": "英超", "home": "阿森纳", "away": "曼城", "time": "23:30",
        "odds_1x2": {"主胜": 2.55, "平局": 3.20, "客胜": 2.38},
        "odds_goals": {"0球": 9.50, "1球": 4.20, "2球": 3.10, "3球": 3.50, "4球": 5.00, "5+球": 7.00},
        "odds_score": {"1:0": 8.0, "2:0": 11.5, "1:1": 6.5, "0:1": 7.5, "0:0": 10.0, "其他": 13.0},
        "odds_htft": {"胜胜": 4.10, "平胜": 5.50, "平平": 4.80, "平负": 5.00, "负负": 3.80} 
    },
    {
        "id": "M002", "league": "西甲", "home": "皇马", "away": "巴萨", "time": "03:00",
        "odds_1x2": {"主胜": 2.15, "平局": 3.40, "客胜": 2.80},
        "odds_goals": {"2球": 4.10, "3球": 3.80, "4球": 4.50, "5球": 7.00},
        "odds_score": {"2:1": 7.5, "1:1": 6.0, "1:2": 8.5, "2:2": 11.0, "其他": 9.0},
        "odds_htft": {"胜胜": 3.20, "平平": 5.10, "负负": 4.50}
    }
]

REWARDS = [
    {"name": "🥤 到店凭券出票送红牛", "cost": 500},
    {"name": "🎟️ 出票满50减5代金券", "cost": 1000},
    {"name": "👑 进【一线蛛网】核心群", "cost": 3000},
]

# ==========================================
# 🔐 基础架构与内存加载
# ==========================================
st.set_page_config(page_title="蛛网方盒", layout="centered", page_icon="🕸️")

if 'user_db' not in st.session_state: st.session_state.user_db = load_data()
if 'sys_results' not in st.session_state: st.session_state.sys_results = load_results()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'cart' not in st.session_state: st.session_state.cart = {} 

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; margin-top:30px;'>🕸️ 蛛网方盒</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>实战推演 · 赢取代金券</p>", unsafe_allow_html=True)
    
    t_log, t_reg = st.tabs(["🔐 登录", "🆔 注册"])
    with t_log:
        u = st.text_input("代号", key="l_u")
        p = st.text_input("密码", type="password", key="l_p")
        if st.button("⚡ 登入大厅", use_container_width=True, type="primary"):
            if u in st.session_state.user_db and st.session_state.user_db[u]["pwd"] == p:
                st.session_state.logged_in, st.session_state.current_user = True, u
                st.rerun() 
            else: st.error("🚨 账号或密码错误！")
    with t_reg:
        ru = st.text_input("设置代号", key="r_u")
        rp = st.text_input("设置密码", type="password", key="r_p")
        if st.button("📝 注册领 50 积分", use_container_width=True, type="primary"):
            if ru in st.session_state.user_db: 
                st.warning("🚨 该代号已被注册，请换一个名字！")
            elif ru and rp:
                # 🌟 新用户注册，初始化 last_sign_in 为空
                st.session_state.user_db[ru] = {"pwd": rp, "balance": 50.0, "orders": [], "redeemed": [], "last_sign_in": ""}
                save_data(st.session_state.user_db)
                st.success("✅ 注册成功！系统已赠送 50 枚蛛网币。请切换到登录。")
    st.stop() 

user_data = st.session_state.user_db[st.session_state.current_user]

col_head1, col_head2 = st.columns([3, 1])
col_head1.markdown(f"**👤 {st.session_state.current_user}** | 💰 积分: **{user_data['balance']:.0f}**")
if col_head2.button("退出", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.cart = {}
    st.rerun()

# ==========================================
# 📱 四大核心导航区
# ==========================================
tab_play, tab_cart, tab_rewards, tab_profile = st.tabs(["🎯 大厅", "🛒 购物车", "🎁 兑换", "👤 我的"])

# --- 🎯 选赛大厅 ---
def render_btn(m_id, m_name, p_type, opt_name, odd):
    k = f"{m_id}_{p_type}_{opt_name}"
    is_sel = k in st.session_state.cart
    if st.button(f"{opt_name}\n@{odd:.2f}", type="primary" if is_sel else "secondary", key=f"ui_{k}", use_container_width=True):
        if is_sel: del st.session_state.cart[k] 
        else:
            st.session_state.cart[k] = {"match_id": m_id, "match_name": m_name, "play": p_type, "choice": opt_name, "odd": odd}
            st.toast("✅ 已加入购物车", icon="🛒")
        st.rerun()

with tab_play:
    st.info("💡 提示：点击选项高亮，选好后去【🛒 购物车】结算。")
    for match in TODAYS_MATCHES:
        m_name = f"{match['home']} vs {match['away']}"
        st.markdown(f"**⚽ {m_name}** `[{match['league']}]`")
        
        st.caption("胜平负")
        c1, c2, c3 = st.columns(3)
        for i, (opt, odd) in enumerate(match['odds_1x2'].items()):
            with [c1, c2, c3][i % 3]: render_btn(match['id'], m_name, "胜平负", opt, odd)
                
        st.caption("总进球数")
        g_items = list(match['odds_goals'].items())
        for row in range(0, len(g_items), 3):
            cols = st.columns(3)
            for i in range(3):
                if row + i < len(g_items):
                    opt, odd = g_items[row + i]
                    with cols[i]: render_btn(match['id'], m_name, "进球", opt, odd)

        st.caption("半全场") 
        h_items = list(match['odds_htft'].items())
        for row in range(0, len(h_items), 3):
            cols = st.columns(3)
            for i in range(3):
                if row + i < len(h_items):
                    opt, odd = h_items[row + i]
                    with cols[i]: render_btn(match['id'], m_name, "半全场", opt, odd)
        
        st.caption("比分波胆")
        score_opts = {f"{k} (@{v:.2f})": (k, v) for k, v in match['odds_score'].items()}
        sel_score = st.selectbox("选择比分:", list(score_opts.keys()), key=f"sc_{match['id']}", label_visibility="collapsed")
        sc_name, sc_odd = score_opts[sel_score]
        btn_key_sc = f"{match['id']}_比分_{sc_name}"
        sc_is_selected = btn_key_sc in st.session_state.cart
        if st.button(f"{'✅ 已锁定' if sc_is_selected else '🎯 锁定比分'} {sc_name} (@{sc_odd:.2f})", type="primary" if sc_is_selected else "secondary", key=f"btn_sc_{match['id']}", use_container_width=True):
            if sc_is_selected: del st.session_state.cart[btn_key_sc]
            else: 
                st.session_state.cart[btn_key_sc] = {"match_id": match['id'], "match_name": m_name, "play": "比分", "choice": sc_name, "odd": sc_odd}
                st.toast("✅ 已加入购物车")
            st.rerun()

        st.markdown("---") 

# --- 🛒 购物车 ---
with tab_cart:
    if not st.session_state.cart:
        st.info("🛒 你的推演单空空如也，快去【🎯 大厅】挑选比赛吧！")
    else:
        st.markdown("### 📝 待确认方案")
        for key, item in list(st.session_state.cart.items()):
            cc1, cc2 = st.columns([4, 1])
            cc1.markdown(f"**{item['match_name']}**<br><span style='color:#666; font-size:14px;'>{item['play']}: {item['choice']} @{item['odd']}</span>", unsafe_allow_html=True)
            if cc2.button("❌", key=f"del_{key}"):
                del st.session_state.cart[key]
                st.rerun()
            st.markdown("<hr style='margin: 0.2em 0;'>", unsafe_allow_html=True)
        
        st.markdown("#### 🔄 选择玩法")
        mode = st.radio("模式", ["单关 (各买一注)", "普通串关 (同玩法)", "混合过关 (跨玩法)"], label_visibility="collapsed")
        
        can_bet = True
        max_bet_allowed = int(user_data['balance'])
        
        if max_bet_allowed < 2:
            st.error("🚨 你的积分不足 2 币，已无法下注！请点击【👤 我的】进行每日签到或联系店长。")
            can_bet = False
            stake = 0
        else:
            stake = st.number_input("💰 注入蛛网币 (最少2币，必须为2的倍数):", min_value=2, max_value=max_bet_allowed, value=2, step=2)
            if stake % 2 != 0:
                st.error("🚨 注入算力必须是 2 的倍数！")
                can_bet = False
        
        if can_bet:
            cart_items = list(st.session_state.cart.values())
            match_ids_in_cart = [item['match_id'] for item in cart_items]
            
            total_odds = 1.0
            for item in cart_items: total_odds *= item['odd']
            
            if mode == "单关 (各买一注)":
                total_cost = stake * len(cart_items)
                potential_return = sum(stake * item['odd'] for item in cart_items)
                desc_text = f"{len(cart_items)}个单关"
            else:
                if len(cart_items) < 2:
                    st.error("🚨 串关至少选 2 场不同比赛！")
                    can_bet = False
                elif len(match_ids_in_cart) != len(set(match_ids_in_cart)):
                    st.error("🚨 规则拦截：同一场比赛不能串在一起！")
                    can_bet = False
                else:
                    play_types = set([item['play'] for item in cart_items])
                    if mode == "普通串关 (同玩法)" and len(play_types) > 1:
                        st.error("🚨 包含多种玩法，请切换为【混合过关】！")
                        can_bet = False
                    else:
                        total_cost = stake
                        potential_return = stake * total_odds
                        desc_text = f"{len(cart_items)}串1"
                        st.markdown(f"**⚡ 组合总赔率: <span style='color:#ff4b4b;'>@{total_odds:.2f}</span>**", unsafe_allow_html=True)

            if can_bet:
                net_profit = potential_return - total_cost
                if total_cost > max_bet_allowed:
                    st.error(f"🚨 本次方案总共需要 {total_cost} 币，您的余额不足！")
                else:
                    st.info(f"💵 成本: **{total_cost}** 币 | 💰 返还: **{potential_return:.0f}** 币\n🎯 预计净赚: **<span style='color:#00e5ff; font-size:18px;'>{net_profit:.0f}</span>** 币")
                    
                    if st.button(f"🚀 确认出单 (扣除 {total_cost} 币)", type="primary", use_container_width=True):
                        user_data['balance'] -= total_cost
                        
                        user_data['orders'].insert(0, {
                            "id": "W" + (datetime.utcnow() + timedelta(hours=8)).strftime("%H%M%S"), "match": desc_text, "play": mode,
                            "cost": total_cost, "return": potential_return, 
                            "status": "🟡 待开奖", "time": (datetime.utcnow() + timedelta(hours=8)).strftime("%m-%d %H:%M"),
                            "raw_items": cart_items 
                        })
                        st.session_state.cart = {} 
                        save_data(st.session_state.user_db)
                        st.toast("✅ 指令锁定成功！请前往【👤 我的】查看。")
                        st.rerun()

# --- 🎁 福利兑换 ---
with tab_rewards:
    st.markdown("### 🏆 福利兑换")
    for reward in REWARDS:
        r_name = reward['name']
        st.markdown(f"**{r_name}**\n<span style='color:#666; font-size:14px;'>💎 消耗: {reward['cost']} 币</span>", unsafe_allow_html=True)
        if st.session_state.get(f"confirm_{r_name}"):
            c_yes, c_no = st.columns(2)
            if c_yes.button("✅ 确认扣费", key=f"yes_{r_name}", type="primary"):
                if user_data['balance'] >= reward['cost']:
                    user_data['balance'] -= reward['cost']
                    user_data['redeemed'].append({"item": r_name, "time": (datetime.utcnow() + timedelta(hours=8)).strftime("%m-%d %H:%M")})
                    save_data(st.session_state.user_db)
                    st.session_state[f"confirm_{r_name}"] = False
                    st.success("🎉 兑换成功！")
                    st.rerun()
                else:
                    st.error("余额不足")
                    st.session_state[f"confirm_{r_name}"] = False
                    st.rerun()
            if c_no.button("❌ 取消", key=f"no_{r_name}"):
                st.session_state[f"confirm_{r_name}"] = False
                st.rerun()
        else:
            if st.button("🎁 立即兑换", key=f"rw_{r_name}", use_container_width=True):
                st.session_state[f"confirm_{r_name}"] = True
                st.rerun()
        st.markdown("<hr style='margin: 0.5em 0;'>", unsafe_allow_html=True)

# --- 👤 个人中心 & 👑 店长超级后台 ---
with tab_profile:
    
    # ==========================================
    # 🌟 每日签到系统 (强制使用北京/台北时间 UTC+8)
    # ==========================================
    st.markdown("### 📅 每日军需补给")
    today_str = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d")
    last_sign_in = user_data.get("last_sign_in", "")
    
    if last_sign_in == today_str:
        st.success("✅ 今日已签到领取 2 币，请明天再来。")
    else:
        if st.button("🎁 每日签到 免费领 2 币", type="primary", use_container_width=True):
            user_data['balance'] += 2
            user_data['last_sign_in'] = today_str
            save_data(st.session_state.user_db)
            st.balloons()
            st.toast("✅ 签到成功！余额 +2 币")
            st.rerun()
            
    st.markdown("---")

    st.markdown("### 📜 我的推演单")
    if not user_data['orders']: st.info("暂无订单记录。")
    
    for idx, order in enumerate(user_data['orders']):
        with st.expander(f"{order['status']} | {order['match']} | 投入 {order['cost']} 币"):
            st.write(f"⏱️ {order['time']} | 模式: {order['play']}")
            
            st.markdown("**方案明细：**")
            if 'raw_items' in order:
                for item in order['raw_items']:
                    m_id = item['match_id']
                    play = item['play']
                    choice = item['choice']
                    odd = item['odd']
                    m_name = item['match_name']
                    
                    actual_res = st.session_state.sys_results.get(m_id, {}).get(play, None)
                    
                    if actual_res:
                        if choice == actual_res:
                            res_text = f"<span style='color:#2ecc71; font-weight:bold;'> [赛果: {actual_res} ✅]</span>"
                        else:
                            res_text = f"<span style='color:#e74c3c; font-weight:bold;'> [赛果: {actual_res} ❌]</span>"
                    else:
                        res_text = "<span style='color:#95a5a6; font-size:12px;'> (待开奖...)</span>"
                        
                    st.markdown(f"• {m_name} | {play}: **{choice}** @{odd:.2f} {res_text}", unsafe_allow_html=True)
            
            st.write(f"💵 预期返还: **{order['return']:.0f} 币**")
            
            if order['status'] == "🟡 待开奖":
                st.info("🕒 比赛结束后，系统将自动对奖结算")
                    
    st.markdown("### 🎒 我的背包 (兑换记录)")
    if not user_data['redeemed']: st.write("空空如也~")
    for item in user_data['redeemed']:
        st.success(f"🎟️ {item['item']}\n(时间: {item['time']})")

    # ==========================================
    # 👑 专属：店长超级后台
    # ==========================================
    if st.session_state.current_user == "养虎人":
        st.markdown("---")
        st.markdown("<h3 style='color:#ff4b4b;'>👑 店长超级后台</h3>", unsafe_allow_html=True)
        
        st.markdown("#### 🎛️ 第一步：录入完场比赛赛果")
        
        match_dict = {f"{m['home']} vs {m['away']}": m for m in TODAYS_MATCHES}
        sel_m_name = st.selectbox("选择已结束的比赛:", list(match_dict.keys()))
        target_m = match_dict[sel_m_name]
        m_id = target_m['id']
        
        c1, c2 = st.columns(2)
        r_1x2 = c1.selectbox("真实赛果 - 胜平负", list(target_m["odds_1x2"].keys()))
        r_goals = c2.selectbox("真实赛果 - 总进球", list(target_m["odds_goals"].keys()))
        r_score = c1.selectbox("真实赛果 - 比分", list(target_m["odds_score"].keys()))
        r_htft = c2.selectbox("真实赛果 - 半全场", list(target_m["odds_htft"].keys()))
        
        if st.button(f"💾 确认保存【{sel_m_name}】的赛果", type="primary", use_container_width=True):
            st.session_state.sys_results[m_id] = {
                "胜平负": r_1x2, "总进球": r_goals, "比分": r_score, "半全场": r_htft 
            }
            save_results(st.session_state.sys_results)
            st.success(f"✅ 赛果保存成功！现在你可以点击下方的【一键对奖】了。")
            
        st.markdown("#### ⚡ 第二步：智能核对与派奖")
        if st.button("🚀 一键核对全站待开奖订单", type="primary", use_container_width=True):
            settled_count = 0
            
            for u_name, u_info in st.session_state.user_db.items():
                for idx, order in enumerate(u_info['orders']):
                    if order['status'] == "🟡 待开奖" and 'raw_items' in order:
                        is_lost = False
                        all_won = True
                        
                        for item in order['raw_items']:
                            check_m_id = item['match_id']
                            play = item['play']
                            choice = item['choice']
                            
                            if check_m_id in st.session_state.sys_results:
                                actual_result = st.session_state.sys_results[check_m_id].get(play)
                                if choice != actual_result:
                                    is_lost = True
                                    break
                            else:
                                all_won = False
                                
                        if is_lost:
                            u_info['orders'][idx]['status'] = "🔴 未命中"
                            settled_count += 1
                        elif all_won:
                            u_info['orders'][idx]['status'] = "🟢 已中奖" 
                            u_info['balance'] += order['return'] 
                            settled_count += 1
                            
            save_data(st.session_state.user_db)
            if settled_count > 0:
                st.success(f"✅ 派奖完成！共清算了 {settled_count} 笔订单。")
            else:
                st.warning("⚠️ 没有发生状态变动的订单。")
        
        st.divider()
        st.markdown("#### 👥 客户数据总览")
        all_users = []
        for u_name, u_info in st.session_state.user_db.items():
            all_users.append({
                "代号": u_name, "密码": u_info['pwd'], 
                "可用积分": u_info['balance'], 
                "待开奖": len([o for o in u_info['orders'] if '待开奖' in o['status']])
            })
        st.dataframe(pd.DataFrame(all_users), use_container_width=True)
        
        st.markdown("#### 💰 手工上下分")
        c_user = st.text_input("输入客户代号：")
        c_amount = st.number_input("调整积分 (正数加，负数扣)：", value=0, step=10)
        if st.button("⚡ 确认执行", type="primary"):
            if c_user in st.session_state.user_db:
                st.session_state.user_db[c_user]['balance'] += c_amount
                save_data(st.session_state.user_db)
                st.success(f"✅ 成功！客户【{c_user}】最新积分：{st.session_state.user_db[c_user]['balance']}")
            else:
                st.error("🚨 找不到此客户！")