#!/usr/bin/env python3
"""
실제 백업 리포트 템플릿을 사용한 CSS 경고 억제 테스트.

templates/report_template.html 파일을 읽어서 CSS 변환을 테스트합니다.
"""

import logging
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.mail.email_sender import EmailSender


def test_real_template():
    """실제 템플릿을 사용한 CSS 경고 억제 테스트."""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("실제 템플릿 CSS 경고 억제 테스트 시작")
    logger.info("=" * 60)

    # 템플릿 파일 경로
    template_path = Path(__file__).parent / "templates" / "report_template.html"

    if not template_path.exists():
        logger.error(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        return False

    try:
        # 템플릿 읽기
        logger.info(f"\n템플릿 파일 읽기: {template_path}")
        html_content = template_path.read_text(encoding='utf-8')
        logger.info(f"템플릿 크기: {len(html_content)} bytes")

        # EmailSender 인스턴스 생성
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
        result_html = sender._transform_css_to_inline(html_content)

        logger.info("-" * 60)
        logger.info("CSS 변환 완료!")

        # 결과 검증
        inline_count = result_html.count('style=')
        logger.info(f"\n변환된 인라인 스타일 개수: {inline_count}")

        if inline_count > 0:
            logger.info("✓ 성공: CSS가 인라인 스타일로 변환되었습니다.")
        else:
            logger.warning("⚠ 경고: CSS 변환 결과에 인라인 스타일이 없습니다.")

        # 결과 파일 크기
        logger.info(f"변환된 HTML 크기: {len(result_html)} bytes")

        logger.info("\n" + "=" * 60)
        logger.info("테스트 완료!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"\n✗ 테스트 실패: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_real_template()
    sys.exit(0 if success else 1)
