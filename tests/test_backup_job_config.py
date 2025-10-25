"""BackupJobConfig 모델 테스트"""

import pytest
from src.models.backup_job_config import BackupJobConfig


class TestBackupJobConfig:
    """BackupJobConfig 클래스 테스트"""

    def test_valid_full_backup_config(self):
        """정상적인 Full 백업 설정 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='F',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset',
            priority=10
        )

        assert config.name == 'test-job'
        assert config.level == 'F'
        assert config.client == 'test-client'
        assert config.storage == 'test-storage'
        assert config.pool == 'test-pool'
        assert config.fileset == 'test-fileset'
        assert config.priority == 10

    def test_valid_incremental_backup_config(self):
        """정상적인 Incremental 백업 설정 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='I',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset'
        )

        assert config.level == 'I'

    def test_valid_differential_backup_config(self):
        """정상적인 Differential 백업 설정 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='D',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset'
        )

        assert config.level == 'D'

    def test_invalid_level(self):
        """잘못된 백업 레벨 테스트"""
        with pytest.raises(ValueError, match="백업 레벨.*F, I, D"):
            BackupJobConfig(
                name='test-job',
                level='X',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset'
            )

    def test_empty_name(self):
        """빈 작업 이름 테스트"""
        with pytest.raises(ValueError, match="백업 작업 이름.*필수"):
            BackupJobConfig(
                name='',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset'
            )

    def test_empty_client(self):
        """빈 클라이언트 이름 테스트"""
        with pytest.raises(ValueError, match="클라이언트 이름.*필수"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset'
            )

    def test_empty_storage(self):
        """빈 스토리지 이름 테스트"""
        with pytest.raises(ValueError, match="스토리지 이름.*필수"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='',
                pool='test-pool',
                fileset='test-fileset'
            )

    def test_empty_pool(self):
        """빈 풀 이름 테스트"""
        with pytest.raises(ValueError, match="풀 이름.*필수"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='',
                fileset='test-fileset'
            )

    def test_empty_fileset(self):
        """빈 파일셋 이름 테스트"""
        with pytest.raises(ValueError, match="파일셋 이름.*필수"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset=''
            )

    def test_invalid_priority_type(self):
        """잘못된 우선순위 타입 테스트"""
        with pytest.raises(ValueError, match="우선순위.*정수"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset',
                priority='high'  # type: ignore
            )

    def test_invalid_priority_range_low(self):
        """너무 낮은 우선순위 테스트"""
        with pytest.raises(ValueError, match="우선순위.*1-100"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset',
                priority=0
            )

    def test_invalid_priority_range_high(self):
        """너무 높은 우선순위 테스트"""
        with pytest.raises(ValueError, match="우선순위.*1-100"):
            BackupJobConfig(
                name='test-job',
                level='F',
                client='test-client',
                storage='test-storage',
                pool='test-pool',
                fileset='test-fileset',
                priority=101
            )

    def test_to_api_params(self):
        """API 파라미터 변환 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='F',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset',
            priority=50
        )

        params = config.to_api_params()

        assert params == {
            'name': 'test-job',
            'level': 'F',
            'client': 'test-client',
            'storage': 'test-storage',
            'pool': 'test-pool',
            'fileset': 'test-fileset',
            'priority': 50
        }

    def test_to_api_params_default_priority(self):
        """기본 우선순위 API 파라미터 변환 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='F',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset'
        )

        params = config.to_api_params()

        assert 'priority' in params
        assert params['priority'] == 10

    def test_str_representation(self):
        """문자열 표현 테스트"""
        config = BackupJobConfig(
            name='test-job',
            level='F',
            client='test-client',
            storage='test-storage',
            pool='test-pool',
            fileset='test-fileset'
        )

        str_repr = str(config)
        assert 'test-job' in str_repr
        assert 'F' in str_repr
        assert 'test-client' in str_repr
