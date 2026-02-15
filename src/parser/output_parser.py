
import json
import re
from typing import Any

class OutputParser():
    def parse(self, raw: str, schema) -> Any:
        clean_markdown = self._clean_markdown(raw)
        text = self._extract_first_json(clean_markdown)
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            text = self._try_fix_truncated(text)
            text = json.loads(text)
        return schema(**text)

    def _clean_markdown(self, text: str) -> str:
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return text
    
    def _extract_first_json(self, text: str) -> str:
        index = text.find('{')
        if index == -1:
            raise ValueError("No JSON object found in the text.")
        return text[index:]
    
    def _try_fix_truncated(self, text: str) -> str:
        m, n = 0, 0
        for c in text:
            if c == '{':
                m += 1
            elif c == '[':
                n += 1
            elif c == '}':
                m -= 1
            elif c == ']':
                n -= 1
        if m > 0:
            text += '}' * m
        if n > 0:
            text += ']' * n
        return text
        
        