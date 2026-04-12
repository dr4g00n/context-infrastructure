# 次日行动清单 2026-04-08

## 目标
明天优先完成测试 - 补充缺失的测试覆盖，提升测试质量和可靠性

## 当前测试状态
- **总计**: 72 个测试全部通过
- **test_message.py**: 22 个测试 (A2AMessage + MessageStore)
- **test_proxy.py**: 11 个测试 (A2ADebugProxy)
- **test_validator.py**: 24 个测试 (A2AMessageValidator)
- **test_analyzer.py**: 15 个测试 (ConversationAnalyzer)

## 行动清单

### P0 - 高优先级 (必须完成)

1. [ ] **补充 Web Dashboard 测试** - 创建 `tests/test_dashboard.py`
   - 当前 dashboard.py 完全没有测试覆盖
   - 测试关键函数: `render_sidebar`, `render_header`, `render_message_flow`, `render_statistics`
   - 使用 mock 测试 Streamlit 组件调用

2. [ ] **补充 CLI 测试** - 创建 `tests/test_cli.py`
   - 当前 cli.py 完全没有测试覆盖
   - 测试参数解析逻辑
   - 测试日志配置
   - 使用 pytest 的 `capsys` 和 `monkeypatch` 测试命令行输出

3. [ ] **补充 MessageStore 边界测试**
   - `filter_by_target` 方法未测试 (代码位置: `src/a2a_debugger/models/message.py:194`)
   - `filter_by_time_range` 方法未测试 (代码位置: `src/a2a_debugger/models/message.py:202`)
   - 测试空存储、单条消息、边界时间范围

### P1 - 中优先级 (建议完成)

4. [ ] **补充 Proxy 上下文管理器测试**
   - 测试 `__aenter__` 和 `__aexit__` (代码位置: `src/a2a_debugger/proxy/debug_proxy.py:305-312`)
   - 验证资源正确释放

5. [ ] **补充 Validator 边界测试**
   - 测试 `_validate_method_name` 的警告场景 (代码位置: `src/a2a_debugger/analyzer/validator.py:243-261`)
   - 测试 `_validate_error_format` 的 data 字段验证 (代码位置: `src/a2a_debugger/analyzer/validator.py:309-316`)
   - 测试 `_validate_strict_rules` 的 SHORT_ID 检测 (代码位置: `src/a2a_debugger/analyzer/validator.py:354-362`)

6. [ ] **补充 Analyzer 边界测试**
   - 测试 `visualize_topology` 非空数据场景 (代码位置: `src/a2a_debugger/analyzer/conversation.py:426-505`)
   - 测试 `get_centrality_metrics` 异常处理 (代码位置: `src/a2a_debugger/analyzer/conversation.py:507-531`)

### P2 - 低优先级 (可选)

7. [ ] **添加集成测试**
   - 端到端测试: CLI 启动代理 -> 发送消息 -> 验证存储
   - 多 Agent 并发通信场景

8. [ ] **添加性能测试**
   - MessageStore 大容量性能测试 (10000+ 消息)
   - Validator 批量验证性能测试

9. [ ] **添加覆盖率报告**
   - 配置 pytest-cov 生成 HTML 报告
   - 目标: 核心代码覆盖率 > 90%

## 代码指针

### 未测试的核心代码位置

| 文件 | 行号 | 函数/类 | 说明 |
|------|------|---------|------|
| `src/a2a_debugger/web/dashboard.py` | 1-404 | 全部 | **完全未测试** - Streamlit UI 组件 |
| `src/a2a_debugger/cli.py` | 1-114 | 全部 | **完全未测试** - CLI 入口 |
| `src/a2a_debugger/models/message.py` | 194-196 | `filter_by_target` | 按目标过滤消息 |
| `src/a2a_debugger/models/message.py` | 202-213 | `filter_by_time_range` | 按时间范围过滤 |
| `src/a2a_debugger/proxy/debug_proxy.py` | 305-312 | `__aenter__`, `__aexit__` | 异步上下文管理器 |
| `src/a2a_debugger/analyzer/validator.py` | 243-261 | `_validate_method_name` | 方法名格式验证 |
| `src/a2a_debugger/analyzer/validator.py` | 309-316 | `_validate_error_format` (data字段) | 错误 data 类型检查 |
| `src/a2a_debugger/analyzer/validator.py` | 354-362 | `_validate_strict_rules` (SHORT_ID) | 短 ID 警告 |
| `src/a2a_debugger/analyzer/conversation.py` | 445-505 | `visualize_topology` (非空分支) | 拓扑图可视化 |
| `src/a2a_debugger/analyzer/conversation.py` | 530-531 | `get_centrality_metrics` (异常分支) | 异常处理 |

### 关键测试参考位置

| 文件 | 行号 | 说明 |
|------|------|------|
| `tests/test_message.py` | 1-237 | A2AMessage + MessageStore 测试模板 |
| `tests/test_proxy.py` | 1-267 | 异步测试 + Mock 使用示例 |
| `tests/test_validator.py` | 1-287 | 验证器测试模式 |
| `tests/test_analyzer.py` | 1-289 | 复杂数据结构测试示例 |

## 建议补充的测试

### 1. test_dashboard.py (新建)
```python
# 测试要点:
# - mock streamlit 组件 (st.title, st.metric, st.dataframe 等)
# - 测试 render_sidebar 返回值
# - 测试 render_header 的统计指标显示
# - 测试 render_message_flow 的消息格式化
# - 测试 render_statistics 的图表生成
```

### 2. test_cli.py (新建)
```python
# 测试要点:
# - 使用 argparse 测试参数解析
# - mock asyncio.run 避免实际启动代理
# - 测试 setup_logging 的日志级别设置
# - 测试主函数的异常处理
```

### 3. MessageStore 补充测试
```python
# 添加到 tests/test_message.py:
# - test_filter_by_target: 测试按目标过滤
# - test_filter_by_time_range: 测试时间范围过滤
# - test_filter_by_time_range_empty: 测试空结果
```

### 4. Proxy 上下文管理器测试
```python
# 添加到 tests/test_proxy.py:
# - test_async_context_manager: 测试 async with 语法
# - test_context_manager_exception: 测试异常时资源释放
```

## 测试执行命令

```bash
# 运行所有测试
source .venv/bin/activate && python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_dashboard.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src/a2a_debugger --cov-report=html

# 运行特定标记的测试
python -m pytest tests/ -v -k "not integration"  # 跳过集成测试
```

## 关键实施文件

- `tests/test_dashboard.py` (新建 - 最高优先级)
- `tests/test_cli.py` (新建 - 最高优先级)
- `tests/test_message.py` (补充 - 添加 filter_by_target 和 filter_by_time_range 测试)
- `tests/test_proxy.py` (补充 - 添加上下文管理器测试)
- `pyproject.toml` (配置 - 添加 pytest-cov 配置)
