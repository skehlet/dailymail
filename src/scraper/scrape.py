import shutil
import tempfile
import time
import requests
from unstructured.partition.html import partition_html
from unstructured.documents.elements import NarrativeText
from bs4 import BeautifulSoup
from app_settings import PAYWALL_TEXTS


def extract_title_from_html(html):
    """Extract the title from the HTML text"""
    soup = BeautifulSoup(html, "lxml")
    if soup.title is None:
        return "Unknown"
    return soup.title.string


def fetch_site_content(url):
    print(f"Now fetching {url}...")
    page_title = "Unknown"
    body_pieces = []

    headers = {
        # Provide a browser-like User-Agent so we don't get blocked as a scraper
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        # don't gzip it, unstructured cannot handle gzipped docs
        "Accept-Encoding": "identity",
    }

    # unstructured supports fetching directly from url, but has no timeout
    # option, so use request ourselves with timeout.
    start_time = time.time()
    response = requests.get(
        url,
        headers=headers,
        timeout=20,
        stream=True,
    )

    # create a temporary file using a context manager
    # close the file, use the name to open the file again
    # https://docs.python.org/3/library/tempfile.html#examples
    with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
        print(f"Streaming HTML to temp file: {fp.name}")
        shutil.copyfileobj(response.raw, fp)
        fp.close()
        end_time = time.time()
        print(f"Downloading and saving took {(end_time - start_time):0.1f} seconds")
        # the file is closed, but not removed
        # open the file again by using its name
        with open(fp.name, mode="rb") as f:
            start_time = time.time()
            elements = partition_html(file=f)
            end_time = time.time()
            print(f"Unstructured partitioning took {(end_time - start_time):0.1f} seconds")
        with open(fp.name, mode="rb") as f:
            # I cannot figure out how to get the HTML title using unstructured.
            # So just use BeautifulSoup.
            start_time = time.time()
            page_title = extract_title_from_html(f.read())
            end_time = time.time()
            print(f"Extracting title took {(end_time - start_time):0.1f} seconds")
    # file is now removed

    is_paywalled = False
    for element in elements:
        # See: https://docs.unstructured.io/api-reference/api-services/document-elements
        element_text = str(element)

        # print(f"Element ({type(element)}): ${element_text}")

        # Look out for text that indicates the article is paywalled. For this,
        # we examine all element types, not just NarrativeText.
        for paywall_text in PAYWALL_TEXTS:
            if paywall_text in element_text:
                print(f"Found paywall text '{paywall_text}'")
                is_paywalled = True
                break

        # Collect text from NarrativeText elements only, for now. Title seems to
        # get too much garbage.
        if isinstance(element, (NarrativeText,)):
            body_pieces.append(element_text)

    content = "\n".join(body_pieces)
    return (page_title, content, is_paywalled)


if __name__ == "__main__":
    (my_page_title, my_content, my_is_paywalled) = fetch_site_content(
        # "https://www.caranddriver.com/news/a46717089/vw-id-buzz-super-bowl-ad-sale-date/"
        # "https://www.klbjfm.com/blogs/chillville-spotify-playlist-may-19-2024/"
        # "https://yourlocalepidemiologist.substack.com/p/time100"
        # "https://fandomwire.com/it-was-money-we-didnt-spend-but-money-we-had-to-make-one-game-saving-take-two-from-a-100m-debt-is-how-you-got-gta-v-red-dead-redemption-2/"
        # "https://yourlocalepidemiologist.substack.com/p/h5n1-update"
        # "https://europe.autonews.com/paris-auto-show/2024-paris-auto-show-adds-vw-group-brands"
        # "https://www.rli.uk.com/pret-a-manger-lands-in-los-angeles/"
        # "https://www.carexpert.com.au/car-news/volkswagen-to-dump-gtx-badge-for-hot-electric-vehicles"
        # "https://www.carsales.com.au/editorial/details/spy-pics-2025-volkswagen-id-2-spotted-147136/"
        # "https://www.tweaktown.com/news/100351/cooler-masters-shark-concept-pc-available-for-pre-order-7000-an-rtx-4070-ti-super/index.html"
        # "https://www.roadandtrack.com/news/a63081162/volkswagen-rivian-mk9-golf/"
        "https://heathercoxrichardson.substack.com/p/march-11-2025-fbc"
    )
    print(f"Title: {my_page_title}")
    print(f"Content: {my_content}")
    print(f"Is paywalled: {my_is_paywalled}")
