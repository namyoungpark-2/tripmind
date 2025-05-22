import logging
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)

class ResponseMonitor:
    """
    LLM 응답 모니터링 및 이슈 추적 도구
    
    주요 기능:
    1. 응답 품질 측정
    2. 이슈 추적 및 알림
    3. 피드백 수집을 통한 개선
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        모니터 초기화
        
        Args:
            log_dir: 로그 저장 디렉토리 (기본값: 'logs/monitor')
        """
        if log_dir is None:
            # 기본 로그 디렉토리 설정
            base_dir = Path(__file__).parent.parent
            log_dir = os.path.join(base_dir, 'logs', 'monitor')
            
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        self.issues_count = {}
        self.known_issues = set()
        
        # 이슈 로그 파일 경로
        today = datetime.now().strftime('%Y-%m-%d')
        self.issues_log = os.path.join(log_dir, f'issues-{today}.json')
        
        # 기존 이슈 로드
        self._load_known_issues()
        
    def _load_known_issues(self):
        """기존 이슈 정보 로드"""
        try:
            if os.path.exists(self.issues_log):
                with open(self.issues_log, 'r', encoding='utf-8') as f:
                    issues_data = json.load(f)
                    self.issues_count = issues_data.get('count', {})
                    self.known_issues = set(issues_data.get('known_issues', []))
        except Exception as e:
            logger.error(f"이슈 로그 로딩 오류: {str(e)}")
            
    def _save_issues_data(self):
        """현재 이슈 정보 저장"""
        try:
            issues_data = {
                'count': self.issues_count,
                'known_issues': list(self.known_issues),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.issues_log, 'w', encoding='utf-8') as f:
                json.dump(issues_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"이슈 로그 저장 오류: {str(e)}")
            
    def detect_hallucinations(self, response: str) -> List[Dict[str, Any]]:
        """
        응답에서 환각 내용(hallucination) 감지
        
        Args:
            response: LLM 응답 텍스트
            
        Returns:
            감지된 환각 내용 목록
        """
        issues = []
        
        # 전화번호 패턴 (임의 생성 가능성 높음)
        phone_patterns = [
            r'(?<!\d)010-\d{4}-\d{4}(?!\d)',  # 010-1234-5678
            r'(?<!\d)02-\d{3,4}-\d{4}(?!\d)',  # 02-123-4567
            r'(?<!\d)0\d{1,2}-\d{3,4}-\d{4}(?!\d)',  # 지역번호
        ]
        
        # 명확한 가격/시간 정보 (임의 생성 가능성 높음)
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*)[원|₩]',  # 10,000원
            r'([₩|\\]\s*\d{1,3}(?:,\d{3})*)',  # ₩10,000
        ]
        
        # 명확한 주소 패턴
        address_patterns = [
            r'서울특별시\s\w+구\s\w+동\s[\d-]+',
            r'서울시\s\w+구\s\w+동\s[\d-]+',
            r'\w+도\s\w+시\s\w+구\s\w+동\s[\d-]+',
        ]
        
        # 보증 표현 패턴
        guarantee_patterns = [
            r'확실히',
            r'보장합니다',
            r'틀림없이',
            r'100%',
            r'반드시',
            r'항상',
            r'절대로',
        ]
        
        # 패턴 검사 및 이슈 기록
        all_patterns = {
            '전화번호': phone_patterns,
            '가격정보': price_patterns,
            '주소정보': address_patterns,
            '보증표현': guarantee_patterns,
        }
        
        for issue_type, patterns in all_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, response)
                for match in matches:
                    # 앞뒤 컨텍스트 포함하여 이슈 저장
                    start = max(0, match.start() - 20)
                    end = min(len(response), match.end() + 20)
                    context = response[start:end]
                    
                    # 감지된 내용
                    detected = match.group(0)
                    
                    # 이슈 횟수 업데이트
                    if issue_type not in self.issues_count:
                        self.issues_count[issue_type] = 0
                    self.issues_count[issue_type] += 1
                    
                    # 이슈 기록
                    issue = {
                        'type': issue_type,
                        'detected': detected,
                        'context': context,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # 중복 필터링을 위한 키 생성
                    issue_key = f"{issue_type}:{detected}"
                    if issue_key not in self.known_issues:
                        self.known_issues.add(issue_key)
                        issues.append(issue)
        
        # 이슈 정보 저장
        if issues:
            self._save_issues_data()
            
        return issues
    
    def check_factual_accuracy(self, response: str) -> List[Dict[str, Any]]:
        """
        응답의 사실 정확성 검증
        
        Args:
            response: LLM 응답 텍스트
            
        Returns:
            감지된 부정확 정보 목록
        """
        # 사실 정확성 검증을 위한 휴리스틱 규칙들
        issues = []
        
        # 확정적 표현을 사용한 부분 감지
        definitive_statements = re.finditer(r'(실제로|사실은|사실상|실제|사실|진짜로)[^.]*?[.?!]', response)
        for match in definitive_statements:
            statement = match.group(0)
            
            # 이슈 기록
            issue = {
                'type': '사실주장',
                'detected': statement,
                'context': statement,
                'timestamp': datetime.now().isoformat()
            }
            
            # 중복 필터링을 위한 키 생성
            issue_key = f"사실주장:{statement[:50]}"
            if issue_key not in self.known_issues:
                self.known_issues.add(issue_key)
                issues.append(issue)
                
                # 이슈 카운터 업데이트
                if '사실주장' not in self.issues_count:
                    self.issues_count['사실주장'] = 0
                self.issues_count['사실주장'] += 1
                
        # 이슈 정보 저장
        if issues:
            self._save_issues_data()
            
        return issues
    
    def detect_ethical_issues(self, response: str) -> List[Dict[str, Any]]:
        """
        응답에서 윤리적 문제 감지
        
        Args:
            response: LLM 응답 텍스트
            
        Returns:
            감지된 윤리적 문제 목록
        """
        # 윤리적 문제를 감지하기 위한 휴리스틱 규칙들
        issues = []
        
        # 불법 활동 암시
        illegal_patterns = [
            r'불법으로',
            r'허가 없이',
            r'몰래',
            r'등록 필요없이',
            r'증명서 없이',
        ]
        
        for pattern in illegal_patterns:
            matches = re.finditer(pattern, response)
            for match in matches:
                # 이슈 컨텍스트 추출
                start = max(0, match.start() - 20)
                end = min(len(response), match.end() + 40)
                context = response[start:end]
                
                # 이슈 기록
                issue = {
                    'type': '윤리문제',
                    'detected': match.group(0),
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 중복 필터링
                issue_key = f"윤리문제:{context[:50]}"
                if issue_key not in self.known_issues:
                    self.known_issues.add(issue_key)
                    issues.append(issue)
                    
                    # 이슈 카운터 업데이트
                    if '윤리문제' not in self.issues_count:
                        self.issues_count['윤리문제'] = 0
                    self.issues_count['윤리문제'] += 1
        
        # 이슈 정보 저장
        if issues:
            self._save_issues_data()
            
        return issues
    
    def analyze_response(self, response: str, node_name: str = None) -> Dict[str, Any]:
        """
        응답 분석 및 모든 이슈 탐지
        
        Args:
            response: 분석할 LLM 응답
            node_name: 노드 이름 (옵션)
            
        Returns:
            분석 결과
        """
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'node': node_name,
                'response_length': len(response),
                'issues': [],
                'score': 10.0,  # 기본 점수 10점 만점
            }
            
            # 다양한 이슈 감지 수행
            hallucinations = self.detect_hallucinations(response)
            factual_issues = self.check_factual_accuracy(response)
            ethical_issues = self.detect_ethical_issues(response)
            
            # 모든 이슈 통합
            result['issues'] = hallucinations + factual_issues + ethical_issues
            
            # 이슈 개수에 따른 점수 감소
            result['score'] -= len(result['issues']) * 0.5
            result['score'] = max(0, result['score'])  # 최소 0점
            
            # 결과 로깅
            if result['issues']:
                logger.warning(
                    f"응답 분석 결과: {len(result['issues'])}개 이슈 발견, 점수={result['score']:.1f}/10.0",
                )
                for i, issue in enumerate(result['issues']):
                    logger.warning(f"  이슈 {i+1}: [{issue['type']}] {issue['detected']}")
            else:
                logger.info(f"응답 분석 결과: 이슈 없음, 점수={result['score']:.1f}/10.0")
                
            return result
            
        except Exception as e:
            logger.error(f"응답 분석 오류: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'issues': [],
                'score': 0
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        감지된 이슈 통계 정보 반환
        
        Returns:
            이슈 타입별 건수 통계
        """
        return {
            'updated_at': datetime.now().isoformat(),
            'issue_counts': self.issues_count,
            'total_issues': sum(self.issues_count.values()),
            'unique_issues': len(self.known_issues)
        }
    
    def clear_statistics(self):
        """통계 데이터 초기화"""
        self.issues_count = {}
        self.known_issues = set()
        self._save_issues_data()
        
    def analyze_and_log(self, response: str, node_name: str = None, session_id: str = None):
        """
        응답 분석 및 이슈 로깅
        
        Args:
            response: 분석할 LLM 응답
            node_name: 노드 이름 (옵션)
            session_id: 세션 ID (옵션)
            
        Returns:
            분석 결과
        """
        try:
            # 빈 응답 처리
            if not response or not isinstance(response, str):
                return {
                    'timestamp': datetime.now().isoformat(),
                    'error': '유효하지 않은 응답',
                    'issues': [],
                    'score': 0
                }
                
            # 분석 실행
            result = self.analyze_response(response, node_name)
            
            # 결과 로깅을 위한 컨텍스트 정보 추가
            result['session_id'] = session_id
            
            # 저장할 로그 파일 경로
            today = datetime.now().strftime('%Y-%m-%d')
            analysis_log = os.path.join(self.log_dir, f'analysis-{today}.jsonl')
            
            # 로그 저장
            with open(analysis_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                
            return result
            
        except Exception as e:
            logger.error(f"응답 분석 및 로깅 오류: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'issues': [],
                'score': 0
            }


# 싱글톤 모니터 인스턴스
response_monitor = ResponseMonitor() 