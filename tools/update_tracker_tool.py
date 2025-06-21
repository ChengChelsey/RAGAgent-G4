import os
import re
import time
import glob
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from apscheduler.schedulers.background import BackgroundScheduler
from .file_tool import FileLoaderTool

def safe_filename(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "", title)


def wait_for_new_file(directory: str, before: set, timeout: int = 30):
    elapsed = 0
    while elapsed < timeout:
        now_set = set(glob.glob(os.path.join(directory, "*")))
        new_files = now_set - before
        if new_files:
            return new_files.pop()
        time.sleep(1)
        elapsed += 1
    return None

def fetch_latest_papers():
    loader = FileLoaderTool()
    save_dir = loader.get_save_dir()

    chrome_opts = Options()
    chrome_opts.headless = True
    prefs = {
        "download.default_directory": save_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_opts.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_opts)

    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://kns.cnki.net/kns8/defaultresult/index")
        wait.until(EC.presence_of_element_located((By.ID, "txt_search"))).send_keys("药膳")
        driver.find_element(By.ID, "btnSearch").click()

        try:
            wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "按时间排序"))).click()
        except Exception:
            pass

        main_window = driver.current_window_handle
        results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/Detail']"))
        )[:20]

        downloaded = 0
        for link in results:
            title = link.text.strip()
            if not title:
                continue

            base_name = safe_filename(title)
            pdf_path = os.path.join(save_dir, base_name + ".pdf")
            txt_path = os.path.join(save_dir, base_name + ".txt")
            if os.path.exists(pdf_path) or os.path.exists(txt_path):
                continue

            link.click()
            time.sleep(2)
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    break

            pdf_downloaded = False
            abstract_text = ""

            try:
                driver.find_element(By.LINK_TEXT, "PDF下载").click()
                before_set = set(glob.glob(os.path.join(save_dir, "*")))
                new_file = wait_for_new_file(save_dir, before_set, timeout=40)
                if new_file:
                    os.rename(new_file, pdf_path)
                    pdf_downloaded = True
            except Exception:
                pass

            try:
                abstract_text = driver.find_element(By.ID, "ChDivSummary").text.strip()
            except Exception:
                pass

            driver.close()
            driver.switch_to.window(main_window)

            if abstract_text:
                loader.save_document(title, abstract_text)

            if pdf_downloaded or abstract_text:
                downloaded += 1
                print(f"[UpdateTracker] 已抓取：{title}")

            if downloaded >= 10:
                break  # 最多10篇

    except Exception as e:
        print(f"[UpdateTracker] 抓取异常：{e}")
    finally:
        driver.quit()


def start_daily_updates():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_latest_papers, 'cron', hour=0, minute=0)
    scheduler.start()
    print("[UpdateTracker] 已启动每日 00:00 自动抓取“药膳”文献任务")
