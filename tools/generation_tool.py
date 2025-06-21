import time
from typing import List

def is_chinese(text): return any('\u4e00' <= ch <= '\u9fff' for ch in text)


class Answerer:
    """
    :param llm:      已初始化的 LLM 对象
    :param num_candidates: 候选答案数量
    """
    def __init__(self, llm, num_candidates: int = 2):
        self.llm = llm
        self.num = num_candidates

    def answer(self, question: str, docs: List[str]) -> List[str]:
        ctx = "\n\n".join(docs) if docs else ""
        if is_chinese(question):
            prompt = (f"以下是一些相关信息：\n{ctx}\n\n"
                      f"请根据以上信息回答问题，请确保所有要点都与原问题强相关，"
                      f"相关性低的去除：\"{question}\"")
        else:
            prefix = f"Background:\n{ctx}\n\n" if ctx else ""
            prompt = f"{prefix}Answer concisely: \"{question}\""

        answers = []
        for _ in range(self.num):
            try:
                ans = self.llm.complete(prompt).text.strip()
                if ans:
                    answers.append(ans)
            except Exception as e:
                print("[WARN] LLM 调用异常:", e)
            time.sleep(0.05) # 规避限流
        return answers
