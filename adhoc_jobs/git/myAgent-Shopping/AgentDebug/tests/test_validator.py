"""
A2AMessageValidator 单元测试
"""

import pytest
from a2a_debugger.analyzer.validator import (
    A2AMessageValidator,
    ValidationResult,
    ValidationSeverity,
)
from a2a_debugger.models.message import A2AMessage


class TestValidationResult:
    """测试验证结果类"""

    def test_initial_valid(self):
        """测试初始状态为有效"""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_add_error(self):
        """测试添加错误会使结果无效"""
        result = ValidationResult(is_valid=True)
        result.add_issue("TEST", "Test error", ValidationSeverity.ERROR)
        assert result.is_valid is False
        assert len(result.issues) == 1

    def test_add_warning(self):
        """测试添加警告不会使结果无效"""
        result = ValidationResult(is_valid=True)
        result.add_issue("TEST", "Test warning", ValidationSeverity.WARNING)
        assert result.is_valid is True
        assert len(result.get_warnings()) == 1

    def test_get_errors(self):
        """测试获取错误列表"""
        result = ValidationResult(is_valid=True)
        result.add_issue("E1", "Error 1", ValidationSeverity.ERROR)
        result.add_issue("W1", "Warning 1", ValidationSeverity.WARNING)
        result.add_issue("E2", "Error 2", ValidationSeverity.ERROR)

        errors = result.get_errors()
        assert len(errors) == 2


class TestA2AMessageValidator:
    """测试消息验证器"""

    @pytest.fixture
    def validator(self):
        return A2AMessageValidator()

    @pytest.fixture
    def valid_request(self):
        return A2AMessage(
            message_type="request",
            payload={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "test"},
                "id": 1,
            },
            headers={"X-Agent-ID": "agent-a", "Content-Type": "application/json"},
        )

    @pytest.fixture
    def valid_response(self):
        return A2AMessage(
            message_type="response",
            payload={
                "jsonrpc": "2.0",
                "result": {"data": "success"},
                "id": 1,
            },
            headers={"X-Agent-ID": "agent-b", "Content-Type": "application/json"},
        )

    def test_valid_request(self, validator, valid_request):
        """测试有效请求"""
        result = validator.validate(valid_request)
        assert result.is_valid is True
        assert len(result.get_errors()) == 0

    def test_valid_response(self, validator, valid_response):
        """测试有效响应"""
        result = validator.validate(valid_response)
        assert result.is_valid is True

    def test_missing_jsonrpc(self, validator):
        """测试缺少 jsonrpc 字段"""
        msg = A2AMessage(
            message_type="request",
            payload={"method": "test", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "MISSING_JSONRPC" for i in result.issues)

    def test_unsupported_jsonrpc_version(self, validator):
        """测试不支持的 JSON-RPC 版本"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "1.0", "method": "test", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "UNSUPPORTED_JSONRPC" for i in result.issues)

    def test_invalid_id_type(self, validator):
        """测试无效的 ID 类型"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "method": "test", "id": {"bad": "id"}},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "INVALID_ID_TYPE" for i in result.issues)

    def test_missing_method(self, validator):
        """测试缺少 method 字段"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "MISSING_METHOD" for i in result.issues)

    def test_empty_method(self, validator):
        """测试空 method 字段"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "method": "   ", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "EMPTY_METHOD" for i in result.issues)

    def test_invalid_params_type(self, validator):
        """测试无效的 params 类型"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "method": "test", "params": "string", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "INVALID_PARAMS_TYPE" for i in result.issues)

    def test_missing_result_and_error(self, validator):
        """测试响应缺少 result 和 error"""
        msg = A2AMessage(
            message_type="response",
            payload={"jsonrpc": "2.0", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "MISSING_RESULT_OR_ERROR" for i in result.issues)

    def test_both_result_and_error(self, validator):
        """测试响应同时有 result 和 error"""
        msg = A2AMessage(
            message_type="response",
            payload={"jsonrpc": "2.0", "result": "ok", "error": {"code": -1}, "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "BOTH_RESULT_AND_ERROR" for i in result.issues)

    def test_invalid_error_format(self, validator):
        """测试无效的错误格式"""
        msg = A2AMessage(
            message_type="response",
            payload={"jsonrpc": "2.0", "error": "just a string", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "INVALID_ERROR_TYPE" for i in result.issues)

    def test_missing_error_code(self, validator):
        """测试错误缺少 code 字段"""
        msg = A2AMessage(
            message_type="response",
            payload={"jsonrpc": "2.0", "error": {"message": "Oops"}, "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "MISSING_ERROR_CODE" for i in result.issues)

    def test_missing_error_message(self, validator):
        """测试错误缺少 message 字段"""
        msg = A2AMessage(
            message_type="response",
            payload={"jsonrpc": "2.0", "error": {"code": -32600}, "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "MISSING_ERROR_MESSAGE" for i in result.issues)

    def test_missing_agent_id_header_warning(self, validator):
        """测试缺少 X-Agent-ID 头产生警告"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "method": "test", "id": 1},
            headers={},  # 缺少 X-Agent-ID
        )
        result = validator.validate(msg)
        # 不是错误，只是警告
        assert result.is_valid is True
        assert any(i.code == "MISSING_AGENT_ID_HEADER" for i in result.get_warnings())

    def test_invalid_content_type(self, validator):
        """测试无效 Content-Type"""
        msg = A2AMessage(
            message_type="request",
            payload={"jsonrpc": "2.0", "method": "test", "id": 1},
            headers={"X-Agent-ID": "agent", "Content-Type": "text/plain"},
        )
        result = validator.validate(msg)
        assert any(i.code == "INVALID_CONTENT_TYPE" for i in result.get_warnings())

    def test_notification_valid(self, validator):
        """测试有效 Notification"""
        msg = A2AMessage(
            message_type="notification",
            payload={"jsonrpc": "2.0", "method": "notify"},  # 无 id
            headers={"X-Agent-ID": "agent"},
        )
        result = validator.validate(msg)
        # notification 不需要 id
        assert result.is_valid is True

    def test_strict_mode_extra_fields(self, validator):
        """测试严格模式检测额外字段"""
        strict_validator = A2AMessageValidator(strict=True)
        msg = A2AMessage(
            message_type="request",
            payload={
                "jsonrpc": "2.0",
                "method": "test",
                "id": 1,
                "extra_field": "should not be here",
            },
            headers={"X-Agent-ID": "agent"},
        )
        result = strict_validator.validate(msg)
        assert any(i.code == "EXTRA_FIELDS" for i in result.issues)

    def test_batch_validation(self, validator):
        """测试批量验证"""
        messages = [
            A2AMessage(message_type="request", payload={"jsonrpc": "2.0", "method": "m1", "id": 1}),
            A2AMessage(message_type="request", payload={"method": "m2", "id": 2}),  # 无效
        ]
        results = validator.validate_batch(messages)
        assert len(results) == 2
        assert results[messages[0].id].is_valid is True
        assert results[messages[1].id].is_valid is False

    def test_custom_rule(self, validator):
        """测试自定义验证规则"""
        def custom_rule(msg, result):
            if msg.source == "banned-agent":
                result.add_issue("BANNED", "Banned agent", ValidationSeverity.ERROR)

        validator.add_rule(custom_rule)

        msg = A2AMessage(
            message_type="request",
            source="banned-agent",
            payload={"jsonrpc": "2.0", "method": "test", "id": 1},
        )
        result = validator.validate(msg)
        assert result.is_valid is False
        assert any(i.code == "BANNED" for i in result.issues)

    def test_valid_notification_no_id(self, validator):
        """测试 Notification 无 id 是有效的"""
        msg = A2AMessage(
            message_type="notification",
            payload={"jsonrpc": "2.0", "method": "update"},
            headers={"X-Agent-ID": "agent"},
        )
        result = validator.validate(msg)
        assert result.is_valid is True
