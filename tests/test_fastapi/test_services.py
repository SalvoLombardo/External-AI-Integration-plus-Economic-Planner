import pytest
import asyncio 
from FASTAPI_APP.app.services.llm_service import chunk_data, send_to_llm

def test_chunk_data_single_chunk():
    data = [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}]
    chunks = chunk_data(data, max_len=1000)
    assert len(chunks) == 1
    assert chunks[0] == data


def test_chunk_data_multiple_chunks():
    # Dati artificialmente grandi per forzare la divisione
    data = [{"id": i, "text": "x" * 1000} for i in range(5)]
    chunks = chunk_data(data, max_len=2000)
    assert len(chunks) > 1
    total_items = sum(len(c) for c in chunks)
    assert total_items == len(data)  # nessun item perso


def test_chunk_data_large_item():
    # Caso limite: un singolo item più grande del limite
    data = [{"id": 1, "text": "x" * 3000}]
    chunks = chunk_data(data, max_len=2000)
    assert len(chunks) == 1
    assert len(chunks[0]) == 1









@pytest.mark.asyncio
async def test_send_to_llm_success(mocker):
    mock_create = mocker.AsyncMock()
    mock_create.return_value = mocker.MagicMock(
        choices=[mocker.MagicMock(message=mocker.MagicMock(content="response 1"))]
    )

    
    mocker.patch(
        "FASTAPI_APP.app.services.ai_service.client.chat.completions.create",
        new=mock_create,
    )

    data = [{"a": 1}]
    prompt = "Analyze this"

    result = await send_to_llm(data, prompt)

    
    assert "response 1" in result

    
    mock_create.assert_awaited_once()