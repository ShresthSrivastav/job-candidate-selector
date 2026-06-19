from src.parser.jd_parser import JDParser


def test_jd_parser_basic():
    jd_text = """
    We are hiring a Senior AI Engineer. Must have: experience with retrieval, ranking, and evaluation metrics such as NDCG. Good to have: Pinecone, Faiss, RAG, LLMs.
    """
    p = JDParser()
    parsed = p.parse(jd_text)
    assert "retrieval" in parsed["must_have"] or "ranking" in parsed["must_have"]
    assert "pinecone" in parsed["retrieval_reqs"] or "faiss" in parsed["retrieval_reqs"]
    assert parsed["total_requirements"] > 0
