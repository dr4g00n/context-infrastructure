"""
对话分析器

分析 Agent 间通信模式，检测循环依赖、计算延迟、生成诊断报告。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt

from a2a_debugger.models.message import A2AMessage, MessageStore


@dataclass
class LatencyStats:
    """延迟统计"""
    avg_ms: float
    min_ms: float
    max_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    count: int


@dataclass
class ConversationPattern:
    """对话模式"""
    initiator: str                      # 发起者
    responder: str                      # 响应者
    request_count: int
    response_count: int
    avg_latency_ms: float
    error_count: int


@dataclass
class DiagnosisReport:
    """诊断报告"""
    timestamp: datetime = field(default_factory=datetime.now)
    issues: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""

    def add_issue(
        self,
        severity: str,
        category: str,
        description: str,
        affected_agents: Optional[list[str]] = None,
    ) -> None:
        """添加诊断问题"""
        self.issues.append({
            "severity": severity,
            "category": category,
            "description": description,
            "affected_agents": affected_agents or [],
            "timestamp": datetime.now().isoformat(),
        })


class ConversationAnalyzer:
    """
    对话分析器

    分析 Agent 间通信模式，提供拓扑分析、延迟统计、故障诊断等功能。
    """

    def __init__(self, messages: list[A2AMessage]):
        """
        初始化分析器

        Args:
            messages: 消息列表
        """
        self.messages = messages
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self) -> None:
        """构建通信拓扑图"""
        for msg in self.messages:
            if msg.source and msg.target and msg.source != msg.target:
                # 添加边，附带消息信息
                edge_data = self.graph.get_edge_data(msg.source, msg.target, default={})
                messages = edge_data.get("messages", [])
                messages.append({
                    "timestamp": msg.timestamp,
                    "type": msg.message_type,
                    "status": msg.metadata.get("status", 200),
                    "latency_ms": msg.get_latency_ms(),
                })

                self.graph.add_edge(
                    msg.source,
                    msg.target,
                    messages=messages,
                    count=len(messages),
                )

            # 确保所有节点都有属性
            if msg.source:
                self.graph.add_node(msg.source)
            if msg.target:
                self.graph.add_node(msg.target)

    def detect_cycles(self) -> list[list[str]]:
        """
        检测循环依赖

        Returns:
            循环路径列表，每个路径是一个 Agent ID 列表
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []
        except Exception:
            return []

    def detect_lonely_agents(self) -> dict[str, list[str]]:
        """
        检测孤立 Agent

        Returns:
            {"only_source": [...], "only_target": [...], "isolated": [...]}
        """
        all_nodes = set(self.graph.nodes())

        only_source = []
        only_target = []
        isolated = []

        for node in all_nodes:
            out_degree = self.graph.out_degree(node)
            in_degree = self.graph.in_degree(node)

            if out_degree > 0 and in_degree == 0:
                only_source.append(node)
            elif out_degree == 0 and in_degree > 0:
                only_target.append(node)
            elif out_degree == 0 and in_degree == 0:
                isolated.append(node)

        return {
            "only_source": only_source,
            "only_target": only_target,
            "isolated": isolated,
        }

    def latency_analysis(self) -> dict[str, LatencyStats]:
        """
        分析请求-响应延迟

        Returns:
            Agent ID 到延迟统计的映射
        """
        # 匹配请求和响应
        requests = {m.id: m for m in self.messages if m.is_request()}
        latencies_by_agent: dict[str, list[float]] = defaultdict(list)

        for msg in self.messages:
            if not msg.is_response():
                continue

            req_id = msg.metadata.get("request_id")
            if req_id and req_id in requests:
                latency = msg.get_latency_ms()
                if latency is not None:
                    source = requests[req_id].source
                    latencies_by_agent[source].append(latency)

        # 计算统计
        result = {}
        for agent, times in latencies_by_agent.items():
            if not times:
                continue

            sorted_times = sorted(times)
            count = len(sorted_times)

            result[agent] = LatencyStats(
                avg_ms=sum(times) / count,
                min_ms=min(times),
                max_ms=max(times),
                p50_ms=sorted_times[int(count * 0.5)],
                p95_ms=sorted_times[int(count * 0.95)] if count >= 20 else max(times),
                p99_ms=sorted_times[int(count * 0.99)] if count >= 100 else max(times),
                count=count,
            )

        return result

    def analyze_patterns(self) -> list[ConversationPattern]:
        """
        分析对话模式

        Returns:
            对话模式列表
        """
        patterns: dict[tuple[str, str], dict] = defaultdict(
            lambda: {"requests": 0, "responses": 0, "latencies": [], "errors": 0}
        )

        requests = {m.id: m for m in self.messages if m.is_request()}

        for msg in self.messages:
            if msg.is_request():
                key = (msg.source, msg.target)
                patterns[key]["requests"] += 1

            elif msg.is_response():
                req_id = msg.metadata.get("request_id")
                if req_id and req_id in requests:
                    req = requests[req_id]
                    key = (req.source, req.target)
                    patterns[key]["responses"] += 1

                    if msg.get_latency_ms():
                        patterns[key]["latencies"].append(msg.get_latency_ms())

                    if msg.metadata.get("status", 200) >= 400:
                        patterns[key]["errors"] += 1

        result = []
        for (initiator, responder), data in patterns.items():
            avg_latency = (
                sum(data["latencies"]) / len(data["latencies"])
                if data["latencies"]
                else 0
            )

            result.append(ConversationPattern(
                initiator=initiator,
                responder=responder,
                request_count=data["requests"],
                response_count=data["responses"],
                avg_latency_ms=avg_latency,
                error_count=data["errors"],
            ))

        return sorted(result, key=lambda x: x.request_count, reverse=True)

    def detect_timeouts(self, threshold_ms: float = 5000) -> list[dict]:
        """
        检测超时请求

        Args:
            threshold_ms: 超时阈值 (毫秒)

        Returns:
            超时事件列表
        """
        timeouts = []

        for msg in self.messages:
            if not msg.is_response():
                continue

            latency = msg.get_latency_ms()
            if latency and latency > threshold_ms:
                timeouts.append({
                    "request_id": msg.metadata.get("request_id"),
                    "source": msg.source,
                    "target": msg.target,
                    "latency_ms": latency,
                    "threshold_ms": threshold_ms,
                    "timestamp": msg.timestamp.isoformat(),
                })

        return sorted(timeouts, key=lambda x: x["latency_ms"], reverse=True)

    def detect_error_patterns(self) -> dict[str, any]:
        """
        检测错误模式

        Returns:
            错误分析报告
        """
        error_counts: dict[int, int] = defaultdict(int)
        error_by_agent: dict[str, int] = defaultdict(int)
        error_timeline: list[dict] = []

        for msg in self.messages:
            status = msg.metadata.get("status", 200)
            if status >= 400:
                error_counts[status] += 1
                error_by_agent[msg.source] += 1
                error_timeline.append({
                    "timestamp": msg.timestamp,
                    "status": status,
                    "source": msg.source,
                    "target": msg.target,
                })

        # 检测错误突发
        burst_threshold = 5  # 5分钟内5个错误视为突发
        bursts = []

        if error_timeline:
            # 按时间排序
            sorted_errors = sorted(error_timeline, key=lambda x: x["timestamp"])

            window_start = sorted_errors[0]["timestamp"]
            window_errors = []

            for error in sorted_errors:
                if error["timestamp"] - window_start <= timedelta(minutes=5):
                    window_errors.append(error)
                else:
                    if len(window_errors) >= burst_threshold:
                        bursts.append({
                            "start": window_start.isoformat(),
                            "count": len(window_errors),
                            "errors": window_errors,
                        })
                    window_start = error["timestamp"]
                    window_errors = [error]

            # 检查最后一个窗口
            if len(window_errors) >= burst_threshold:
                bursts.append({
                    "start": window_start.isoformat(),
                    "count": len(window_errors),
                    "errors": window_errors,
                })

        return {
            "total_errors": sum(error_counts.values()),
            "error_counts_by_status": dict(error_counts),
            "error_counts_by_agent": dict(error_by_agent),
            "error_rate": sum(error_counts.values()) / max(len(self.messages), 1) * 100,
            "bursts": bursts,
        }

    def generate_diagnosis_report(self) -> DiagnosisReport:
        """
        生成诊断报告

        Returns:
            诊断报告对象
        """
        report = DiagnosisReport()

        # 1. 检查循环依赖
        cycles = self.detect_cycles()
        if cycles:
            report.add_issue(
                severity="warning",
                category="circular_dependency",
                description=f"Detected {len(cycles)} circular dependency cycles",
                affected_agents=list(set(agent for cycle in cycles for agent in cycle)),
            )

        # 2. 检查超时
        timeouts = self.detect_timeouts(threshold_ms=3000)
        if timeouts:
            report.add_issue(
                severity="error" if len(timeouts) > 5 else "warning",
                category="timeout",
                description=f"Detected {len(timeouts)} requests exceeding 3s latency",
            )

        # 3. 检查错误模式
        error_analysis = self.detect_error_patterns()
        if error_analysis["total_errors"] > 0:
            report.add_issue(
                severity="error" if error_analysis["error_rate"] > 10 else "warning",
                category="error_rate",
                description=f"Error rate: {error_analysis['error_rate']:.1f}% "
                           f"({error_analysis['total_errors']} errors)",
            )

        # 4. 检查孤立 Agent
        lonely = self.detect_lonely_agents()
        if lonely["isolated"]:
            report.add_issue(
                severity="info",
                category="isolated_agents",
                description=f"Found {len(lonely['isolated'])} isolated agents",
                affected_agents=lonely["isolated"],
            )

        # 5. 延迟分析
        latency_stats = self.latency_analysis()
        high_latency_agents = [
            agent for agent, stats in latency_stats.items()
            if stats.avg_ms > 1000
        ]
        if high_latency_agents:
            report.add_issue(
                severity="warning",
                category="high_latency",
                description=f"{len(high_latency_agents)} agents have avg latency > 1s",
                affected_agents=high_latency_agents,
            )

        # 生成建议
        if cycles:
            report.recommendations.append(
                "Review circular dependencies - consider refactoring communication patterns"
            )
        if timeouts:
            report.recommendations.append(
                "Consider implementing timeout handling or circuit breaker patterns"
            )
        if error_analysis["error_rate"] > 5:
            report.recommendations.append(
                "Investigate high error rate - check service health and logs"
            )

        # 生成摘要
        issue_count = len(report.issues)
        if issue_count == 0:
            report.summary = "No significant issues detected in conversation patterns"
        else:
            report.summary = f"Detected {issue_count} potential issues - see details below"

        return report

    def visualize_topology(self, figsize: tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        生成通信拓扑可视化

        Args:
            figsize: 图像尺寸

        Returns:
            matplotlib Figure 对象
        """
        if len(self.graph.nodes()) == 0:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No communication data",
                   ha="center", va="center", fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            return fig

        fig, ax = plt.subplots(figsize=figsize)

        # 使用 spring 布局
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)

        # 节点大小基于度数
        node_sizes = [
            1000 + self.graph.degree(node) * 500
            for node in self.graph.nodes()
        ]

        # 绘制节点
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_size=node_sizes,
            node_color="lightblue",
            edgecolors="darkblue",
            linewidths=2,
            ax=ax,
        )

        # 绘制标签
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_weight="bold",
            ax=ax,
        )

        # 边的颜色基于消息数量
        edge_colors = [
            "green" if d.get("count", 0) > 10 else "gray"
            for u, v, d in self.graph.edges(data=True)
        ]

        # 绘制边
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color=edge_colors,
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            node_size=node_sizes,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

        ax.set_title("Agent Communication Topology", fontsize=14, fontweight="bold")
        ax.axis("off")

        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="lightblue", edgecolor="darkblue", label="Agent"),
            plt.Line2D([0], [0], color="green", label="High traffic (>10 msgs)"),
            plt.Line2D([0], [0], color="gray", label="Normal traffic"),
        ]
        ax.legend(handles=legend_elements, loc="upper right")

        plt.tight_layout()
        return fig

    def get_centrality_metrics(self) -> dict[str, dict[str, float]]:
        """
        获取中心性指标

        Returns:
            Agent ID 到中心性指标的映射
        """
        if len(self.graph.nodes()) == 0:
            return {}

        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness_centrality = nx.betweenness_centrality(self.graph)
            closeness_centrality = nx.closeness_centrality(self.graph)

            return {
                node: {
                    "degree": degree_centrality.get(node, 0),
                    "betweenness": betweenness_centrality.get(node, 0),
                    "closeness": closeness_centrality.get(node, 0),
                }
                for node in self.graph.nodes()
            }
        except Exception:
            return {}
