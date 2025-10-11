"""리포트 통계 데이터 모델

백업 작업 리포트의 통계 정보를 표현하는 데이터 클래스를 제공합니다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from .backup_job import BackupJob


@dataclass
class ReportStats:
    """리포트 통계 클래스

    백업 작업들의 통계 정보를 계산하고 보관합니다.

    Attributes:
        total_jobs: 전체 작업 수
        success_count: 성공한 작업 수
        failed_count: 실패한 작업 수
        canceled_count: 취소된 작업 수
        running_count: 실행 중인 작업 수
        total_clients: 총 클라이언트 수
        start_period: 조회 시작 시간
        end_period: 조회 종료 시간
        report_time: 리포트 생성 시간
        total_backup_bytes: 전체 백업 크기 (바이트)
        total_files: 전체 백업 파일 수
    """

    total_jobs: int
    success_count: int
    failed_count: int
    canceled_count: int
    running_count: int
    total_clients: int
    start_period: datetime
    end_period: datetime
    report_time: datetime
    total_backup_bytes: int
    total_files: int

    @property
    def success_rate(self) -> float:
        """성공률 계산

        Returns:
            성공률 (0.0 ~ 100.0)
        """
        if self.total_jobs == 0:
            return 0.0
        return (self.success_count / self.total_jobs) * 100

    @property
    def failed_rate(self) -> float:
        """실패율 계산

        Returns:
            실패율 (0.0 ~ 100.0)
        """
        if self.total_jobs == 0:
            return 0.0
        return (self.failed_count / self.total_jobs) * 100

    @property
    def total_backup_size_display(self) -> str:
        """전체 백업 크기를 읽기 쉬운 형식으로 변환

        Returns:
            사람이 읽기 쉬운 크기 문자열
        """
        if self.total_backup_bytes == 0:
            return '0 B'

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.total_backup_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    @classmethod
    def from_jobs(
        cls,
        jobs: List[BackupJob],
        start_period: datetime,
        end_period: datetime
    ) -> 'ReportStats':
        """백업 작업 리스트에서 통계 생성

        Args:
            jobs: 백업 작업 리스트
            start_period: 조회 시작 시간
            end_period: 조회 종료 시간

        Returns:
            ReportStats 객체
        """
        # 클라이언트 중복 제거
        unique_clients = set(job.client_name for job in jobs)

        # 상태별 집계
        success_count = sum(1 for job in jobs if job.is_success)
        failed_count = sum(1 for job in jobs if job.is_failed)
        canceled_count = sum(1 for job in jobs if job.is_canceled)
        running_count = sum(1 for job in jobs if job.is_running)

        # 전체 백업 크기 및 파일 수
        total_backup_bytes = sum(job.backup_bytes for job in jobs)
        total_files = sum(job.job_files for job in jobs)

        return cls(
            total_jobs=len(jobs),
            success_count=success_count,
            failed_count=failed_count,
            canceled_count=canceled_count,
            running_count=running_count,
            total_clients=len(unique_clients),
            start_period=start_period,
            end_period=end_period,
            report_time=datetime.now(),
            total_backup_bytes=total_backup_bytes,
            total_files=total_files,
        )

    def __str__(self) -> str:
        """객체 문자열 표현

        Returns:
            통계 요약 문자열
        """
        return (
            f"ReportStats(total={self.total_jobs}, "
            f"success={self.success_count}, "
            f"failed={self.failed_count}, "
            f"clients={self.total_clients})"
        )
