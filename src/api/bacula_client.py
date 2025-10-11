"""Bacula API 클라이언트 모듈

Bacula REST API와 통신하여 백업 작업 정보를 조회하는 클라이언트 클래스를 제공합니다.
"""

import logging
import time
from typing import Dict, List, Optional, Any
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


logger = logging.getLogger(__name__)


class BaculaAPIError(Exception):
    """Bacula API 관련 기본 예외"""
    pass


class ConnectionError(BaculaAPIError):
    """API 연결 실패 예외"""
    pass


class TimeoutError(BaculaAPIError):
    """API 타임아웃 예외"""
    pass


class BaculaClient:
    """Bacula REST API 클라이언트

    Bacula REST API와 통신하여 백업 작업 정보를 조회합니다.
    재시도 로직과 타임아웃 처리를 포함합니다.

    Attributes:
        api_host: API 서버 호스트 주소
        api_port: API 서버 포트 번호
        username: API 인증 사용자명
        password: API 인증 비밀번호
        base_url: API 베이스 URL
        timeout: 요청 타임아웃 (초)
        max_retries: 최대 재시도 횟수
    """

    def __init__(
        self,
        api_host: str,
        api_port: int,
        username: str,
        password: str,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """BaculaClient 초기화

        Args:
            api_host: API 서버 호스트 주소
            api_port: API 서버 포트 번호
            username: API 인증 사용자명
            password: API 인증 비밀번호
            timeout: 요청 타임아웃 (초), 기본값 10
            max_retries: 최대 재시도 횟수, 기본값 3
        """
        self.api_host = api_host
        self.api_port = api_port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = f'http://{api_host}:{api_port}/api/v1'
        self.auth = HTTPBasicAuth(username, password)

        logger.info(
            f"BaculaClient 초기화: {api_host}:{api_port}, "
            f"timeout={timeout}s, max_retries={max_retries}"
        )

    def connect(self) -> bool:
        """API 연결 테스트

        API 서버에 연결이 가능한지 확인합니다.

        Returns:
            연결 성공 시 True, 실패 시 False

        Raises:
            ConnectionError: 연결 실패 시
            TimeoutError: 타임아웃 발생 시
        """
        try:
            logger.info("API 연결 테스트 시작")
            self._request('GET', 'jobs', params={'limit': 1})
            logger.info("API 연결 테스트 성공")
            return True
        except Exception as e:
            logger.error(f"API 연결 테스트 실패: {e}")
            raise

    def get_jobs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """백업 작업 목록 조회

        지정된 시간 범위의 백업 작업 목록을 조회합니다.

        Args:
            start_time: 조회 시작 시간 (선택)
            end_time: 조회 종료 시간 (선택)

        Returns:
            백업 작업 정보 딕셔너리 리스트

        Raises:
            BaculaAPIError: API 호출 실패 시
        """
        logger.info(
            f"백업 작업 목록 조회 시작: "
            f"start={start_time}, end={end_time}"
        )

        params = {}
        if start_time:
            params['starttime'] = start_time.strftime('%Y-%m-%d %H:%M:%S')
        if end_time:
            params['endtime'] = end_time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            response = self._request('GET', 'jobs', params=params)
            jobs = response.get('output', [])
            logger.info(f"백업 작업 {len(jobs)}건 조회 완료")
            return jobs
        except Exception as e:
            logger.error(f"백업 작업 조회 실패: {e}")
            raise BaculaAPIError(f"작업 목록 조회 실패: {e}")

    def get_job_details(self, job_id: int) -> Dict[str, Any]:
        """백업 작업 상세 정보 조회

        특정 작업의 상세 정보를 조회합니다.

        Args:
            job_id: 작업 ID

        Returns:
            작업 상세 정보 딕셔너리

        Raises:
            BaculaAPIError: API 호출 실패 시
        """
        logger.info(f"작업 상세 정보 조회 시작: job_id={job_id}")

        try:
            response = self._request('GET', f'jobs/{job_id}')
            job_detail = response.get('output', {})
            logger.info(f"작업 상세 정보 조회 완료: job_id={job_id}")
            return job_detail
        except Exception as e:
            logger.error(f"작업 상세 정보 조회 실패: job_id={job_id}, {e}")
            raise BaculaAPIError(f"작업 상세 정보 조회 실패: {e}")

    def get_clients(self) -> List[Dict[str, Any]]:
        """클라이언트 목록 조회

        백업 대상 클라이언트 목록을 조회합니다.

        Returns:
            클라이언트 정보 딕셔너리 리스트

        Raises:
            BaculaAPIError: API 호출 실패 시
        """
        logger.info("클라이언트 목록 조회 시작")

        try:
            response = self._request('GET', 'clients')
            clients = response.get('output', [])
            logger.info(f"클라이언트 {len(clients)}개 조회 완료")
            return clients
        except Exception as e:
            logger.error(f"클라이언트 목록 조회 실패: {e}")
            raise BaculaAPIError(f"클라이언트 목록 조회 실패: {e}")

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """공통 HTTP 요청 처리

        재시도 로직과 타임아웃 처리를 포함한 HTTP 요청을 수행합니다.

        Args:
            method: HTTP 메서드 (GET, POST 등)
            endpoint: API 엔드포인트
            params: URL 쿼리 파라미터
            json_data: JSON 요청 본문

        Returns:
            API 응답 딕셔너리

        Raises:
            ConnectionError: 연결 실패 시
            TimeoutError: 타임아웃 발생 시
            BaculaAPIError: 기타 API 오류 시
        """
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"API 요청 시도 {attempt}/{self.max_retries}: "
                    f"{method} {url}"
                )

                start_time = time.time()
                response = requests.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                )
                elapsed = time.time() - start_time

                logger.debug(
                    f"API 응답: status={response.status_code}, "
                    f"elapsed={elapsed:.2f}s"
                )

                # HTTP 오류 체크
                response.raise_for_status()

                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(
                    f"API 타임아웃 발생 (시도 {attempt}/{self.max_retries}): "
                    f"{url}"
                )
                if attempt == self.max_retries:
                    raise TimeoutError(
                        f"API 타임아웃: {url} (최대 재시도 횟수 초과)"
                    )
                # 지수 백오프
                wait_time = 2 ** (attempt - 1)
                logger.info(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)

            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"API 연결 실패 (시도 {attempt}/{self.max_retries}): "
                    f"{url}, {e}"
                )
                if attempt == self.max_retries:
                    raise ConnectionError(
                        f"API 연결 실패: {url} (최대 재시도 횟수 초과)"
                    )
                # 지수 백오프
                wait_time = 2 ** (attempt - 1)
                logger.info(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)

            except requests.exceptions.HTTPError:
                logger.error(
                    f"API HTTP 오류: status={response.status_code}, "
                    f"url={url}, response={response.text}"
                )
                raise BaculaAPIError(
                    f"API HTTP 오류: {response.status_code} - {response.text}"
                )

            except Exception as e:
                logger.error(f"API 요청 중 예상치 못한 오류: {e}")
                raise BaculaAPIError(f"API 요청 실패: {e}")

        # 모든 재시도 실패
        raise BaculaAPIError("API 요청 실패: 최대 재시도 횟수 초과")
