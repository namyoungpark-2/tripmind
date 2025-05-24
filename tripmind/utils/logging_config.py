import os
import logging
import logging.config
from datetime import datetime
import sys

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
GENERAL_LOG = os.path.join(LOG_DIR, f"tripmind-{today}.log")
ERROR_LOG = os.path.join(LOG_DIR, f"tripmind-error-{today}.log")
LLM_LOG = os.path.join(LOG_DIR, f"tripmind-llm-{today}.log")
GUARD_LOG = os.path.join(LOG_DIR, f"tripmind-guard-{today}.log")


class LLMResponseFilter(logging.Filter):
    def filter(self, record):
        return hasattr(record, "llm_response") and record.llm_response is True


class GuardrailsFilter(logging.Filter):
    def filter(self, record):
        return hasattr(record, "guardrails") and record.guardrails is True


class RequestResponseAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault("extra", {})

        session_id = getattr(self.extra, "session_id", None)
        request_id = getattr(self.extra, "request_id", None)

        prefix = []
        if session_id:
            prefix.append(f"session={session_id}")
        if request_id:
            prefix.append(f"req={request_id}")

        prefix_str = " ".join(prefix)
        if prefix_str:
            msg = f"[{prefix_str}] {msg}"

        return msg, kwargs


def log_llm_response(logger, response, metadata=None):
    extra = {"llm_response": True}
    if metadata is not None:
        extra.update(metadata)

    if len(response) > 1000:
        summary = f"{response[:500]}...{response[-500:]}"
        logger.info(f"LLM 응답 (길이: {len(response)}): {summary}", extra=extra)
    else:
        logger.info(f"LLM 응답: {response}", extra=extra)


def log_guardrail_action(logger, action, details, original=None, modified=None):
    extra = {"guardrails": True}

    if original and modified:
        if len(original) > 200:
            original = f"{original[:100]}...{original[-100:]}"
        if len(modified) > 200:
            modified = f"{modified[:100]}...{modified[-100:]}"
        logger.info(
            f"가드레일 {action}: {details}\n" f"원본: {original}\n" f"수정: {modified}",
            extra=extra,
        )
    else:
        logger.info(f"가드레일 {action}: {details}", extra=extra)


# 로깅 설정
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        },
        "simple": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
        "llm": {"format": "%(asctime)s [LLM] %(message)s"},
        "guard": {"format": "%(asctime)s [GUARD] %(message)s"},
    },
    "filters": {
        "llm_response_filter": {"()": LLMResponseFilter},
        "guardrails_filter": {"()": GuardrailsFilter},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "filename": GENERAL_LOG,
            "maxBytes": 10485760,
            "backupCount": 10,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "verbose",
            "filename": ERROR_LOG,
            "maxBytes": 10485760,
            "backupCount": 10,
        },
        "llm_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "llm",
            "filename": LLM_LOG,
            "maxBytes": 10485760,
            "backupCount": 10,
            "filters": ["llm_response_filter"],
        },
        "guard_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "guard",
            "filename": GUARD_LOG,
            "maxBytes": 10485760,
            "backupCount": 10,
            "filters": ["guardrails_filter"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "tripmind": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tripmind.llm": {
            "handlers": ["console", "llm_file", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tripmind.utils.guardrails": {
            "handlers": ["console", "guard_file", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tripmind.agents.nodes": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def configure_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger("tripmind")
    logger.info(f"로깅 설정 완료: 로그 디렉토리 = {LOG_DIR}")


def get_logger(name):
    return logging.getLogger(name)


def get_request_logger(name, session_id=None, request_id=None):
    logger = logging.getLogger(name)

    extra = {}
    if session_id:
        extra["session_id"] = session_id
    if request_id:
        extra["request_id"] = request_id

    return RequestResponseAdapter(logger, extra)


# 로깅 설정 자동 적용
configure_logging()
