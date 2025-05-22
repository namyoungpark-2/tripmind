#!/usr/bin/env python
# tripmind/tests/run_tests.py
"""모든 테스트를 실행하는 스크립트"""

import unittest
import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Django 설정 로드 (필요한 경우)
try:
    from tripmind.tests.test_settings import setup_django

    setup_django()
except ImportError:
    print("Django 설정을 로드할 수 없습니다. 필요한 경우 설정하세요.")

if __name__ == "__main__":
    # 현재 디렉토리에서 모든 테스트 케이스 찾기
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(current_dir, pattern="test_*.py")

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 테스트 결과에 따라 종료 코드 설정
    sys.exit(not result.wasSuccessful())
