"""백업 서비스 레이어

백업 작업 조회 및 가공 비즈니스 로직을 제공합니다.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from src.api.client import BaculaClient, BaculaAPIError
from src.models.backup_job import BackupJob
from src.utils.datetime import (
    get_test_period,
    get_production_period,
    format_datetime_display
)


logger = logging.getLogger(__name__)


@dataclass
class JobsClassification:
    """백업 작업 분류 결과

    Attributes:
        all_jobs: 전체 작업 리스트
        success_jobs: 성공한 작업 리스트
        failed_jobs: 실패한 작업 리스트
        running_jobs: 실행 중인 작업 리스트
        canceled_jobs: 취소된 작업 리스트
    """
    all_jobs: List[BackupJob]
    success_jobs: List[BackupJob]
    failed_jobs: List[BackupJob]
    running_jobs: List[BackupJob]
    canceled_jobs: List[BackupJob]


class BackupService:
    """백업 서비스

    백업 작업 조회, 데이터 파싱, 분류 등의 비즈니스 로직을 제공합니다.

    Attributes:
        client: BaculaClient 인스턴스
    """

    def __init__(self, client: BaculaClient):
        """BackupService 초기화

        Args:
            client: BaculaClient 인스턴스
        """
        self.client = client

    def get_jobs_by_period(
        self,
        mode: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Tuple[List[BackupJob], datetime, datetime]:
        """기간별 백업 작업 조회

        Args:
            mode: 실행 모드 ('test' 또는 'production')
                  - test: 최근 1주일 데이터
                  - production: 전일 22시 ~ 현재
            start_time: 커스텀 시작 시간 (선택)
            end_time: 커스텀 종료 시간 (선택)

        Returns:
            (백업 작업 리스트, 시작 시간, 종료 시간) 튜플

        Raises:
            BaculaAPIError: API 호출 실패 시
            ValueError: mode가 잘못된 경우
        """
        # 조회 기간 설정
        if start_time and end_time:
            start_period = start_time
            end_period = end_time
            logger.info(f"커스텀 기간: {format_datetime_display(start_period)} ~ "
                        f"{format_datetime_display(end_period)}")
        elif mode == 'test':
            start_period, end_period = get_test_period()
            logger.info("테스트 모드: 최근 1주일 데이터 조회")
        elif mode == 'production':
            start_period, end_period = get_production_period()
            logger.info("프로덕션 모드: 전일 22시 ~ 현재 데이터 조회")
        else:
            raise ValueError(f"잘못된 모드: {mode}. 'test' 또는 'production'을 사용하세요.")

        logger.info(
            f"조회 기간: {format_datetime_display(start_period)} ~ "
            f"{format_datetime_display(end_period)}"
        )

        # 백업 작업 조회
        jobs_data = self._fetch_jobs_by_level(start_period, end_period)

        # 데이터 파싱
        jobs = self._parse_jobs_data(jobs_data)

        return jobs, start_period, end_period

    def get_jobs_by_level(
        self,
        start_time: datetime,
        end_time: datetime,
        level: str
    ) -> List[BackupJob]:
        """레벨별 백업 작업 조회

        Args:
            start_time: 시작 시간
            end_time: 종료 시간
            level: 백업 레벨 ('F', 'I', 'D')

        Returns:
            백업 작업 리스트

        Raises:
            BaculaAPIError: API 호출 실패 시
        """
        jobs_data = self.client.get_jobs(
            start_time=start_time,
            end_time=end_time,
            level=level,
            type='B'
        )

        return self._parse_jobs_data(jobs_data)

    def classify_jobs(self, jobs: List[BackupJob]) -> JobsClassification:
        """백업 작업 분류

        Args:
            jobs: 백업 작업 리스트

        Returns:
            JobsClassification 객체
        """
        success_jobs = [job for job in jobs if job.is_success]
        failed_jobs = [job for job in jobs if job.is_failed]
        running_jobs = [job for job in jobs if job.is_running]
        canceled_jobs = [job for job in jobs if job.is_canceled]

        logger.debug(
            f"작업 분류: success={len(success_jobs)}, "
            f"failed={len(failed_jobs)}, "
            f"running={len(running_jobs)}, "
            f"canceled={len(canceled_jobs)}"
        )

        return JobsClassification(
            all_jobs=jobs,
            success_jobs=success_jobs,
            failed_jobs=failed_jobs,
            running_jobs=running_jobs,
            canceled_jobs=canceled_jobs
        )

    def _fetch_jobs_by_level(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """레벨별 백업 작업 조회 및 병합

        Full, Incremental, Differential 백업을 각각 조회하여 병합합니다.

        Args:
            start_time: 시작 시간
            end_time: 종료 시간

        Returns:
            백업 작업 데이터 리스트

        Raises:
            BaculaAPIError: API 호출 실패 시
        """
        api_start = time.time()

        logger.info("백업 레벨별 작업 조회 중...")

        # Full 백업 조회
        full_jobs_data = self.client.get_jobs(
            start_time, end_time, level='F', type='B'
        )
        logger.info(f"  Full 백업: {len(full_jobs_data)}건")

        # Incremental 백업 조회
        incremental_jobs_data = self.client.get_jobs(
            start_time, end_time, level='I', type='B'
        )
        logger.info(f"  Incremental 백업: {len(incremental_jobs_data)}건")

        # Differential 백업 조회
        differential_jobs_data = self.client.get_jobs(
            start_time, end_time, level='D', type='B'
        )
        logger.info(f"  Differential 백업: {len(differential_jobs_data)}건")

        # 모든 작업 합치기
        jobs_data = full_jobs_data + incremental_jobs_data + differential_jobs_data
        api_elapsed = time.time() - api_start

        logger.info(f"✓ 백업 작업 총 {len(jobs_data)}건 조회 완료")
        logger.info(f"  API 호출 시간: {api_elapsed:.2f}초")

        if api_elapsed > 10:
            logger.warning(
                f"⚠ API 호출 시간이 10초를 초과했습니다: {api_elapsed:.2f}초"
            )

        return jobs_data

    def _parse_jobs_data(self, jobs_data: List[Dict]) -> List[BackupJob]:
        """백업 작업 데이터 파싱

        Args:
            jobs_data: 백업 작업 원본 데이터 리스트

        Returns:
            파싱된 BackupJob 객체 리스트
        """
        jobs: List[BackupJob] = []
        parse_errors = 0

        for job_data in jobs_data:
            try:
                job = BackupJob.from_api_response(job_data)
                jobs.append(job)
            except ValueError as e:
                logger.warning(f"작업 데이터 파싱 실패: {e}")
                parse_errors += 1

        logger.info(f"✓ 데이터 파싱 완료: {len(jobs)}건")
        if parse_errors > 0:
            logger.warning(f"  파싱 실패: {parse_errors}건")

        # 통계 출력
        success_count = sum(1 for job in jobs if job.is_success)
        failed_count = sum(1 for job in jobs if job.is_failed)
        running_count = sum(1 for job in jobs if job.is_running)
        canceled_count = sum(1 for job in jobs if job.is_canceled)

        logger.info(f"  성공: {success_count}건")
        logger.info(f"  실패: {failed_count}건")
        logger.info(f"  실행 중: {running_count}건")
        logger.info(f"  취소됨: {canceled_count}건")

        return jobs
