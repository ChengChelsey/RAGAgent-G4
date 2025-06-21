import os
OLLAMA_API_URL = "disabled"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  
STORAGE_DIR = "storage"
DATA_DIR = "data"
MODEL_DIR = "localmodels"
CONFIG_STORE_FILE = "config_store.json"

LLM_DEVICE = "cpu"
EMBEDDING_DEVICE = "cpu"

HISTORY_LEN = 3
MAX_TOKENS = 2048
TEMPERATURE = 0.1
TOP_K = 5

SYSTEM_PROMPT = "You are an AI assistant that helps users to find accurate information. You can answer questions, provide explanations, and generate text based on the input. Please answer the user's question exactly in the same language as the question or follow user's instructions. For example, if user's question is in Chinese, please generate answer in Chinese as well. If you don't know the answer, please reply the user that you don't know. If you need more information, you can ask the user for clarification. Please be professional to the user."

RESPONSE_MODE = [
            "compact",
            "refine",
            "tree_summarize",
            "simple_summarize",
            "accumulate",
            "compact_accumulate",
]
DEFAULT_RESPONSE_MODE = "simple_summarize"

# 需要填入key LLM才能正常运行
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

LLM_API_LIST = {
    "DeepSeek": {
        "api_key": DEEPSEEK_API_KEY,
        "api_base": "https://uni-api.cstcloud.cn/v1/",
        "models": ["deepseek-v3:671b"],
        "provider": "DeepSeek",
    },
    "OpenAI": {
        "api_key": OPENAI_API_KEY,
        "api_base": "https://api.openai.com/v1/",
        "models": ["gpt-4", "gpt-3.5", "gpt-4o"],
        "provider": "OpenAI",
    },
    "Ollama": {
        "api_base": OLLAMA_API_URL,
        "models": [],
        "provider": "Ollama",}
    
}

DEFAULT_CHUNK_SIZE = 2048
DEFAULT_CHUNK_OVERLAP = 512
ZH_TITLE_ENHANCE = False


MONGO_URI = "mongodb://localhost:27017"
REDIS_URI = "redis://localhost:6379"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
ES_URI = "http://localhost:9200"

DEFAULT_VS_TYPE = "chroma"

DEFAULT_CHAT_STORE = "simple"#"redis"
CHAT_STORE_FILE_NAME = "chat_store.json"
CHAT_STORE_KEY = "user1"

HF_ENDPOINT = "https://hf-mirror.com"

DEFAULT_EMBEDDING_MODEL = "bge-small-zh-v1.5"
EMBEDDING_MODEL_PATH = {
    "bge-small-zh-v1.5": "BAAI/bge-small-zh-v1.5",
    "bge-large-zh-v1.5": "BAAI/bge-large-zh-v1.5",
}

DEFAULT_RERANKER_MODEL = "bge-reranker-base"
RERANKER_MODEL_PATH = {
    "bge-reranker-base": "BAAI/bge-reranker-base",
    "bge-reranker-large": "BAAI/bge-reranker-large",
}

USE_RERANKER = False
RERANKER_MODEL_TOP_N = 2
RERANKER_MAX_LENGTH = 1024


RAGA_ENV = os.getenv("RAGA_ENV", "development")
DEV_MODE = RAGA_ENV == "development"

DEFAULT_INDEX_NAME = "knowledge_base"