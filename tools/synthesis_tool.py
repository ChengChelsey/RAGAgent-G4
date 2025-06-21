from typing import List

def is_chinese(text): return any('\u4e00' <= ch <= '\u9fff' for ch in text)


class Synthesizer:
    def __init__(self, llm):
        self.llm = llm

    def synthesize(self, original_q: str, answers: List[str]) -> str:
        if not answers:
            return ""
        if len(answers) == 1:
            return answers[0]

        if is_chinese(original_q):
            prompt = f"原始问题：\"{original_q}\"。\n"
            prompt += "请仅基于以下子问题答案，撰写完整、连贯且结构清晰的最终回答，去除与原问题关联性低的内容：\n"
            for i, ans in enumerate(answers, 1):
                prompt += f"子问题{i}答案：{ans}\n"
            prompt += "最终回答："
        else:
            prompt = f"Original question: \"{original_q}\"\n"
            prompt += "Based ONLY on the answers below, craft a coherent final answer.\n"
            for i, ans in enumerate(answers, 1):
                prompt += f"Answer {i}: {ans}\n"
            prompt += "Final answer:"

        return self.llm.complete(prompt).text.strip()
