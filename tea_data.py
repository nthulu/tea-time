# tea_data.py
import streamlit as st

APP_VERSION = "v1.3.32"  # 应用版本号

def get_tea_options():
    """获取茶叶配置字典"""
    return {
        "测试用茶": [2, 2, 3],  # 测试用茶可以泡三次
        "漳平水仙": [30, 20, 20, 30, 40, 50, 60],  # 漳平水仙 8g:150ml，100°C，功夫泡1:30，浓香乌龙茶，可以泡7~8次
        "油切乌龙": [25, 20, 30, 40, 65, 100],  # 油切乌龙可以泡6次
        "台湾乌龙-四季春": [30, 30, 35, 35, 40, 45, 50],  # 台湾乌龙-四季春可以泡7次
        "台湾乌龙-花果香":[60,40,60,70,80,90,90,90,90],  # 台湾乌龙-花果香可以泡9次
        "东方美人茶":[30,25,30,40,50,60,70,80],  # 东方美人茶可以泡8次
        "英红九号": [5, 5, 5, 7, 8, 9,10,12,15],  # 英红九号可以泡6次，5g:150ml，90°C，功夫泡1:30，浓香红茶/英德红茶，
        "绿茶": [40, 50, 60],  # 绿茶可以泡三次
        "红茶": [15, 20, 25, 30, 35],
        "乌龙茶": [20, 25, 30, 40, 50, 60],
        "普洱茶": [120, 150, 180],
    }

# 参数初始化
def init_session_state():
    """
    初始化 session_state 参数
    只在首次加载 防止后续rerun覆盖
    """
    defaults = {
        "active_time_list": [],  # 用来存储每次泡茶的时间记录
        "current_step": 1,  # 用来记录当前是第几泡，从1开始
        "tea_time": 0,  # 当前泡茶的剩余时间
        "total_time": 0,  # 当前泡茶的总时间
        "is_running": False,  # 当前是否正在倒计时
        "warning_msg": "",  # 警告消息
        "is_active": False,  # 用来标记当前是否在泡茶对话中
        "custom_time_toggle": False,  # 用来标记自定义时间模式是否开启
        "force_toggle_off": False,  # 用来标记是否强制关闭自定义时间模式
    }

    # 遍历 赋值默认值
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value