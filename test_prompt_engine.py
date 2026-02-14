from src.prompt_engine.template import PromptTemplate
from src.prompt_engine.schemas import RenderResult


if __name__ == '__main__':
    role = {"language":"python","which_language":"写好python代码"}
    task = PromptTemplate("gpt-4o-mini","src/prompts")
    result = task.render(role, "code_review.j2")
    print(f'rendered_text:{result.rendered_text}\n, token_count:{result.token_count}\n, template_name:{result.template_name}\n, variable_used : {result.variables_used}')


    

