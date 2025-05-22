import os
import logging
import logging.config
from datetime import datetime
import sys

# 로그 디렉토리 설정
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 현재 날짜 기반 로그 파일명
today = datetime.now().strftime('%Y-%m-%d')
GENERAL_LOG = os.path.join(LOG_DIR, f'tripmind-{today}.log')
ERROR_LOG = os.path.join(LOG_DIR, f'tripmind-error-{today}.log')
LLM_LOG = os.path.join(LOG_DIR, f'tripmind-llm-{today}.log')
GUARD_LOG = os.path.join(LOG_DIR, f'tripmind-guard-{today}.log')

class LLMResponseFilter(logging.Filter):
    """LLM 응답만 필터링하는 로그 필터"""
    def filter(self, record):
        return hasattr(record, 'llm_response') and record.llm_response is True

class GuardrailsFilter(logging.Filter):
    """가드레일 동작만 필터링하는 로그 필터"""
    def filter(self, record):
        return hasattr(record, 'guardrails') and record.guardrails is True

class RequestResponseAdapter(logging.LoggerAdapter):
    """세션 ID와 요청 ID를 로그에 추가하는 어댑터"""
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        
        # 세션 ID와 요청 ID가 있으면 포함
        session_id = getattr(self.extra, 'session_id', None)
        request_id = getattr(self.extra, 'request_id', None)
        
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
    """LLM 응답 로깅 헬퍼 함수"""
    extra = {'llm_response': True}
    if metadata is not None:
        extra.update(metadata)
    
    # 길이에 따라 응답 요약
    if len(response) > 1000:
        summary = f"{response[:500]}...{response[-500:]}"
        logger.info(f"LLM 응답 (길이: {len(response)}): {summary}", extra=extra)
    else:
        logger.info(f"LLM 응답: {response}", extra=extra)

def log_guardrail_action(logger, action, details, original=None, modified=None):
    """가드레일 동작 로깅 헬퍼 함수"""
    extra = {'guardrails': True}
    
    if original and modified:
        if len(original) > 200:
            original = f"{original[:100]}...{original[-100:]}"
        if len(modified) > 200:
            modified = f"{modified[:100]}...{modified[-100:]}"
        logger.info(
            f"가드레일 {action}: {details}\n"
            f"원본: {original}\n"
            f"수정: {modified}",
            extra=extra
        )
    else:
        logger.info(f"가드레일 {action}: {details}", extra=extra)

# 로깅 설정
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
        'llm': {
            'format': '%(asctime)s [LLM] %(message)s'
        },
        'guard': {
            'format': '%(asctime)s [GUARD] %(message)s'
        }
    },
    'filters': {
        'llm_response_filter': {
            '()': LLMResponseFilter
        },
        'guardrails_filter': {
            '()': GuardrailsFilter
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': sys.stdout
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': GENERAL_LOG,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'verbose',
            'filename': ERROR_LOG,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        },
        'llm_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'llm',
            'filename': LLM_LOG,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'filters': ['llm_response_filter']
        },
        'guard_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'guard',
            'filename': GUARD_LOG,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'filters': ['guardrails_filter']
        }
    },
    'loggers': {
        '': {  # 루트 로거
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True
        },
        'tripmind': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'tripmind.llm': {
            'handlers': ['console', 'llm_file', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'tripmind.utils.guardrails': {
            'handlers': ['console', 'guard_file', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'tripmind.agents.nodes': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

def configure_logging():
    """로깅 설정 적용"""
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.config.dictConfig(logging_config)
    
    # 설정 로그 출력
    logger = logging.getLogger('tripmind')
    logger.info(f"로깅 설정 완료: 로그 디렉토리 = {LOG_DIR}")

def get_logger(name):
    """지정된 이름으로 로거 생성"""
    return logging.getLogger(name)

def get_request_logger(name, session_id=None, request_id=None):
    """요청/세션 정보가 포함된 로거 생성"""
    logger = logging.getLogger(name)
    
    # 어댑터에 세션 ID와 요청 ID 추가
    extra = {}
    if session_id:
        extra['session_id'] = session_id
    if request_id:
        extra['request_id'] = request_id
        
    return RequestResponseAdapter(logger, extra)

# 로깅 설정 자동 적용
configure_logging() 