"""테스트 설정 파일"""

import os
import django
from django.conf import settings


# 테스트 전에 Django 설정 구성
def setup_django():
    # Django 설정 모듈 지정
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tripmind.settings")

    # Django 설정 로드
    django.setup()

    # 테스트시 필요한 추가 설정
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",  # 메모리 DB 사용
        }
    }

    # 로깅 설정 간소화
    settings.LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }

    # 기타 테스트 환경 설정
    settings.DEBUG = False
    settings.LANGUAGE_CODE = "ko-kr"
    settings.TIME_ZONE = "Asia/Seoul"

    return settings
