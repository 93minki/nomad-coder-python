from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from job import Job


class WantedScraper:
    def __init__(self, search_words: str | list[str] | None = None):
        if search_words is None:
            self.search_words = []
        elif isinstance(search_words, str):
            self.search_words = [search_words]
        else:
            self.search_words = search_words
        self.search_results: list[Job] = []
        self.base_url = "https://www.wanted.co.kr"
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )

    def search(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
        context = browser.new_context(
            locale="ko-KR",
            user_agent=self.user_agent,
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        try:
            for search_word in self.search_words:
                search_url = f"{self.base_url}/search?query={search_word}&search_method=direct&tab=position"
                print(search_url)
                page.goto(search_url)

                previous_height = page.evaluate("document.body.scrollHeight")
                while True:
                    page.keyboard.press("End")
                    try:
                        page.wait_for_function(
                            "(prev) => document.body.scrollHeight > prev",
                            arg=previous_height,
                            timeout=3000,
                        )
                    except PlaywrightTimeoutError:
                        break

                    previous_height = page.evaluate("document.body.scrollHeight")

                content = page.content()
                page.close()

                soup = BeautifulSoup(content, "html.parser")
                jobs = soup.find_all("div", class_="JobCard_container__zQcZs")

                for job in jobs:
                    a = job.find("a")

                    link = f"https://www.wanted.co.kr{a['href']}"
                    company_name = a["data-company-name"]
                    title = a["data-position-name"]

                    spans = [s.get_text(strip=True) for s in a.find_all("span")]
                    experience = next(
                        (s for s in spans if s.startswith(("신입", "경력"))), None
                    )
                    reward = next((s for s in spans if "합격보상금" in s), None)

                    self.search_results.append(
                        Job(
                            title=title,
                            url=link,  # link → url
                            company_name=company_name,
                            experience=experience,
                            reward=reward,
                        )
                    )
        finally:
            page.close()
            browser.close()
            playwright.stop()


if __name__ == "__main__":
    s = WantedScraper("apple")
    s.search()
    print(s.search_results)
