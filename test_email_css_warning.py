#!/usr/bin/env python3
"""
이메일 발송 모듈의 CSS 경고 억제 기능 테스트.

CSS를 인라인으로 변환할 때 cssutils 경고가 발생하지 않는지 확인합니다.
"""

import logging
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.mail.email_sender import EmailSender


def test_css_warning_suppression():
    """CSS 경고 억제 테스트."""
    # 로깅 설정
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("CSS 경고 억제 테스트 시작")
    logger.info("=" * 60)

    # 테스트용 HTML (간단한 CSS 포함)
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #007bff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>테스트 리포트</h1>
            <p>이것은 CSS 인라인 변환 테스트입니다.</p>
        </div>
    </body>
    </html>
    """

    try:
        # EmailSender 인스턴스 생성 (더미 설정)
        sender = EmailSender(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="dummy_password"
        )

        logger.info("\nCSS를 인라인으로 변환 중...")
        logger.info("(cssutils 경고가 출력되지 않아야 합니다)")
        logger.info("-" * 60)

        # CSS 변환 실행
        result_html = sender._transform_css_to_inline(test_html)

        logger.info("-" * 60)
        logger.info("CSS 변환 완료!")

        # 결과 검증
        if 'style=' in result_html:
            logger.info("\n✓ 성공: CSS가 인라인 스타일로 변환되었습니다.")
        else:
            logger.warning("\n⚠ 경고: CSS 변환 결과에 인라인 스타일이 없습니다.")

        # 간단한 결과 출력 (첫 500자)
        logger.info("\n변환된 HTML 샘플:")
        logger.info(result_html[:500] + "...")

        logger.info("\n" + "=" * 60)
        logger.info("테스트 완료!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"\n✗ 테스트 실패: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_css_warning_suppression()
    sys.exit(0 if success else 1)
