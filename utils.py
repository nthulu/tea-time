# utils.py
import subprocess
import os
import streamlit as st

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

# 🌟 隐藏 Streamlit 默认菜单与底部标志
def hide_streamlit_style():
    """隐藏 Streamlit 默认菜单与底部标志"""
    hide_style = """
    <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        footer {visibility: hidden;}
        #stDecoration {display: none;}
        /* 新增：使用 CSS 强制按钮在移动端并排显示 */
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
        /* 主按钮：渐变 + 阴影 + hover 上浮 */
        .st-key-start button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .st-key-start button:hover {
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .st-key-start button:active {
            transform: translateY(0) scale(0.97);
            transition: all 0.1s;
        }

        /* 次按钮：描边风，类似 ElementUI 的 plain 按钮 */
        .st-key-reset button {
            background: white;
            color: #764ba2;
            border: 2px solid #764ba2;
            border-radius: 12px;
            padding: 12px 26px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.25s ease;
        }
        .st-key-reset button:hover {
            background: #764ba2;
            color: white;
            box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        }
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# 获取自定义泡茶时间函数
def get_custom_time(current_step):
    """
    提供一个滑块让用户自定义当前泡次的时间。
    参数 current_step: 当前是第几泡，用于显示在滑块标签上。
    """
    # 默认时间设为 60 秒，范围 10~300 秒
    custom_time = st.slider(
        label=f"自定义第 {current_step} 泡的时间（秒）",
        min_value=10,
        max_value=300,
        value=60,
        step=5,
    )
    return custom_time

def get_git_branch() -> str:
    """获取当前git分支名称，获取失败返回unknown"""
    # print("utils 当前工作目录:", os.getcwd())   # 打印当前目录
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        # 没有git、没有.git目录、打包部署环境都会走到这里
        # print("git调用异常：", repr(e))   # 打印真实报错
        return "unknown"