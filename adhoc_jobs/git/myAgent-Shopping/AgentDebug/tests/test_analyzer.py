"""
ConversationAnalyzer 单元测试
"""

import pytest
from datetime import datetime, timedelta

from a2a_debugger.analyzer.conversation import (
    ConversationAnalyzer,
    LatencyStats,
    DiagnosisReport,
)
from a2a_debugger.models.message import A2AMessage


class TestConversationAnalyzer:
    """测试对话分析器"""

    @pytest.fixture
    def sample_messages(self):
        """创建测试消息样本"""
        base_time = datetime.now()

        return [
            # Agent A -> Agent B 请求
            A2AMessage(
                id="req-1",
                source="agent-a",
                target="agent-b",
                message_type="request",
                payload={"jsonrpc": "2.0", "method": "test", "id": 1},
                timestamp=base_time,
            ),
            # Agent B -> Agent A 响应 (100ms 延迟)
            A2AMessage(
                id="resp-1",
                source="agent-b",
                target="agent-a",
                message_type="response",
                payload={"jsonrpc": "2.0", "result": "ok", "id": 1},
                metadata={"request_id": "req-1", "status": 200, "latency_ms": 100},
                timestamp=base_time + timedelta(milliseconds=100),
            ),
            # Agent A -> Agent C 请求
            A2AMessage(
                id="req-2",
                source="agent-a",
                target="agent-c",
                message_type="request",
                payload={"jsonrpc": "2.0", "method": "test", "id": 2},
                timestamp=base_time + timedelta(seconds=1),
            ),
            # Agent C -> Agent A 响应 (200ms 延迟)
            A2AMessage(
                id="resp-2",
                source="agent-c",
                target="agent-a",
                message_type="response",
                payload={"jsonrpc": "2.0", "result": "ok", "id": 2},
                metadata={"request_id": "req-2", "status": 200, "latency_ms": 200},
                timestamp=base_time + timedelta(seconds=1, milliseconds=200),
            ),
            # Agent C -> Agent B 通知
            A2AMessage(
                id="notif-1",
                source="agent-c",
                target="agent-b",
                message_type="notification",
                payload={"jsonrpc": "2.0", "method": "notify"},
                timestamp=base_time + timedelta(seconds=2),
            ),
        ]

    def test_build_graph(self, sample_messages):
        """测试图构建"""
        analyzer = ConversationAnalyzer(sample_messages)

        assert len(analyzer.graph.nodes()) == 3  # 3 个 agent
        assert "agent-a" in analyzer.graph.nodes()
        assert "agent-b" in analyzer.graph.nodes()
        assert "agent-c" in analyzer.graph.nodes()

    def test_detect_no_cycles(self):
        """测试无循环依赖"""
        # 单向通信，无循环
        messages = [
            A2AMessage(source="a", target="b", message_type="request"),
            A2AMessage(source="a", target="c", message_type="request"),
        ]
        analyzer = ConversationAnalyzer(messages)
        cycles = analyzer.detect_cycles()
        assert len(cycles) == 0

    def test_detect_cycles(self):
        """测试检测循环依赖"""
        # 创建循环: A -> B -> C -> A
        messages = [
            A2AMessage(source="a", target="b", message_type="request"),
            A2AMessage(source="b", target="c", message_type="request"),
            A2AMessage(source="c", target="a", message_type="request"),
        ]

        analyzer = ConversationAnalyzer(messages)
        cycles = analyzer.detect_cycles()
        assert len(cycles) > 0
        # 检查是否检测到 a -> b -> c -> a 循环
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)
        assert {"a", "b", "c"}.issubset(cycle_nodes)

    def test_detect_lonely_agents(self):
        """测试检测孤立 Agent"""
        messages = [
            A2AMessage(source="active", target="target", message_type="request"),
            A2AMessage(source="only-source", target="x", message_type="request"),
            A2AMessage(id="orphan"),
        ]

        analyzer = ConversationAnalyzer(messages)
        lonely = analyzer.detect_lonely_agents()

        assert "only-source" in lonely["only_source"]
        assert "target" in lonely["only_target"]

    def test_latency_analysis(self, sample_messages):
        """测试延迟分析"""
        analyzer = ConversationAnalyzer(sample_messages)
        stats = analyzer.latency_analysis()

        assert "agent-a" in stats
        assert stats["agent-a"].count == 2
        assert stats["agent-a"].avg_ms == 150  # (100 + 200) / 2
        assert stats["agent-a"].min_ms == 100
        assert stats["agent-a"].max_ms == 200

    def test_analyze_patterns(self, sample_messages):
        """测试对话模式分析"""
        analyzer = ConversationAnalyzer(sample_messages)
        patterns = analyzer.analyze_patterns()

        assert len(patterns) > 0

        # 查找 A -> B 模式
        ab_pattern = next((p for p in patterns if p.initiator == "agent-a" and p.responder == "agent-b"), None)
        assert ab_pattern is not None
        assert ab_pattern.request_count == 1
        assert ab_pattern.response_count == 1

    def test_detect_timeouts(self):
        """测试超时检测"""
        messages = [
            A2AMessage(
                id="req-slow",
                source="agent-a",
                target="agent-b",
                message_type="request",
            ),
            A2AMessage(
                id="resp-slow",
                source="agent-b",
                target="agent-a",
                message_type="response",
                metadata={"request_id": "req-slow", "latency_ms": 5000},
            ),
        ]

        analyzer = ConversationAnalyzer(messages)
        timeouts = analyzer.detect_timeouts(threshold_ms=3000)

        assert len(timeouts) == 1
        assert timeouts[0]["latency_ms"] == 5000

    def test_detect_error_patterns(self):
        """测试错误模式检测"""
        messages = [
            A2AMessage(
                message_type="response",
                metadata={"status": 500},
                source="agent-a",
                timestamp=datetime.now(),
            ),
            A2AMessage(
                message_type="response",
                metadata={"status": 404},
                source="agent-b",
                timestamp=datetime.now(),
            ),
        ]

        analyzer = ConversationAnalyzer(messages)
        errors = analyzer.detect_error_patterns()

        assert errors["total_errors"] == 2
        assert errors["error_counts_by_status"][500] == 1
        assert errors["error_counts_by_status"][404] == 1

    def test_generate_diagnosis_report(self, sample_messages):
        """测试诊断报告生成"""
        analyzer = ConversationAnalyzer(sample_messages)
        report = analyzer.generate_diagnosis_report()

        assert report.timestamp is not None
        assert report.summary is not None
        # 样本数据没有问题，应该没有严重问题
        assert len(report.issues) == 0 or all(i["severity"] != "error" for i in report.issues)

    def test_generate_diagnosis_report_with_issues(self):
        """测试有问题的诊断报告"""
        messages = [
            A2AMessage(
                id="req-1",
                source="a",
                target="b",
                message_type="request",
            ),
            A2AMessage(
                id="resp-1",
                source="b",
                target="a",
                message_type="response",
                metadata={"request_id": "req-1", "status": 500, "latency_ms": 5000},
            ),
        ]

        analyzer = ConversationAnalyzer(messages)
        report = analyzer.generate_diagnosis_report()

        # 应该有错误 (高延迟和错误状态)
        assert len(report.issues) >= 1

    def test_visualize_topology_empty(self):
        """测试空数据拓扑图"""
        analyzer = ConversationAnalyzer([])
        fig = analyzer.visualize_topology()

        assert fig is not None

    def test_centrality_metrics(self, sample_messages):
        """测试中心性指标"""
        analyzer = ConversationAnalyzer(sample_messages)
        metrics = analyzer.get_centrality_metrics()

        assert "agent-a" in metrics
        assert "degree" in metrics["agent-a"]
        assert "betweenness" in metrics["agent-a"]


class TestLatencyStats:
    """测试延迟统计"""

    def test_latency_stats_creation(self):
        """测试延迟统计创建"""
        stats = LatencyStats(
            avg_ms=100,
            min_ms=50,
            max_ms=200,
            p50_ms=95,
            p95_ms=180,
            p99_ms=195,
            count=100,
        )

        assert stats.avg_ms == 100
        assert stats.count == 100


class TestDiagnosisReport:
    """测试诊断报告"""

    def test_add_issue(self):
        """测试添加问题"""
        report = DiagnosisReport()
        report.add_issue(
            severity="error",
            category="timeout",
            description="Test issue",
            affected_agents=["agent-a"],
        )

        assert len(report.issues) == 1
        assert report.issues[0]["severity"] == "error"
        assert report.issues[0]["affected_agents"] == ["agent-a"]

    def test_empty_report(self):
        """测试空报告"""
        report = DiagnosisReport()
        assert len(report.issues) == 0
        assert len(report.recommendations) == 0
