import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.mcq_parser import MCQParserService


@pytest.fixture
def parser():
    return MCQParserService()


def test_validate_and_read_file_size_limit(parser):
    large_mock_file = MagicMock()
    large_mock_file.read = AsyncMock(return_value=b"0" * (51 * 1024 * 1024))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(parser.validate_and_read_file(large_mock_file))
    assert exc_info.value.status_code == 413
    assert "50 MiB" in str(exc_info.value.detail)


def test_validate_and_read_file_success(parser):
    valid_mock_file = MagicMock()
    content_bytes = b"sample content"
    valid_mock_file.read = AsyncMock(return_value=content_bytes)

    result = asyncio.run(parser.validate_and_read_file(valid_mock_file))
    assert result == content_bytes


def test_parse_csv_spreadsheet(parser):
    csv_content = (
        "question,option_a,option_b,option_c,option_d,answer,topic\n"
        "What is 2+2?,1,2,4,5,C,Math\n"
        "Capital of France?,Berlin,Paris,Madrid,Rome,B,Geography\n"
    ).encode("utf-8")

    parsed = parser.parse_mcqs("questions.csv", csv_content)
    assert len(parsed) == 2
    assert parsed[0]["question_text"] == "What is 2+2?"
    assert parsed[0]["options"] == ["1", "2", "4", "5"]
    assert parsed[0]["correct_answer"] == "4"
    assert parsed[0]["topic"] == "Math"

    assert parsed[1]["question_text"] == "Capital of France?"
    assert parsed[1]["correct_answer"] == "Paris"


def test_parse_invalid_extension(parser):
    with pytest.raises(HTTPException) as exc_info:
        parser.parse_mcqs("notes.txt", b"random content")
    assert exc_info.value.status_code == 400
