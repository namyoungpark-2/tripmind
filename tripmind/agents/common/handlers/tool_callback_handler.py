from langchain.callbacks.base import BaseCallbackHandler
import logging


class ToolUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tool_usage = []
        self.logger = logging.getLogger("tool_usage")

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "unknown_tool")
        self.logger.info(f"도구 시작: {tool_name}, 입력: {input_str}")
        self.tool_usage.append(
            {"tool": tool_name, "input": input_str, "output": None, "status": "started"}
        )

    def on_tool_end(self, output, **kwargs):
        if self.tool_usage:
            self.tool_usage[-1]["output"] = output
            self.tool_usage[-1]["status"] = "completed"
            self.logger.info(f"도구 완료: 출력: {output}")

    def on_tool_error(self, error, **kwargs):
        if self.tool_usage:
            self.tool_usage[-1]["error"] = str(error)
            self.tool_usage[-1]["status"] = "error"
            self.logger.error(f"도구 오류: {error}")

    def get_tool_usage(self):
        return self.tool_usage
