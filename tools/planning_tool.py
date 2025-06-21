
import re, difflib, time
from typing import List

def is_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


class Planner:
    def __init__(self, llm):
        self.llm = llm

    def _prompt(self, question: str) -> str:
        if is_chinese(question):
            return (
                "你是一名任务规划助手。\n"
                "若下列问题已足够具体，请直接原样输出；"
                "若需要，可拆分为至多两条子问题，每行一个。\n"
                f"问题：\"{question}\"\n输出："
            )
        return (
            "You are a task-planner.\n"
            "If the question below is already atomic, return it as-is; "
            "otherwise split it into **at most two** ordered sub-questions "
            "(one per line).\n"
            f"Question: \"{question}\"\nOutput:"
        )
    
    def plan(self, question: str) -> List[str]:
        resp = self.llm.complete(self._prompt(question)).text.strip()
        subqs = [re.sub(r"^[\d\-\.\s]*", "", ln).strip()
                 for ln in resp.splitlines() if ln.strip()]

        seen, uniq = set(), []
        for q in subqs:
            key = q.lower()
            if key not in seen:
                seen.add(key)
                uniq.append(q)

        if len(uniq) == 1:
            sim = difflib.SequenceMatcher(None, uniq[0], question).ratio()
            return [question] if sim >= .8 else uniq
        return uniq[:2]          # 最多两条
