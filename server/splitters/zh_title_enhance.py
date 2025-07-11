
from llama_index.core.schema import BaseNode # modified based on Document in Langchain
from typing import List
import re


def under_non_alpha_ratio(text: str, threshold: float = 0.5):
    
    if len(text) == 0:
        return False

    alpha_count = len([char for char in text if char.strip() and char.isalpha()])
    total_count = len([char for char in text if char.strip()])
    try:
        ratio = alpha_count / total_count
        return ratio < threshold
    except:
        return False


def is_possible_title(
        text: str,
        title_max_word_length: int = 20,
        non_alpha_threshold: float = 0.5,
) -> bool:

    if len(text) == 0:
        print("Not a title. Text is empty.")
        return False

    ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    if ENDS_IN_PUNCT_RE.search(text) is not None:
        return False

    if len(text) > title_max_word_length:
        return False

    if under_non_alpha_ratio(text, threshold=non_alpha_threshold):
        return False

    if text.endswith((",", ".", "，", "。")):
        return False

    if text.isnumeric():
        print(f"Not a title. Text is all numeric:\n\n{text}")
        return False

    if len(text) < 5:
        text_5 = text
    else:
        text_5 = text[:5]
    alpha_in_text_5 = sum(list(map(lambda x: x.isnumeric(), list(text_5))))
    if not alpha_in_text_5:
        return False

    return True


def zh_title_enhance(docs: List[BaseNode]) -> List[BaseNode]: 
    title = None
    if len(docs) > 0:
        for doc in docs:
            if is_possible_title(doc.text):
                doc.metadata['category'] = 'cn_Title'
                title = doc.text
            elif title:
                doc.text = f"下文与({title})有关。{doc.text}"
        return docs
    else:
        print("文件不存在")


import re
from llama_index.core.schema import TransformComponent

class ChineseTitleExtractor(TransformComponent):
    def __call__(self, nodes, **kwargs):
        nodes = zh_title_enhance(nodes)
        return nodes