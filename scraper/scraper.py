import asyncio
import csv
import os
import time
from typing import Generator, List, Optional, Tuple

import aiofiles
import requests
from aiocsv.writers import AsyncWriter
from bs4 import BeautifulSoup

from .constants import parts_of_speech


class WebScraper:
    CSV_PATH: str = os.path.join("data", "idioms-2.csv")
    CSV_HEADERS: List[str] = ["idiom", "part_of_speech", "word_url"]
    BASE_URL: str = "https://en.wiktionary.org/"
    IDIOMS_URL: str = "https://en.wiktionary.org/wiki/Category:English_idioms"

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.row_index = 0

    def run(self):
        print("starting scraper.")
        start = time.time()
        with open(self.CSV_PATH, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.CSV_HEADERS)
        self.loop.run_until_complete(self.write_rows(self.IDIOMS_URL))
        end = time.time()
        print(f"all rows appended.\ncsv saved, time taken: {end - start}s")

    async def write_rows(self, url: str):
        words_list = self.get_words_list(url)
        async with aiofiles.open(
            self.CSV_PATH, mode="a", encoding="utf-8", newline=""
        ) as afp:
            writer = AsyncWriter(afp, dialect="unix")
            for row in self.generate_row(words_list):
                await writer.writerow(row)
                self.row_index += 1
                print(
                    f"row appended for idiom '{row[0]}' - row_count: {self.row_index}"
                )

        url = self.get_next_url(url)
        return await self.write_rows(url) if url else None

    def generate_row(
        self, words_list: Optional[List[BeautifulSoup]]
    ) -> Generator[Tuple, None, None]:
        if not words_list:
            raise Exception("Error: words_list is None")

        for word_el in words_list:
            word = word_el.next.get("title")  # type: ignore
            word_underscores = word.replace(" ", "_")  # type: ignore
            word_url = f"https://en.wiktionary.org/wiki/{word_underscores}#English"
            soup = self.make_soup(word_url)
            main_section = soup.find("div", class_="mw-parser-output")
            if part_of_speech := self.get_pos(main_section):
                yield (
                    word,
                    part_of_speech.lower(),  # type: ignore
                    word_url,
                )

    def get_url_response(self, url: str) -> Optional[requests.Response]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    def get_next_url(self, url: str) -> str:
        soup = self.make_soup(url)
        try:
            href = soup.find(string="next page").parent.get("href")  # type: ignore
        except AttributeError as e:
            raise Exception(f"Error: Cannot find next url %s", e)

        return f"{self.BASE_URL}{href}"

    def make_soup(self, url) -> BeautifulSoup:
        if not (response := self.get_url_response(url)):
            raise Exception("Error: Response should not be None")
        return BeautifulSoup(response.content, "html.parser")

    def get_pos(self, section) -> Optional[List]:
        for p in parts_of_speech:
            try:
                return section.find(id=p).text
            except AttributeError:
                pass

    def get_words_list(self, url: str) -> Optional[List[BeautifulSoup]]:
        soup = self.make_soup(url)
        words_section = soup.find("div", class_="mw-category mw-category-columns")
        if not words_section:
            print(f"Reached final page: {url}")
            return
        return words_section.find_all("li")  # type: ignore


if __name__ == "__main__":
    webscraper = WebScraper()
    webscraper.run()
