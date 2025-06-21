import os, sys, importlib, time
from typing import List, Deque, Tuple
from collections import deque

import config
sys.modules['config'] = config

from tools.file_tool          import FileLoaderTool, save_uploaded_file
from tools.index_tool         import IndexManager
from tools.reranker_tool      import get_reranker
from tools.update_tracker_tool import start_daily_updates

from server.models.llm_tool   import create_openai_llm

from tools.planning_tool import Planner
from tools.retriever_tool import Retriever
from tools.generation_tool import Answerer
from tools.judge_tool import Evaluator
from tools.synthesis_tool import Synthesizer

class ConversationMemory:
    def __init__(self, max_rounds: int = 1, max_chars: int = 1500):
        self.buf: Deque[Tuple[str, str]] = deque(maxlen=max_rounds)
        self.max_chars = max_chars

    def add(self, role: str, content: str):  self.buf.append((role, content))

    def format(self) -> str:
        txt = "\n".join(f"{'用户' if r=='user' else '助手'}: {c}" for r, c in self.buf)
        return txt[-self.max_chars:] if len(txt) > self.max_chars else txt

def is_chinese(text: str) -> bool:
    return any('\u4e00' <= ch <= '\u9fff' for ch in text)


class AgentController:
    def __init__(self, top_k: int = config.TOP_K):

        ds = config.LLM_API_LIST["DeepSeek"]
        self.llm_cold = create_openai_llm(
            model_name=ds["models"][0],
            api_base=ds["api_base"],
            api_key=ds["api_key"],
            temperature=0.1,
        )
        self.llm_warm = create_openai_llm(
            model_name=ds["models"][0],
            api_base=ds["api_base"],
            api_key=ds["api_key"],
            temperature=0.7,
        )

        self.planner   = Planner(self.llm_cold)
        self.answerer  = Answerer(self.llm_warm)
        self.evaluator = Evaluator(self.llm_cold)
        self.synthesizer = Synthesizer(self.llm_cold)

        self.top_k = top_k
        self.use_rerank = getattr(config, "USE_RERANKER", False)
        self._init_index_and_retriever()
        self.reranker = get_reranker() if self.use_rerank else None

        # 记忆&定时
        self.memory = ConversationMemory()
        start_daily_updates()

    def _init_index_and_retriever(self):
        self.index_mgr = IndexManager(config.DEFAULT_INDEX_NAME)
        if not self.index_mgr.check_index_exists():
            self.index_mgr.load_dir(
                input_dir=FileLoaderTool.get_save_dir(),
                chunk_size=config.DEFAULT_CHUNK_SIZE,
                chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
            )
        else:
            self.index_mgr.load_index()

        self.retriever = Retriever(top_k=self.top_k, use_reranker=False)

    def _solve_subq(self, q: str) -> str:
        docs = self.retriever.retrieve(q)
        if self.use_rerank and self.reranker:
            docs = self.reranker(q, docs)
        hist = self.memory.format()
        if hist:
            docs.insert(0, f"对话历史：\n{hist}")

        cands = self.answerer.answer(q, docs)
        return self.evaluator.evaluate(q, cands)

    def run(self, question: str, doc_path: str | None = None) -> str:
        if doc_path and os.path.isfile(doc_path):
            save_uploaded_file(open(doc_path, "rb"), FileLoaderTool.get_save_dir())
            self.index_mgr.load_files(
                [{"name": os.path.basename(doc_path),
                  "getbuffer": lambda: open(doc_path, "rb").read()}],
                chunk_size=config.DEFAULT_CHUNK_SIZE,
                chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
            )
            self.retriever = Retriever(top_k=self.top_k, use_reranker=False)

        self.memory.add("user", question)
        sub_qs = self.planner.plan(question)
        bests  = [self._solve_subq(sq) for sq in sub_qs]
        final  = self.synthesizer.synthesize(question, bests)
        self.memory.add("assistant", final)
        return final
