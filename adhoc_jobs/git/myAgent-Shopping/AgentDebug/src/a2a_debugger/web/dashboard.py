"""
A2A 调试仪表盘 (Streamlit)

提供可视化的消息流监控、统计分析和协议验证。
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from a2a_debugger.models.message import A2AMessage, MessageStore, MessageType
from a2a_debugger.analyzer.validator import A2AMessageValidator


# 页面配置
st.set_page_config(
    page_title="A2A Protocol Debugger",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 初始化 session state
if "message_store" not in st.session_state:
    st.session_state.message_store = MessageStore(max_size=10000)

if "validator" not in st.session_state:
    st.session_state.validator = A2AMessageValidator()

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 2


def load_messages_from_proxy():
    """从代理加载消息 (预留接口)"""
    # 这里可以扩展为从代理的 HTTP 接口获取消息
    pass


def get_message_type_icon(message_type: str) -> str:
    """获取消息类型图标"""
    icons = {
        "request": "📤",
        "response": "📥",
        "notification": "📢",
    }
    return icons.get(message_type, "❓")


def get_status_icon(status_code: int) -> str:
    """获取状态码图标"""
    if status_code < 300:
        return "✅"
    elif status_code < 400:
        return "🔄"
    elif status_code < 500:
        return "⚠️"
    else:
        return "❌"


def format_payload_preview(payload: dict, max_length: int = 100) -> str:
    """格式化 payload 预览"""
    text = json.dumps(payload, ensure_ascii=False)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🔧 控制面板")

        # 自动刷新设置
        st.session_state.auto_refresh = st.toggle(
            "自动刷新",
            value=st.session_state.auto_refresh,
            help="自动刷新消息列表"
        )

        if st.session_state.auto_refresh:
            st.session_state.refresh_interval = st.slider(
                "刷新间隔 (秒)",
                min_value=1,
                max_value=10,
                value=st.session_state.refresh_interval,
            )

        st.divider()

        # 过滤设置
        st.subheader("🔍 过滤器")

        message_types = st.multiselect(
            "消息类型",
            options=["request", "response", "notification"],
            default=["request", "response", "notification"],
        )

        source_filter = st.text_input(
            "来源 Agent",
            placeholder="输入 Agent ID 过滤...",
        )

        status_filter = st.multiselect(
            "HTTP 状态",
            options=["200-299 (Success)", "300-399 (Redirect)", "400-499 (Client Error)", "500-599 (Server Error)"],
            default=[],
        )

        st.divider()

        # 操作按钮
        if st.button("🗑️ 清空消息", use_container_width=True):
            st.session_state.message_store.clear()
            st.success("消息已清空")
            st.rerun()

        if st.button("🔄 立即刷新", use_container_width=True):
            st.rerun()

        return {
            "message_types": message_types,
            "source_filter": source_filter,
            "status_filter": status_filter,
        }


def render_header():
    """渲染页面头部"""
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.title("🔍 A2A Protocol Debugger")
        st.caption("Agent-to-Agent 协议调试与监控工具")

    with col2:
        stats = st.session_state.message_store.get_stats()
        st.metric(
            label="总消息数",
            value=stats["total"],
            delta=f"{stats['requests']} 请求 / {stats['responses']} 响应",
        )

    with col3:
        stats = st.session_state.message_store.get_stats()
        error_rate = stats.get("error_rate", 0)
        st.metric(
            label="错误率",
            value=f"{error_rate:.1f}%",
            delta="正常" if error_rate < 5 else "⚠️ 过高",
            delta_color="normal" if error_rate < 5 else "inverse",
        )


def render_message_flow(messages: list[A2AMessage]):
    """渲染消息流"""
    st.subheader("📨 消息流")

    if not messages:
        st.info("暂无消息，等待 Agent 通信...")
        return

    # 转换为 DataFrame
    data = []
    for msg in reversed(messages[-100:]):  # 只显示最近 100 条
        status = msg.metadata.get("status", 200)
        data.append({
            "ID": msg.id[:8],
            "Time": msg.timestamp.strftime("%H:%M:%S.%f")[:-3],
            "Type": f"{get_message_type_icon(msg.message_type)} {msg.message_type}",
            "Source": msg.source[:20] if msg.source else "-",
            "Target": msg.target[:20] if msg.target else "-",
            "Method": msg.get_method() or "-",
            "Size": len(json.dumps(msg.payload)),
            "Status": f"{get_status_icon(status)} {status}",
            "Latency": f"{msg.get_latency_ms():.1f}ms" if msg.get_latency_ms() else "-",
            "_msg": msg,  # 存储完整消息对象
        })

    df = pd.DataFrame(data)

    # 使用 st.dataframe 显示
    st.dataframe(
        df.drop(columns=["_msg"]),
        use_container_width=True,
        height=400,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Time": st.column_config.TextColumn("时间", width="small"),
            "Type": st.column_config.TextColumn("类型", width="small"),
            "Source": st.column_config.TextColumn("来源", width="medium"),
            "Target": st.column_config.TextColumn("目标", width="medium"),
            "Method": st.column_config.TextColumn("方法", width="medium"),
            "Size": st.column_config.NumberColumn("大小", width="small"),
            "Status": st.column_config.TextColumn("状态", width="small"),
            "Latency": st.column_config.TextColumn("延迟", width="small"),
        },
    )

    # 消息详情
    st.subheader("📄 消息详情")

    selected_indices = st.multiselect(
        "选择消息查看详情",
        options=range(len(data)),
        format_func=lambda i: f"{data[i]['Time']} - {data[i]['Type']} ({data[i]['ID']})",
        max_selections=1,
    )

    if selected_indices:
        selected_msg = data[selected_indices[0]]["_msg"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**基本信息**")
            st.json({
                "id": selected_msg.id,
                "timestamp": selected_msg.timestamp.isoformat(),
                "source": selected_msg.source,
                "target": selected_msg.target,
                "protocol_version": selected_msg.protocol_version,
                "message_type": selected_msg.message_type,
            })

            st.markdown("**HTTP 头**")
            st.json(selected_msg.headers)

        with col2:
            st.markdown("**Payload**")
            st.json(selected_msg.payload)

            st.markdown("**Metadata**")
            st.json(selected_msg.metadata)

        # 协议验证
        st.markdown("**🔍 协议验证结果**")
        result = st.session_state.validator.validate(selected_msg)

        if result.is_valid:
            st.success("✅ 消息格式有效")
        else:
            st.error("❌ 消息格式存在问题")

        if result.issues:
            for issue in result.issues:
                if issue.severity == "error":
                    st.error(f"❌ [{issue.code}] {issue.message}")
                elif issue.severity == "warning":
                    st.warning(f"⚠️ [{issue.code}] {issue.message}")
                else:
                    st.info(f"ℹ️ [{issue.code}] {issue.message}")


def render_statistics(messages: list[A2AMessage]):
    """渲染统计图表"""
    st.subheader("📊 统计分析")

    if not messages:
        st.info("暂无数据")
        return

    # 按时间聚合
    df_msgs = pd.DataFrame([
        {
            "timestamp": m.timestamp,
            "type": m.message_type,
            "source": m.source,
            "status": m.metadata.get("status", 200),
            "latency_ms": m.get_latency_ms() or 0,
        }
        for m in messages
    ])

    col1, col2 = st.columns(2)

    with col1:
        # 消息类型分布
        type_counts = df_msgs["type"].value_counts()
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="消息类型分布",
            color=type_counts.index,
            color_discrete_map={
                "request": "#3498db",
                "response": "#2ecc71",
                "notification": "#f39c12",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Agent 通信统计
        source_counts = df_msgs["source"].value_counts().head(10)
        fig = px.bar(
            x=source_counts.values,
            y=source_counts.index,
            orientation="h",
            title="Agent 消息量 (Top 10)",
            labels={"x": "消息数", "y": "Agent"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # 时序图
    st.subheader("⏱️ 消息时序")

    df_msgs["minute"] = df_msgs["timestamp"].dt.floor("min")
    time_series = df_msgs.groupby(["minute", "type"]).size().reset_index(name="count")

    fig = px.line(
        time_series,
        x="minute",
        y="count",
        color="type",
        title="消息流量趋势 (每分钟)",
        labels={"minute": "时间", "count": "消息数", "type": "类型"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # 延迟分析
    latencies = [m.get_latency_ms() for m in messages if m.get_latency_ms()]
    if latencies:
        st.subheader("⏱️ 延迟分析")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均延迟", f"{sum(latencies)/len(latencies):.1f}ms")
        with col2:
            st.metric("最大延迟", f"{max(latencies):.1f}ms")
        with col3:
            st.metric("最小延迟", f"{min(latencies):.1f}ms")
        with col4:
            p95 = sorted(latencies)[int(len(latencies) * 0.95)]
            st.metric("P95 延迟", f"{p95:.1f}ms")

        # 延迟分布直方图
        fig = px.histogram(
            x=latencies,
            nbins=20,
            title="延迟分布",
            labels={"x": "延迟 (ms)", "y": "频次"},
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    """主函数"""
    # 渲染界面
    render_header()
    filters = render_sidebar()

    # 加载消息
    load_messages_from_proxy()

    # 获取所有消息
    all_messages = st.session_state.message_store.get_all()

    # 应用过滤器
    filtered_messages = all_messages

    if filters["message_types"]:
        filtered_messages = [m for m in filtered_messages if m.message_type in filters["message_types"]]

    if filters["source_filter"]:
        filtered_messages = [m for m in filtered_messages if filters["source_filter"] in m.source]

    # 标签页
    tab1, tab2 = st.tabs(["📨 消息流", "📊 统计分析"])

    with tab1:
        render_message_flow(filtered_messages)

    with tab2:
        render_statistics(filtered_messages)

    # 自动刷新
    if st.session_state.auto_refresh:
        st.empty()
        import time
        time.sleep(st.session_state.refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
