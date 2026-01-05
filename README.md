# 📈 버핏 스타일 주식 분석기 (StockKing)

**StockKing**은 워렌 버핏의 투자 철학을 바탕으로 주식을 분석해주는 AI 기반 투자 보조 도구입니다. 최신 시장 데이터를 수집하고, 버크셔 해서웨이의 주주 서한(PDF)을 분석하여 통찰력 있는 투자 의견을 제공합니다.

## 🚀 주요 특징

- **워렌 버핏 스타일 분석**: 비즈니스 이해도, 경제적 해자, 경영진 평가, 밸류에이션 등 버핏의 4대 투자 원칙을 기준으로 분석합니다.
- **실시간 시장 정보 수집**: Perplexity API를 사용하여 최신 뉴스 및 재무 지표를 실시간으로 가져옵니다.
- **RAG (Retrieval-Augmented Generation)**: 버크셔 해서웨이 주주 서한(PDF)을 임베딩하여 실제 버핏의 철학이 담긴 인사이트를 제공합니다.
- **대화형 인터페이스**: Streamlit 기반의 깔끔하고 직관적인 UI를 제공합니다.
- **파라미터 제어**: OpenAI 및 Perplexity API의 Max Tokens, Temperature 등을 사용자가 직접 조정할 수 있습니다.

## 🛠 기술 스택

- **언어**: Python (>= 3.11)
- **프레임워크**: Streamlit, LangChain, LangGraph
- **AI 모델**: OpenAI (GPT-4o), Perplexity (Sonar-Pro)
- **데이터 저장**: FAISS (Vector Store)
- **패키지 관리**: UV

## 📋 설치 및 실행 방법

### 1. 사전 준비
- OpenAI API Key
- Perplexity API Key

### 2. 설치
프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.

```bash
# 의존성 설치 및 가상환경 설정
uv sync
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 아래 내용을 입력합니다.

```env
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### 4. 실행
```bash
# Streamlit 앱 실행
uv run streamlit run streamlit_app.py
```

## 🔍 사용 방법

1. **로그인**: 발급받은 API 키로 로그인합니다.
2. **질문 입력**: 분석하고 싶은 주식에 대해 질문합니다. (예: "NVIDIA에 대한 투자가 가치는 어떤가요?")
3. **분석 시작**: '분석 시작' 버튼을 누르면 인공지능이 시장 데이터와 투자 철학을 종합하여 분석 결과를 보여줍니다.
4. **결과 다운로드**: 종합 분석 결과는 텍스트 파일로 다운로드할 수 있습니다.

## 📂 프로젝트 구조

- `streamlit_app.py`: 메인 UI 및 웹 서비스 로직
- `agent.py`: LangGraph를 이용한 분석 워크플로우 및 에이전트 핵심 로직
- `stockking.pdf`: (기본 제공) 워렌 버핏의 투자 철학이 담긴 PDF 파일
- `pyproject.toml`: 의존성 및 프로젝트 설정

---
> **주의**: 본 프로그램에서 제공하는 분석 결과는 정보 제공 목적이며, 모든 투자 결정의 책임은 본인에게 있습니다.
