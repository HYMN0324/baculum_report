# Task Active: Phase 10 - 백업 리포트 필터링 및 표시 개선

**Phase**: 10
**상태**: ✅ 완료
**시작일**: 2025-10-17
**완료일**: 2025-10-17

## 📋 작업 개요

Phase 10에서는 백업 리포트의 가독성과 유용성을 개선합니다. 성공한 백업 목록에서 Full 백업만 표시하도록 필터링하고, 실패 백업 목록의 구조를 개선하여 상세보기 링크를 추가합니다. 이를 통해 사용자는 핵심 정보에 빠르게 접근하고, 백업 상태를 효율적으로 모니터링할 수 있습니다.

**브랜치**: `git checkout -b phase-10-report-table-optimization` (작업 시작 시 생성)

## 단계별 상세 작업

### 10.1 환경 변수 설정 추가

**담당 Agent**: `general-purpose`

**목적**: Baculum Web UI 접근을 위한 호스트 및 포트 정보를 환경 변수로 관리

**구현 위치**:
- `/root/dev/baculum/.env.example`
- `/root/dev/baculum/.env`

**작업 내용**:
- `.env.example` 파일에 Baculum Web UI 설정 추가:
  ```
  # Baculum Web Interface (Optional)
  BACULUM_WEB_HOST=172.16.1.0
  BACULUM_WEB_PORT=9095
  ```
- 실제 `.env` 파일에도 동일한 설정 추가:
  ```
  BACULUM_WEB_HOST=172.16.1.0
  BACULUM_WEB_PORT=9095
  ```
- 주석으로 용도 설명: "백업 작업 상세보기 링크에 사용되는 Baculum Web UI 접속 정보"
- Phase 9에서 이미 `.env.example`에 추가되었으나, 실제 `.env` 파일에는 구체적인 IP 설정 필요

**체크리스트**:
- [ ] `.env.example`에 BACULUM_WEB_HOST, BACULUM_WEB_PORT 확인/추가
- [ ] 실제 `.env` 파일에 `BACULUM_WEB_HOST=172.16.1.0` 추가
- [ ] 실제 `.env` 파일에 `BACULUM_WEB_PORT=9095` 추가
- [ ] 주석으로 설정 용도 명확히 기재

---

### 10.2 성공한 백업 목록 필터링 - Full 백업만 표시

**담당 Agent**: `python-pep8-senior-dev`

**목적**: 성공한 백업 목록에서 Incremental 백업을 제외하고 Full 백업만 표시하여 핵심 정보에 집중

**구현 위치**:
- `/root/dev/baculum/src/report/report_generator.py` - `generate_report()` 메서드 (라인 112-126)
- `/root/dev/baculum/src/main.py` - API 호출 로직 (라인 132-160)

**작업 내용**:
- `src/report/report_generator.py`의 `generate_report()` 메서드에서 성공한 백업 필터링 로직 추가:
  ```python
  # 작업 분류 (type='B'인 Backup 작업만 포함, Restore 작업 제외)
  success_jobs = [
      job for job in jobs
      if job.is_success and job.is_backup and job.level == 'F'  # Full 백업만
  ]
  failed_jobs = [job for job in jobs if job.is_failed]  # 모든 레벨 포함
  running_jobs = [job for job in jobs if job.is_running]  # 모든 레벨 포함
  ```
- `src/main.py`의 API 호출 로직은 유지 (모든 레벨 조회하여 통계 계산):
  - Full, Incremental, Differential 모두 조회
  - `jobs` 리스트에 모든 작업 포함
  - `ReportStats` 계산에 모든 작업 사용하여 백업 현황 요약 통계 생성
- 필터링 후 빈 리스트인 경우에도 정상 처리 (템플릿에서 조건부 렌더링)

**체크리스트**:
- [ ] `success_jobs` 필터링에 `job.level == 'F'` 조건 추가
- [ ] `failed_jobs`와 `running_jobs`는 모든 레벨 포함 확인
- [ ] `BackupStats` 계산에는 모든 작업 사용 확인
- [ ] API 호출은 Full, Incremental, Differential 모두 조회하는지 확인
- [ ] PEP 8 코드 스타일 준수 (`flake8 src/report/report_generator.py`)

---

### 10.3 성공한 백업 테이블 명칭 및 레벨 컬럼 제거

**담당 Agent**: `fullstack-web-optimizer`

**목적**: Full 백업만 표시하므로 테이블 명칭 변경 및 불필요한 레벨 컬럼 제거

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 성공한 백업 목록 섹션 (라인 326-367)

**작업 내용**:
- 테이블 헤더 제목 변경:
  - 기존: `<h2>✅ 성공한 백업 목록</h2>`
  - 변경: `<h2>✅ Full 백업 성공 목록</h2>`
- 테이블 헤더(`<thead>`)에서 "레벨" 컬럼 제거:
  - 기존 컬럼 순서 (8개): 작업 ID, 작업명, **레벨**, 시작 시간, 완료 시간, 소요 시간, 백업 크기, 상세보기
  - 변경 컬럼 순서 (7개): 작업 ID, 작업명, 시작 시간, 완료 시간, 소요 시간, 백업 크기, 상세보기
  ```html
  <thead>
      <tr>
          <th>작업 ID</th>
          <th>작업명</th>
          <!-- <th>레벨</th> 제거 -->
          <th>시작 시간</th>
          <th>완료 시간</th>
          <th>소요 시간</th>
          <th>백업 크기</th>
          <th>상세보기</th>
      </tr>
  </thead>
  ```
- 테이블 본문(`<tbody>`)에서 레벨 데이터 셀 제거:
  ```html
  <tbody>
      {% for job in success_jobs %}
      <tr>
          <td>{{ job.job_id }}</td>
          <td>{{ job.job_name }}</td>
          <!-- <td>{{ job.level_display }}</td> 제거 -->
          <td>{{ job.start_time.strftime('%Y-%m-%d %H:%M:%S') }}</td>
          <td>{{ job.end_time.strftime('%Y-%m-%d %H:%M:%S') }}</td>
          <td>{{ job.duration_display }}</td>
          <td>{{ job.backup_size_display }}</td>
          <td style="text-align: center;">
              {% if baculum_web_url %}
              ...
              {% endif %}
          </td>
      </tr>
      {% endfor %}
  </tbody>
  ```
- 상세보기 링크는 Phase 9에서 이미 구현되어 있으므로 유지

**체크리스트**:
- [ ] `<h2>` 제목이 "✅ Full 백업 성공 목록"으로 변경됨
- [ ] `<thead>` 섹션에서 "레벨" `<th>` 제거 완료
- [ ] `<tbody>` 섹션에서 `{{ job.level_display }}` `<td>` 제거 완료
- [ ] 테이블 컬럼 정렬 확인: 7개 컬럼
- [ ] HTML 문법 검증 및 들여쓰기 일관성 확인

---

### 10.4 실패 백업 목록 테이블 명칭 변경

**담당 Agent**: `fullstack-web-optimizer`

**목적**: 일관성 있는 명명 규칙 적용

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 실패한 백업 상세 섹션 (라인 288-324)

**작업 내용**:
- 테이블 헤더 제목 변경:
  - 기존: `<h2>⚠️ 실패한 백업 상세</h2>`
  - 변경: `<h2>⚠️ 실패 백업 목록</h2>`
- HTML 코드 수정:
  ```html
  <h2>⚠️ 실패 백업 목록</h2>
  ```

**체크리스트**:
- [ ] 테이블 제목을 "⚠️ 실패 백업 목록"으로 변경
- [ ] 스타일 속성 유지 확인

---

### 10.5 실패 백업 목록 컬럼 구조 변경 - 클라이언트, 에러 개수, 에러 로그 제거

**담당 Agent**: `fullstack-web-optimizer`

**목적**: 실패 백업 목록에서 불필요한 컬럼을 제거하여 간결하게 구성

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 실패 백업 상세 섹션 (라인 290-323)

**작업 내용**:
- 테이블 헤더 HTML 수정 (클라이언트, 에러 개수, 에러 로그 제거):
  - 기존 컬럼 (8개): 작업 ID, 작업명, **클라이언트**, 레벨, 시작 시간, 실패 시간, **에러 개수**, **에러 로그**
  - 변경 컬럼 (5개 + 상세보기): 작업 ID, 작업명, 레벨, 시작 시간, 실패 시간, 상세보기
  ```html
  <thead>
      <tr>
          <th>작업 ID</th>
          <th>작업명</th>
          <!-- <th>클라이언트</th> 제거 -->
          <th>레벨</th>
          <th>시작 시간</th>
          <th>실패 시간</th>
          <!-- <th>에러 개수</th> 제거 -->
          <!-- <th>에러 로그</th> 제거 -->
          <th>상세보기</th>
      </tr>
  </thead>
  ```
- 테이블 데이터 행 HTML 수정 (해당 컬럼 제거):
  ```html
  <tbody>
      {% for job in failed_jobs %}
      <tr style="background-color: #fadbd8;">
          <td>{{ job.job_id }}</td>
          <td>{{ job.job_name }}</td>
          <!-- <td>{{ job.client_name }}</td> 제거 -->
          <td><span class="status-badge">{{ job.level_display }}</span></td>
          <td>{{ job.start_time.strftime('%Y-%m-%d %H:%M') }}</td>
          <td>{{ job.end_time.strftime('%Y-%m-%d %H:%M') if job.end_time else '-' }}</td>
          <!-- <td style="text-align: center;">{{ job.job_errors }}</td> 제거 -->
          <!-- 에러 로그 섹션 제거 -->
          <td style="text-align: center;">
              <!-- 상세보기 링크 추가 (10.6에서 구현) -->
          </td>
      </tr>
      {% endfor %}
  </tbody>
  ```

**체크리스트**:
- [ ] 테이블 헤더에서 "클라이언트" `<th>` 제거
- [ ] 테이블 헤더에서 "에러 개수" `<th>` 제거
- [ ] 테이블 헤더에서 "에러 로그" `<th>` 제거
- [ ] 데이터 행에서 `{{ job.client_name }}` `<td>` 제거
- [ ] 데이터 행에서 `{{ job.job_errors }}` `<td>` 제거
- [ ] 데이터 행에서 에러 로그 표시 `<td>` 제거
- [ ] 레이아웃 깨짐 없이 정상 렌더링 확인

---

### 10.6 실패 백업 목록에 상세보기 링크 추가

**담당 Agent**: `fullstack-web-optimizer`

**목적**: 실패한 백업도 성공한 백업과 동일하게 Baculum Web UI 상세보기 링크 제공

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 실패한 백업 상세 섹션

**작업 내용**:
- 실패 백업 목록 테이블에 "상세보기" 컬럼 추가 (성공한 백업 목록과 동일):
  ```html
  <thead>
      <tr>
          ...
          <th>상세보기</th>
      </tr>
  </thead>
  <tbody>
      {% for job in failed_jobs %}
      <tr style="background-color: #fadbd8;">
          ...
          <td style="text-align: center;">
              {% if baculum_web_url %}
              <a href="{{ baculum_web_url }}/web/job/history/{{ job.job_id }}/"
                 target="_blank"
                 title="Baculum에서 상세 정보 보기"
                 style="color: #3498db; text-decoration: none; font-size: 18px;">
                  🔍
              </a>
              {% else %}
              <span style="color: #95a5a6;">-</span>
              {% endif %}
          </td>
      </tr>
      {% endfor %}
  </tbody>
  ```
- 링크 스타일은 성공한 백업 목록과 동일하게 유지
- target="_blank"로 새 탭에서 열리도록 설정
- `baculum_web_url`이 없는 경우 "-" 표시
- Phase 9에서 이미 `baculum_web_url` 변수가 템플릿에 전달되고 있으므로 동일하게 사용

**체크리스트**:
- [ ] 테이블 헤더에 "상세보기" `<th>` 추가
- [ ] 데이터 행에 상세보기 링크 `<td>` 추가
- [ ] 새 탭에서 열리도록 설정 (target="_blank")
- [ ] `baculum_web_url` 없는 경우 "-" 표시 확인
- [ ] 성공한 백업 목록과 동일한 스타일 적용

---

### 10.7 통합 테스트 및 검증

**담당 Agent**: `general-purpose`

**목적**: 전체 기능 동작 확인 및 품질 보증

**구현 위치**: 프로젝트 루트 디렉토리

**작업 내용**:
- 환경 변수 설정 확인:
  ```bash
  grep -E "BACULUM_WEB_HOST|BACULUM_WEB_PORT" .env
  ```
- 백업 리포트 생성 테스트:
  ```bash
  python -m src.main --mode test
  ```
- HTML 리포트 렌더링 확인:
  - Full 백업만 "✅ Full 백업 성공 목록"에 표시되는지 확인
  - Incremental 백업이 제외되는지 확인
  - "⚠️ 실패 백업 목록"에 클라이언트, 에러 개수, 에러 로그 컬럼이 없는지 확인
  - 실패 백업 목록에 상세보기 링크가 정상 표시되는지 확인
  - 성공한 백업 목록에서 레벨 컬럼이 제거되었는지 확인
- 상세보기 링크 동작 확인:
  - 링크 클릭 시 새 탭에서 Baculum Web UI가 열리는지 확인
  - URL 형식: `http://172.16.1.0:9095/web/job/history/{jobID}/`
- 테스트 이메일 발송:
  ```bash
  python -m src.main --mode test --send-mail
  ```
- 브라우저 및 이메일 클라이언트에서 렌더링 확인 (CSS, 레이아웃, 링크 동작)

**체크리스트**:
- [ ] 환경 변수 정상 로드 확인
- [ ] Full 백업 필터링 정상 동작
- [ ] 성공한 백업 목록 제목 "✅ Full 백업 성공 목록" 확인
- [ ] 성공한 백업 목록에서 레벨 컬럼 제거 확인
- [ ] 성공한 백업 목록에 Full 백업만 표시되는지 확인
- [ ] 실패 백업 목록 제목 "⚠️ 실패 백업 목록" 확인
- [ ] 실패 백업 목록에서 클라이언트, 에러 개수, 에러 로그 제거 확인
- [ ] 실패 백업 목록에 상세보기 링크 추가 확인
- [ ] 상세보기 링크 정상 동작 확인 (새 탭 열림)
- [ ] 백업 현황 요약에 Full, Incremental 통계 정상 표시
- [ ] 테스트 이메일 발송 성공
- [ ] 브라우저 및 이메일 클라이언트 렌더링 정상 확인
- [ ] flake8 검증 통과 (`flake8 src/`)

---

## 🔍 테스트 방법

### 개발 환경 테스트
```bash
# 1. 환경 변수 설정 확인
cat .env | grep BACULUM_WEB
# 출력 예상:
# BACULUM_WEB_HOST=172.16.1.0
# BACULUM_WEB_PORT=9095

# 2. 테스트 모드로 리포트 생성
python -m src.main --mode test

# 3. 생성된 HTML 파일 확인
# reports/mail_YYYYMMDDHHMMSS.html

# 4. 브라우저에서 HTML 파일 열어서 확인
# - "✅ Full 백업 성공 목록" 제목
# - 레벨 컬럼 제거 확인 (7개 컬럼)
# - Full 백업만 표시되는지 확인
# - "⚠️ 실패 백업 목록" 제목
# - 클라이언트, 에러 개수, 에러 로그 컬럼 제거 확인 (6개 컬럼)
# - 실패 백업 목록에 상세보기 링크 확인
# - 백업 현황 요약의 Full/Incremental 통계 확인

# 5. 상세보기 링크 테스트
# - 링크 URL 형식: http://172.16.1.0:9095/web/job/history/{jobID}/
# - 클릭 시 새 탭에서 Baculum 페이지 열림 확인

# 6. 메일 발송 테스트
python -m src.main --mode test --send-mail

# 7. 이메일 클라이언트에서 확인
# - 모든 테이블 레이아웃 정상 렌더링
# - 상세보기 링크 작동
# - 제목 및 컬럼 변경사항 반영
```

### flake8 코드 검증
```bash
# 수정된 Python 파일 검증
flake8 src/report/report_generator.py
flake8 src/main.py

# 전체 프로젝트 검증
flake8 src/
```

### 확인 사항
1. **성공한 백업 목록**
   - 제목: "✅ Full 백업 성공 목록"
   - 컬럼: 작업 ID, 작업명, 시작 시간, 완료 시간, 소요 시간, 백업 크기, 상세보기 (7개)
   - 레벨 컬럼이 제거되었는지
   - Full 백업만 표시되는지
   - 상세보기 링크가 정상 작동하는지

2. **실패 백업 목록**
   - 제목: "⚠️ 실패 백업 목록"
   - 컬럼: 작업 ID, 작업명, 레벨, 시작 시간, 실패 시간, 상세보기 (6개)
   - 클라이언트 컬럼이 제거되었는지
   - 에러 개수 컬럼이 제거되었는지
   - 에러 로그 컬럼이 제거되었는지
   - 상세보기 링크가 추가되었는지
   - 모든 레벨(Full, Incremental, Differential) 포함되는지

3. **백업 현황 요약**
   - Full 백업 통계 정상 표시 (전체, 성공, 실패)
   - Incremental 백업 통계 정상 표시 (전체, 성공, 실패)
   - Differential 백업 통계 정상 표시 (전체, 성공, 실패)

4. **환경 변수 설정**
   - `.env` 파일에 `BACULUM_WEB_HOST=172.16.1.0` 추가됨
   - `.env` 파일에 `BACULUM_WEB_PORT=9095` 추가됨
   - 상세보기 링크가 올바른 URL로 생성됨

5. **이메일 호환성**
   - Gmail, Outlook 등에서 정상 렌더링
   - 모든 테이블이 정렬되어 표시됨
   - 링크와 스타일이 정상 작동

---

## ⚠️ 중요 주의사항

1. **Incremental 통계는 유지**
   - 백업 현황 요약 섹션의 Incremental 통계는 제거하지 않음
   - Full, Incremental, Differential 모든 레벨의 통계가 표시되어야 함
   - API 호출 시 모든 레벨을 조회하여 통계 계산에 사용

2. **실패한 백업은 모든 레벨 포함**
   - 실패 백업 목록에는 Full, Incremental, Differential 모두 표시
   - 레벨 컬럼은 실패한 백업에서 유지 (어떤 레벨에서 실패했는지 파악 필요)
   - 성공한 백업 목록만 Full로 제한

3. **데이터 필터링 위치**
   - API 호출은 모든 레벨 조회 (통계 목적)
   - 필터링은 리포트 생성 단계에서 수행 (`ReportGenerator.generate_report()`)
   - `main.py`에서는 모든 작업을 조회하여 `jobs` 리스트에 포함

4. **환경 변수 관리**
   - `.env` 파일은 Git에 커밋하지 않음 (`.gitignore` 확인)
   - `.env.example`은 Git에 커밋하여 템플릿으로 사용
   - `BACULUM_WEB_HOST`는 선택사항이므로 없어도 리포트 생성은 정상 작동

5. **HTML 테이블 일관성**
   - 컬럼 개수 변경 시 `<thead>`와 `<tbody>`의 `<th>`, `<td>` 개수 일치 확인
   - 들여쓰기는 기존 템플릿 스타일 유지 (4 스페이스)
   - 인라인 CSS 스타일 유지 (이메일 호환성)

6. **이메일 호환성**
   - 테이블 레이아웃 변경 후 Gmail, Outlook에서 테스트 필수
   - 일부 이메일 클라이언트는 복잡한 CSS를 지원하지 않으므로 간단한 스타일 유지
   - 상세보기 링크는 `target="_blank"` 속성 유지

7. **코드 품질**
   - 모든 Python 코드는 PEP 8 준수
   - 리스트 컴프리헨션 사용 시 가독성 고려
   - 필터링 로직에 명확한 주석 추가
   - HTML 템플릿의 Jinja2 문법 정확성 검증

8. **역호환성**
   - 기존 Phase 9 기능 (상세보기 링크, 실패 시간 명칭) 유지
   - Config 클래스의 기존 메서드 변경 없음
   - BackupJob 모델의 기존 프로퍼티 유지

9. **에러 로그 제거 이유**
   - 실패한 백업의 에러 로그는 상세보기 링크를 통해 Baculum Web UI에서 확인
   - 이메일 리포트에서는 간결한 정보만 제공하여 가독성 향상
   - 상세한 에러 정보가 필요한 경우 Baculum Web UI 접속

---

## 📌 관련 정보

- **브랜치**: `phase-10-report-table-optimization`
- **관련 이슈**: N/A
- **의존성**:
  - Phase 9 (리포트 레이아웃 개선 및 상세보기 기능) 완료 필요
  - 추가 Python 패키지 설치 불필요
  - Baculum API 및 Web 인터페이스 접근 가능 환경
- **문서 업데이트**:
  - `README.md`: .env 설정 섹션에 `BACULUM_WEB_HOST=172.16.1.0`, `BACULUM_WEB_PORT=9095` 추가
  - `.env.example`: 기존 템플릿 확인
  - `docs/task-active.md`: Phase 10 작업 문서화
- **테스트 데이터 필요**:
  - Full 백업 성공 데이터 (성공 목록 필터링 확인)
  - Incremental 백업 성공 데이터 (통계 확인, 목록에서 제외 확인)
  - Full 및 Incremental 실패 데이터 (실패 목록에 모두 표시 확인)
  - 상세보기 링크 테스트용 jobID

---

## 💡 완료 기준

Phase 10은 다음 조건을 모두 만족할 때 완료됩니다:

1. [ ] `.env` 파일에 `BACULUM_WEB_HOST=172.16.1.0` 추가됨
2. [ ] `.env` 파일에 `BACULUM_WEB_PORT=9095` 추가됨
3. [ ] 성공한 백업 목록 제목이 "✅ Full 백업 성공 목록"으로 변경됨
4. [ ] 성공한 백업 목록에서 레벨 컬럼이 제거됨 (7개 컬럼)
5. [ ] 성공한 백업 목록에 Full 백업만 표시됨 (Incremental 제외)
6. [ ] 실패 백업 목록 제목이 "⚠️ 실패 백업 목록"으로 변경됨
7. [ ] 실패 백업 목록에서 클라이언트 컬럼이 제거됨
8. [ ] 실패 백업 목록에서 에러 개수 컬럼이 제거됨
9. [ ] 실패 백업 목록에서 에러 로그 컬럼이 제거됨
10. [ ] 실패 백업 목록에 상세보기 링크가 추가됨 (6개 컬럼)
11. [ ] 실패 백업 목록에 모든 레벨(Full, Incremental, Differential) 포함됨
12. [ ] 백업 현황 요약에 Full, Incremental 통계가 정상 표시됨
13. [ ] 상세보기 링크가 `http://172.16.1.0:9095/web/job/history/{jobID}/`로 생성됨
14. [ ] 상세보기 링크 클릭 시 Baculum 웹 페이지로 이동함 (새 탭)
15. [ ] 모든 수정 코드가 flake8 검사를 통과함
16. [ ] 브라우저에서 HTML 리포트가 정상적으로 표시됨
17. [ ] 이메일 클라이언트(Gmail, Outlook)에서 리포트가 정상적으로 표시됨
18. [ ] Git 커밋 완료 및 main 브랜치에 병합

---

## 🔗 관련 문서

- [프로젝트 요구사항](./project.md)
- [개발 가이드](./dev.md)
- [이전 태스크](./tasks/)
- [Phase 9: 리포트 레이아웃 개선 및 상세보기 기능](./tasks/task-009-report-layout-improvements.md)
