import os
import requests
from typing import TypedDict, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END


class InvestmentState(TypedDict):
    user_query: str
    market_data: dict
    buffett_insights: List[str]
    final_analysis: str
    error: str
    perplexity_max_tokens: int
    perplexity_temperature: float
    openai_max_tokens: int
    openai_temperature: float


class InvestmentAgent:
    def __init__(self, openai_api_key: str, perplexity_api_key: str):
        self.openai_api_key = openai_api_key
        self.perplexity_api_key = perplexity_api_key
        self.vector_store = None
        os.environ["OPENAI_API_KEY"] = openai_api_key

    def perplexity_research_node(self, state: InvestmentState) -> InvestmentState:
        """Perplexity API로 정보 수집"""
        user_query = state["user_query"]
        max_tokens = state.get("perplexity_max_tokens", 1500)
        temperature = state.get("perplexity_temperature", 0.2)

        print(f"🔍 Perplexity로 정보 수집 중: '{user_query}'")
        print(f"   📊 설정: max_tokens={max_tokens}, temperature={temperature}")

        try:
            url = "https://api.perplexity.ai/chat/completions"
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a financial data researcher. When asked about a stock:
1. Identify the company and ticker symbol
2. Provide current stock price and today's change
3. Recent news (last 7 days)
4. Analyst ratings summary
5. Key financial metrics (P/E, market cap, revenue growth)
6. Major risks or concerns

Be concise and factual. Always include the ticker symbol in your response.
Only use information from reliable financial sources."""
                    },
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "return_citations": True,
                "search_domain_filter": [
                    "bloomberg.com", "reuters.com", "wsj.com",
                    "finance.yahoo.com", "investing.com", "seekingalpha.com"
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            market_data = {
                "raw_response": result["choices"][0]["message"]["content"],
                "citations": result.get("citations", []),
                "user_query": user_query
            }

            print(f"✓ Perplexity 정보 수집 완료")
            return {**state, "market_data": market_data}

        except Exception as e:
            print(f"❌ Perplexity API 오류: {str(e)}")
            return {
                **state,
                "market_data": {
                    "raw_response": f"정보 수집 실패: {str(e)}",
                    "user_query": user_query
                },
                "error": str(e)
            }

    def initialize_rag(self, pdf_path: str):
        """RAG 시스템 초기화"""
        print(f"📄 PDF 로딩 중: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS.from_documents(splits, embeddings)

        print(f"✓ RAG 초기화 완료: {len(splits)}개 청크")

    def rag_buffett_wisdom_node(self, state: InvestmentState) -> InvestmentState:
        """버크셔 서한에서 투자 철학 검색"""
        user_query = state["user_query"]
        print(f"📚 버핏의 투자 철학 검색 중...")

        if self.vector_store is None:
            print("⚠️ RAG 시스템이 초기화되지 않았습니다. 기본 원칙 사용")
            return {
                **state,
                "buffett_insights": [
                    "경제적 해자(Economic Moat)가 있는 기업을 찾아라",
                    "이해할 수 있는 비즈니스에만 투자하라",
                    "훌륭한 경영진이 있는가를 확인하라",
                    "적정 가격에 매수하라"
                ]
            }

        search_queries = [
            user_query,
            "competitive advantage moat",
            "business quality evaluation",
            "valuation principles"
        ]

        insights = []
        for query in search_queries[:3]:
            docs = self.vector_store.similarity_search(query, k=2)
            for doc in docs:
                insights.append(doc.page_content[:300])

        print(f"✓ {len(insights)}개 인사이트 추출 완료")
        return {**state, "buffett_insights": insights}

    def openai_analysis_node(self, state: InvestmentState) -> InvestmentState:
        """OpenAI로 종합 분석"""
        user_query = state["user_query"]
        market_data = state["market_data"]
        buffett_insights = state["buffett_insights"]
        max_tokens = state.get("openai_max_tokens", 2000)
        temperature = state.get("openai_temperature", 0.3)

        print(f"🤖 OpenAI로 종합 분석 중...")
        print(f"   📊 설정: max_tokens={max_tokens}, temperature={temperature}")

        prompt = f"""당신은 워렌 버핏의 투자 철학을 깊이 이해하는 전문 애널리스트입니다.

## 사용자 질문
{user_query}

## Perplexity가 수집한 최신 시장 정보
{market_data.get('raw_response', '정보 없음')}

## 버크셔 해서웨이 서한에서 추출한 투자 원칙
{chr(10).join(f"- {insight[:200]}..." for insight in buffett_insights)}

## 분석 요청
위 정보를 바탕으로 다음 구조로 분석하세요:

1. **회사 및 티커 확인**
2. **비즈니스 이해도** (1-5점)
3. **경제적 해자** (1-5점)
4. **경영진 평가** (1-5점)
5. **밸류에이션** (1-5점)
6. **종합 투자 의견**

한국어로 명확하고 실용적으로 작성해주세요.
"""

        try:
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=temperature,
                max_tokens=max_tokens
            )
            response = llm.invoke(prompt)
            analysis = response.content

            print(f"✓ 분석 완료 ({len(analysis)} 글자)")
            return {**state, "final_analysis": analysis}

        except Exception as e:
            print(f"❌ OpenAI API 오류: {str(e)}")
            return {
                **state,
                "final_analysis": f"분석 중 오류 발생: {str(e)}",
                "error": str(e)
            }

    def create_workflow(self):
        """워크플로우 생성"""
        workflow = StateGraph(InvestmentState)

        workflow.add_node("perplexity_research", self.perplexity_research_node)
        workflow.add_node("rag_wisdom", self.rag_buffett_wisdom_node)
        workflow.add_node("openai_analysis", self.openai_analysis_node)

        workflow.set_entry_point("perplexity_research")
        workflow.add_edge("perplexity_research", "rag_wisdom")
        workflow.add_edge("rag_wisdom", "openai_analysis")
        workflow.add_edge("openai_analysis", END)

        return workflow.compile()

    def analyze_stock(
        self,
        user_query: str,
        pdf_path: str = None,
        perplexity_max_tokens: int = 1500,
        perplexity_temperature: float = 0.2,
        openai_max_tokens: int = 2000,
        openai_temperature: float = 0.3
    ):
        """주식 분석 실행"""
        print("=" * 60)
        print("🎯 버핏 스타일 주식 분석 시작")
        print("=" * 60)

        print("pdf path :" + pdf_path)
        if pdf_path:
            self.initialize_rag(pdf_path)

        app = self.create_workflow()

        initial_state = {
            "user_query": user_query,
            "market_data": {},
            "buffett_insights": [],
            "final_analysis": "",
            "error": "",
            "perplexity_max_tokens": perplexity_max_tokens,
            "perplexity_temperature": perplexity_temperature,
            "openai_max_tokens": openai_max_tokens,
            "openai_temperature": openai_temperature
        }

        result = app.invoke(initial_state)

        print("\n" + "=" * 60)
        print("📊 분석 결과")
        print("=" * 60)
        print(result["final_analysis"])

        if result.get("error"):
            print(f"\n⚠️ 경고: {result['error']}")

        return result
