import os
import csv
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .constants import parts_of_speech

FILE_PATH = os.path.join("data", "idioms-2.csv")
BASE_URL = "https://en.wiktionary.org/"
IDIOMS_URL = "https://en.wiktionary.org/wiki/Category:English_idioms"
HEADERS = ["idiom", "part_of_speech", "word_url"]


def get_url_response(url: str) -> Optional[requests.Response]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def get_next_url(url: str) -> Optional[str]:
    response = get_url_response(url)
    soup = make_soup(response)
    try:
        href = soup.find(string="next page").parent.get("href")
    except AttributeError:
        return

    return f"{BASE_URL}{href}"


def make_soup(response: requests.Response) -> BeautifulSoup:
    return BeautifulSoup(response.content, "html.parser")


def get_pos(section) -> Optional[List]:
    for p in parts_of_speech:
        try:
            return section.find(id=p).text
        except AttributeError:
            pass


def get_etymology(section) -> Optional[List]:
    try:
        etymology = []
        etymology_id = section.find(id="Etymology")
        for etym in etymology_id.parent.next_siblings:
            if etym.name == "h3":
                break
            if etym.text != "\n":
                etymology.append(etym.text)
        return etymology
    except AttributeError:
        pass


def get_definitions(section) -> Optional[List]:
    try:
        definition_elements = section.find("ol").find_all("li")
        return [definition.text for definition in definition_elements]
    except AttributeError:
        pass


def create_rows(url: str, row_count: int):
    response = get_url_response(url)
    soup = make_soup(response)
    words_section = soup.find("div", class_="mw-category mw-category-columns")
    if not words_section:
        print(f"Reached final page: {url}")
        return

    words_list = words_section.find_all("li")
    with open(FILE_PATH, "a") as f:
        writer = csv.writer(f)
        for word_el in words_list:
            word = word_el.next.get("title")
            _word_ = word.replace(" ", "_")
            word_url = f"https://en.wiktionary.org/wiki/{_word_}#English"
            response = get_url_response(word_url)
            soup = make_soup(response)
            main_section = soup.find("div", class_="mw-parser-output")
            if part_of_speech := get_pos(main_section):
                row = [
                    word,
                    part_of_speech.lower(),
                    word_url,
                ]
                writer.writerow(row)
                row_count += 1
                print(f"row appended for idiom '{word}' - row_count: {row_count}")

    url = get_next_url(url)
    return create_rows(url, row_count) if url else None

def main():
    print("starting scraper.")
    start = time.time()
    url = IDIOMS_URL
    row_count = 0
    with open(FILE_PATH, "w") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

    create_rows(url, row_count)
    print("all rows appended.")
    print("csv saved.")
    end = time.time()
    print(f"time taken: {end - start}s")


if __name__ == "__main__":
    main()
