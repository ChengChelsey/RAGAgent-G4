from llama_index.core import Settings
from langchain_openai import ChatOpenAI
from llama_index.llms.langchain import LangChainLLM

def create_openai_llm(model_name:str, api_base:str, api_key:str, temperature:float = 0.5, system_prompt:str = None) -> ChatOpenAI:
    try:
        llm = LangChainLLM(
            llm=ChatOpenAI(
                base_url=api_base, 
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                timeout=60
            ),
            system_prompt=system_prompt,
        )
        Settings.llm = llm
        return llm
    except Exception as e:
        print(f"An error occurred while creating the OpenAI compatibale model: {type(e).__name__}: {e}")
        return None
    
def check_openai_llm(model_name, api_base, api_key) -> bool:
        # Make a simple API call to verify the key
    try:
        llm = ChatOpenAI(
            base_url=api_base, 
            api_key=api_key,
            model_name=model_name,
            timeout=60,
            max_retries=1
        )
        llm.invoke("ping")         
        return True
    except Exception as e:
        print(f"An error occurred while verifying the LLM API: {type(e).__name__}: {e}")
        return False
