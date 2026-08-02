import pytest

from rag.pipeline import RAGPipeline


@pytest.mark.asyncio
async def test_rag_ingest_and_answer():
    rag = RAGPipeline()
    count = rag.ingest_texts(
        ["WHO sample: Vaccination can reduce influenza risk."],
        collection="hospital_guidelines",
        source_type="who",
    )
    assert count >= 1
    result = await rag.answer("What helps reduce influenza risk?")
    assert "answer" in result
    assert result["disclaimer"]
