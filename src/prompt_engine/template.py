from src.llm.tokentracker import TokenTracker
from jinja2 import Environment, FileSystemLoader, meta
from src.prompt_engine.schemas import RenderResult, FewShotExample
from typing import List

class PromptTemplate():
    def __init__(self, model: str, template_dir: str):
        self.model = model
        self.env = Environment(loader = FileSystemLoader(template_dir))

    def render(self, prompts: dict, user_template: str) -> RenderResult:
        template = self.env.get_template(user_template)
        text = template.render(**prompts)
        tracker = TokenTracker(self.model)
        tracker.add(text)
        tracker = tracker.get_usage()
        return RenderResult(
            rendered_text = text,
            token_count = tracker,
            template_name = user_template,
            variables_used = prompts,
        )
    #看看还有哪些模板可以用
    def show_templates(self) -> List:
        return self.env.list_templates()
    
    #看看一共有多少模板可以用
    def show_missing_context(self, user_template: str) -> set:
        orig_code = self.env.loader.get_source(self.env, user_template)
        table = meta.find_undeclared_variables(self.env.parse(orig_code[0]))
        return table

