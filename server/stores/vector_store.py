
import config

def create_vector_store(type=config.DEFAULT_VS_TYPE):
    if type == "chroma":

        import chromadb
        from llama_index.vector_stores.chroma import ChromaVectorStore

        db = chromadb.PersistentClient(path=".chroma")
        chroma_collection = db.get_or_create_collection("think")
        chroma_vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        return chroma_vector_store
    elif type == "es":
        

        from llama_index.vector_stores.elasticsearch import ElasticsearchStore
        from llama_index.vector_stores.elasticsearch import AsyncDenseVectorStrategy

        es_vector_store = ElasticsearchStore(
        es_url="http://localhost:9200",
        index_name="think",
        retrieval_strategy=AsyncDenseVectorStrategy(hybrid=False),
        )
        return es_vector_store
    elif type == "lancedb":
        
        from llama_index.vector_stores.lancedb import LanceDBVectorStore
        from lancedb.rerankers import LinearCombinationReranker
        reranker = LinearCombinationReranker(weight=0.9)

        lance_vector_store = LanceDBVectorStore(
            uri=".lancedb", mode="overwrite", query_type="vector", reranker=reranker
        )
        return lance_vector_store
    elif type == "simple":
        from llama_index.core.vector_stores import SimpleVectorStore
        return SimpleVectorStore()
    else:
        raise ValueError(f"Invalid vector store type: {type}")

if config.RAGA_ENV == "production":
    VECTOR_STORE = create_vector_store(type="chroma")
else:
    VECTOR_STORE = create_vector_store(type="simple")