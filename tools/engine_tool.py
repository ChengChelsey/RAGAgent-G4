
import config as config
from reranker_tool import create_reranker_model
from server.prompt import text_qa_template, refine_template
from retriever_tool import SimpleFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

def create_query_engine(index, 
                        top_k=config.TOP_K, 
                        response_mode=config.RESPONSE_MODE, 
                        use_reranker=config.USE_RERANKER, 
                        top_n=config.RERANKER_MODEL_TOP_N, 
                        reranker=config.DEFAULT_RERANKER_MODEL):
    node_postprocessors = [create_reranker_model(model_name=reranker, top_n=top_n)] if use_reranker else []
    retriever = SimpleFusionRetriever(vector_index=index, top_k=top_k)

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        node_postprocessors=node_postprocessors,
        response_mode=response_mode,
        verbose=True,
        streaming=True,
    )

    return query_engine
