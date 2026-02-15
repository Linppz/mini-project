from src.prompt_engine.template import PromptTemplate
from typing import List
from src.prompt_engine.schemas import PromptVersion, RenderResult, PromptAuditLog
import hashlib
import difflib
import json


class PromptRegistry():
    def __init__(self, template_engine: PromptTemplate, manifest_path: str):
        self.template_engine = template_engine
        self.audit_logs = []
        self.manifest_path = manifest_path
        try:
            with open(manifest_path, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            self.data = {}

    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
    
    def render_and_log(self, prompts: dict, user_template: str) -> RenderResult:
        result = self.template_engine.render(prompts, user_template)
        hashcode = self._compute_hash(result.rendered_text)
        temp_prompt_version = PromptVersion( 
            template_name = user_template,
            version_hash = hashcode,
            rendered_text = result.rendered_text)
        
        if user_template not in self.data:
            self.data[user_template] = []
        self.data[user_template].append(temp_prompt_version)

        temp_PromptAuditLog = PromptAuditLog(
            template_name = user_template,
            version_hash = hashcode,
            rendered_prompt = result.rendered_text,
            variables = prompts)
        
        self.audit_logs.append(temp_PromptAuditLog)
        return result

    def get(self, user_template: str, hashcode: str):
        if user_template not in self.data:
            return None
        else:
            for version in self.data[user_template]:
                if version.version_hash == hashcode:
                    return version
        
        return None
    

    def diff(self, name: str, v1: str, v2: str):
        if name not in self.data:
            return None
        text1, text2 = "", ""
        for version in self.data[name]:
            if version.version_hash == v1:
                text1 = version.rendered_text
            elif version.version_hash == v2:
                text2 = version.rendered_text
        if text1 and text2:
            diff = difflib.unified_diff(
                text1.splitlines(),
                text2.splitlines(),
                lineterm = ""
            )
            result = list(diff)
            return result
        return None
    
    def _save_manifest(self):
        temp_dict = {}
        for name, value in self.data.items():
            temp_dict[name] = []
            for prompt in value:
                box = []
                box.append(prompt.template_name)
                box.append(prompt.version_hash)
                box.append(prompt.rendered_text)
                box.append(str(prompt.timestamp))
                temp_dict[name].append(box)
        with open(self.manifest_path, 'w') as f:
            json.dump(temp_dict, f)
        





            


        


