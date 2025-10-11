"""API 연결 테스트 스크립트

실제 Bacula API에 연결하여 응답을 확인하고 샘플 데이터를 저장합니다.
"""

import json
import sys
from pathlib import Path

# src 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from api.bacula_client import BaculaClient
from utils.config import Config
from utils.logger import setup_logger
from utils.datetime_helper import get_test_period

# 로거 설정
logger = setup_logger('test_api', log_level='DEBUG')


def main():
    """API 연결 테스트 메인 함수"""
    try:
        logger.info("=" * 60)
        logger.info("Bacula API 연결 테스트 시작")
        logger.info("=" * 60)

        # 설정 로드
        logger.info("설정 로드 중...")
        config = Config()
        logger.info(f"API 서버: {config.api_host}:{config.api_port}")
        logger.info(f"사용자명: {config.api_username}")
        logger.info(f"타임아웃: {config.api_timeout}초")

        # BaculaClient 생성
        logger.info("BaculaClient 생성 중...")
        client = BaculaClient(**config.get_baculum_client_config())

        # 연결 테스트
        logger.info("API 연결 테스트 중...")
        client.connect()
        logger.info("✓ API 연결 성공")

        # 클라이언트 목록 조회
        logger.info("")
        logger.info("클라이언트 목록 조회 중...")
        clients = client.get_clients()
        logger.info(f"✓ 클라이언트 {len(clients)}개 조회 완료")

        # 백업 작업 목록 조회 (1주일)
        logger.info("")
        logger.info("백업 작업 목록 조회 중 (최근 1주일)...")
        start_time, end_time = get_test_period()
        logger.info(f"조회 기간: {start_time} ~ {end_time}")
        jobs = client.get_jobs(start_time, end_time)
        logger.info(f"✓ 백업 작업 {len(jobs)}건 조회 완료")

        # 응답 샘플 저장
        logger.info("")
        logger.info("API 응답 샘플 저장 중...")
        fixtures_dir = Path(__file__).parent / 'tests' / 'fixtures'
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        # 클라이언트 샘플 저장
        clients_file = fixtures_dir / 'api_response_clients.json'
        with open(clients_file, 'w', encoding='utf-8') as f:
            json.dump(clients, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ 클라이언트 샘플 저장: {clients_file}")

        # 백업 작업 샘플 저장
        jobs_file = fixtures_dir / 'api_response_jobs.json'
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ 백업 작업 샘플 저장: {jobs_file}")

        # 통계 출력
        logger.info("")
        logger.info("=" * 60)
        logger.info("테스트 결과 요약")
        logger.info("=" * 60)
        logger.info(f"총 클라이언트 수: {len(clients)}")
        logger.info(f"총 백업 작업 수: {len(jobs)}")

        if jobs:
            # 작업 상태별 집계
            status_count = {}
            for job in jobs:
                status = job.get('jobstatus', 'Unknown')
                status_count[status] = status_count.get(status, 0) + 1

            logger.info("")
            logger.info("작업 상태별 집계:")
            for status, count in sorted(status_count.items()):
                logger.info(f"  {status}: {count}건")

            # 샘플 작업 정보 출력
            logger.info("")
            logger.info("샘플 작업 정보 (최근 5건):")
            for i, job in enumerate(jobs[:5], 1):
                logger.info(f"  {i}. JobId={job.get('jobid')}, "
                           f"Name={job.get('name')}, "
                           f"Status={job.get('jobstatus')}")

        logger.info("")
        logger.info("=" * 60)
        logger.info("API 연결 테스트 완료!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"테스트 실패: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
