# QRGate
**QRGate**는 오프라인 환경에서 QR코드 인식을 통해 사용자의 신원을 확인하는 프로그램입니다. 오프라인 환경에서 인증 과정을 간편하게 하는것을 목표로 개발되었습니다.

## 시연 사이트
[QRGate](https://qrgate-six.vercel.app/)

## 특징
- **현장 인증**: 키오스크에서 표시되는 QR코드를 스마트폰으로 스캔하여 즉시 로그인
- **보안성 강화**: JWT 토큰, 만료 시간, 인증용 서명을 통해 위변조 방지
- **접근성**: 누구나 소지한 스마트폰으로 간편하게 인증 가능

## 동작 원리

> **예시: 병원 접수 프로세스**

1. **QR 코드 생성**
   - 사용자가 키오스크의 접수 버튼을 누르면, 로그인 페이지로 연결되는 QR코드를 생성합니다.
   - 서버는 WebSocket을 통해 실시간으로 사용자의 인증 상태를 모니터링합니다.
   - QR 코드에는 UUID를 포함한 JWT 토큰, 만료 시간(5분), 그리고 인증용 서명이 포함되어 있습니다.

2. **QR 코드 스캔 및 인증**
   - 사용자는 자신의 스마트폰으로 키오스크에 표시된 QR 코드를 스캔합니다.
   - 스캔 후, 스마트폰은 자동으로 로그인 페이지로 리다이렉트되어 인증 과정을 진행합니다.

3. **인증 완료 및 서비스 제공**
   - 사용자가 로그인에 성공하면, 서버는 Redis의 PUBLISH 기능을 통해 인증 완료 신호를 전송합니다.
   - 키오스크는 WebSocket의 SUBSCRIBE 기능으로 해당 신호를 감지하여 인증 성공 메시지를 표시합니다.
   - 인증이 완료되면, 키오스크는 사용자가 서비스를 이용할 수 있도록 관련 기능을 제공합니다.

이러한 절차를 통해 QRGate는 현장에서 스마트폰 로그인을 이용한 안전하고 간편한 인증을 제공합니다.

## API 목록
1. /api/qr/start
   - 설명 : QR 로그인 절차의 초기 단계로, 클라이언트가 서버에 제출할 토큰과 인증 처리 성공 여부를 반환합니다.
   - HTTP 메서드 : GET
```
{
  "token": "generated-token-string",
  "success": true
}
```

2. /api/qr/auth/{token}
   - 설명 : 전달받은 토큰과 사용자 입력 정보를 바탕으로 로그인을 처리합니다. 로그인 성공 시, 서버는 해당 토큰과 연계된 WebSocket에 신호를 전송하여 클라이언트에게 인증 완료를 알립니다.
   - HTTP 메서드: POST
   - Path Parameter:
     - token: 인증에 사용되는 JWT 토큰
```
# request body
{
  "id": "user_example",
  "pwd": "secure_password"
}

# response body
{
    "success" : True
}
```

3. /api/qr/ws/loading/{token}
   - 설명 : 클라이언트가 WebSocket 연결을 통해 로그인 성공 신호를 대기하는 엔드포인트입니다. 사용자가 로그인에 성공하면, 이 연결을 통해 인증 완료 신호가 전달됩니다.
   - 프로토콜: WebSocket
   - Path Parameter:
     - token: 인증 토큰 (WebSocket 연결과 연계하여 사용)
```
success
```
4. /api/test/insert
   - 설명 : 사용자를 추가합니다
   - HTTP 메서드 : POST
   - Query Parameter:
     - user_id: 사용자 아이디
     - user_pwd: 사용자 비밀번호
```
{
  "success": true
}
```

## 설치
### 요구 사항
- **Python**: 3.10 (테스트 완료)
- **Redis**가 필요합니다
- **필수 라이브러리**:
  - FastAPI
  - uvicorn
  - aioredis
  - Pydantic
  - 기타: 자세한 내용은 `requirements.txt` 참고
### 의존성 설치
```shell
pip install -r requirements.txt
```

### **중요**
1. .env.example을 채우고 .env로 바꿔주세요
2. app/utils/database.py 파일에서 main.sqlite -> database.sqlite로 변경해주세요


## 테스트 실행
```shell
uvicorn app.main:app --host 0.0.0.0 --reload
```

## 문의
프로젝트 관련 문의나 제안 사항은 아래 연락처로 부탁드립니다
- 이메일 : yuno.jung.07@gmail.com
