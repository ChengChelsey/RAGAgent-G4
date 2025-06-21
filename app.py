
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import streamlit as st
from frontend.state import init_state

if __name__ == '__main__':

    st.set_page_config(
        page_title="RAGAgent",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    init_state()

    pages = {
        "聊天" : [
            st.Page("frontend/Document_QA.py", title="智能问答助手")
        ],
        "知识库" : [
           st.Page("frontend/KB_File.py", title="文件上传"),
           st.Page("frontend/KB_Manage.py", title="文件管理"),
        ],
    }

    pg = st.navigation(pages, position="sidebar")

    pg.run()