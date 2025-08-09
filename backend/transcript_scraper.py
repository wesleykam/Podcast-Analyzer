import re
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


class TranscriptScraper:
    """
    Scrapes transcript text from a page that either:
      1) renders transcript directly with .cfm-transcript-content
      2) embeds transcript in an <iframe> whose src is a full HTML page of <p> tags

    Use:
        scraper = TranscriptScraper()
        driver = scraper.new_driver()
        driver.get(url)
        text = scraper.extract(driver)
    """

    TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")

    def __init__(
        self,
        timeout: int = 15,
        strip_timestamps: bool = True,
        iframe_selector: str = (
            "iframe.transcript-iframe, "
            ".transcript-section iframe, "
            "iframe[src*='transcripts'], "
            "iframe[src*='transcript']"
        ),
        basic_selector_class: str = "cfm-transcript-content",
    ):
        self.timeout = timeout
        self.strip_timestamps = strip_timestamps
        self.iframe_selector = iframe_selector
        self.basic_selector_class = basic_selector_class

    # ---------- public API ----------

    def new_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,1200")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

    def extract(self, driver) -> str:
        """
        Try basic scrape first; if empty, try iframe scrape.
        """
        text = self.scrape_basic(driver)
        if text:
            return text

        return self.scrape_iframe(driver) or ""

    # ---------- basic scrape ----------

    def scrape_basic(self, driver) -> str:
        """
        Get transcript text from on-page elements with the configured class.
        """
        try:
            elements = WebDriverWait(driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, self.basic_selector_class))
            )
        except Exception:
            return ""

        paragraphs = [e.text.strip() for e in elements if e.text and e.text.strip()]
        return self._clean_join(paragraphs)

    # ---------- iframe scrape (open src in new tab and collect <p>) ----------

    def scrape_iframe(self, driver) -> str:
        """
        Find a transcript iframe, open its src in a NEW TAB, and return all <p> text.
        """
        wait = WebDriverWait(driver, self.timeout)
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.iframe_selector)))
        except Exception:
            return ""

        src = iframe.get_attribute("src")
        if not src:
            return ""
        
        original = driver.current_window_handle
        driver.switch_to.default_content()

        driver.switch_to.new_window("tab")
        driver.get(src)

        try:
            ps = WebDriverWait(driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "p"))
            )
            paragraphs = [p.text for p in ps if p.text]
            return self._clean_join(paragraphs)
        finally:
            # Close the iframe tab and return to original window
            try:
                driver.close()
            finally:
                driver.switch_to.window(original)

    # ---------- helpers ----------

    def _clean_join(self, paragraphs: List[str]) -> str:
        cleaned = []
        for p in paragraphs:
            t = p
            if self.strip_timestamps:
                t = self.TIMESTAMP_RE.sub("", t)
            t = re.sub(r"\s+", " ", t).strip()
            if t:
                cleaned.append(t)
        # join with newlines for readability
        return "\n".join(cleaned)


if __name__ == "__main__":
    # Replace this with a page URL that contains ONLY an iframe transcript
    test_url = "https://thisweekhealth.com/"

    scraper = TranscriptScraper(strip_timestamps=True)  # change to True if you want timestamps removed
    driver = scraper.new_driver()

    try:
        driver.get(test_url)
        transcript = scraper.extract(driver)  # directly test iframe method
        if transcript:
            print("=== TRANSCRIPT ===")
            print(transcript)
        else:
            print("No transcript found in iframe.")
    finally:
        driver.quit()
