from src.parser.output_parser import OutputParser
from src.schemas.code_review import CodeReviewResult
import pytest

def test_clean_markdown():
    obj = OutputParser()
    text = '```json\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}\n```'
    assert obj._clean_markdown(text) == '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8
    assert result.issues == []
    assert result.summary == "This is a well written code review result"

def test_extract_prefix_garbage():
    text = 'Here is my review:\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    obj = OutputParser()
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8

def test_truncated_json():
    text = '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"'
    obj = OutputParser()
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8