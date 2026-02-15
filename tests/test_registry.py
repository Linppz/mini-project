from src.prompt_engine.template import PromptTemplate
from src.prompt_engine.registry import PromptRegistry
import pytest

def test_render_and_log():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    record = PromptRegistry(test, "tests/test_manifest.json")
    result = record.render_and_log(role, "code_review.j2")
    assert len(record.audit_logs) == 1
    assert record.audit_logs[0].template_name == "code_review.j2"

def test_version_hash_stability():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    record = PromptRegistry(test, "tests/test_manifest.json")
    result1 = record.render_and_log(role, "code_review.j2")
    result2 = record.render_and_log(role, "code_review.j2")
    assert record.audit_logs[0].version_hash == record.audit_logs[1].version_hash 

def test_get_version():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    record = PromptRegistry(test, "tests/test_manifest.json")
    result1 = record.render_and_log(role, "code_review.j2")
    number = record.get("code_review.j2", record.data["code_review.j2"][0].version_hash)
    assert number.version_hash == record.data["code_review.j2"][0].version_hash

def test_diff_versions():
    test = PromptTemplate("gpt-4o-mini","src/prompts")
    role = {"lanuage" : "c++", "role" : "猪", "your_code" : "cout << I Love you"}
    second_role = {"lanuage" : "c++", "role" : "狗", "your_code" : "cout << I Love you"}
    record = PromptRegistry(test, "tests/test_manifest.json")
    result1 = record.render_and_log(role, "code_review.j2")
    result2 = record.render_and_log(second_role, "code_review.j2")
    assert record.diff("code_review.j2", record.data["code_review.j2"][0].version_hash, record.data["code_review.j2"][1].version_hash) != None
