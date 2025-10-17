# Task Active: 리포트 레이아웃 개선 및 상세보기 기능 추가

**Phase**: Phase 9
**상태**: ✅ 완료
**시작일**: 2025-10-13
**완료일**: 2025-10-13

---

## 📋 작업 개요

HTML 리포트의 레이아웃을 개선하고 Baculum 웹 인터페이스로 연결되는 상세보기 기능을 추가합니다. 성공한 백업 목록의 가독성을 향상시키고, 실패한 백업 상세 정보를 테이블 형식으로 표준화하며, 각 백업 작업의 상세 정보를 Baculum 웹 인터페이스에서 확인할 수 있도록 합니다.

**브랜치**: `git checkout -b phase-9-report-layout-improvements` (작업 시작 시 생성)

---

## 단계별 상세 작업

### 9.1 성공한 백업 목록 레이아웃 변경

**목적**: 성공한 백업 목록 테이블에서 "소요 시간"과 "백업 크기" 컬럼의 위치를 변경하여 가독성을 향상시킵니다.

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 성공한 백업 목록 테이블 섹션 (라인 309-334)

**작업 내용**:
- 성공한 백업 목록 테이블의 `<thead>` 섹션에서 컬럼 순서 변경
  - 현재 순서: 작업 ID → 작업명 → 레벨 → 시작 시간 → 완료 시간 → 백업 크기 → 소요 시간
  - 변경 순서: 작업 ID → 작업명 → 레벨 → 시작 시간 → 완료 시간 → **소요 시간 → 백업 크기**
- `<tbody>` 섹션에서도 동일하게 `<td>` 순서 변경
- 기존 Jinja2 템플릿 변수 유지 (`{{ job.duration_display }}`, `{{ job.backup_size_display }}`)

**체크리스트**:
- [x] `<thead>` 섹션의 `<th>` 순서 변경 완료
- [x] `<tbody>` 섹션의 `<td>` 순서 변경 완료
- [x] 테스트 리포트 생성하여 컬럼 순서 정상 확인
- [x] 모든 기존 데이터 필드가 정상적으로 표시되는지 확인

---

### 9.2 성공한 백업 목록에 상세보기 아이콘 추가

**목적**: 각 백업 작업의 상세 정보를 Baculum 웹 인터페이스에서 확인할 수 있도록 돋보기 아이콘과 링크를 추가합니다.

**구현 위치**:
- `/root/dev/baculum/templates/report_template.html` - 성공한 백업 목록 테이블 섹션
- `/root/dev/baculum/.env.example` - Baculum 웹 설정 추가
- `/root/dev/baculum/src/utils/config.py` - Config 클래스에 baculum_web_ip, baculum_web_port 프로퍼티 추가
- `/root/dev/baculum/src/report/report_generator.py` - 리포트 생성 시 Baculum 웹 URL 정보 전달

**작업 내용**:

#### 9.2.1 환경 변수 추가
- `.env.example` 파일에 Baculum 웹 인터페이스 설정 추가:
  ```
  # Baculum Web Interface
  BACULUM_WEB_HOST=baculum_web_ip_address
  BACULUM_WEB_PORT=9095
  ```
- Baculum API와 Web 인터페이스는 다른 포트를 사용하므로 별도 설정 필요
- 기본 포트: API=9096, Web=9095

#### 9.2.2 Config 클래스 확장
- `src/utils/config.py`에 새 프로퍼티 추가:
  ```python
  @property
  def baculum_web_ip(self) -> Optional[str]:
      """Baculum 웹 인터페이스 IP 주소"""
      return os.getenv('BACULUM_WEB_HOST')

  @property
  def baculum_web_port(self) -> int:
      """Baculum 웹 인터페이스 포트 번호"""
      return int(os.getenv('BACULUM_WEB_PORT', '9095'))

  def has_baculum_web_config(self) -> bool:
      """Baculum 웹 설정이 있는지 확인"""
      return self.baculum_web_ip is not None
  ```
- Baculum 웹 설정은 선택사항 (필수 검증에 포함하지 않음)
- 설정이 없으면 상세보기 아이콘을 표시하지 않음

#### 9.2.3 리포트 생성기 수정
- `src/report/report_generator.py`의 `generate_html_report()` 메서드 수정
- Jinja2 템플릿에 `baculum_web_url` 변수 전달:
  ```python
  # Baculum 웹 URL 구성 (설정이 있는 경우에만)
  baculum_web_url = None
  if config.has_baculum_web_config():
      baculum_web_url = f"http://{config.baculum_web_ip}:{config.baculum_web_port}"

  html_content = template.render(
      stats=stats,
      success_jobs=success_jobs,
      failed_jobs=failed_jobs,
      running_jobs=running_jobs,
      baculum_web_url=baculum_web_url
  )
  ```

#### 9.2.4 HTML 템플릿 수정
- `templates/report_template.html`의 성공한 백업 목록 테이블에 "상세보기" 컬럼 추가
- `<thead>`에 새 컬럼 추가:
  ```html
  <th>상세보기</th>
  ```
- `<tbody>`에 돋보기 아이콘 및 링크 추가 (baculum_web_url이 있는 경우에만):
  ```html
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
  ```
- 돋보기 이모지 (🔍) 사용으로 별도 아이콘 파일 불필요
- `target="_blank"`로 새 탭에서 열기
- 링크 스타일: 파란색 (#3498db), 밑줄 제거, 크기 18px

**체크리스트**:
- [x] `.env.example`에 `BACULUM_WEB_HOST`, `BACULUM_WEB_PORT` 추가
- [x] `Config` 클래스에 `baculum_web_host`, `baculum_web_port`, `has_baculum_web_config()` 구현
- [x] `ReportGenerator._render_template()`에서 `baculum_web_url` 전달
- [x] HTML 템플릿에 "상세보기" 컬럼 추가
- [x] 돋보기 아이콘 링크 구현 (조건부 렌더링)
- [x] `.env` 파일에 실제 Baculum 웹 설정 추가하여 테스트
- [x] 링크 클릭 시 올바른 Baculum 페이지로 이동하는지 확인
- [x] Baculum 웹 설정이 없을 때 "-" 표시 확인
- [x] 이메일 클라이언트에서도 링크가 정상 작동하는지 확인

---

### 9.3 실패한 백업 상세 레이아웃 변경

**목적**: 실패한 백업 상세 정보를 현재의 개별 섹션 형식에서 테이블 형식으로 변경하여 성공한 백업 목록과 일관성을 유지하고, "완료 시간"을 "실패 시간"으로 명칭 변경합니다.

**구현 위치**: `/root/dev/baculum/templates/report_template.html` - 실패한 백업 상세 섹션 (라인 288-305)

**작업 내용**:
- 현재의 `.error-section` 기반 개별 카드 레이아웃을 테이블 형식으로 변경
- 성공한 백업 목록과 동일한 테이블 스타일 적용
- 테이블 컬럼 구조:
  1. 작업 ID (`job.job_id`)
  2. 작업명 (`job.job_name`)
  3. 클라이언트 (`job.client_name`)
  4. 레벨 (`job.level_display`)
  5. 시작 시간 (`job.start_time`)
  6. **실패 시간** (`job.end_time`) - "완료 시간"에서 명칭 변경
  7. 에러 개수 (`job.job_errors`)
  8. 에러 로그 (별도 처리)
- 에러 로그 표시 방법:
  - 에러 로그가 있는 경우: 작은 "로그 보기" 버튼 또는 아이콘 표시
  - 클릭 시 토글 방식으로 해당 행 아래에 에러 로그 전체 표시
  - 또는 테이블 하단에 선택된 작업의 에러 로그를 표시하는 영역 추가
- 에러 로그가 없는 경우 "로그 없음" 표시
- 테이블 스타일:
  - 실패한 작업임을 나타내기 위해 행 배경색을 연한 빨간색 (#fadbd8) 적용
  - 헤더는 기존 테이블과 동일한 스타일 유지

**구현 고려사항**:
- 에러 로그는 길이가 매우 다양할 수 있으므로 테이블 셀에 직접 표시하기보다는:
  1. **추천 방식**: 각 행에 "로그 보기" 아이콘 추가, 클릭 시 JavaScript 없이 CSS만으로 토글
  2. **대안 방식**: 테이블 하단에 에러 로그 섹션을 별도로 유지하되, 작업 ID로 연결
- 이메일 호환성을 위해 JavaScript 사용 최소화 (CSS `:target` 선택자 또는 순수 HTML 구조 활용)
- 에러 로그가 긴 경우 스크롤 가능한 영역으로 제한 (max-height 적용)

**체크리스트**:
- [x] 실패한 백업 상세 섹션을 테이블 구조로 변경
- [x] 테이블 컬럼에 "실패 시간" 명칭 사용 (기존 "완료 시간"에서 변경)
- [x] 에러 로그 표시 방법 구현 (인라인 표시)
- [x] 테이블 행 배경색을 연한 빨간색으로 설정 (#fadbd8)
- [x] 에러 로그가 없는 경우 "로그 없음" 메시지 표시
- [x] 테스트 리포트 생성하여 레이아웃 정상 확인
- [x] 이메일 클라이언트에서 테이블이 정상적으로 렌더링되는지 확인
- [x] 에러 로그가 이메일에서도 정상 표시되는지 확인

---

## 🔍 테스트 방법

### 개발 환경 테스트
```bash
# 1. .env 파일에 Baculum 웹 설정 추가
BACULUM_WEB_HOST=<your_baculum_web_ip>
BACULUM_WEB_PORT=9095

# 2. 테스트 모드로 리포트 생성
python -m src.main --mode test

# 3. 생성된 HTML 파일 확인
# reports/backup_report_YYYYMMDD_HHMMSS.html

# 4. 브라우저에서 HTML 파일 열어서 확인
# - 성공한 백업 목록: 소요 시간과 백업 크기 순서
# - 상세보기 아이콘 표시 및 링크 작동
# - 실패한 백업 상세: 테이블 형식 및 "실패 시간" 명칭

# 5. 메일 발송 테스트 (선택)
python -m src.main --mode test --send-mail

# 6. 이메일 클라이언트에서 확인
# - 모든 레이아웃이 정상적으로 표시되는지
# - 상세보기 링크가 작동하는지
# - 실패한 백업 테이블이 정상적으로 표시되는지
```

### flake8 코드 검증
```bash
# 수정된 파일 검증
flake8 src/utils/config.py
flake8 src/report/report_generator.py
```

### 확인 사항
1. **성공한 백업 목록 레이아웃**
   - 컬럼 순서: 작업 ID, 작업명, 레벨, 시작 시간, 완료 시간, 소요 시간, 백업 크기, 상세보기
   - 모든 데이터가 올바른 컬럼에 표시됨

2. **상세보기 기능**
   - Baculum 웹 설정이 있을 때: 🔍 아이콘 표시 및 링크 작동
   - Baculum 웹 설정이 없을 때: "-" 표시
   - 링크 클릭 시 올바른 Baculum 페이지로 이동
   - 새 탭에서 열림 (target="_blank")

3. **실패한 백업 상세 레이아웃**
   - 테이블 형식으로 표시
   - "실패 시간" 명칭 사용
   - 에러 로그가 있는 경우 적절하게 표시
   - 에러 로그가 없는 경우 "로그 없음" 메시지
   - 테이블 행 배경색이 연한 빨간색

4. **이메일 호환성**
   - Gmail, Outlook 등에서 정상 렌더링
   - 모든 링크와 스타일이 정상 작동

---

## ⚠️ 중요 주의사항

1. **Baculum 웹 인터페이스 URL 구조**
   - 표준 URL 형식: `http://{IP}:{PORT}/web/job/history/{jobID}/`
   - 실제 Baculum 설치에 따라 URL 구조가 다를 수 있음
   - 테스트 전 실제 Baculum 웹 인터페이스의 URL 형식 확인 필요
   - jobID가 올바르게 전달되는지 확인

2. **선택적 기능 처리**
   - Baculum 웹 설정은 선택사항
   - 설정이 없어도 리포트 생성이 정상적으로 작동해야 함
   - `has_baculum_web_config()` 메서드로 설정 존재 여부 확인
   - Jinja2 템플릿에서 조건부 렌더링 사용 (`{% if baculum_web_url %}`)

3. **이메일 호환성**
   - 일부 이메일 클라이언트는 JavaScript를 차단함
   - 에러 로그 토글 기능은 CSS 기반 또는 순수 HTML 구조 사용
   - 돋보기 이모지 (🔍)는 대부분의 이메일 클라이언트에서 지원됨
   - 링크 스타일은 인라인 CSS 사용 (이메일 호환성)

4. **테이블 레이아웃 일관성**
   - 성공한 백업과 실패한 백업의 테이블 스타일 일관성 유지
   - 헤더 스타일, 셀 패딩, 폰트 크기 등 기존 스타일 재사용
   - 모바일 환경에서의 반응형 레이아웃 고려 (viewport meta 태그 이미 존재)

5. **에러 로그 표시**
   - 에러 로그가 매우 긴 경우 레이아웃 깨짐 방지
   - `max-height`와 `overflow-y: auto` 적용
   - 폰트는 고정폭 (`Courier New`, `monospace`) 사용
   - `white-space: pre-wrap`으로 줄바꿈 처리

6. **코드 품질**
   - 모든 수정 코드는 PEP 8 준수
   - 새로운 Config 프로퍼티에 대한 docstring 작성
   - HTML 템플릿의 들여쓰기 일관성 유지

---

## 📌 관련 정보

- **브랜치**: `phase-9-report-layout-improvements`
- **관련 이슈**: N/A
- **의존성**:
  - 기존 Phase 8 (메일 발송 기능) 완료 필요
  - 추가 Python 패키지 설치 불필요
- **문서 업데이트**:
  - `README.md`: .env 설정 섹션에 `BACULUM_WEB_HOST`, `BACULUM_WEB_PORT` 추가
  - `.env.example`: 새 환경 변수 추가
- **테스트 데이터 필요**:
  - 성공한 백업 데이터 (레이아웃 확인)
  - 실패한 백업 데이터 (테이블 형식 및 에러 로그 표시 확인)
  - 에러 로그가 있는 실패 백업과 없는 실패 백업 모두 필요

---

## 💡 완료 기준

Phase 9는 다음 조건을 모두 만족할 때 완료됩니다:

1. ✅ 성공한 백업 목록에서 "소요 시간"과 "백업 크기" 컬럼 순서가 변경됨
2. ✅ 성공한 백업 목록에 상세보기 아이콘 및 링크가 추가됨
3. ✅ Baculum 웹 설정 환경 변수가 추가되고 Config 클래스가 확장됨
4. ✅ 상세보기 링크가 올바른 Baculum 페이지로 연결됨
5. ✅ 실패한 백업 상세가 테이블 형식으로 변경됨
6. ✅ "완료 시간" 명칭이 "실패 시간"으로 변경됨
7. ✅ 에러 로그가 적절하게 표시됨 (있는 경우/없는 경우 모두)
8. ✅ 모든 수정 코드가 flake8 검사를 통과함
9. ✅ 브라우저에서 HTML 리포트가 정상적으로 표시됨
10. ✅ 이메일 클라이언트에서 리포트가 정상적으로 표시됨
11. ✅ Git 커밋 완료 및 main 브랜치에 병합

---

## 🔗 관련 문서

- [프로젝트 요구사항](./project.md)
- [개발 가이드](./dev.md)
- [이전 태스크](./tasks/)
- [Phase 8: 메일 발송 기능](./tasks/task-008-mail-sending.md)
