
import os
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core import load_index_from_storage, load_indices_from_storage
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from file_tool import get_save_dir
from server.stores.strage_context import STORAGE_CONTEXT
from server.ingestion import AdvancedIngestionPipeline
from config import DEV_MODE
from datetime import datetime

class IndexManager:
    def __init__(self, index_name):
        self.index_name: str = index_name
        self.storage_context: StorageContext = STORAGE_CONTEXT
        self.index_id: str = None
        self.index: VectorStoreIndex = None

    def check_index_exists(self):
        indices = load_indices_from_storage(self.storage_context)
        print(f"Loaded {len(indices)} indices")
        if len(indices) > 0:
            self.index = indices[0]
            self.index_id = indices[0].index_id
            return True
        else:
            return False

    def init_index(self, nodes):
        if self.check_index_exists():
            return self.index
        self.index = VectorStoreIndex(nodes, 
                                      storage_context=self.storage_context, 
                                      store_nodes_override=True) # note: no nodes in doc store if using vector database, set store_nodes_override=True to add nodes to doc store
        self.index_id = self.index.index_id
        if DEV_MODE:
            self.storage_context.persist()
        print(f"Created index {self.index.index_id}")
        return self.index

    def load_index(self):
        if self.index_id is not None:
            self.index = load_index_from_storage(
                self.storage_context,
                index_id=self.index_id,
            )
            print(f"[IndexManager] Loaded index by id: {self.index_id}")

        else:
            indices = load_indices_from_storage(self.storage_context)
            if not indices:
                raise ValueError("No index found in storage_context .")
            self.index = indices[0]
            self.index_id = self.index.index_id
            print(f"[IndexManager] Loaded first index in storage: {self.index_id}")

        self.index._store_nodes_override = True
        return self.index
    
    def insert_nodes(self, nodes):
        if self.index is not None:

            self.index._store_nodes_override = True
            self.index.insert_nodes(nodes=nodes)
        else:
            self.init_index(nodes=nodes)

        # 持久化
        self.storage_context.persist()
        print(f"Inserted {len(nodes)} nodes into index {self.index.index_id}")
        return self.index
    
    def load_dir(self, input_dir, chunk_size, chunk_overlap):
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
        documents = SimpleDirectoryReader(input_dir=input_dir, recursive=True).load_data()
        if len(documents) > 0:
            pipeline = AdvancedIngestionPipeline()
            nodes = pipeline.run(documents=documents)
            index = self.insert_nodes(nodes)
            return nodes
        else:
            print("No documents found")
            return []
        
    def load_files(self, uploaded_files, chunk_size, chunk_overlap):
        
        from datetime import datetime
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap

        save_dir = get_save_dir()
        file_paths = [os.path.join(save_dir, f["name"]) for f in uploaded_files]
        print("[IndexManager] preparing to load files:", file_paths)

        documents = SimpleDirectoryReader(input_files=file_paths).load_data()

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for doc in documents:
            md = doc.metadata
            if "file_path" not in md or not md["file_path"]:
                md["file_path"] = doc.metadata.get("file_path", doc.id)
            if "file_name" not in md or not md["file_name"]:
                md["file_name"] = os.path.basename(md["file_path"])
            if "creation_date" not in md:
                md["creation_date"] = now_str


        if documents:
            pipeline = AdvancedIngestionPipeline()
            nodes = pipeline.run(documents=documents)
            return self.insert_nodes(nodes)
        else:
            print("[IndexManager] No documents found")
            return []
        
    def load_websites(self, websites, chunk_size, chunk_overlap):
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap

        from server.readers.beautiful_soup_web import BeautifulSoupWebReader
        documents = BeautifulSoupWebReader().load_data(websites)        
        if len(documents) > 0:
            pipeline = AdvancedIngestionPipeline()
            nodes = pipeline.run(documents=documents)
            index = self.insert_nodes(nodes)
            return nodes
        else:
            print("No documents found")
            return []
    
    def delete_ref_doc(self, ref_doc_id):
        self.index.delete_ref_doc(ref_doc_id=ref_doc_id, delete_from_docstore=True)
        self.storage_context.persist()
        print("Deleted document", ref_doc_id)