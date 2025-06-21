
from llama_index.core import Settings
from llama_index.core.ingestion import IngestionPipeline, DocstoreStrategy
from server.splitters import ChineseTitleExtractor
from server.stores.strage_context import STORAGE_CONTEXT
from server.stores.ingestion_cache import INGESTION_CACHE

class AdvancedIngestionPipeline(IngestionPipeline):
    def __init__(
        self, 
    ):
        embed_model = Settings.embed_model
        text_splitter = Settings.text_splitter

        super().__init__(
            transformations=[
                text_splitter,
                embed_model,
                ChineseTitleExtractor(),
            ],
            docstore=STORAGE_CONTEXT.docstore,
            vector_store=STORAGE_CONTEXT.vector_store,
            cache=INGESTION_CACHE,
            docstore_strategy=DocstoreStrategy.UPSERTS, 
        )

    def run(self, documents):
        print(f"Load {len(documents)} Documents")
        nodes = super().run(documents=documents)
        print(f"Ingested {len(nodes)} Nodes")
        return nodes