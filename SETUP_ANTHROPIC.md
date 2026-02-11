# Anthropic API 키 설정 가이드

## 🔑 API 키 설정 방법

### 1. Anthropic API 키 발급

1. [Anthropic Console](https://console.anthropic.com/)에 로그인
2. **Settings** → **API Keys** 이동
3. **Create Key** 클릭
4. 키 이름 입력 후 생성
5. 생성된 키 복사 (한 번만 표시됨!)

### 2. .env 파일에 키 추가

프로젝트 루트에 `.env` 파일을 만들거나 수정:

```bash
cd /Users/meteorresearch/vibe-coding/ppt
nano .env
```

다음 형식으로 입력:
```
ANTHROPIC_API_KEY=sk-ant-api03-실제키여기전체를복사해서붙여넣기
```

**중요:**
- `sk-ant-your-actual-api-key-here` 같은 플레이스홀더가 아닌 **실제 키**를 넣어야 합니다
- 키는 `sk-ant-api03-` 또는 `sk-ant-`로 시작합니다
- 키 길이는 보통 50자 이상입니다
- 공백이나 따옴표 없이 그대로 입력하세요

### 3. 백엔드 재시작

```bash
./run_backend.sh
```

### 4. 확인

백엔드 시작 시 다음 메시지가 보이면 성공:
```
✅ Anthropic client initialized successfully
```

## ❌ 문제 해결

### "invalid x-api-key" 오류
- API 키가 실제 키가 아닌 플레이스홀더인지 확인
- 키 앞뒤 공백 제거
- `.env` 파일 저장 후 백엔드 재시작

### "ANTHROPIC_API_KEY not found" 메시지
- `.env` 파일이 프로젝트 루트에 있는지 확인
- 파일명이 정확히 `.env`인지 확인 (`.env.txt` 아님)
- 백엔드 재시작

## 💡 테스트

견적 생성 버튼을 클릭하고 백엔드 로그에서 다음을 확인:
- `✅ Using Anthropic Claude API...` - LLM 사용 중
- `📤 Sending request to Anthropic Claude API...` - API 호출
- `✅ Received response from Anthropic Claude API` - 성공!

