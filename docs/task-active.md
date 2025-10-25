# Task Active: 확장 가능한 아키텍처 리팩터링

**Phase**: Phase 11
**상태**: 대기
**시작일**: 예정
**완료일**: 예정

## 📋 작업 개요

현재 Baculum 프로젝트는 "리포트 생성" 기능에 강하게 결합된 구조로 되어 있습니다. 향후 다른 기능(예: 백업 스케줄 관리, 실시간 모니터링, 통계 대시보드 등)을 추가할 수 있도록 **기능 분리 및 확장 가능한 아키텍처**로 리팩터링합니다.

**목표**:
- 리포트 생성 기능을 독립적인 모듈로 분리
- 공통 기능(API 클라이언트, 데이터 모델, 설정 등)을 재사용 가능한 구조로 변경
- 새로운 기능을 쉽게 추가할 수 있는 플러그인 형태의 아키텍처 구축
- main.py를 기능별 커맨드를 실행하는 CLI 진입점으로 개선

**브랜치**: `git checkout -b refactor/phase-11-modular-architecture` (작업 시작 시 생성)

## 🔍 현재 구조 분석 및 문제점

### 문제점 1: main.py의 리포트 생성 강결합
- `src/main.py`가 리포트 생성 워크플로우에 강하게 결합되어 있음
- 다른 기능을 추가하려면 main.py를 크게 수정해야 함

### 문제점 2: 공통 로직과 기능별 로직 혼재
- API 조회, 데이터 변환, 리포트 생성이 main.py에 모두 섞여 있음
- 재사용성이 낮음

### 문제점 3: 확장성 부족
- 새로운 기능(예: CLI 대시보드, 알림, 백업 작업 트리거 등)을 추가하기 어려운 구조

### 문제점 4: 파일명과 역할의 불일치
- `bacula_client.py`: Bacula 전용 클라이언트 → 더 일반적인 이름 필요
- `report_generator.py`: 리포트 생성만 담당 → HTML 생성기로 명확화
- `email_sender.py`: 이메일 전용 → 메일 발송으로 명확화

## 단계별 상세 작업

### 1단계: 커맨드 패턴 기반 아키텍처 설계

**목적**: 각 기능을 독립적인 커맨드로 분리하여 확장 가능한 구조를 만듦

**구현 위치**:
- `src/commands/` (신규 디렉토리)
- `src/commands/__init__.py`
- `src/commands/base.py` (추상 베이스 클래스) ✨ 명확한 이름
- `src/commands/report.py` (리포트 생성 커맨드) ✨ 간결한 이름

**작업 내용**:
1. `src/commands/` 디렉토리 생성
2. `BaseCommand` 추상 클래스 작성 (`src/commands/base.py`)
   - `execute()` 메서드 정의
   - `setup_args()` 메서드로 각 커맨드별 CLI 인자 설정
   - 공통 초기화 로직 (로거, 설정 로드 등) 제공
3. `ReportCommand` 클래스 작성 (`src/commands/report.py`)
   - 현재 main.py의 리포트 생성 로직을 이관
   - BaseCommand를 상속받아 구현

**파일명 규칙**:
- 커맨드 파일은 `{기능명}.py` 형식 (예: `report.py`, `monitor.py`)
- 베이스 클래스는 `base.py`로 명확히 구분

**체크리스트**:
- [ ] `src/commands/` 디렉토리 생성
- [ ] `base.py`에 `BaseCommand` 추상 클래스 작성 완료
- [ ] `report.py`에 `ReportCommand` 클래스로 리포트 생성 로직 이관
- [ ] 기존 main.py와 동일한 기능 동작 확인

---

### 2단계: 서비스 레이어 분리

**목적**: 비즈니스 로직을 재사용 가능한 서비스 레이어로 분리

**구현 위치**:
- `src/services/` (신규 디렉토리)
- `src/services/__init__.py`
- `src/services/backup.py` (백업 작업 조회 및 가공 서비스) ✨ 간결한 이름

**작업 내용**:
1. `BackupService` 클래스 작성 (`src/services/backup.py`)
   - `get_jobs_by_period()`: 기간별 백업 작업 조회
   - `get_jobs_by_level()`: 레벨별 백업 작업 조회
   - `classify_jobs()`: 작업 분류 (성공/실패/진행중/취소)
   - API 호출 → 데이터 파싱 → 분류 로직을 캡슐화
2. `ReportCommand`에서 `BackupService` 사용하도록 변경
3. 기존 main.py의 데이터 수집/가공 로직을 서비스로 이관

**파일명 규칙**:
- 서비스 파일은 `{도메인명}.py` 형식 (예: `backup.py`, `schedule.py`)
- 서비스 클래스는 `{Domain}Service` 형식 (예: `BackupService`)

**체크리스트**:
- [ ] `src/services/` 디렉토리 생성
- [ ] `backup.py`에 `BackupService` 클래스 작성 및 테스트
- [ ] `ReportCommand`에서 서비스 레이어 사용
- [ ] 기존 기능 정상 동작 확인

---

### 3단계: main.py를 CLI 진입점으로 재구성 및 파일명 정리

**목적**: main.py를 가벼운 CLI 라우터로 변경하고, 기존 파일명을 더 명확하게 개선

**구현 위치**:
- `src/cli.py` (main.py 리팩터링 후 이름 변경) ✨ CLI 진입점 명확화
- `src/__main__.py` (신규) ✨ 모듈 실행을 위한 진입점

**작업 내용**:
1. CLI 라우터를 `src/cli.py`로 작성
   ```bash
   python -m src report --mode test --send-mail
   python -m src monitor --real-time  # 미래 확장 예시
   python -m src schedule --list       # 미래 확장 예시
   ```
2. `src/__main__.py` 작성하여 모듈 실행 지원
   ```python
   from src.cli import main
   if __name__ == '__main__':
       main()
   ```
3. argparse의 subparsers를 사용하여 커맨드 라우팅
4. 각 커맨드 클래스를 동적으로 로드 및 실행
5. 기존 `main.py`는 하위 호환성을 위해 일시적으로 유지 (deprecation 경고 추가)

**파일명 변경 사항**:
- `src/main.py` → `src/cli.py` (CLI 라우터)
- 신규: `src/__main__.py` (모듈 실행 진입점)

**체크리스트**:
- [ ] `src/cli.py` 작성 (argparse subparsers 구조)
- [ ] `src/__main__.py` 작성
- [ ] `report` 서브커맨드 등록 및 동작 확인
- [ ] 기존 `main.py`에 deprecation 경고 추가
- [ ] 도움말 메시지 정리 (`python -m src --help`)

---

### 4단계: 기존 파일명 개선 및 리포트 생성기 분리

**목적**: 기존 파일명을 더 명확하게 개선하고 리포트 생성기를 재사용 가능한 구조로 변경

**파일명 변경 사항**:
- `src/api/bacula_client.py` → `src/api/client.py` ✨ 간결화 (패키지명에서 이미 api임)
- `src/report/report_generator.py` → `src/report/generator.py` ✨ 간결화
- `src/mail/email_sender.py` → `src/mail/sender.py` ✨ 간결화
- `src/utils/datetime_helper.py` → `src/utils/datetime.py` ✨ 간결화

**구현 위치**:
- `src/api/client.py` (기존 bacula_client.py)
- `src/report/generator.py` (기존 report_generator.py)
- `src/mail/sender.py` (기존 email_sender.py)
- `src/utils/datetime.py` (기존 datetime_helper.py)
- `src/report/formatters/` (신규 - 선택사항)
  - `html.py` (HTML 포맷터)
  - `json.py` (JSON 포맷터 - 미래 확장용)

**작업 내용**:
1. 파일명 변경 및 임포트 경로 업데이트
   - 모든 `from src.api.bacula_client import` → `from src.api.client import`
   - 모든 `from src.report.report_generator import` → `from src.report.generator import`
   - 모든 `from src.mail.email_sender import` → `from src.mail.sender import`
   - 모든 `from src.utils.datetime_helper import` → `from src.utils.datetime import`
2. ReportGenerator에서 하드코딩된 로직 최소화
3. 템플릿 선택 가능하도록 개선 (다양한 리포트 스타일 지원 대비)
4. (선택) Formatter 패턴 도입하여 출력 형식 확장 가능하게 구성

**파일명 규칙**:
- 패키지명이 이미 도메인을 나타내므로 파일명은 간결하게 유지
- `{domain}_{role}.py` 형식 → `{role}.py` 형식으로 변경
- 예: `email_sender.py` → `sender.py` (mail 패키지 내)

**체크리스트**:
- [ ] 파일명 변경 및 모든 임포트 경로 업데이트
- [ ] 변경된 파일 정상 동작 확인 (pytest 실행)
- [ ] ReportGenerator 코드 리뷰 및 개선점 파악
- [ ] 템플릿 선택 기능 추가 (선택사항)
- [ ] Formatter 패턴 도입 검토 및 구현 (선택사항)
- [ ] 기존 리포트 생성 기능 정상 동작 확인

---

### 5단계: 디렉토리 구조 정리 및 문서화

**목적**: 새로운 구조를 명확하게 문서화하고 디렉토리 구조 정리

**구현 위치**:
- `README.md` (수정)
- `docs/architecture.md` (신규)
- 프로젝트 루트 디렉토리

**작업 내용**:
1. 새로운 디렉토리 구조 문서화
   ```
   src/
   ├── api/              # API 클라이언트 (공통)
   ├── models/           # 데이터 모델 (공통)
   ├── services/         # 비즈니스 로직 서비스 레이어 (공통)
   ├── commands/         # 기능별 커맨드 (확장 가능)
   │   ├── base_command.py
   │   ├── report_command.py
   │   └── (future: monitor_command.py, schedule_command.py)
   ├── report/           # 리포트 생성 전용 모듈
   ├── mail/             # 메일 발송 모듈
   ├── utils/            # 유틸리티 (공통)
   └── main.py           # CLI 진입점
   ```
2. `docs/architecture.md` 작성
   - 아키텍처 개요
   - 레이어별 역할 설명
   - 새로운 기능 추가 방법 가이드
3. README.md 업데이트
   - 새로운 CLI 사용법
   - 서브커맨드 설명

**체크리스트**:
- [ ] `docs/architecture.md` 작성 완료
- [ ] README.md 업데이트 (CLI 사용법)
- [ ] 디렉토리 구조 다이어그램 추가

---

### 6단계: 테스트 코드 업데이트

**목적**: 리팩터링된 코드에 맞춰 테스트 코드 업데이트 및 추가

**구현 위치**:
- `tests/test_commands.py` (신규)
- `tests/test_services.py` (신규) ✨ 서비스 레이어 테스트
- `tests/` (기존 테스트 수정)

**파일명 변경 사항**:
- 기존 테스트 파일들도 파일명 변경에 맞춰 임포트 경로 수정 필요

**작업 내용**:
1. `BaseCommand` 및 `ReportCommand` 테스트 작성 (`tests/test_commands.py`)
2. `BackupService` 유닛 테스트 작성 (`tests/test_services.py`)
3. 기존 테스트 파일의 임포트 경로 업데이트
   - `from src.api.bacula_client` → `from src.api.client`
   - `from src.report.report_generator` → `from src.report.generator`
   - 등등
4. 전체 테스트 실행 및 통과 확인

**체크리스트**:
- [ ] `test_commands.py` 작성
- [ ] `test_services.py` 작성 (BackupService 테스트)
- [ ] 기존 테스트 파일 임포트 경로 수정
- [ ] pytest 전체 실행 성공 (`pytest -v`)

---

### 7단계: 코드 품질 검증 및 최종 점검

**목적**: 리팩터링 후 코드 품질 확인 및 flake8 검증

**구현 위치**:
- 전체 프로젝트

**작업 내용**:
1. flake8 코드 스타일 검사 및 수정
2. 전체 기능 통합 테스트
   - 테스트 모드 리포트 생성
   - 프로덕션 모드 리포트 생성
   - 메일 발송 기능
3. 성능 확인 (API 호출 시간 등)
4. 에러 처리 및 로깅 점검

**체크리스트**:
- [ ] flake8 검사 통과
- [ ] 통합 테스트 성공
- [ ] 기존 기능 모두 정상 동작 확인
- [ ] 로그 메시지 정리

---

## 🔍 테스트 방법

### 기본 기능 테스트
```bash
# 1. 유닛 테스트
pytest -v

# 2. flake8 검사
flake8 src/

# 3. 리포트 생성 테스트 (새로운 CLI)
python -m src report --mode test --verbose

# 4. 메일 발송 테스트
python -m src report --mode test --send-mail

# 5. 새로운 CLI 구조 테스트
python -m src --help
python -m src report --help

# 6. 하위 호환성 테스트 (기존 main.py - deprecated)
python -m src.main --mode test  # deprecation 경고 출력 확인
```

### 확장성 검증
```bash
# 새로운 커맨드 추가 시뮬레이션 (실제 구현은 하지 않고 구조만 검증)
# - BaseCommand를 상속받아 새로운 커맨드 추가 가능한지
# - BackupService를 재사용할 수 있는지
```

---

## ⚠️ 중요 주의사항

1. **파일명 변경 순서**: 파일명 변경 시 임포트 깨짐 주의
   - 먼저 새 파일 생성 → 임포트 업데이트 → 기존 파일 삭제 순서로 진행
   - 또는 git mv 사용 후 즉시 임포트 경로 업데이트
2. **하위 호환성 유지**: 기존 `main.py`는 deprecation 경고와 함께 유지
   - 사용자에게 새로운 CLI 사용법 안내
3. **점진적 리팩터링**: 큰 변경사항이므로 단계별로 커밋하여 롤백 가능하게 유지
4. **기존 기능 보존**: 리팩터링 후에도 모든 기존 기능이 정상 동작해야 함
5. **테스트 우선**: 각 단계마다 테스트 코드를 먼저 작성하거나 업데이트
6. **문서화 필수**: 새로운 구조는 반드시 문서로 남겨야 향후 유지보수 가능
7. **임포트 경로 일관성**: 모든 파일명 변경 후 프로젝트 전체 임포트 경로 검증 필요

---

## 📌 관련 정보

- **브랜치**: `refactor/phase-11-modular-architecture`
- **관련 이슈**: N/A
- **의존성**: 기존 모든 기능 정상 동작 필요
- **문서 업데이트**:
  - `README.md` (CLI 사용법 변경)
  - `docs/architecture.md` (신규)
  - `docs/project.md` (프로젝트 구조 업데이트)

---

## 💡 완료 기준

Phase는 다음 조건을 모두 만족할 때 완료됩니다:

1. [ ] 커맨드 패턴 기반 아키텍처 구현 완료 (`BaseCommand`, `ReportCommand`)
2. [ ] 서비스 레이어 분리 완료 (`BackupService`)
3. [ ] main.py 서브커맨드 CLI로 재구성 완료
4. [ ] 기존 모든 기능 정상 동작 (리포트 생성, 메일 발송)
5. [ ] 테스트 코드 작성 및 통과 (pytest 성공)
6. [ ] flake8 검사 통과
7. [ ] 아키텍처 문서 작성 완료 (`docs/architecture.md`)
8. [ ] README.md 업데이트 완료
9. [ ] 새로운 기능 추가 가이드 문서화 완료

---

## 🔗 관련 문서

- [프로젝트 요구사항](./project.md)
- [개발 가이드](./dev.md)
- [이전 태스크](./tasks/)

---

## 📊 예상 디렉토리 구조 (리팩터링 후)

```
baculum/
├── src/
│   ├── api/                    # [공통] API 클라이언트
│   │   ├── __init__.py
│   │   └── client.py           ✨ 변경 (bacula_client.py → client.py)
│   ├── models/                 # [공통] 데이터 모델
│   │   ├── __init__.py
│   │   ├── backup_job.py
│   │   └── report_stats.py
│   ├── services/               # [공통] 비즈니스 로직 서비스 레이어 ✨ 신규
│   │   ├── __init__.py
│   │   └── backup.py           ✨ 신규 (BackupService)
│   ├── commands/               # [확장] 기능별 커맨드 ✨ 신규
│   │   ├── __init__.py
│   │   ├── base.py             ✨ 신규 (BaseCommand)
│   │   └── report.py           ✨ 신규 (ReportCommand)
│   ├── report/                 # [기능] 리포트 생성 전용
│   │   ├── __init__.py
│   │   ├── generator.py        ✨ 변경 (report_generator.py → generator.py)
│   │   └── formatters/         # (선택) 출력 형식 확장
│   │       ├── __init__.py
│   │       ├── html.py         ✨ 신규
│   │       └── json.py         ✨ 신규 (미래 확장용)
│   ├── mail/                   # [기능] 메일 발송
│   │   ├── __init__.py
│   │   └── sender.py           ✨ 변경 (email_sender.py → sender.py)
│   ├── utils/                  # [공통] 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── datetime.py         ✨ 변경 (datetime_helper.py → datetime.py)
│   ├── __main__.py             ✨ 신규 (모듈 실행 진입점)
│   ├── cli.py                  ✨ 변경 (main.py → cli.py)
│   └── main.py                 ⚠️  deprecated (하위 호환성 유지용)
├── templates/
│   └── report_template.html
├── tests/
│   ├── test_commands.py        ✨ 신규
│   ├── test_services.py        ✨ 신규 (BackupService 테스트)
│   └── (기존 테스트들 - 임포트 경로 수정 필요)
├── docs/
│   ├── architecture.md         ✨ 신규
│   ├── project.md
│   └── dev.md
├── README.md
└── requirements.txt
```

### 파일명 변경 매핑 테이블

| 기존 파일명 | 새 파일명 | 변경 이유 |
|------------|----------|-----------|
| `src/api/bacula_client.py` | `src/api/client.py` | 패키지명(api)이 이미 명확하므로 간결화 |
| `src/report/report_generator.py` | `src/report/generator.py` | 패키지명(report)이 이미 명확하므로 간결화 |
| `src/mail/email_sender.py` | `src/mail/sender.py` | 패키지명(mail)이 이미 명확하므로 간결화 |
| `src/utils/datetime_helper.py` | `src/utils/datetime.py` | helper 접미사 제거로 간결화 |
| `src/main.py` | `src/cli.py` | CLI 라우터 역할 명확화 |
| - | `src/__main__.py` | Python 모듈 실행 표준 진입점 |
| - | `src/commands/base.py` | 커맨드 베이스 클래스 |
| - | `src/commands/report.py` | 리포트 커맨드 |
| - | `src/services/backup.py` | 백업 서비스 레이어 |

---

## 🎯 리팩터링의 기대 효과

1. **확장성**: 새로운 기능을 쉽게 추가 가능 (새 커맨드 클래스만 작성)
2. **재사용성**: 공통 로직(API, 서비스)을 여러 기능에서 재사용
3. **유지보수성**: 기능별로 코드가 분리되어 이해하기 쉬움
4. **테스트 용이성**: 레이어별로 독립적인 테스트 가능
5. **협업 효율**: 기능별로 병렬 개발 가능

---

## 📝 향후 추가 가능한 기능 예시

리팩터링 완료 후 다음과 같은 기능을 쉽게 추가할 수 있습니다:

1. **실시간 모니터링 커맨드**
   ```bash
   python -m src.main monitor --real-time
   ```
   - `MonitorCommand` 클래스 작성
   - `BackupService` 재사용하여 실시간 작업 상태 조회

2. **백업 스케줄 관리 커맨드**
   ```bash
   python -m src.main schedule --list
   python -m src.main schedule --add "daily-backup"
   ```
   - `ScheduleCommand` 클래스 작성

3. **통계 대시보드 커맨드**
   ```bash
   python -m src.main stats --range 30days
   ```
   - `StatsCommand` 클래스 작성
   - `BackupService` 재사용

4. **알림 설정 커맨드**
   ```bash
   python -m src.main alert --set-threshold "failure-rate:10%"
   ```
   - `AlertCommand` 클래스 작성
