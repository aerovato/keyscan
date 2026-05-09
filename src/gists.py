import re
import time
import urllib.parse
from typing import Dict, Generator, List, Literal, Sequence, Set, Tuple, TypedDict, cast

import requests
from bs4 import BeautifulSoup, Tag

import config
from src.storage import print_err


GIST_API_BASE_URL = "https://api.github.com/gists"
GIST_SEARCH_BASE_URL = "https://gist.github.com/search"


def _default_headers() -> Dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }


# --- Search (HTML scraping) ---


def build_search_url(keyword: str, page_number: int, file_type: str) -> str:
    return f"{GIST_SEARCH_BASE_URL}?l={file_type}&q={urllib.parse.quote(keyword)}&p={page_number}"


def fetch_search_html(
    keyword: str,
    page_number: int,
    file_type: str,
    session: requests.Session,
    timeout_seconds: int = 20,
) -> str:
    url = build_search_url(keyword, page_number, file_type)
    response = session.get(url, headers=_default_headers(), timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def get_gist_ids_from_html(html_text: str) -> List[str]:
    """
    Parse gist IDs from a GitHub Gist search HTML page.
    Searches for <a> tags with links to the gist page.
    The link will match the pattern /{username}/{gist_id}.
    """

    beautiful_soup = BeautifulSoup(html_text, "html.parser")

    def href_check(href: str) -> bool:
        return re.compile(r"\/[^\/]+\/[0-9a-f]{20,}").search(href) != None

    a_tags: Sequence[Tag] = cast(
        Sequence[Tag],
        beautiful_soup.find_all("a", class_="Link--muted", href=href_check),
    )

    id_matcher = re.compile(r"\/[^\/]+\/([0-9a-f]{20,})", re.IGNORECASE)

    gist_ids: Set[str] = set()
    for a in a_tags:
        href: str = cast(str, a.get("href"))
        match = id_matcher.search(href)
        if match:
            gist_ids.add(match.group(1))

    return list(gist_ids)


def check_page_no_results(html_text: str) -> bool:
    return "We couldn\u2019t find any gists matching" in html_text


last_fetch_time = time.time() - 99999


def search_gists(
    keyword: str, file_type: str, delay_seconds: float
) -> Generator[Tuple[int, List[str]], None, None]:
    """
    Continuously iterates through search result pages yielding (page_number, List[gist_ids]).

    Stops when no results page is detected or when an HTTP error occurs.
    """

    session = requests.Session()
    global last_fetch_time
    try:
        current_page = 1
        while True:
            time_since_last_fetch = time.time() - last_fetch_time
            sleep_duration = delay_seconds - time_since_last_fetch
            if sleep_duration > 0:
                time.sleep(delay_seconds)

            html = fetch_search_html(keyword, current_page, file_type, session)
            last_fetch_time = time.time()

            if check_page_no_results(html):
                break

            gist_ids = get_gist_ids_from_html(html)
            yield current_page, gist_ids

            current_page += 1
    finally:
        session.close()


# --- API fetching ---


class FileJSON(TypedDict):
    language: str | None
    size: int
    """
    Note on file content and truncation:

    Entire books have been uploaded on GitHub gists (ex: Alice in Wonderland,
    size 100k+) without being truncated. Therefore, we can be confident that
    99.999% of legitimate env files will not be truncated by the GitHub API.
    """
    truncated: bool
    content: str


class GistJSON(TypedDict):
    html_url: str
    files: Dict[str, FileJSON]
    owner: Dict[Literal["login"], str]


def build_gist_api_url(gist_id: str) -> str:
    return f"{GIST_API_BASE_URL}/{gist_id}"


def get_api_headers() -> Dict[str, str]:
    headers = _default_headers()
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
    return headers


def fetch_gist_by_id(
    session: requests.Session, gist_id: str, timeout_seconds: int = 20
) -> GistJSON:
    url = build_gist_api_url(gist_id)
    while True:
        response = session.get(url, headers=get_api_headers(), timeout=timeout_seconds)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            reset_time = response.headers.get("X-RateLimit-Reset")
            if reset_time:
                wait_seconds = max(int(reset_time) - int(time.time()), 1)
            else:
                wait_seconds = 60
            print_err(f"Rate limited. Waiting {wait_seconds}s for reset...")
            time.sleep(wait_seconds)
            continue
        response.raise_for_status()
        return cast(GistJSON, response.json())


def filter_file_type(gist_json: GistJSON, file_type: str) -> List[FileJSON]:
    files = gist_json.get("files", {})
    result: List[FileJSON] = []
    for file in files.values():
        language = cast(str, file.get("language", ""))
        if language == file_type:
            result.append(file)
    return result


class GistInfo:
    owner: str
    file_contents: List[str]

    def __init__(self, owner: str, file_contents: List[str]):
        self.owner = owner
        self.file_contents = file_contents


def get_gist_info(
    session: requests.Session, gist_id: str, file_type: str, timeout_seconds: int = 20
) -> GistInfo:
    """
    Return an array of strings containing the file contents of the desired type.
    """

    gist_json = fetch_gist_by_id(session, gist_id, timeout_seconds=timeout_seconds)
    filtered_files = filter_file_type(gist_json, file_type)

    owner = gist_json.get("owner").get("login", "_UNKNOWN_USER")
    file_contents: List[str] = []
    for file in filtered_files:
        truncated = file.get("truncated")
        if not truncated:
            file_contents.append(file.get("content"))
        else:
            print(f"Truncated file encountered: {gist_id}")

    return GistInfo(owner, file_contents)
