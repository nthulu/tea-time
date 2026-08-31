# 导入框架
import streamlit as st
from data import APP_VERSION, get_tea_options, init_session_state
from utils import play_audio_queue, hide_streamlit_style, get_custom_time


# ==========================================
# 🌟 页面配置与全局样式
# ==========================================
# region 全局配置

# 页面基础配置（必须是第一个 st 命令）
st.set_page_config(
    page_title="泡茶倒计时",
    page_icon="🍵",  # 浏览器标签页的图标
    layout="wide",  # 关键：宽屏布局，完美适配手机端
)
hide_streamlit_style()  # 使用自定义CSS代码，隐藏默认菜单，让按钮并排显示

st.title(f"🍵 泡茶倒计时", anchor="tea-timer")
# endregion

            
# region 主程序逻辑

# 初始化记忆背包（session_state）
init_session_state()

# 茶叶选择
tea_options = get_tea_options()  # 获取茶叶配置字典

col1, col2 = st.columns(2)  # 分成两列
with col1:
    st.write("请选择你要泡的茶叶：")
with col2:
    # 创建下拉框
    selected_tea = st.selectbox(
        label="请选择你要泡的茶叶：", options=list(tea_options.keys()),label_visibility="collapsed"
    )

# 自定义时间模式切换开关
use_custom_time = st.toggle("🎛️ 开启自定义时间模式", value=False)
if use_custom_time:
    # 如果开启自定义时间模式，显示滑块让用户自定义当前泡次的时间
    custom_time = get_custom_time(st.session_state.current_step)

# 展示用户的选择
st.success(f"你选择了：【{selected_tea}】  \n泡茶方式：盖碗 水量：140ml 茶叶：7g")
st.caption(f"💡 这种茶建议冲泡 {tea_options[selected_tea]} 秒")

# 创建按钮逻辑
col1, col2 = st.columns(2)  # 把按钮分成两列

with col1:
    if st.button("☕ 开始泡茶", key="start",use_container_width=True):
        # 🌟 核心修改：根据模式决定使用哪种时间
        if use_custom_time:
            # 自定义模式：使用滑块的时间，并包装成单元素列表（兼容多泡次逻辑）
            st.session_state.time_list = [custom_time]
        else:
            # 默认模式：使用预设的茶叶时间列表
            st.session_state.time_list = tea_options[selected_tea]

        if not use_custom_time and st.session_state.current_step > len(tea_options[selected_tea]):
            st.session_state.warning_msg=f"⚠️ {selected_tea} 最多只能泡 {len(tea_options[selected_tea])} 次哦。如果一定要继续泡，请开启自定义时间模式。或者停止/重置后再开始。"
        else:
            # 取出当前泡数的时间
            if use_custom_time:
                st.session_state.tea_time = st.session_state.time_list[0]  # 只有一个自定义时间
                st.session_state.warning_msg=f"⚠️ {selected_tea} 最多只能泡 {len(tea_options[selected_tea])} 次哦，当前已泡 {st.session_state.current_step} 次。"
            else:
                st.session_state.tea_time = st.session_state.time_list[st.session_state.current_step - 1]
                st.session_state.warning_msg=""  # 清空警告消息
            st.session_state.total_time = st.session_state.tea_time  # 记录总时间
            st.session_state.is_running = True
            
            st.rerun()  # 点击后立刻刷新页面，开始倒计时

with col2:
    if st.button("⏹ 停止/重置", key="reset",use_container_width=True):
        st.session_state.is_running = False
        st.session_state.tea_time = 0
        st.session_state.current_step = 1
        st.rerun()  # 点击后停止倒计时，重置记忆背包

# endregion

# ==========================================
# 倒计时展示与结束提示
# ==========================================

# 正在倒计时中（使用 st.fragment 实现每秒独立刷新）
if st.session_state.is_running and st.session_state.tea_time > 0:
    @st.fragment(run_every=1)  # 核心魔法：每秒自动刷新这个片段

    def countdown_timer():
        current_time = st.session_state.tea_time
        minutes, seconds = divmod(current_time, 60)

        # 创建占位符
        countdown_placeholder = st.empty()
        # 显示大数字倒计时
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
# 创建告警占位符
warning_placeholder = st.empty()
if st.session_state.warning_msg:
    warning_placeholder.warning(st.session_state.warning_msg)
else:
    warning_placeholder.empty()

# ==========================================
# 🌟 页面底部
# ==========================================
st.caption(f"🚀 当前应用版本：{APP_VERSION}")