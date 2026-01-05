# test_agent.py
import os
from agent import InvestmentAgent


def main():
    """CLI에서 API 키를 입력받아 에이전트 테스트"""
    print("=" * 60)
    print("🧪 InvestmentAgent 테스트")
    print("=" * 60)

    # API 키 입력받기
    openai_api_key = input("\n🔑 OpenAI API 키를 입력하세요: ").strip()
    perplexity_api_key = input("🔑 Perplexity API 키를 입력하세요: ").strip()

    if not openai_api_key or not perplexity_api_key:
        print("❌ API 키를 모두 입력해야 합니다.")
        return

    # PDF 파일 경로 입력
    pdf_path = input("\n📄 PDF 파일 경로를 입력하세요 (기본값: berkshire_letters.pdf): ").strip()
    if not pdf_path:
        pdf_path = "berkshire_letters.pdf"

    # PDF 파일 존재 확인
    if not os.path.exists(pdf_path):
        print(f"⚠️ 경고: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        use_pdf = input("PDF 없이 계속하시겠습니까? (y/n): ").strip().lower()
        if use_pdf != 'y':
            return
        pdf_path = None

    # 에이전트 초기화
    try:
        agent = InvestmentAgent(
            openai_api_key=openai_api_key,
            perplexity_api_key=perplexity_api_key
        )
        print("\n✓ 에이전트 초기화 성공")
    except Exception as e:
        print(f"\n❌ 에이전트 초기화 실패: {e}")
        return

    # 테스트 쿼리 입력
    print("\n" + "=" * 60)
    print("📝 분석할 주식을 입력하세요")
    print("예시: 애플 주식 분석해줘, TSLA는 어때?, Microsoft 투자 의견")
    print("=" * 60)

    user_query = input("\n질문: ").strip()
    if not user_query:
        user_query = "애플 주식에 대해 분석해줘"
        print(f"기본 질문 사용: {user_query}")

    # 파라미터 설정
    print("\n⚙️ 파라미터 설정 (Enter 키로 기본값 사용)")

    try:
        perplexity_max_tokens = input("Perplexity max_tokens (기본: 1500): ").strip()
        perplexity_max_tokens = int(perplexity_max_tokens) if perplexity_max_tokens else 1500

        perplexity_temperature = input("Perplexity temperature (기본: 0.2): ").strip()
        perplexity_temperature = float(perplexity_temperature) if perplexity_temperature else 0.2

        openai_max_tokens = input("OpenAI max_tokens (기본: 2000): ").strip()
        openai_max_tokens = int(openai_max_tokens) if openai_max_tokens else 2000

        openai_temperature = input("OpenAI temperature (기본: 0.3): ").strip()
        openai_temperature = float(openai_temperature) if openai_temperature else 0.3
    except ValueError as e:
        print(f"⚠️ 잘못된 입력입니다. 기본값을 사용합니다: {e}")
        perplexity_max_tokens = 1500
        perplexity_temperature = 0.2
        openai_max_tokens = 2000
        openai_temperature = 0.3

    # 분석 실행
    print("\n🚀 분석을 시작합니다...\n")

    try:
        result = agent.analyze_stock(
            user_query=user_query,
            pdf_path=pdf_path,
            perplexity_max_tokens=perplexity_max_tokens,
            perplexity_temperature=perplexity_temperature,
            openai_max_tokens=openai_max_tokens,
            openai_temperature=openai_temperature
        )

        # 결과 요약
        print("\n" + "=" * 60)
        print("✅ 테스트 완료")
        print("=" * 60)
        print(f"📌 질문: {result['user_query']}")
        print(f"📊 수집된 인사이트: {len(result['buffett_insights'])}개")
        print(f"📈 분석 길이: {len(result['final_analysis'])} 글자")

        if result.get('error'):
            print(f"⚠️ 에러: {result['error']}")

    except Exception as e:
        print(f"\n❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
