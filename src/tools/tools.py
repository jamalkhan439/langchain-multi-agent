from langchain.tools import tool
from dotenv import load_dotenv
import os
import requests
from tavily import TavilyClient
from rich import print
import re
from bs4 import BeautifulSoup
from readability import Document
import trafilatura

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAIL_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query, max_results=5)
    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and extract clean readable content from a URL.
     Uses multiple extraction strategies for better reliability."""

    import requests
    from bs4 import BeautifulSoup
    from langchain_core.tools import tool

    @tool
    def scrap_url(url: str) -> str:
        """Read an HTML webpage and return its title, source URL, and readable text."""
        try:
            response = requests.get(
                url.strip(),
                headers={"User-Agent": "ResearchAgent/1.0"},
                timeout=(10, 20),
            )
            response.raise_for_status()

        except requests.exceptions.Timeout:
            return f"Error: The website took too long to respond. URL: {url}"

        except requests.exceptions.HTTPError as error:
            return (
                f"Error: Website returned HTTP {error.response.status_code}. "
                f"URL: {url}"
            )

        except requests.exceptions.ConnectionError:
            return f"Error: Could not connect to the website. URL: {url}"

        except requests.exceptions.RequestException:
            return f"Error: Could not download the webpage. URL: {url}"

        # Skip PDFs, images, and other non-HTML responses.
        content_type = response.headers.get("Content-Type", "").lower()
        if content_type and not any(
                kind in content_type
                for kind in ("text/html", "application/xhtml+xml")
        ):
            return f"Error: This URL does not contain an HTML webpage. URL: {url}"

        # Parse the HTML. Passing bytes lets Beautiful Soup detect encoding.
        soup = BeautifulSoup(response.content, "html.parser")
        # Remove scripts and common navigation elements.
        for tag in soup([
            "script", "style", "noscript", "nav", "form", "svg", "iframe"
        ]):
            tag.decompose()

        # Prefer the main content when the page identifies it.
        content = soup.find("main") or soup.find("article") or soup.body or soup

        text = content.get_text(separator="\n", strip=True)

        # Clean extra whitespace while preserving separate lines.
        text = "\n".join(
            " ".join(line.split())
            for line in text.splitlines()
            if line.strip()
        )

        if not text:
            return f"Error: No readable text found on this webpage. URL: {url}"

        # Limit the amount of text sent back to the model.
        max_characters = 10000
        if len(text) > max_characters:
            text = text[:max_characters] + "\n[Content truncated]"

        return text
