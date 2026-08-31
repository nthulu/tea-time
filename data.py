# tea_data.py
import streamlit as st

APP_VERSION = "v1.1.19b"  # 应用版本号

def get_tea_options():
    """获取茶叶配置字典"""
    return {
        "台湾乌龙-四季春": [30, 30, 35, 35, 40, 45, 50],  # 台湾乌龙-四季春可以泡六次，分别是 30 秒、30 秒、35 秒、35 秒、40 秒、45 秒
        "绿茶": [4, 5, 6],  # 绿茶可以泡三次，分别是 40 秒、50 秒、60 秒
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
        "app_version": APP_VERSION,  # 应用版本号
        "time_list": [],  # 用来存储每次泡茶的时间记录
        "current_step": 1,  # 用来记录当前是第几泡，从1开始
        "tea_time": 0,  # 当前泡茶的剩余时间
        "total_time": 0,  # 当前泡茶的总时间
        "is_running": False,  # 当前是否正在倒计时
        "warning_msg": "",  # 警告消息
    }

    # 遍历 赋值默认值
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value