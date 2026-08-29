# 导入框架
import streamlit as st
import time

# 页面基础配置（必须是第一个 st 命令）
st.set_page_config(
    page_title="泡茶倒计时",
    page_icon="🍵",  # 浏览器标签页的图标
    layout="wide"    # 关键：宽屏布局，完美适配手机端
)

# 设置应用标题
st.title("泡茶倒计时 🍵")

# st.info("这是一个简单的 Streamlit 应用示例，展示了如何使用文本输入框和条件显示内容。")

# ==========================================
# 🌟 新增：使用 CSS 强制按钮在移动端并排显示
# ==========================================
st.markdown("""
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
""", unsafe_allow_html=True)

# 准备茶叶数据
# 我们用字典来存储茶叶和对应的冲泡时间（秒）
tea_options = {
    "绿茶": 40,    
    "红茶": 15,    
    "乌龙茶": 20,  
    "普洱茶": 120   
}

# 创建下拉框
# label: 下拉框前面的提示文字
# options: 下拉框里的选项（这里用字典的 keys）
selected_tea = st.selectbox(
    label="请选择你要泡的茶叶：",
    options=list(tea_options.keys())
)

# 展示用户的选择
st.success(f"你选择了：【{selected_tea}】")
st.caption(f"💡 提示：这种茶建议冲泡 {tea_options[selected_tea]} 秒")

# 初始化记忆背包
# 我们检查背包里有没有 'tea_time' 这个物品。
# 如果没有（说明是第一次打开网页），我们就给它一个默认值 0。
# 如果有，就保持原来的值不变。
if 'tea_time' not in st.session_state:
    st.session_state.tea_time = 0
# 增加了一个 'is_running' 变量，用来记录当前是否正在倒计时
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# 创建按钮逻辑
col1, col2 = st.columns(2) # 把按钮分成两列，手机上更好看

with col1:
    if st.button("☕ 开始泡茶",use_container_width=True):
        st.session_state.tea_time = tea_options[selected_tea]
        st.session_state.total_time = tea_options[selected_tea] # 记录总时间
        st.session_state.is_running = True
        st.rerun()  # 点击后立刻刷新页面，开始倒计时

with col2:
    if st.button("⏹ 停止/重置",use_container_width=True):
        st.session_state.tea_time = 0
        st.rerun()  # 点击后立刻刷新页面，停止倒计时

# ==========================================
# 🌟 核心新增部分：倒计时展示
# ==========================================

# 如果正在倒计时，执行以下逻辑
if st.session_state.is_running and st.session_state.tea_time > 0:
    # 创建占位符
    countdown_placeholder = st.empty()

    # 显示大数字倒计时
    minutes, seconds = divmod(st.session_state.tea_time, 60)
    countdown_placeholder.metric(label="⏳ 倒计时中：剩余时间", value=f"{minutes:02d}:{seconds:02d} ")

    # 🌟 新增：计算并显示进度条
    # 进度 = 1 - (剩余时间 / 总时间)，这样进度条是从左往右填满的
    progress = 1 - (st.session_state.tea_time / st.session_state.total_time)
    st.progress(progress, text="🍵 正在萃取茶香...")

    st.info(f"⏳ 倒计时中：剩余 {st.session_state.tea_time} 秒")
    
    # 使用 Streamlit 的计时器功能，每秒减少 1 秒
    time.sleep(1)  # 等待 1 秒
    st.session_state.tea_time -= 1  # 减少 1 秒
    st.rerun()  # 刷新页面，更新显示的时间

# 倒计时结束后，提示用户
elif st.session_state.tea_time <= 0 and st.session_state.is_running:
    st.balloons()  # 放个气球动画庆祝一下！
    st.success("✅ 泡茶完成！请享用你的茶！")

    # 🌟 新增：播放提示音
    # 这里使用了一个公共的免费提示音 URL，Streamlit 原生支持 mp3/wav
    st.audio("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3", format="audio/mp3", autoplay=True)

    # 重置状态 防止无限循环
    st.session_state.is_running = False  # 重置状态
