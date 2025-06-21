
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.retrievers.bm25 import BM25Retriever
import os, config
from typing import List
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from tools.index_tool  import IndexManager
from tools.engine_tool import create_query_engine


import jieba
from typing import List

class Retriever:
    def __init__(self, top_k: int = 3, use_reranker: bool = True):
        embed_name = config.EMBEDDING_MODEL_PATH[config.DEFAULT_EMBEDDING_MODEL]
        Settings.embed_model = HuggingFaceEmbedding(model_name=embed_name)

        config.USE_RERANKER = use_reranker
        im = IndexManager(index_name=config.DEFAULT_INDEX_NAME)

        if im.check_index_exists():
            index = im.load_index()
        else:
            data_dir = config.DATA_DIR
            if not os.path.isabs(data_dir):
                cand = os.path.join(os.getcwd(), data_dir)
                if not os.path.isdir(cand):
                    pkg_root = os.path.dirname(config.__file__)
                    cand = os.path.join(pkg_root, data_dir)
                data_dir = cand
            if not (os.path.isdir(data_dir) and os.listdir(data_dir)):
                raise RuntimeError("未发现已持久化索引，且 data 目录为空。")
            im.load_dir(
                input_dir=data_dir,
                chunk_size=config.DEFAULT_CHUNK_SIZE,
                chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
            )
            index = im.index

        self.qe = create_query_engine(
            index=index,
            top_k=top_k,
            response_mode=config.DEFAULT_RESPONSE_MODE,
            use_reranker=use_reranker,
            top_n=config.RERANKER_MODEL_TOP_N,
        )
        self.top_k = top_k

    def retrieve(self, query: str) -> List[str]:
        nodes = self.qe._retriever.retrieve(query)[: self.top_k]
        return [n.node.get_content().strip() for n in nodes]
    
def chinese_tokenizer(text: str) -> List[str]:
    return list(jieba.cut(text))

class SimpleBM25Retriever(BM25Retriever):
    @classmethod
    def from_defaults(cls, index, similarity_top_k, **kwargs) -> "BM25Retriever":
        docstore = index.docstore
        return BM25Retriever.from_defaults(
            docstore=docstore, similarity_top_k=similarity_top_k, verbose=True,
            tokenizer=chinese_tokenizer, **kwargs
        )


class SimpleHybridRetriever(BaseRetriever):
    def __init__(self, vector_index, top_k=2):
        self.top_k = top_k

        self.vector_retriever = VectorIndexRetriever(
            index=vector_index, similarity_top_k=top_k, verbose=True,
        )

        self.bm25_retriever = SimpleBM25Retriever.from_defaults(
            index=vector_index, similarity_top_k=top_k,
        )

        super().__init__()

    def _retrieve(self, query, **kwargs):
        bm25_nodes = self.bm25_retriever.retrieve(query, **kwargs)

        min_score = min(item.score for item in bm25_nodes)
        max_score = max(item.score for item in bm25_nodes)

        normalized_data = [(item.score - min_score) / (max_score - min_score) for item in bm25_nodes]

        for item, normalized_score in zip(bm25_nodes, normalized_data):
            item.score = normalized_score

        vector_nodes = self.vector_retriever.retrieve(query, **kwargs)

        all_nodes = []
        node_ids = set()
        count = 0
        for n in vector_nodes + bm25_nodes:
            if n.node.node_id not in node_ids:
                all_nodes.append(n)
                node_ids.add(n.node.node_id)
                count += 1
            if count >= self.top_k:
                break
        for node in all_nodes:
            print(f"Hybrid Retrieved Node: {node.node_id} - Score: {node.score:.2f} - {node.text[:10]}...\n-----")
        return all_nodes

from llama_index.core.retrievers import QueryFusionRetriever
from enum import Enum



class FUSION_MODES(str, Enum):
    RECIPROCAL_RANK = "reciprocal_rerank" 
    RELATIVE_SCORE = "relative_score"
    DIST_BASED_SCORE = "dist_based_score"
    SIMPLE = "simple"

class SimpleFusionRetriever(QueryFusionRetriever):
    def __init__(self, vector_index, top_k=2, mode=FUSION_MODES.DIST_BASED_SCORE):
        self.top_k = top_k
        self.mode = mode

        self.vector_retriever = VectorIndexRetriever(
            index=vector_index, similarity_top_k=top_k, verbose=True,
        )

        self.bm25_retriever = SimpleBM25Retriever.from_defaults(
            index=vector_index, similarity_top_k=top_k,
        )

        super().__init__(
            [self.vector_retriever, self.bm25_retriever],
            retriever_weights=[0.6, 0.4],
            similarity_top_k=top_k,
            num_queries=1,
            mode=mode,
            use_async=True,
            verbose=True,
        )