# -*- coding: utf-8 -*-
from typing import List

def is_chinese(text): return any('\u4e00' <= ch <= '\u9fff' for ch in text)


class Evaluator:
    def __init__(self, llm):
        self.llm = llm

    def evaluate(self, question: str, candidates: List[str]) -> str:
        if not candidates:
            return ""
        if len(candidates) == 1:
            return candidates[0]

        if is_chinese(question):
            prompt = f"问题：\"{question}\"\n候选答案：\n"
            prompt += "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
            prompt += "\n请选择与问题最相关且与提供信息一致的一条，仅输出该答案："
        else:
            prompt = f"Question: \"{question}\"\nCandidates:\n"
            prompt += "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
            prompt += "\nChoose the best answer and output only it:"

        return self.llm.complete(prompt).text.strip()
