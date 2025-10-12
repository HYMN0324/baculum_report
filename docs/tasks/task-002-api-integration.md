# Task 002: Bacula API 연동

**Phase**: Phase 2
**상태**: ✅ 완료
**완료일**: 2025-10-12

---

## 📋 작업 개요

Bacula REST API 연동 및 백업 데이터 수집 기능 구현

**브랜치**: `git checkout -b phase-2-api`

---

## 2.1 API 클라이언트 구현

### API 분석 및 설계
- [x] Bacula REST API 문서 검토 (https://bacula.org/downloads/baculum/baculum-api-v1)
- [x] `test.py` 코드 분석 - API 호출 방식, 인증 방법, 응답 구조 파악
- [x] `src/api/__init__.py` 생성

### BaculaClient 클래스 구현
- [x] `src/api/bacula_client.py` 생성
  - BaculaClient 클래스 설계
  - `__init__`: API URL, 인증 정보 초기화
  - `connect()`: API 연결 테스트
  - `get_jobs()`: 백업 작업 목록 조회
  - `_request()`: 공통 HTTP 요청 처리 (타임아웃, 재시도)

### 설정 및 인증
- [x] `.env`에서 설정 로드 (python-dotenv 사용)
  ```python
  BACULUM_API_HOST='172.16.1.0'
  BACULUM_API_PORT='9096'
  BACULUM_API_USERNAME=...
  BACULUM_API_PASSWORD=...
  ```

### 에러 처리 및 로깅
- [x] 타임아웃 설정 (requests timeout=10)
- [x] 재시도 로직 추가 (최대 3회, 지수 백오프)
- [x] 커스텀 예외 클래스 정의 (BaculaAPIError, ConnectionError, TimeoutError)
- [x] 상세 로깅 추가 (요청/응답, 에러 정보)

---

## 2.2 데이터 수집 로직

### 시간 범위 설정
- [x] 시간 범위 설정 함수 구현
  - 테스트 모드: 1주일 전 ~ 현재
  - 프로덕션 모드: 전일 22시 ~ 실행 시점

### 데이터 파싱
- [x] API 응답 데이터 파싱 함수 구현
- [x] 백업 상태 분류 로직 (성공/실패/진행중)
- [x] **실패한 백업의 에러 로그 추출** (필수 - 강조 표시)

---

## 2.3 API 테스트

### 실제 API 연동 테스트
- [x] **실제 API 호출 테스트** (실제 Bacula 시스템 대상)
  - API 연결 확인
  - 응답 데이터 구조 파악 및 저장 (JSON 샘플)
  - API 호출 시간 측정 (10초 이하 확인)

### 파싱 로직 구현 및 테스트
- [x] 응답 데이터 기반으로 파싱 로직 구현
- [x] 파싱 로직 단위 테스트 작성 (실제 응답 샘플 사용)

### Phase 완료
- [x] Phase 2 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-2-api --no-ff -m "Phase 2: Bacula API 연동 완료"
  git tag v0.2-phase2
  ```

---

## 📝 작업 결과

- Bacula API 클라이언트 클래스 구현 완료
- API 연결 테스트 및 데이터 수집 성공
- 에러 처리 및 재시도 로직 구현
- API 호출 성능 요구사항 충족 (10초 이하)

---

## 🔗 관련 문서

- [Bacula API 문서](https://bacula.org/downloads/baculum/baculum-api-v1)
- [프로젝트 요구사항](../project.md)
