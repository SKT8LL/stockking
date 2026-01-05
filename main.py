from agent import InvestmentAgent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

# API 키 설정
OPENAI_API_KEY = "your-openai-key-here"
PERPLEXITY_API_KEY = "your-perplexity-key-here"


def check_pdf_file(pdf_path: str):
    """PDF 파일 존재 여부 및 접근 가능성 확인"""
    print(f"\n🔍 PDF 파일 확인: {pdf_path}")

    # 절대 경로 확인
    abs_path = os.path.abspath(pdf_path)
    print(f"   절대 경로: {abs_path}")

    # 현재 작업 디렉토리 확인
    current_dir = os.getcwd()
    print(f"   현재 작업 디렉토리: {current_dir}")

    # 파일 존재 여부
    if os.path.exists(pdf_path):
        print(f"   ✓ 파일 존재함")

        # 파일 크기
        file_size = os.path.getsize(pdf_path)
        print(f"   ✓ 파일 크기: {file_size:,} bytes ({file_size / 1024:.2f} KB)")

        # 읽기 권한 확인
        if os.access(pdf_path, os.R_OK):
            print(f"   ✓ 읽기 권한 있음")
        else:
            print(f"   ❌ 읽기 권한 없음")
            return False

        # 파일 확장자 확인
        if not pdf_path.lower().endswith('.pdf'):
            print(f"   ⚠️ PDF 확장자가 아닙니다")

        return True
    else:
        print(f"   ❌ 파일이 존재하지 않습니다")

        # 현재 디렉토리의 PDF 파일 찾기
        print(f"\n   현재 디렉토리의 PDF 파일 목록:")
        pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
        if pdf_files:
            for pdf in pdf_files:
                print(f"   - {pdf}")
        else:
            print(f"   (PDF 파일 없음)")

        return False


def inspect_pdf_processing(pdf_path: str, openai_api_key: str):
    """PDF가 어떻게 로드되고 벡터화되었는지 상세 확인"""

    print("=" * 60)
    print("📋 PDF 처리 과정 분석")
    print("=" * 60)

    # 파일 확인 먼저 실행
    if not check_pdf_file(pdf_path):
        print("\n❌ PDF 파일 접근 불가. 경로를 확인하세요.")
        return None

    # 1. PDF 로드
    print("\n[1단계] PDF 로딩...")
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            print("❌ PDF는 로드되었지만 내용이 비어있습니다.")
            return None

        print(f"✓ 총 페이지 수: {len(documents)}페이지")
        print(f"\n첫 번째 페이지 미리보기 (처음 500자):")
        print("-" * 60)
        first_content = documents[0].page_content[:500]
        print(first_content if first_content else "(빈 페이지)")
        print("-" * 60)
    except Exception as e:
        print(f"❌ PDF 로딩 실패: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

    # 2. 텍스트 분할
    print("\n[2단계] 텍스트 분할...")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        if not splits:
            print("❌ 텍스트 분할 결과가 비어있습니다.")
            return None

        print(f"✓ 생성된 청크 수: {len(splits)}개")
        print(f"\n청크 예시 (처음 3개):")
        for i, split in enumerate(splits[:3]):
            print(f"\n--- 청크 #{i + 1} ---")
            print(f"페이지: {split.metadata.get('page', 'N/A')}")
            print(f"길이: {len(split.page_content)} 글자")
            print(f"내용 미리보기:")
            content_preview = split.page_content[:300]
            print(content_preview if content_preview else "(빈 청크)")
            if content_preview:
                print("...")
    except Exception as e:
        print(f"❌ 텍스트 분할 실패: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

    # 3. 벡터화 및 검색 테스트
    print("\n[3단계] 벡터 스토어 생성 및 검색 테스트...")
    try:
        os.environ["OPENAI_API_KEY"] = openai_api_key

        embeddings = OpenAIEmbeddings()
        print("   임베딩 생성 중...")
        vector_store_test = FAISS.from_documents(splits, embeddings)
        print("   ✓ 벡터 스토어 생성 완료")

        # 테스트 쿼리들
        test_queries = [
            "investment philosophy",
            "competitive advantage",
            "경제적 해자",
            "valuation"
        ]

        print(f"\n검색 테스트 결과:")
        for query in test_queries:
            print(f"\n🔍 검색어: '{query}'")
            results = vector_store_test.similarity_search(query, k=2)
            if not results:
                print(f"   ⚠️ 검색 결과 없음")
            for j, doc in enumerate(results):
                print(f"  [{j + 1}] 유사도 높은 청크 (페이지 {doc.metadata.get('page', 'N/A')}):")
                print(f"      {doc.page_content[:200]}...")
    except Exception as e:
        print(f"❌ 벡터화 실패: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

    # 4. 통계 정보
    print("\n" + "=" * 60)
    print("📊 요약 통계")
    print("=" * 60)
    total_chars = sum(len(split.page_content) for split in splits)
    avg_chunk_size = total_chars / len(splits) if splits else 0

    print(f"전체 문자 수: {total_chars:,} 글자")
    print(f"평균 청크 크기: {avg_chunk_size:.0f} 글자")
    if splits:
        print(f"최소 청크 크기: {min(len(s.page_content) for s in splits)} 글자")
        print(f"최대 청크 크기: {max(len(s.page_content) for s in splits)} 글자")

    return {
        "documents": documents,
        "splits": splits,
        "vector_store": vector_store_test
    }


def main():
    """메인 실행 함수"""

    # PDF 경로
    pdf_path = os.path.abspath('stockking.pdf')

    print("\n" + "=" * 60)
    print("🚀 버핏 스타일 주식 분석기")
    print("=" * 60)

    if not os.path.exists(pdf_path):
        print(f"⚠️ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        print("현재 디렉토리의 PDF 파일:")
        current_dir = os.getcwd()
        pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
        for pdf in pdf_files:
            print(f"  - {pdf}")

        if pdf_files:
            pdf_path = os.path.join(current_dir, pdf_files[0])
            print(f"\n첫 번째 PDF 사용: {pdf_path}")
        else:
            pdf_path = None
            print("\nPDF 없이 진행합니다 (기본 투자 원칙 사용)")
    # 메뉴 선택
    print("\n옵션을 선택하세요:")
    print("1. PDF 처리 과정 확인")
    print("2. 주식 분석 실행")
    print("3. 둘 다 실행")

    choice = input("\n선택 (1/2/3): ").strip()

    # PDF 검사 실행
    if choice in ["1", "3"]:
        print("\n" + "=" * 60)
        print("📄 PDF 검사 시작")
        print("=" * 60)
        inspection_result = inspect_pdf_processing(pdf_path, OPENAI_API_KEY)

        if inspection_result is None:
            print("\n❌ PDF 검사 실패.")

            # 대안 경로 제안
            alt_path = input("\n다른 PDF 경로를 입력하시겠습니까? (경로 입력 또는 Enter로 건너뛰기): ").strip()
            if alt_path and os.path.exists(alt_path):
                pdf_path = alt_path
                inspection_result = inspect_pdf_processing(pdf_path, OPENAI_API_KEY)
            elif choice == "1":
                return
        else:
            print("\n✅ PDF 검사 완료!")

    # 주식 분석 실행
    if choice in ["2", "3"]:
        print("\n" + "=" * 60)
        print("📈 주식 분석 시작")
        print("=" * 60)




        # 에이전트 초기화 (PDF 경로 포함)
        print(f"\n🔧 에이전트 초기화 중...")
        print(f"   📄 PDF 경로: {pdf_path if pdf_path else '없음 (RAG 비활성화)'}")

        agent = InvestmentAgent(
            openai_api_key=OPENAI_API_KEY,
            perplexity_api_key=PERPLEXITY_API_KEY,
            pdf_path=pdf_path  # PDF 경로 전달
        )

        # RAG 초기화 확인
        if agent.vector_store:
            print(f"   ✓ RAG 초기화 완료")
        else:
            print(f"   ⚠️ RAG 미활성화 (PDF 없음)")


        # 사용자 입력
        user_query = input("\n분석할 주식을 입력하세요 (예: what is iren?): ").strip()
        if not user_query:
            user_query = "what is iren?"
            print(f"기본 질문 사용: {user_query}")

        # 분석 실행
        try:
            result = agent.analyze_stock(
                user_query=user_query,
                pdf_path=None  # 이미 초기화 시 설정됨
            )

            # 결과 출력
            print("\n" + "=" * 60)
            print("📊 최종 분석 결과")
            print("=" * 60)
            print(result["final_analysis"])

            # 추가 정보
            if result.get("error"):
                print(f"\n⚠️ 경고: {result['error']}")

            # 결과 저장 여부
            save = input("\n결과를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"분석결과_{user_query[:20].replace(' ', '_')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("📊 투자 분석 결과\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"질문: {user_query}\n\n")
                    f.write(result["final_analysis"])
                    f.write("\n\n" + "=" * 60 + "\n")
                    f.write("📚 시장 데이터\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(result["market_data"].get("raw_response", "정보 없음"))
                print(f"✅ 저장 완료: {filename}")

        except Exception as e:
            print(f"\n❌ 분석 중 오류 발생: {str(e)}")
            import traceback
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
