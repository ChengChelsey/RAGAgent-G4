import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.readers.base import BasePydanticReader
from llama_index.core.schema import Document

logger = logging.getLogger(__name__)


def _mpweixin_reader(soup: Any, **kwargs) -> Tuple[str, Dict[str, Any]]:
    """Extract text from Substack blog post."""
    meta_tag_title = soup.find('meta', attrs={'property': 'og:title'})
    title = meta_tag_title['content']
    extra_info = {
        "title": title,
    }
    text = soup.select_one("div #page-content").getText()
    return text, extra_info


DEFAULT_WEBSITE_EXTRACTOR: Dict[
    str, Callable[[Any, str], Tuple[str, Dict[str, Any]]]
] = {
    "mp.weixin.qq.com": _mpweixin_reader,
}


class BeautifulSoupWebReader(BasePydanticReader):

    is_remote: bool = True
    _website_extractor: Dict[str, Callable] = PrivateAttr()

    def __init__(self, website_extractor: Optional[Dict[str, Callable]] = None) -> None:
        super().__init__()
        self._website_extractor = website_extractor or DEFAULT_WEBSITE_EXTRACTOR

    @classmethod
    def class_name(cls) -> str:
        """Get the name identifier of the class."""
        return "BeautifulSoupWebReader"

    def load_data(
        self,
        urls: List[str],
        custom_hostname: Optional[str] = None,
        include_url_in_text: Optional[bool] = True,
    ) -> List[Document]:

        from urllib.parse import urlparse

        import requests
        from bs4 import BeautifulSoup

        documents = []
        for url in urls:
            try:
                page = requests.get(url)
                hostname = custom_hostname or urlparse(url).hostname or ""

                soup = BeautifulSoup(page.content, "html.parser")

                data = ""
                extra_info = {
                    "title": soup.select_one("title"),
                    "url_source": url,
                    "creation_date": datetime.now().date().isoformat(),
                    }
                if hostname in self._website_extractor:
                    data, metadata = self._website_extractor[hostname](
                        soup=soup, url=url, include_url_in_text=include_url_in_text
                    )
                    extra_info.update(metadata)

                else:
                    data = soup.getText()

                documents.append(Document(text=data, id_=url, extra_info=extra_info))
            except Exception:
                print(f"Could not scrape {url}")
                raise ValueError(f"One of the inputs is not a valid url: {url}")

        return documents
