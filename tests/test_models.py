"""데이터 모델 테스트"""

from datetime import datetime

from src.models.backup_job import BackupJob
from src.models.report_stats import ReportStats


class TestBackupJob:
    """BackupJob 모델 테스트"""

    def test_from_api_response(self):
        """API 응답에서 BackupJob 객체 생성 테스트"""
        api_data = {
            'jobid': 1,
            'name': 'test-job',
            'client': 'test-client',
            'jobstatus': 'T',
            'level': 'F',
            'type': 'B',
            'starttime': '2025-10-11 10:00:00',
            'endtime': '2025-10-11 10:05:00',
            'jobbytes': 1024000,
            'jobfiles': 100,
            'joberrors': 0,
            'pool': 'test-pool',
            'fileset': 'test-fileset',
        }

        job = BackupJob.from_api_response(api_data)

        assert job.job_id == 1
        assert job.job_name == 'test-job'
        assert job.client_name == 'test-client'
        assert job.status == 'T'
        assert job.job_type == 'B'
        assert job.is_success is True
        assert job.is_failed is False
        assert job.is_backup is True

    def test_status_properties(self):
        """상태 프로퍼티 테스트"""
        job = BackupJob(
            job_id=1,
            job_name='test',
            client_name='client',
            status='T',
            level='F',
            job_type='B',
            start_time=datetime(2025, 10, 11, 10, 0, 0),
            end_time=datetime(2025, 10, 11, 10, 5, 0),
            backup_bytes=1024,
            job_files=10,
            job_errors=0
        )

        assert job.is_success is True
        assert job.status_display == '성공'

        job.status = 'f'
        assert job.is_failed is True
        assert job.status_display == '실패'

        job.status = 'A'
        assert job.is_canceled is True
        assert job.status_display == '취소됨'

    def test_backup_size_display(self):
        """백업 크기 표시 테스트"""
        job = BackupJob(
            job_id=1,
            job_name='test',
            client_name='client',
            status='T',
            level='F',
            job_type='B',
            start_time=datetime.now(),
            end_time=datetime.now(),
            backup_bytes=1024 * 1024 * 1024,  # 1 GB
            job_files=10,
            job_errors=0
        )

        assert 'GB' in job.backup_size_display

    def test_is_backup_property(self):
        """백업 작업 타입 확인 테스트"""
        # Backup 작업 (type='B')
        backup_job = BackupJob(
            job_id=1,
            job_name='backup-job',
            client_name='client',
            status='T',
            level='F',
            job_type='B',
            start_time=datetime.now(),
            end_time=datetime.now(),
            backup_bytes=1024,
            job_files=10,
            job_errors=0
        )
        assert backup_job.is_backup is True

        # Restore 작업 (type='R')
        restore_job = BackupJob(
            job_id=2,
            job_name='restore-job',
            client_name='client',
            status='T',
            level='F',
            job_type='R',
            start_time=datetime.now(),
            end_time=datetime.now(),
            backup_bytes=1024,
            job_files=10,
            job_errors=0
        )
        assert restore_job.is_backup is False


class TestReportStats:
    """ReportStats 모델 테스트"""

    def test_from_jobs(self):
        """백업 작업 리스트에서 통계 생성 테스트"""
        jobs = [
            BackupJob(
                job_id=i,
                job_name=f'job-{i}',
                client_name='client-1',
                status='T' if i % 2 == 0 else 'f',
                level='F',
                job_type='B',
                start_time=datetime(2025, 10, 11, 10, 0, 0),
                end_time=datetime(2025, 10, 11, 10, 5, 0),
                backup_bytes=1024,
                job_files=10,
                job_errors=0 if i % 2 == 0 else 1
            )
            for i in range(10)
        ]

        start = datetime(2025, 10, 11, 0, 0, 0)
        end = datetime(2025, 10, 11, 23, 59, 59)
        stats = ReportStats.from_jobs(jobs, start, end)

        assert stats.total_jobs == 10
        assert stats.success_count == 5
        assert stats.failed_count == 5
        assert stats.success_rate == 50.0
        assert stats.failed_rate == 50.0
