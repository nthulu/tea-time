# ====================== TODO 遗留 2026‑09‑01 今日开发暂停 ======================
# 遗留问题清单：
# 1. 选择自定义时间后，停止按钮消失，需点击继续泡茶
# =============================================================================

# 导入框架
import streamlit as st
import importlib
import tea_data
import utils

# ✅开发用：强制重载，解决开发中模块缓存问题，发布版本移除 reload 代码。
importlib.reload(tea_data)  # 生产环境中注释掉
importlib.reload(utils)  # 生产环境中注释掉

from utils import play_audio_queue, hide_streamlit_style, get_git_branch, get_custom_time, render_sidebar

# ==========================================
# 🌟 页面配置与全局样式
# ==========================================
# region 全局配置

# 页面基础配置（必须是第一个 st 命令）
st.set_page_config(
    page_title="泡茶倒计时",
    page_icon="🍵",  # 浏览器标签页的图标
    layout="centered",  # 关键：宽屏布局，完美适配手机端
    initial_sidebar_state="expanded",  # 侧边栏默认展开
)

hide_streamlit_style()  # 使用自定义CSS代码，隐藏默认菜单，让按钮并排显示
    
st.title(f"🍵 泡茶倒计时", anchor="tea-timer",)

# ==========================================
# 🌟 侧边栏：使用说明
# ==========================================
render_sidebar({"app_version": tea_data.APP_VERSION, "current_branch": get_git_branch()})
# endregion
            
# region 主程序逻辑

# 初始化记忆背包（session_state）
tea_data.init_session_state()

# region 茶叶选择
tea_options = tea_data.get_tea_options()  # 获取茶叶配置字典

# 创建两列
col1, col2 = st.columns(2)  
with col1:
    st.write("请选择你要泡的茶叶：")
with col2:
    use_custom_time = st.toggle("🎛️ 自定义时间模式", value=False)

selected_tea = st.selectbox(
    label="请选择你要泡的茶叶：", options=list(tea_options.keys()),label_visibility="collapsed"
)

# 获取原始时间列表
original_time_list = tea_options[selected_tea]

# 据模式决定使用哪种时间列表
if use_custom_time:
    # 如果开启自定义时间模式，显示滑块让用户自定义当前泡次的时间
    custom_time = get_custom_time(st.session_state.current_step)
    active_time_list = [custom_time]  # 使用自定义时间列表
else:
    active_time_list = original_time_list  # 使用默认的茶叶时间列表

# 运行中状态的安全钳制（Clamp）
# 确保切换模式时，current_step 不会越界，且 is_running 不被重置
if st.session_state.is_running:
    max_step = len(active_time_list) - 1
    if st.session_state.current_step > max_step:
        # 越界时停留在最后一泡，保持运行状态
        st.session_state.current_step = max_step
    # 防御性检查：防止 step 为负数
    if st.session_state.current_step < 0:
        st.session_state.current_step = 0

# 将处理后的安全列表存入 session_state
# 供后续 @st.fragment 和按钮渲染统一使用，避免重复计算导致不一致
st.session_state.active_time_list = active_time_list

# 展示用户的选择
st.success(f"你选择了：【{selected_tea}】  \n泡茶方式：盖碗 水量：140ml 茶叶：7g")
st.caption(f"💡 这种茶建议冲泡 {len(original_time_list)} 次，{original_time_list} 秒")

# region 创建按钮逻辑
col1, col2 = st.columns(2)  # 把按钮分成两列

with col1:
    btn_text = "⏸️ 继续泡茶" if st.session_state.is_running else "☕ 开始泡茶"
    if st.button(btn_text, key="start",use_container_width=True):
        if st.session_state.current_step > len(tea_options[selected_tea]):
            st.session_state.warning_msg=f"⚠️ {selected_tea} 建议最多泡 {len(tea_options[selected_tea])} 次哦。如果想继续泡，请使用自定义时间模式。否则请点击停止/重置。"
        else:
            # 取出当前泡数的时间
            st.session_state.tea_time = st.session_state.active_time_list[st.session_state.current_step - 1]
            st.session_state.warning_msg=""  # 清空警告消息
            st.session_state.total_time = st.session_state.tea_time  # 记录总时间
            st.session_state.is_running = True
            
            st.rerun()  # 点击后立刻刷新页面，开始倒计时

with col2:
    if st.session_state.is_running :
        if st.button("⏹ 停止/重置", key="reset",use_container_width=True):
            st.session_state.is_running = False
            st.session_state.tea_time = 0
            st.session_state.current_step = 1
            st.rerun()  # 点击后停止倒计时，重置记忆背包

# endregion

# ==========================================
# region 倒计时Fragment 
# ==========================================

# 正在倒计时中（使用 st.fragment 实现每秒独立刷新）
if st.session_state.is_running and st.session_state.tea_time > 0:
    @st.fragment(run_every=1)  # 核心魔法：每秒自动刷新这个片段

    def countdown_timer():
        current_time = st.session_state.tea_time
        minutes, seconds = divmod(current_time, 60)

        # 倒计时占位符
        countdown_placeholder = st.empty()
        countdown_placeholder.metric(
            label=f"⏳ {selected_tea} 第{st.session_state.current_step}泡：剩余时间",
            value=f"{minutes:02d}:{seconds:02d} ")

        # 🌟 新增：计算并显示进度条
        progress = 1 - (st.session_state.tea_time / st.session_state.total_time)
        st.progress(progress, text="🍵 正在萃取茶香...")

        st.session_state.tea_time -= 1  # 减少 1 秒
        if st.session_state.tea_time <=0:
            st.session_state.current_step += 1  # 泡数加1
            st.rerun()  # 刷新页面，更新显示的时间

    countdown_timer()  # 递归调用，继续倒计时
# 倒计时刚好结束（由主程序刷新触发）
elif st.session_state.tea_time <= 0 and st.session_state.is_running:

    st.balloons()  # 放个气球动画庆祝一下！
    st.success(
        f"✅ {selected_tea} 第{st.session_state.current_step-1}泡完成！请享用你的茶！"
    )

    play_audio_queue("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3")

    # 重置状态 防止无限循环
    st.session_state.is_running = False  # 重置状态

    st.info(
        f"💡 你已经泡了 {st.session_state.current_step - 1} 次，下一泡建议冲泡 {tea_options[selected_tea][st.session_state.current_step - 1] if st.session_state.current_step <= len(tea_options[selected_tea]) else '无可用建议'} 秒。"
    )
# endregion

# region 告警提示
warning_placeholder = st.empty()
if st.session_state.warning_msg:
    warning_placeholder.warning(st.session_state.warning_msg)
else:
    warning_placeholder.empty()

# ==========================================
# 🌟 页面底部
# ==========================================
with st.expander(label="🔍 调试：Session State",expanded=True):
    st.write(st.session_state)