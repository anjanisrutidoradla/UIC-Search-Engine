import os
from collections import deque
import requests
from bs4 import BeautifulSoup
import pickle

url_domain = "uic.edu"
url_start = "https://cs.uic.edu"
pages_folder = "FetchedPages/FetchedPage"

crawl_limit = 3500


url_queue = deque()
url_queue.append(url_start)

crawled_url = []
crawled_url.append(url_start)

crawled_pages = {}
page_number = 0

while url_queue:

    try:
        url = url_queue.popleft()
        request = requests.get(url)
        print(request)
        if request.status_code == 200 and "text/html" in request.headers["Content-Type"]:

            soup = BeautifulSoup(request.text, "lxml")
            anchors_extracted = soup.find_all("a")

            crawled_pages[page_number] = url
            output_file = pages_folder + str(page_number)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as file:
                file.write(request.text)

            for anchors in anchors_extracted:
                link = anchors.get("href")
                if (
                    link is not None
                    and link.startswith("http")
                ):

                    link = link.lower()
                    link = link.split("#")[0]
                    link = link.split("?", maxsplit=1)[0]
                    link = link.rstrip("/")
                    link = link.strip()

                    if link not in crawled_url and url_domain in link:
                        url_queue.append(link)
                        crawled_url.append(link)

            if len(crawled_pages) > crawl_limit:
                break

            page_number += 1
    except Exception as e:
        continue

pickle_folder = "./PickleFile/"
os.makedirs(pickle_folder, exist_ok=True)

with open(pickle_folder + "3500_crawled_pages.pickle", "wb") as f:
    pickle.dump(crawled_pages, f)
