"""백업 작업 데이터 모델

Bacula API에서 조회한 백업 작업 정보를 표현하는 데이터 클래스를 제공합니다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BackupJob:
    """백업 작업 데이터 클래스

    Bacula API의 백업 작업 정보를 파이썬 객체로 표현합니다.

    Attributes:
        job_id: 작업 ID
        job_name: 작업명
        client_name: 클라이언트명
        status: 작업 상태 코드 (T=성공, f=실패, A=취소 등)
        level: 백업 레벨 (F=Full, I=Incremental, D=Differential)
        job_type: 작업 타입 (B=Backup, R=Restore, V=Verify, etc.)
        start_time: 작업 시작 시간
        end_time: 작업 종료 시간 (진행 중인 경우 None)
        backup_bytes: 백업 데이터 크기 (바이트)
        job_files: 백업된 파일 개수
        job_errors: 에러 개수
        error_message: 에러 메시지 (선택)
        pool_name: 풀 이름
        fileset_name: 파일셋 이름
    """

    job_id: int
    job_name: str
    client_name: str
    status: str
    level: str
    job_type: str
    start_time: datetime
    end_time: Optional[datetime]
    backup_bytes: int
    job_files: int
    job_errors: int
    error_message: Optional[str] = None
    pool_name: Optional[str] = None
    fileset_name: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """작업 성공 여부

        Returns:
            성공 시 True, 그 외 False
        """
        return self.status == 'T'

    @property
    def is_failed(self) -> bool:
        """작업 실패 여부

        Returns:
            실패 시 True, 그 외 False
        """
        return self.status in ('f', 'E')

    @property
    def is_canceled(self) -> bool:
        """작업 취소 여부

        Returns:
            취소됨 시 True, 그 외 False
        """
        return self.status == 'A'

    @property
    def is_running(self) -> bool:
        """작업 실행 중 여부

        Returns:
            실행 중이면 True, 그 외 False
        """
        return self.status == 'R'

    @property
    def is_backup(self) -> bool:
        """백업 작업 여부

        Returns:
            백업 작업이면 True, 그 외 (Restore, Verify 등) False
        """
        return self.job_type == 'B'

    @property
    def status_display(self) -> str:
        """상태 표시 문자열

        Returns:
            한글로 된 상태 설명
        """
        status_map = {
            'T': '성공',
            'f': '실패',
            'E': '에러',
            'A': '취소됨',
            'R': '실행 중',
            'C': '생성됨',
            'M': '마이그레이션됨',
            'S': '스캔됨',
            'F': '대기 중',
            'e': '실패 (비치명적)',
        }
        return status_map.get(self.status, f'알 수 없음 ({self.status})')

    @property
    def level_display(self) -> str:
        """백업 레벨 표시 문자열

        Returns:
            한글로 된 백업 레벨 설명
        """
        level_map = {
            'F': 'Full',
            'I': 'Incremental',
            'D': 'Differential',
        }
        return level_map.get(self.level, self.level)

    @property
    def backup_size_display(self) -> str:
        """백업 크기를 읽기 쉬운 형식으로 변환

        Returns:
            사람이 읽기 쉬운 크기 문자열 (예: 1.5 GB)
        """
        if self.backup_bytes == 0:
            return '0 B'

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.backup_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    @property
    def duration_seconds(self) -> int:
        """작업 실행 시간 (초)

        Returns:
            작업 시작부터 종료까지의 시간 (초)
            진행 중인 작업의 경우 현재 시간 기준으로 계산
        """
        end = self.end_time if self.end_time else datetime.now()
        return int((end - self.start_time).total_seconds())

    @property
    def duration_display(self) -> str:
        """작업 실행 시간을 읽기 쉬운 형식으로 변환

        Returns:
            사람이 읽기 쉬운 시간 문자열 (예: 1시간 30분)
        """
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds}초"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}분 {secs}초"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}시간 {minutes}분"

    @classmethod
    def from_api_response(cls, data: dict) -> 'BackupJob':
        """API 응답 데이터에서 BackupJob 객체 생성

        Args:
            data: Bacula API 응답 딕셔너리

        Returns:
            BackupJob 객체

        Raises:
            ValueError: 필수 필드가 없거나 형식이 잘못된 경우
        """
        try:
            # 날짜/시간 파싱
            start_time = datetime.strptime(
                data['starttime'],
                '%Y-%m-%d %H:%M:%S'
            )

            # endtime이 None이거나 빈 문자열이면 None으로 설정 (진행 중인 job)
            endtime_str = data.get('endtime')
            end_time = None
            if endtime_str:
                end_time = datetime.strptime(
                    endtime_str,
                    '%Y-%m-%d %H:%M:%S'
                )

            # 에러 메시지는 별도로 조회 필요 (여기서는 None)
            # 실제 에러 메시지는 API의 jobs/{id}/log 엔드포인트에서 조회

            return cls(
                job_id=int(data['jobid']),
                job_name=data['name'],
                client_name=data['client'],
                status=data['jobstatus'],
                level=data['level'],
                job_type=data.get('type', ''),
                start_time=start_time,
                end_time=end_time,
                backup_bytes=int(data.get('jobbytes', 0)),
                job_files=int(data.get('jobfiles', 0)),
                job_errors=int(data.get('joberrors', 0)),
                error_message=None,
                pool_name=data.get('pool'),
                fileset_name=data.get('fileset'),
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"API 응답 데이터 파싱 실패: {e}")

    def __str__(self) -> str:
        """객체 문자열 표현

        Returns:
            객체의 주요 정보를 포함한 문자열
        """
        return (
            f"BackupJob(id={self.job_id}, "
            f"name={self.job_name}, "
            f"client={self.client_name}, "
            f"status={self.status_display})"
        )
