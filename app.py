# 导入框架
import streamlit as st
import time

# ==========================================
# 🌟 页面配置与全局样式（使用 region 折叠）
# ==========================================

# region 全局配置
APP_VERSION = "v1.0.10"  # 应用版本号

# 页面基础配置（必须是第一个 st 命令）
st.set_page_config(
    page_title="泡茶倒计时",
    page_icon="🍵",  # 浏览器标签页的图标
    layout="wide",  # 关键：宽屏布局，完美适配手机端
)

# 自定义CSS代码
# ==========================================
# 🌟 新增：使用 CSS 强制按钮在移动端并排显示
# ==========================================
st.markdown(
    """
<style>
/* 1. 强制列容器不折行，保持水平排列 */
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
}

/* 2. 强制列及其内部按钮按内容自适应宽度，消除 100% 撑满行为 */
div[data-testid="stColumn"] {
    min-width: 0 !important;
    flex: 1 1 0% !important; /* 让两个列平分剩余空间 */
}

/* 3. 优化按钮在窄屏下的显示，防止文字溢出 */
.stButton > button {
    white-space: nowrap !important;
    font-size: 0.85rem !important; /* 稍微缩小字体 */
    padding: 0.4rem 0.8rem !important; /* 缩小按钮内边距 */
    width: 100% !important; /* 让按钮撑满它所在的窄列 */
}
</style>
""",
    unsafe_allow_html=True,
)
# endregion

# ==========================================
# 🌟 数据和工具函数（使用 def 封装）
# ==========================================


# 茶叶数据 字典来存储茶叶和对应的冲泡时间（秒）支持多泡次
def get_tea_options():
    """获取茶叶配置字典"""
    return {
        "绿茶": [4, 5, 6],  # 绿茶可以泡三次，分别是 40 秒、50 秒、60 秒
        "红茶": [15, 20, 25, 30, 35],
        "乌龙茶": [20, 25, 30, 40, 50, 60],
        "普洱茶": [120, 150, 180],
    }


# 🌟 HTML5 音频队列播放函数
def play_audio_queue(audio_url):
    """HTML5 音频队列播放函数"""
    audio_script = f"""
    <script>
    // 1. 初始化全局音频队列（如果还没创建的话）
    if (!window.teaAudioQueue) {{
        window.teaAudioQueue = [];
        window.isTeaAudioPlaying = false;
    }}
    
    // 2. 将新的提示音加入队列
    window.teaAudioQueue.push("{audio_url}");
    
    // 3. 定义播放队列的函数
    function playNextTeaAudio() {{
        if (window.teaAudioQueue.length > 0 && !window.isTeaAudioPlaying) {{
            window.isTeaAudioPlaying = true;
            const url = window.teaAudioQueue.shift(); // 取出队首的声音
            const audio = new Audio(url);
            
            // 播放结束后，标记为空闲，并检查队列里还有没有声音
            audio.onended = function() {{
                window.isTeaAudioPlaying = false;
                playNextTeaAudio(); 
            }};
            audio.play().catch(e => {{
                // 如果还是被浏览器拦截，静默失败，不影响程序运行
                console.log("Audio autoplay blocked:", e);
                window.isTeaAudioPlaying = false;
            }});
        }}
    }}
    
    // 4. 立即尝试播放
    playNextTeaAudio();
    </script>
    """
    st.components.v1.html(audio_script, height=0)

# 参数初始化
def init_session_state():
    """
    初始化 session_state 参数
    只在首次加载 防止后续rerun覆盖
    """
    defaults = {
        "app_version": APP_VERSION,  # 应用版本号
        "time_list": [],  # 用来存储每次泡茶的时间记录
        "current_step": 1,  # 用来记录当前是第几泡，从1开始
        "tea_time": 0,  # 当前泡茶的剩余时间
        "total_time": 0,  # 当前泡茶的总时间
        "is_running": False,  # 当前是否正在倒计时
        "just_finished": False  # 标记是否刚刚完成泡茶
    }

    # 遍历 赋值默认值
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
# ==========================================
# 🌟 核心 UI 与业务逻辑（使用 region 折叠）
# ==========================================
# region 主程序逻辑

# 初始化记忆背包（session_state）
init_session_state()

st.title(f"🍵 泡茶倒计时{APP_VERSION}")

# 茶叶选择
tea_options = get_tea_options()
# 创建下拉框
selected_tea = st.selectbox(
    label="请选择你要泡的茶叶：", options=list(tea_options.keys())
)

# 展示用户的选择
st.success(f"你选择了：【{selected_tea}】")
st.caption(f"💡 提示：这种茶建议冲泡 {tea_options[selected_tea]} 秒")

# 创建按钮逻辑
col1, col2 = st.columns(2)  # 把按钮分成两列

with col1:
    if st.button("☕ 开始泡茶", use_container_width=True):
        st.session_state.time_list = tea_options[
            selected_tea
        ]  # 重置时间列表为当前茶叶的冲泡时间
        if st.session_state.current_step > len(tea_options[selected_tea]):
            st.warning(
                f"⚠️ {selected_tea} 最多只能泡 {len(tea_options[selected_tea])} 次哦，再泡就没味道啦。"
            )
        else:
            # 取出当前泡数的时间
            st.session_state.tea_time = st.session_state.time_list[
                st.session_state.current_step - 1
            ]
            st.session_state.total_time = st.session_state.tea_time  # 记录总时间
            st.session_state.is_running = True
            st.rerun()  # 点击后立刻刷新页面，开始倒计时

with col2:
    if st.button("⏹ 停止/重置", use_container_width=True):
        st.session_state.is_running = False
        st.session_state.tea_time = 0
        st.session_state.current_step = 1
        st.rerun()  # 点击后停止倒计时，重置记忆背包

# ==========================================
# 🌟 倒计时展示与结束提示（彻底重构）
# ==========================================

# 如果正在倒计时，执行以下逻辑
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
            st.session_state.is_running = False  # 倒计时结束，停止运行
            st.session_state.current_step += 1  # 泡数加1
            st.rerun()  # 刷新页面，更新显示的时间

    countdown_timer()  # 递归调用，继续倒计时
# 倒计时结束后，泡数加1
elif st.session_state.tea_time <= 0 and st.session_state.is_running:

    st.balloons()  # 放个气球动画庆祝一下！
    st.success(
        f"✅ {selected_tea} 第{st.session_state.current_step}泡完成！请享用你的茶！"
    )

    play_audio_queue("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3")

    # 重置状态 防止无限循环
    st.session_state.is_running = False  # 重置状态

    st.info(
        f"💡 提示：你已经泡了 {st.session_state.current_step - 1} 次，下一泡建议冲泡 {tea_options[selected_tea][st.session_state.current_step - 1] if st.session_state.current_step <= len(tea_options[selected_tea]) else 'N/A'} 秒。"
    )
    # endregion

# ==========================================
# 🌟 页面底部
# ==========================================
st.caption(f"🚀 当前应用版本：{st.session_state.app_version}")
