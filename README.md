# Bacula Backup Report System

Bacula API를 통해 백업 작업 정보를 조회하고 HTML 리포트를 자동 생성하는 시스템입니다.

## 📋 기능

- Bacula REST API를 통한 백업 작업 조회
- 성공/실패/진행 중/취소됨 작업 분류
- HTML 형식의 백업 리포트 자동 생성
- 테스트 모드 및 프로덕션 모드 지원
- 상세한 로깅 및 에러 처리

## 🛠 기술 스택

- **언어**: Python 3.12
- **주요 라이브러리**:
  - `requests`: API 호출
  - `jinja2`: HTML 템플릿 렌더링
  - `python-dotenv`: 환경 변수 관리
  - `pytest`: 테스트

## 📦 설치 방법

### 1. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

### 2. 필수 패키지 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 환경 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 실제 값을 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```ini
BACULUM_API_HOST=baculum_ip_address
BACULUM_API_PORT=9096
BACULUM_API_USERNAME=your_username
BACULUM_API_PASSWORD=your_password
```

## 🚀 사용 방법

### 기본 실행

```bash
# 테스트 모드 (최근 1주일 데이터)
python -m src.main --mode test

# 프로덕션 모드 (전일 22시 ~ 현재)
python -m src.main --mode production
```

### 상세 로그 출력

```bash
python -m src.main --mode test --verbose
```

### 출력 파일명 지정

```bash
python -m src.main --mode test --output custom_report.html
```

## 📂 프로젝트 구조

```
baculum/
├── src/
│   ├── api/                 # API 클라이언트
│   │   └── bacula_client.py
│   ├── models/              # 데이터 모델
│   │   ├── backup_job.py
│   │   └── report_stats.py
│   ├── report/              # 리포트 생성
│   │   └── report_generator.py
│   ├── utils/               # 유틸리티
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── datetime_helper.py
│   └── main.py              # 메인 프로그램
├── templates/               # HTML 템플릿
│   └── report_template.html
├── reports/                 # 생성된 리포트
├── logs/                    # 로그 파일
├── tests/                   # 테스트 코드
├── .env                     # 환경 변수 (git 제외)
├── .env.example             # 환경 변수 예시
├── requirements.txt         # 의존성 패키지
└── README.md
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest -v

# 커버리지 포함
pytest -v --cov=src

# 특정 테스트 파일만 실행
pytest tests/test_models.py -v
```

## 📊 리포트 예시

생성된 HTML 리포트에는 다음 정보가 포함됩니다:

- **백업 현황 요약**: 전체 작업 수, 성공률, 실패율, 클라이언트 수
- **실패한 백업 상세**: 실패한 작업의 상세 정보 및 에러 로그
- **성공한 백업 목록**: 완료 시간, 백업 크기, 소요 시간 등
- **진행 중인 백업**: 현재 실행 중인 작업 목록
- **취소된 백업**: 취소된 작업 목록

## ⚙️ 설정

### API 설정

`.env` 파일에서 다음 설정을 변경할 수 있습니다:

```ini
# API 연결 정보
BACULUM_API_HOST=172.16.1.0
BACULUM_API_PORT=9096
BACULUM_API_USERNAME=admin
BACULUM_API_PASSWORD=password

# 옵션 설정
BACULUM_API_TIMEOUT=10        # API 타임아웃 (초)
BACULUM_API_MAX_RETRIES=3     # 최대 재시도 횟수
LOG_LEVEL=INFO                # 로그 레벨
```

### 조회 기간

- **테스트 모드**: 현재 시점에서 1주일 전까지의 데이터 조회
- **프로덕션 모드**: 전일 22시부터 현재 시점까지의 데이터 조회

## 🔧 코드 품질

```bash
# flake8 코드 스타일 검사
flake8 src/
```

## 📝 로그

로그 파일은 `logs/` 디렉토리에 저장됩니다:

- 파일명: `app_YYYYMMDD.log`
- 로테이션: 10MB 단위, 최대 5개 파일 유지
- 레벨: DEBUG (파일), INFO (콘솔)

## 🐛 트러블슈팅

### API 연결 실패

```
✗ API 오류: API 연결 실패
```

**해결 방법**:
1. `.env` 파일의 API 주소와 포트 확인
2. Bacula 서버가 실행 중인지 확인
3. 네트워크 연결 확인

### 임포트 오류

```
ModuleNotFoundError: No module named 'src'
```

**해결 방법**:
- 반드시 모듈 방식으로 실행: `python -m src.main`

### 권한 오류

```
PermissionError: [Errno 13] Permission denied: 'reports/'
```

**해결 방법**:
```bash
chmod -R 755 reports/ logs/
```

## 📄 라이선스

이 프로젝트는 내부용으로 개발되었습니다.

## 👥 문의

문제가 발생하거나 질문이 있는 경우 시스템 관리자에게 문의하세요.
