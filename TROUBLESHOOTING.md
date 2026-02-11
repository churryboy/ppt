# 문제 해결 가이드

## 인증 문제 해결

### 1. 브라우저 캐시 및 localStorage 초기화

1. 브라우저 개발자 도구 열기 (F12)
2. Application 탭 → Local Storage → `http://localhost:3000` 선택
3. `sessionToken` 키 삭제
4. 브라우저 새로고침 (Cmd+Shift+R 또는 Ctrl+Shift+R)

### 2. 로그인 다시 시도

1. 로그인 페이지에서 새 계정으로 회원가입 또는 기존 계정으로 로그인
2. 성공하면 `sessionToken`이 localStorage에 저장됨

### 3. 네트워크 요청 확인

브라우저 개발자 도구 → Network 탭에서:
- `/api/auth/login` 요청이 `200 OK`인지 확인
- 응답에 `session_token`이 포함되어 있는지 확인
- 이후 요청에 `Authorization` 헤더가 포함되어 있는지 확인

### 4. 백엔드 로그 확인

백엔드 터미널에서:
- 로그인 요청이 들어오는지 확인
- 세션 토큰이 생성되는지 확인
- 이후 API 요청에 인증 헤더가 있는지 확인

## 견적 생성 문제 해결

### 1. Anthropic API 키 확인

`.env` 파일에 실제 API 키가 있는지 확인:
```bash
cat .env
```

키는 `sk-ant-api03-...` 형식이어야 하고, 100자 이상이어야 합니다.

### 2. 백엔드 로그 확인

견적 생성 버튼 클릭 시 백엔드 로그에서:
- `🔍 Generating quote with LLM...` 메시지 확인
- `✅ Using Anthropic Claude API...` 메시지 확인
- 모델 이름 오류가 있는지 확인

### 3. 모델 이름 문제

만약 모델 이름 오류가 발생하면:
- `claude-3-5-sonnet-20240620` 먼저 시도
- 실패 시 `claude-3-5-sonnet-20241022` 자동 시도

## 서버 재시작

### 백엔드 재시작
```bash
./run_backend.sh
```

### 프론트엔드 재시작
```bash
cd frontend
npm start
```

## 일반적인 문제

### 프록시가 작동하지 않음
- `package.json`에 `"proxy": "http://localhost:8000"` 확인
- 프론트엔드 개발 서버 재시작 필요

### CORS 오류
- 백엔드에서 CORS 미들웨어가 설정되어 있는지 확인
- 프록시를 사용하면 CORS 문제가 해결됨

### 401 Unauthorized
- localStorage의 `sessionToken` 확인
- 로그인 다시 시도
- 브라우저 새로고침

