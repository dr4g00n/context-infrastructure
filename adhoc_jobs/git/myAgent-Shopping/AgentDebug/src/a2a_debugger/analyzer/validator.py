"""
A2A 协议验证器

验证消息是否符合 JSON-RPC 2.0 和 A2A 协议规范。
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum

from a2a_debugger.models.message import A2AMessage


class ValidationSeverity(str, Enum):
    """验证严重程度"""
    ERROR = "error"       # 严重违规，可能导致通信失败
    WARNING = "warning"   # 规范建议，不影响功能
    INFO = "info"         # 信息提示


@dataclass
class ValidationIssue:
    """验证问题"""
    code: str                    # 问题代码
    message: str                 # 问题描述
    severity: ValidationSeverity
    field: Optional[str] = None  # 相关字段


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        field: Optional[str] = None,
    ) -> None:
        """添加验证问题"""
        self.issues.append(ValidationIssue(code, message, severity, field))
        if severity == ValidationSeverity.ERROR:
            self.is_valid = False

    def get_errors(self) -> list[ValidationIssue]:
        """获取所有错误"""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    def get_warnings(self) -> list[ValidationIssue]:
        """获取所有警告"""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


ValidationRule = Callable[[A2AMessage, ValidationResult], None]


class A2AMessageValidator:
    """
    A2A 消息验证器

    验证消息是否符合 JSON-RPC 2.0 和 A2A 协议规范。
    支持自定义验证规则。
    """

    # JSON-RPC 2.0 预定义错误码
    JSONRPC_ERRORS = {
        -32700: "Parse error",
        -32600: "Invalid Request",
        -32601: "Method not found",
        -32602: "Invalid params",
        -32603: "Internal error",
    }

    def __init__(self, strict: bool = False):
        """
        初始化验证器

        Args:
            strict: 是否启用严格模式 (更多警告)
        """
        self.strict = strict
        self._custom_rules: list[ValidationRule] = []

    def validate(self, message: A2AMessage) -> ValidationResult:
        """
        验证单个消息

        Args:
            message: 待验证的消息

        Returns:
            ValidationResult 包含验证结果和所有问题
        """
        result = ValidationResult(is_valid=True)

        # 运行内置验证规则
        self._validate_jsonrpc_version(message, result)
        self._validate_message_id(message, result)
        self._validate_request_structure(message, result)
        self._validate_response_structure(message, result)
        self._validate_method_name(message, result)
        self._validate_error_format(message, result)
        self._validate_headers(message, result)

        if self.strict:
            self._validate_strict_rules(message, result)

        # 运行自定义规则
        for rule in self._custom_rules:
            rule(message, result)

        return result

    def validate_batch(self, messages: list[A2AMessage]) -> dict[str, ValidationResult]:
        """
        批量验证消息

        Args:
            messages: 消息列表

        Returns:
            消息 ID 到验证结果的映射
        """
        return {msg.id: self.validate(msg) for msg in messages}

    def add_rule(self, rule: ValidationRule) -> None:
        """
        添加自定义验证规则

        Args:
            rule: 验证函数，接收 (A2AMessage, ValidationResult) 参数
        """
        self._custom_rules.append(rule)

    def _validate_jsonrpc_version(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证 JSON-RPC 版本"""
        version = msg.payload.get("jsonrpc")

        if version is None:
            result.add_issue(
                code="MISSING_JSONRPC",
                message="Missing 'jsonrpc' field",
                severity=ValidationSeverity.ERROR,
                field="jsonrpc",
            )
        elif version != "2.0":
            result.add_issue(
                code="UNSUPPORTED_JSONRPC",
                message=f"Unsupported JSON-RPC version: {version}, expected '2.0'",
                severity=ValidationSeverity.ERROR,
                field="jsonrpc",
            )

    def _validate_message_id(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证消息 ID"""
        msg_id = msg.payload.get("id")

        if msg_id is None:
            # Notification 可以没有 id
            if msg.is_request():
                # 这是 notification，不是错误
                pass
            return

        # id 必须是 string, number, 或 null
        if not isinstance(msg_id, (str, int, float)):
            result.add_issue(
                code="INVALID_ID_TYPE",
                message=f"Invalid 'id' type: {type(msg_id).__name__}",
                severity=ValidationSeverity.ERROR,
                field="id",
            )

    def _validate_request_structure(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证请求结构"""
        if not msg.is_request():
            return

        # 请求必须包含 method
        if "method" not in msg.payload:
            result.add_issue(
                code="MISSING_METHOD",
                message="Request missing 'method' field",
                severity=ValidationSeverity.ERROR,
                field="method",
            )
            return

        method = msg.payload["method"]
        if not isinstance(method, str):
            result.add_issue(
                code="INVALID_METHOD_TYPE",
                message=f"'method' must be string, got {type(method).__name__}",
                severity=ValidationSeverity.ERROR,
                field="method",
            )
        elif not method.strip():
            result.add_issue(
                code="EMPTY_METHOD",
                message="'method' cannot be empty",
                severity=ValidationSeverity.ERROR,
                field="method",
            )

        # 检查 params (可选，但如果存在必须是 object 或 array)
        params = msg.payload.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            result.add_issue(
                code="INVALID_PARAMS_TYPE",
                message=f"'params' must be object or array, got {type(params).__name__}",
                severity=ValidationSeverity.ERROR,
                field="params",
            )

    def _validate_response_structure(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证响应结构"""
        if not msg.is_response():
            return

        has_result = "result" in msg.payload
        has_error = "error" in msg.payload

        # 响应必须有 result 或 error 之一
        if not has_result and not has_error:
            result.add_issue(
                code="MISSING_RESULT_OR_ERROR",
                message="Response must contain either 'result' or 'error'",
                severity=ValidationSeverity.ERROR,
            )
            return

        # 但不能同时有
        if has_result and has_error:
            result.add_issue(
                code="BOTH_RESULT_AND_ERROR",
                message="Response cannot contain both 'result' and 'error'",
                severity=ValidationSeverity.ERROR,
            )

    def _validate_method_name(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证方法名格式 (A2A 特定)"""
        if not msg.is_request():
            return

        method = msg.payload.get("method", "")
        if not isinstance(method, str):
            return

        # A2A 方法名通常使用命名空间格式，如 "tools/call"
        if "/" in method:
            parts = method.split("/")
            if len(parts) != 2:
                result.add_issue(
                    code="INVALID_METHOD_FORMAT",
                    message=f"Method name '{method}' has invalid format",
                    severity=ValidationSeverity.WARNING,
                    field="method",
                )

    def _validate_error_format(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证错误对象格式"""
        error = msg.payload.get("error")
        if error is None:
            return

        if not isinstance(error, dict):
            result.add_issue(
                code="INVALID_ERROR_TYPE",
                message=f"'error' must be object, got {type(error).__name__}",
                severity=ValidationSeverity.ERROR,
                field="error",
            )
            return

        # 错误必须有 code 和 message
        if "code" not in error:
            result.add_issue(
                code="MISSING_ERROR_CODE",
                message="Error object missing 'code' field",
                severity=ValidationSeverity.ERROR,
                field="error.code",
            )
        elif not isinstance(error["code"], int):
            result.add_issue(
                code="INVALID_ERROR_CODE_TYPE",
                message=f"'error.code' must be integer, got {type(error['code']).__name__}",
                severity=ValidationSeverity.ERROR,
                field="error.code",
            )

        if "message" not in error:
            result.add_issue(
                code="MISSING_ERROR_MESSAGE",
                message="Error object missing 'message' field",
                severity=ValidationSeverity.ERROR,
                field="error.message",
            )
        elif not isinstance(error["message"], str):
            result.add_issue(
                code="INVALID_ERROR_MESSAGE_TYPE",
                message=f"'error.message' must be string, got {type(error['message']).__name__}",
                severity=ValidationSeverity.ERROR,
                field="error.message",
            )

        # 可选字段 data
        if "data" in error and not isinstance(error["data"], (dict, list, str, int, float, bool)):
            result.add_issue(
                code="INVALID_ERROR_DATA_TYPE",
                message="'error.data' has invalid type",
                severity=ValidationSeverity.WARNING,
                field="error.data",
            )

    def _validate_headers(self, msg: A2AMessage, result: ValidationResult) -> None:
        """验证 HTTP 头 (A2A 特定)"""
        # 检查 X-Agent-ID 头
        agent_id = msg.headers.get("X-Agent-ID")
        if agent_id is None:
            result.add_issue(
                code="MISSING_AGENT_ID_HEADER",
                message="Missing 'X-Agent-ID' header",
                severity=ValidationSeverity.WARNING,
                field="headers.X-Agent-ID",
            )

        # Content-Type 检查
        content_type = msg.headers.get("Content-Type", "")
        if content_type and "application/json" not in content_type:
            result.add_issue(
                code="INVALID_CONTENT_TYPE",
                message=f"Expected 'application/json' Content-Type, got '{content_type}'",
                severity=ValidationSeverity.WARNING,
                field="headers.Content-Type",
            )

    def _validate_strict_rules(self, msg: A2AMessage, result: ValidationResult) -> None:
        """严格模式额外检查"""
        # 检查 payload 是否有额外字段
        standard_fields = {"jsonrpc", "method", "params", "id", "result", "error"}
        extra_fields = set(msg.payload.keys()) - standard_fields - {"_raw"}

        if extra_fields:
            result.add_issue(
                code="EXTRA_FIELDS",
                message=f"Payload contains non-standard fields: {extra_fields}",
                severity=ValidationSeverity.INFO,
            )

        # 检查响应是否有对应的请求 ID 格式
        if msg.is_response() and "id" in msg.payload:
            msg_id = msg.payload["id"]
            if isinstance(msg_id, str) and len(msg_id) < 4:
                result.add_issue(
                    code="SHORT_ID",
                    message="Response ID is suspiciously short",
                    severity=ValidationSeverity.INFO,
                    field="id",
                )
