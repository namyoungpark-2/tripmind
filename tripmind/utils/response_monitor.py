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
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            base_dir = Path(__file__).parent.parent
            log_dir = os.path.join(base_dir, "logs", "monitor")

        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        self.issues_count = {}
        self.known_issues = set()

        today = datetime.now().strftime("%Y-%m-%d")
        self.issues_log = os.path.join(log_dir, f"issues-{today}.json")

        self._load_known_issues()

    def _load_known_issues(self):
        try:
            if os.path.exists(self.issues_log):
                with open(self.issues_log, "r", encoding="utf-8") as f:
                    issues_data = json.load(f)
                    self.issues_count = issues_data.get("count", {})
                    self.known_issues = set(issues_data.get("known_issues", []))
        except Exception as e:
            logger.error(f"이슈 로그 로딩 오류: {str(e)}")

    def _save_issues_data(self):
        try:
            issues_data = {
                "count": self.issues_count,
                "known_issues": list(self.known_issues),
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.issues_log, "w", encoding="utf-8") as f:
                json.dump(issues_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"이슈 로그 저장 오류: {str(e)}")

    def detect_hallucinations(self, response: str) -> List[Dict[str, Any]]:
        issues = []

        phone_patterns = [
            r"(?<!\d)010-\d{4}-\d{4}(?!\d)",  # 010-1234-5678
            r"(?<!\d)02-\d{3,4}-\d{4}(?!\d)",  # 02-123-4567
            r"(?<!\d)0\d{1,2}-\d{3,4}-\d{4}(?!\d)",  # 지역번호
        ]

        price_patterns = [
            r"(\d{1,3}(?:,\d{3})*)[원|₩]",  # 10,000원
            r"([₩|\\]\s*\d{1,3}(?:,\d{3})*)",  # ₩10,000
        ]

        address_patterns = [
            r"서울특별시\s\w+구\s\w+동\s[\d-]+",
            r"서울시\s\w+구\s\w+동\s[\d-]+",
            r"\w+도\s\w+시\s\w+구\s\w+동\s[\d-]+",
        ]

        guarantee_patterns = [
            r"확실히",
            r"보장합니다",
            r"틀림없이",
            r"100%",
            r"반드시",
            r"항상",
            r"절대로",
        ]

        all_patterns = {
            "전화번호": phone_patterns,
            "가격정보": price_patterns,
            "주소정보": address_patterns,
            "보증표현": guarantee_patterns,
        }

        for issue_type, patterns in all_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, response)
                for match in matches:
                    start = max(0, match.start() - 20)
                    end = min(len(response), match.end() + 20)
                    context = response[start:end]

                    detected = match.group(0)

                    if issue_type not in self.issues_count:
                        self.issues_count[issue_type] = 0
                    self.issues_count[issue_type] += 1

                    issue = {
                        "type": issue_type,
                        "detected": detected,
                        "context": context,
                        "timestamp": datetime.now().isoformat(),
                    }

                    issue_key = f"{issue_type}:{detected}"
                    if issue_key not in self.known_issues:
                        self.known_issues.add(issue_key)
                        issues.append(issue)

        if issues:
            self._save_issues_data()

        return issues

    def check_factual_accuracy(self, response: str) -> List[Dict[str, Any]]:
        issues = []

        definitive_statements = re.finditer(
            r"(실제로|사실은|사실상|실제|사실|진짜로)[^.]*?[.?!]", response
        )
        for match in definitive_statements:
            statement = match.group(0)

            issue = {
                "type": "사실주장",
                "detected": statement,
                "context": statement,
                "timestamp": datetime.now().isoformat(),
            }

            issue_key = f"사실주장:{statement[:50]}"
            if issue_key not in self.known_issues:
                self.known_issues.add(issue_key)
                issues.append(issue)

                if "사실주장" not in self.issues_count:
                    self.issues_count["사실주장"] = 0
                self.issues_count["사실주장"] += 1

        if issues:
            self._save_issues_data()

        return issues

    def detect_ethical_issues(self, response: str) -> List[Dict[str, Any]]:
        issues = []

        illegal_patterns = [
            r"불법으로",
            r"허가 없이",
            r"몰래",
            r"등록 필요없이",
            r"증명서 없이",
        ]

        for pattern in illegal_patterns:
            matches = re.finditer(pattern, response)
            for match in matches:
                start = max(0, match.start() - 20)
                end = min(len(response), match.end() + 40)
                context = response[start:end]

                issue = {
                    "type": "윤리문제",
                    "detected": match.group(0),
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                }

                issue_key = f"윤리문제:{context[:50]}"
                if issue_key not in self.known_issues:
                    self.known_issues.add(issue_key)
                    issues.append(issue)

                    if "윤리문제" not in self.issues_count:
                        self.issues_count["윤리문제"] = 0
                    self.issues_count["윤리문제"] += 1

        if issues:
            self._save_issues_data()

        return issues

    def analyze_response(self, response: str, node_name: str = None) -> Dict[str, Any]:
        try:
            result = {
                "timestamp": datetime.now().isoformat(),
                "node": node_name,
                "response_length": len(response),
                "issues": [],
                "score": 10.0,
            }

            hallucinations = self.detect_hallucinations(response)
            factual_issues = self.check_factual_accuracy(response)
            ethical_issues = self.detect_ethical_issues(response)

            result["issues"] = hallucinations + factual_issues + ethical_issues

            result["score"] -= len(result["issues"]) * 0.5
            result["score"] = max(0, result["score"])

            if result["issues"]:
                logger.warning(
                    f"응답 분석 결과: {len(result['issues'])}개 이슈 발견, 점수={result['score']:.1f}/10.0",
                )
                for i, issue in enumerate(result["issues"]):
                    logger.warning(
                        f"  이슈 {i+1}: [{issue['type']}] {issue['detected']}"
                    )
            else:
                logger.info(
                    f"응답 분석 결과: 이슈 없음, 점수={result['score']:.1f}/10.0"
                )

            return result

        except Exception as e:
            logger.error(f"응답 분석 오류: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "issues": [],
                "score": 0,
            }

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "updated_at": datetime.now().isoformat(),
            "issue_counts": self.issues_count,
            "total_issues": sum(self.issues_count.values()),
            "unique_issues": len(self.known_issues),
        }

    def clear_statistics(self):
        self.issues_count = {}
        self.known_issues = set()
        self._save_issues_data()

    def analyze_and_log(
        self, response: str, node_name: str = None, session_id: str = None
    ):
        try:
            if not response or not isinstance(response, str):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": "유효하지 않은 응답",
                    "issues": [],
                    "score": 0,
                }

            result = self.analyze_response(response, node_name)

            result["session_id"] = session_id

            today = datetime.now().strftime("%Y-%m-%d")
            analysis_log = os.path.join(self.log_dir, f"analysis-{today}.jsonl")

            with open(analysis_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

            return result

        except Exception as e:
            logger.error(f"응답 분석 및 로깅 오류: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "issues": [],
                "score": 0,
            }


response_monitor = ResponseMonitor()
