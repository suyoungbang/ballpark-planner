from app.core.config import PROJECT_ROOT
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 구장 가이드 문서 경로 (프로젝트 루트/data/stadium_guides.md)
GUIDE_PATH = Path(__file__).resolve().parents[2] / "data" / "stadium_guides.md"


def load_guides() -> list[Document]:
    """구장 가이드를 구장·주제 단위로 나눠 Document 목록으로 반환한다."""
    # 1. ## 제목은 구장(stadium), ### 제목은 주제(topic)로 나누는 분할기
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "stadium"), ("###", "topic")]
    )

    # 2. 문서를 읽어 제목 기준으로 나누기
    sections = splitter.split_text(GUIDE_PATH.read_text(encoding="UTF-8"))

    # 3. 머리말(topic이 없는 조각)은 빼고 Document 만들기
    return [
        Document(
            # 임베딩에 구장 이름도 반영되도록 "구장 주제"를 본문 앞에 붙인다.
            page_content=f"{s.metadata['stadium']} {s.metadata['topic']}\n{s.page_content}",
            metadata={
                "source": "stadium_guides.md",
                "stadium": s.metadata["stadium"],
                "topic": s.metadata["topic"],
                "guide_no": s.metadata["topic"].split(" ")[0],
            },
        )
        for s in sections
        if "topic" in s.metadata
    ]

# 조문 임베딩 해서 저장해두기
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
EMBEDDING_MODEL = "text-embedding-3-large"


def get_vectorstore() -> Chroma:
    """구장 가이드를 저장한 Chroma 벡터 DB를 반환한다. 비어있으면 처음 한 번만 임베딩해서 저장한다."""

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name="stadium_guides",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    if not vectorstore.get(limit=1)["ids"]:
        guides = load_guides()
        vectorstore.add_documents(guides, ids=[g.metadata["guide_no"] for g in guides])

    return vectorstore