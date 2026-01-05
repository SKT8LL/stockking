import streamlit as st
from agent import InvestmentAgent
import os

# 페이지 설정
st.set_page_config(
    page_title="버핏 스타일 주식 분석기",
    page_icon="📈",
    layout="wide"
)

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "agent" not in st.session_state:
    st.session_state.agent = None

# 로그인 페이지
if not st.session_state.logged_in:
    st.title("🔐 버핏 스타일 주식 분석기 로그인")

    st.markdown("""
    ### 환영합니다!
    분석을 시작하려면 API 키를 입력해주세요.
    """)

    with st.form("login_form"):
        st.subheader("API 키 입력")

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="https://platform.openai.com/api-keys 에서 발급받으세요"
        )

        perplexity_key = st.text_input(
            "Perplexity API Key",
            type="password",
            help="https://www.perplexity.ai/settings/api 에서 발급받으세요"
        )

        submit_button = st.form_submit_button("🚀 로그인", use_container_width=True)

        if submit_button:
            if not openai_key or not perplexity_key:
                st.error("⚠️ 모든 API 키를 입력해주세요!")
            else:
                try:
                    # API 키 검증을 위해 에이전트 초기화 시도
                    agent = InvestmentAgent(
                        openai_api_key=openai_key,
                        perplexity_api_key=perplexity_key
                    )
                    st.session_state.agent = agent
                    st.session_state.logged_in = True
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ API 키 검증 실패: {str(e)}")

    # 정보 섹션
    st.markdown("---")
    st.info("""
    💡 **API 키 발급 방법**

    **OpenAI API Key:**
    1. https://platform.openai.com 접속
    2. 회원가입/로그인
    3. API Keys 메뉴에서 새 키 생성

    **Perplexity API Key:**
    1. https://www.perplexity.ai 접속
    2. 회원가입/로그인
    3. Settings → API에서 키 생성

    ⚠️ API 키는 안전하게 보관하고 절대 공유하지 마세요!
    """)

# 메인 애플리케이션
else:
    # 헤더 영역
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.title("📈 버핏 스타일 주식 분석기")
    with col_logout:
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.agent = None
            st.rerun()

    st.markdown("---")

    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 분석 설정")

        st.markdown("---")
        st.subheader("🎛️ 파라미터 설정")

        # Perplexity 설정
        st.markdown("**Perplexity 설정**")
        perplexity_max_tokens = st.slider(
            "Max Tokens",
            500, 3000, 1500,
            key="pplx_tokens",
            help="응답 길이 조절"
        )
        perplexity_temperature = st.slider(
            "Temperature",
            0.0, 1.0, 0.2,
            key="pplx_temp",
            help="창의성 조절 (낮을수록 일관적)"
        )

        st.markdown("**OpenAI 설정**")
        openai_max_tokens = st.slider(
            "Max Tokens",
            500, 4000, 2000,
            key="openai_tokens",
            help="분석 길이 조절"
        )
        openai_temperature = st.slider(
            "Temperature",
            0.0, 1.0, 0.3,
            key="openai_temp",
            help="분석 창의성 조절"
        )

        # PDF 업로드
        st.markdown("---")
        st.subheader("📄 버크셔 서한 PDF")
        uploaded_file = st.file_uploader(
            "PDF 업로드 (선택사항)",
            type=["pdf"],
            help="워렌 버핏의 투자 철학이 담긴 PDF를 업로드하세요"
        )

        if uploaded_file:
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✓ PDF 업로드 완료")

    # 메인 영역
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🔍 주식 질문")
        user_query = st.text_area(
            "분석하고 싶은 주식에 대해 질문하세요",
            placeholder="예: What is IREN?\nTesla 주식은 어때?\nApple에 투자해도 될까?",
            height=150
        )

    with col2:
        st.subheader("💡 사용 예시")
        st.markdown("""
        - What is NVIDIA?
        - 삼성전자 주식 분석해줘
        - Should I invest in Tesla?
        - Apple의 투자 가치는?
        - Microsoft 경쟁력 분석
        """)

    # 분석 버튼
    if st.button("🚀 분석 시작", type="primary", use_container_width=True):
        if not user_query:
            st.error("⚠️ 질문을 입력해주세요!")
        else:
            with st.spinner("분석 중... 잠시만 기다려주세요 ⏳"):
                try:
                    # PDF 경로 설정
                    pdf_path = "temp_uploaded.pdf" if uploaded_file else None

                    # 분석 실행
                    result = st.session_state.agent.analyze_stock(
                        user_query=user_query,
                        pdf_path=pdf_path,
                        perplexity_max_tokens=perplexity_max_tokens,
                        perplexity_temperature=perplexity_temperature,
                        openai_max_tokens=openai_max_tokens,
                        openai_temperature=openai_temperature
                    )

                    # 결과 표시
                    st.markdown("---")
                    st.success("✅ 분석 완료!")

                    # 탭으로 구분
                    tab1, tab2, tab3 = st.tabs(["📋 종합 분석", "🔍 시장 데이터", "📚 버핏 인사이트"])

                    with tab1:
                        st.markdown("### 투자 분석 결과")
                        st.markdown(result["final_analysis"])

                        # 다운로드 버튼
                        st.download_button(
                            "📥 분석 결과 다운로드",
                            result["final_analysis"],
                            file_name=f"분석_{user_query[:20]}.txt",
                            mime="text/plain"
                        )

                    with tab2:
                        st.markdown("### Perplexity 수집 정보")
                        st.write(result["market_data"].get("raw_response", "정보 없음"))

                        if result["market_data"].get("citations"):
                            st.markdown("### 📚 출처")
                            for i, citation in enumerate(result["market_data"]["citations"], 1):
                                st.markdown(f"{i}. [{citation}]({citation})")

                    with tab3:
                        st.markdown("### 버크셔 서한 인사이트")
                        if result["buffett_insights"]:
                            for i, insight in enumerate(result["buffett_insights"], 1):
                                with st.expander(f"💡 인사이트 #{i}"):
                                    st.write(insight)
                        else:
                            st.info("PDF를 업로드하면 더 많은 인사이트를 확인할 수 있습니다.")

                    # 에러 표시
                    if result.get("error"):
                        st.warning(f"⚠️ 경고: {result['error']}")

                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
                    st.info("API 키가 올바른지 확인하거나 로그아웃 후 다시 시도해주세요.")

    # 하단 정보
    st.markdown("---")
    st.info("""
    💡 **사용 팁**
    - 명확한 회사명이나 티커 심볼을 입력하면 더 정확한 분석을 받을 수 있습니다.
    - 버크셔 서한 PDF를 업로드하면 워렌 버핏의 투자 철학이 반영됩니다.
    - 파라미터를 조정하여 응답의 창의성과 길이를 조절할 수 있습니다.
    - 분석 결과는 참고용이며 투자 결정은 본인의 책임입니다.
    """)

    # 푸터
    st.markdown("---")
    st.caption("🔐 귀하의 API 키는 세션 동안만 사용되며 저장되지 않습니다.")
