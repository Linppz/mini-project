from src.prompt_engine.template import PromptTemplate
import tiktoken
import pytest

def test_render_with_variables():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    result = test.render(role, "code_review.j2")
    assert "猪" in result.rendered_text
    assert "c++" in result.rendered_text 
    assert result.token_count > 0
    assert result.template_name == "code_review.j2"

def test_missing_variables_raises_error():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++"}

    with pytest.raises(ValueError):
        result = test.render(role, "code_review.j2")

def test_token_count_accuracy():
    test = PromptTemplate("gpt-4o1-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    result = test.render(role, "code_review.j2")
    way = tiktoken.get_encoding("cl100k_base")
    expected = len(way.encode(result.rendered_text))
    assert abs(result.token_count - expected) / expected < 0.05    


