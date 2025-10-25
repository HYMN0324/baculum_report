"""Bacula CLI 진입점

서브커맨드 기반 CLI 라우터를 제공합니다.
"""

import sys
import argparse
from typing import Dict, Type

from src.commands.base import BaseCommand
from src.commands.report import ReportCommand


# 사용 가능한 커맨드 등록
COMMANDS: Dict[str, Type[BaseCommand]] = {
    'report': ReportCommand,
}


def create_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성

    Returns:
        ArgumentParser 인스턴스
    """
    parser = argparse.ArgumentParser(
        prog='baculum',
        description='Bacula 백업 관리 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 백업 리포트 생성 (테스트 모드)
  python -m src report --mode test

  # 백업 리포트 생성 및 이메일 발송 (프로덕션 모드)
  python -m src report --mode production --send-mail

  # 상세 로그 포함
  python -m src report --mode test --verbose
        '''
    )

    # 서브커맨드 추가
    subparsers = parser.add_subparsers(
        title='사용 가능한 커맨드',
        description='다음 커맨드 중 하나를 선택하세요',
        dest='command',
        required=True,
        help='실행할 커맨드'
    )

    # 각 커맨드 등록
    for name, command_class in COMMANDS.items():
        command_instance = command_class()
        subparser = subparsers.add_parser(
            name,
            help=command_instance.description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        command_instance.setup_args(subparser)
        subparser.set_defaults(command_instance=command_instance)

    return parser


def main() -> int:
    """CLI 메인 함수

    Returns:
        종료 코드 (0: 성공, 1: 실패)
    """
    parser = create_parser()
    args = parser.parse_args()

    # 커맨드 실행
    command_instance: BaseCommand = args.command_instance
    return command_instance.run(args)


if __name__ == '__main__':
    sys.exit(main())
