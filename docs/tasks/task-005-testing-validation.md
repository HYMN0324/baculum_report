# Task 005: 테스트 및 검증

**Phase**: Phase 5
**상태**: ✅ 완료
**완료일**: 2025-10-12

---

## 📋 작업 개요

단위 테스트, 통합 테스트, 성능 테스트 수행

**브랜치**: `git checkout -b phase-5-test`

---

## 5.1 단위 테스트 (pytest 사용)

### 테스트 환경 설정
- [x] pytest 관련 패키지 설치 (`pytest`, `pytest-cov`, `pytest-mock`)
- [x] `tests/__init__.py` 생성
- [x] `tests/fixtures/` 디렉토리 생성
  - Phase 2.3에서 수집한 실제 API 응답 샘플 저장
  - `api_response_sample.json` (정상 응답)
  - `api_response_failed.json` (실패 케이스)

### 테스트 코드 작성
- [x] `tests/test_api.py` - API 클라이언트 테스트
  - **실제 응답 샘플 사용** (fixtures/api_response_sample.json)
  - 응답 파싱 로직 테스트
  - 데이터 변환 테스트
  - 에러 응답 처리 테스트
- [x] `tests/test_models.py` - 데이터 모델 테스트
  - BackupJob 프로퍼티 테스트
  - 상태 분류 테스트
- [x] `tests/test_report.py` - 리포트 생성 테스트
  - 템플릿 렌더링 테스트
  - 파일 생성 테스트
- [x] `tests/test_utils.py` - 유틸리티 테스트
  - 시간 계산 로직 테스트
  - 설정 로드 테스트

### 테스트 설정 및 실행
- [x] pytest 설정 파일 생성 (`pytest.ini`)
- [x] 테스트 실행 및 커버리지 확인 (`pytest -v --cov=src`)

---

## 5.2 통합 테스트 (실제 API 사용)

### 실제 환경 테스트
- [x] **실제 Bacula API 연결** (.env 설정 사용)
- [x] 1주일 전 데이터로 전체 프로세스 테스트
- [x] 생성된 HTML 파일 검증

### 시나리오 테스트
- [x] 다양한 시나리오 테스트
  - 모든 백업 성공
  - 일부 백업 실패
  - 진행 중 백업 있음
  - API 오류 상황 (가능하면)

---

## 5.3 성능 테스트

### 성능 요구사항 검증
- [x] API 호출 시간 측정 (10초 이하 확인)
- [x] 대량 데이터 처리 성능 검증
- [x] 메모리 사용량 확인

### Phase 완료
- [x] Phase 5 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-5-test --no-ff -m "Phase 5: 테스트 및 검증 완료"
  git tag v0.5-phase5
  ```

---

## 📝 작업 결과

- 단위 테스트 작성 완료 (커버리지 80% 이상)
- 통합 테스트 성공
- 성능 요구사항 충족 확인
  - API 호출 시간: 10초 이하 ✓
  - 오류율: 0.1% 이하 ✓

---

## 🧪 테스트 실행 방법

```bash
# 모든 테스트 실행
pytest -v

# 커버리지 포함
pytest -v --cov=src

# 특정 테스트만 실행
pytest tests/test_api.py -v
```

---

## 🔗 관련 문서

- [프로젝트 요구사항](../project.md)
- [개발 가이드](../dev.md)
