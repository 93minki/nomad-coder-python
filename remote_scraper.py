from typing import Literal
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from job import Job


class RemoteScraper:
    def __init__(
        self,
        site_name: Literal["weworkremotely", "remoteok"],
        search_words: str | list[str] | None = None,
    ):
        if site_name == "weworkremotely":
            self.site_name = "weworkremotely"
            self.base_url = "https://weworkremotely.com"
        elif site_name == "remoteok":
            self.site_name = "remoteok"
            self.base_url = "https://remoteok.com"

        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        if search_words is None:
            self.search_words = []
        elif isinstance(search_words, str):
            self.search_words = [search_words]
        else:
            self.search_words = search_words
        self.search_result = []

    def search(self) -> None:
        if self.site_name == "weworkremotely":
            self.scrape_weworkremotely()
        elif self.site_name == "remoteok":
            self.scrape_remoteok()

    def scrape_weworkremotely(self) -> None:
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
                search_url = f"{self.base_url}/remote-jobs/search?term={search_word}"
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

                soup = BeautifulSoup(content, "html.parser")
                jobs = soup.select("section.jobs li.new-listing-container")

                for job in jobs:
                    title_tag = job.select_one(
                        "span.new-listing__header__title__text"
                    ) or job.select_one("h3.new-listing__header__title")

                    company_name_tag = job.select_one("p.new-listing__company-name")
                    company_hq_tag = job.select_one(
                        "p.new-listing__company-headquarters"
                    )
                    link_tag = job.select_one("a.listing-link--unlocked")

                    href = link_tag.get("href") if link_tag else None

                    job_url = urljoin(self.base_url, str(href)) if href else None
                    categories = [
                        category.get_text(strip=True)
                        for category in job.select(
                            "p.new-listing__categories__category"
                        )
                    ]

                    self.search_result.append(
                        Job(
                            title=title_tag.get_text(strip=True) if title_tag else None,
                            company_name=(
                                company_name_tag.get_text(strip=True)
                                if company_name_tag
                                else None
                            ),
                            company_hq=(
                                company_hq_tag.get_text(strip=True)
                                if company_hq_tag
                                else None
                            ),
                            categories=categories,
                            url=job_url,
                        )
                    )
        finally:
            page.close()
            browser.close()
            playwright.stop()

    def scrape_remoteok(self) -> None:
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

        try:
            for search_word in self.search_words:
                search_url = f"{self.base_url}/remote-{search_word}-jobs"
                print(search_url)
                page.goto(search_url)
                i = 0
                previous_height = page.evaluate("document.body.scrollHeight")
                while i < 2:
                    page.keyboard.press("End")
                    try:
                        page.wait_for_function(
                            "(prev) => document.body.scrollHeight > prev",
                            arg=previous_height,
                            timeout=3000,
                        )
                    except PlaywrightTimeoutError:
                        break
                    finally:
                        i += 1

                previous_height = page.evaluate("document.body.scrollHeight")

                content = page.content()

                soup = BeautifulSoup(content, "html.parser")
                jobs = soup.select("#jobsboard tr.job")

                for job in jobs:
                    title_tag = job.select_one("h2[itemprop='title']")
                    company_tag = job.select_one("h3[itemprop='name']")
                    location_tags = job.select("td.company.location .location")
                    tag_tags = job.select("td.tags a.tag")
                    link_tag = job.select_one("a[href*='/remote-jobs/']")

                    href = job.get("data-href") or (
                        link_tag.get("href") if link_tag else None
                    )
                    job_url = urljoin(self.base_url, href) if href else None

                    self.search_result.append(
                        Job(
                            title=title_tag.get_text(strip=True) if title_tag else None,
                            company_name=(
                                company_tag.get_text(strip=True)
                                if company_tag
                                else None
                            ),
                            location=[
                                loc.get_text(strip=True) for loc in location_tags
                            ],
                            tags=[tag.get_text(strip=True) for tag in tag_tags],
                            url=job_url,
                        )
                    )
        finally:
            page.close()
            browser.close()
            playwright.stop()


if __name__ == "__main__":
    # scraper = RemoteScraper(
    #     site_name="weworkremotely", search_words=["python", "javascript", "nodejs"]
    # )
    # scraper.search()
    # print(scraper.search_result)
    scraper = RemoteScraper(site_name="remoteok", search_words=["python"])
    scraper.search()
    print(scraper.search_result)
