import time
import re, sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from typing import List   
import streamlit as st
import pandas as pd
from server.stores.chat_store import CHAT_MEMORY
from llama_index.core.llms import ChatMessage, MessageRole
from server.stores.config_store import CONFIG_STORE
from agent_controller import AgentController

if "agent" not in st.session_state:
    st.session_state.agent = AgentController()

def perform_query(prompt: str) -> str:
    """
    调用多轮 AgentController，返回答案字符串和检索片段。
    """
    if not prompt or prompt.strip() == "":
        st.warning("请输入有效问题")
        return None

    try:
        answer = st.session_state.agent.run(prompt)
        src_nodes: List = getattr(st.session_state.agent.retriever, "last_nodes", [])
        return answer, src_nodes
    except Exception as e:
        st.error(f"查询出错: {type(e).__name__}: {e}")
        return None


def chatbox(agent):
    messages = CHAT_MEMORY.get()
    if not messages:
        CHAT_MEMORY.put(ChatMessage(role=MessageRole.ASSISTANT,
                                    content="您好！请在下方提问。"))
        messages = CHAT_MEMORY.get()
    for m in messages:
        with st.chat_message(m.role):
            st.write(m.content)

    if prompt := st.chat_input("请输入问题"):
        with st.chat_message(MessageRole.USER):
            st.write(prompt)
            CHAT_MEMORY.put(ChatMessage(role=MessageRole.USER, content=prompt))

        with st.chat_message(MessageRole.ASSISTANT):
            with st.spinner("生成中..."):
                t0 = time.time()
                try:
                    answer = agent.run(prompt)
                    src_nodes = getattr(agent.retriever, "last_nodes", [])

                    print(f"[INFO] 用时 {time.time()-t0:.2f}s, 子问题 {len(getattr(st.session_state.agent, 'last_subqs', []))}")

                except Exception as e:
                    st.error(f"出错：{e}")
                    return

                st.markdown(answer, unsafe_allow_html=True)

                if src_nodes:
                    with st.expander(f"参考片段（{len(src_nodes)}）", expanded=False):
                        rows = []
                        for n in src_nodes:
                            md = n.node.metadata
                            rows.append({
                                "文件": md.get("file_name", "N/A"),
                                "页码": md.get("page_label", "N/A"),
                                "内容": n.node.get_content()[:60] + "..."
                            })
                        st.table(pd.DataFrame(rows))

                CHAT_MEMORY.put(ChatMessage(role=MessageRole.ASSISTANT,
                                            content=answer))


def _inject_chat_css() -> None:
    st.markdown(
        """
        <style>
        .stChatMessage {
            background: transparent !important;
            box-shadow: none !important;
            padding: 0.25rem 0 !important;
        }

        .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
            display: flex;
            flex-direction: row-reverse;
            align-items: flex-start;
        }

        .stChatMessage:has([data-testid="stChatMessageAvatarUser"])
          [data-testid="stChatMessageAvatarUser"] {
            margin-left: 0.25rem;
            margin-right: 0;
        }

        .stChatMessage:has([data-testid="stChatMessageAvatarUser"])
          [data-testid="stChatMessageContent"] {
            background: transparent !important;
            box-shadow: none !important;
            padding: 0;
            text-align: right;
        }

    .stChatMessage:has([data-testid="stChatMessageAvatarUser"])
      [data-testid="stChatMessageContent"] > div:first-child {
        display: inline-block;
        background: #ECECEC;
        padding: 0.45rem 0.75rem;
        border-radius: 0.75rem;
        max-width: 85%;
        line-height: 1.4;
        margin: 0;
      }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    if "agent" not in st.session_state:
        st.session_state.agent = AgentController()
    agent = st.session_state.agent

    _inject_chat_css()     
    st.header("智能问答助手")
    info = CONFIG_STORE.get("current_llm_info") or {}
    cfg  = CONFIG_STORE.get("current_llm_settings") or {}

    chatbox(agent)

main()