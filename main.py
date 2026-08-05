import csv

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class WantedScraper:
    def __init__(self, search_word):
        self.search_word = search_word
        self.search_results = []
        self.search_url = f"https://www.wanted.co.kr/search?query={search_word}&search_method=direct&tab=position"

    def search(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
        context = browser.new_context(
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        page.goto(self.search_url)

        previous_height = page.evaluate("document.body.scrollHeight")
        while True:
            page.keyboard.press("End")
            try:
                page.wait_for_function(
                    "(prev) => document.body.scrollHeight > prev",
                    arg=previous_height,
                    timeout=3000,
                )
            except Exception:
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

            spans = [s.get_text(strip=True) for s in a.find_all("span")]
            experience = next(
                (s for s in spans if s.startswith(("신입", "경력"))), None
            )
            reward = next((s for s in spans if "합격보상금" in s), None)

            self.search_results.append(
                {
                    "link": link,
                    "company_name": company_name,
                    "experience": experience,
                    "reward": reward,
                }
            )

    def save_jobs(self):
        file = open(f"{self.search_word}.csv", "w")
        writer = csv.writer(file)
        writer.writerow(["title", "company_name", "link"])
        for job in self.search_results:
            writer.writerow(job.values())
        file.close()


if __name__ == "__main__":
    input = input("검색어를 입력하세요: ")
    scraper = WantedScraper(input)
    scraper.search()
    scraper.save_jobs()
