import os
import re
from config import DATA_DIR

class FileLoaderTool:
    
    @staticmethod
    def get_save_dir() -> str:
        return get_save_dir()

    @staticmethod
    def save_document(title: str, content: str) -> bool:
        save_dir = FileLoaderTool.get_save_dir()
        safe_name = re.sub(r'[\\/:*?"<>|]', "", title)
        file_path = os.path.join(save_dir, safe_name + ".txt")
        if os.path.exists(file_path):
            return False
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"新文档已保存：{file_path}")
        return True

def get_save_dir():
    save_dir = os.path.join(os.getcwd(), DATA_DIR)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def save_uploaded_file(uploaded_file: bytes, save_dir: str):
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        path = os.path.join(save_dir, uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        print(f"已保存 {path}")
    except Exception as e:
        print(f"Error saving upload to disk: {e}")