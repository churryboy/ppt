# Stitch MCP 서버 연동 가이드

## 개요

이 애플리케이션은 Stitch MCP (Model Context Protocol) 서버와 연동하여 견적 데이터를 동기화합니다.

## 설정

### 1. API 키 설정

`.env` 파일에 Stitch API 키가 자동으로 추가되었습니다:
```
STITCH_API_KEY=AQ.Ab8RN6K9zPD5iDCtL0W4QrGTYuKkQbch0L_qy_PM1XUMLG4w-w
```

### 2. Stitch MCP 서버 URL

기본 URL: `https://stitch.googleapis.com/mcp`

## 기능

### 자동 동기화

1. **견적서 업로드 시**
   - 견적서 파일을 업로드하면 자동으로 Stitch에 동기화됩니다
   - 백엔드 로그에서 `📤 Syncing quote to Stitch...` 메시지 확인

2. **견적 생성 시**
   - LLM으로 견적을 생성하면 자동으로 Stitch에 동기화됩니다
   - 생성된 견적 데이터가 Stitch에 저장됩니다

### API 엔드포인트

#### 1. Stitch 연결 테스트
```
GET /api/stitch/test
```
Stitch MCP 서버와의 연결을 테스트합니다.

**응답:**
```json
{
  "success": true,
  "message": "Stitch connection test completed"
}
```

#### 2. Stitch에서 견적 가져오기
```
GET /api/stitch/quotes?filters={json}
```
Stitch에서 과거 견적 데이터를 가져옵니다.

**파라미터:**
- `filters` (선택): JSON 형식의 필터 조건

**응답:**
```json
{
  "success": true,
  "quotes": [...],
  "count": 10
}
```

## 동작 방식

1. **견적 업로드/생성 시**
   - 로컬 데이터베이스에 저장
   - Stitch 클라이언트가 자동으로 Stitch에 동기화 시도
   - 동기화 실패해도 로컬 저장은 유지 (non-critical)

2. **에러 처리**
   - Stitch 동기화 실패는 경고로만 표시
   - 로컬 기능은 정상 작동

## 로그 확인

백엔드 로그에서 다음 메시지를 확인할 수 있습니다:
- `✅ Stitch client initialized` - 클라이언트 초기화 성공
- `📤 Syncing quote to Stitch...` - 동기화 시작
- `✅ Quote synced to Stitch successfully` - 동기화 성공
- `⚠️  Stitch sync failed (non-critical): ...` - 동기화 실패 (경고)

## 문제 해결

### Stitch 연결 실패
1. `.env` 파일에 `STITCH_API_KEY`가 올바르게 설정되어 있는지 확인
2. API 키가 유효한지 확인
3. 네트워크 연결 확인

### 동기화 실패
- 동기화 실패는 로컬 기능에 영향을 주지 않습니다
- 백엔드 로그에서 에러 메시지 확인
- Stitch MCP 서버 상태 확인

## 참고

- Stitch 동기화는 비동기적으로 작동합니다
- 동기화 실패 시에도 로컬 데이터는 정상적으로 저장됩니다
- Stitch API 키는 환경 변수로 관리됩니다

