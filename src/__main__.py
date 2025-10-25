"""Python 모듈 실행 진입점

`python -m src` 명령으로 실행할 때 사용됩니다.
"""

import sys
from src.cli import main

if __name__ == '__main__':
    sys.exit(main())
