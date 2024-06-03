import shutil
import tempfile
import requests
from unstructured.partition.auto import partition_html
from unstructured.documents.elements import NarrativeText
from bs4 import BeautifulSoup

def extract_title_from_html(html):
    """Extract the title from the HTML text"""
    soup = BeautifulSoup(html, 'lxml')
    if soup.title is None:
        return "Unknown"
    return soup.title.string

def fetch_site_content(url):
    print(f"Now fetching {url}...")
    page_title = "Unknown"
    body_pieces = []

    headers = {
        # Provide a browser-like User-Agent so we don't get blocked as a scraper
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
         # don't gzip it, unstructured cannot handle gzipped docs
        'Accept-Encoding': 'identity'
    }

    # unstructured supports fetching directly from url, but has no timeout
    # option, so use request ourselves with timeout.
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
        shutil.copyfileobj(response.raw, fp)
        fp.close()
        # the file is closed, but not removed
        # open the file again by using its name
        with open(fp.name, mode='rb') as f:
            elements = partition_html(file=f)
        with open(fp.name, mode='rb') as f:
            # I cannot figure out how to get the HTML title using unstructured.
            # So just use BeautifulSoup.
            page_title = extract_title_from_html(f.read())
    # file is now removed

    for element in elements:
        if isinstance(element, (NarrativeText,)):
            body_pieces.append(str(element))

    content = "\n".join(body_pieces)
    return (page_title, content)

if __name__ == "__main__":
    (my_page_title, my_content) = fetch_site_content(
        # "https://www.caranddriver.com/news/a46717089/vw-id-buzz-super-bowl-ad-sale-date/",
        # "https://www.klbjfm.com/blogs/chillville-spotify-playlist-may-19-2024/",
        "https://yourlocalepidemiologist.substack.com/p/time100",
    )
    print(f"Title: {my_page_title}")
    print(f"Content: {my_content}")
