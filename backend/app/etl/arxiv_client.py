import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import time
from app.config.settings import get_settings

class ArxivClient:
    """
    Extracts AI/ML research papers from the arXiv API.
    This handles the 'E' (Extract) phase of the ETL pipeline.
    """
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "http://export.arxiv.org/api/query"
        # arXiv's API returns an Atom XML feed. We need this namespace to parse the tags.
        self.ns = {'atom': 'http://www.w3.org/2005/Atom'}

    def fetch_papers(self) -> list[dict]:
        """Iterates through configured categories and fetches the latest papers."""
        all_papers = []
        
        for category in self.settings.category_list:
            print(f"Fetching {self.settings.arxiv_max_results_per_category} papers for {category}...")
            
            # 1. Construct the API request
            params = {
                "search_query": f"cat:{category}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": self.settings.arxiv_max_results_per_category
            }
            query_string = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{query_string}"
            
            # 2. Call the API (using built-in urllib to avoid external dependencies)
            try:
                with urllib.request.urlopen(url) as response:
                    xml_data = response.read()
                    
                # 3. Parse the XML response
                root = ET.fromstring(xml_data)
                
                # 4. Extract each paper from the feed
                for entry in root.findall('atom:entry', self.ns):
                    paper_data = self._parse_entry(entry, category)
                    if paper_data:
                        all_papers.append(paper_data)
                        
            except urllib.error.HTTPError as e:
                print(f"HTTP Error fetching category {category}: {e.code} {e.reason}")
            except Exception as e:
                print(f"Error fetching category {category}: {e}")
            
            # --- RATE LIMITER ---
            # arXiv TOS mandates max 1 request per 3 seconds. 
            # We wait 4 seconds to be good net-citizens and prevent 429 crashes.
            print("Waiting 4 seconds to respect arXiv rate limits...")
            time.sleep(4)
                
        return all_papers

    def _parse_entry(self, entry: ET.Element, category: str) -> dict:
        """Transforms a raw XML entry into a dictionary matching our Database Model."""
        try:
            # Extract the arXiv ID (e.g., "http://arxiv.org/abs/2404.12345v1" -> "2404.12345v1")
            id_url = entry.find('atom:id', self.ns).text
            arxiv_id = id_url.split('/')[-1]
            
            # Extract title and abstract, stripping out messy newline characters
            title = entry.find('atom:title', self.ns).text.strip().replace('\n', ' ')
            abstract = entry.find('atom:summary', self.ns).text.strip().replace('\n', ' ')
            
            # Extract authors into a JSON-serialized list string
            authors = [author.find('atom:name', self.ns).text for author in entry.findall('atom:author', self.ns)]
            authors_json = json.dumps(authors)
            
            # Extract published date and convert to Python datetime object
            published_str = entry.find('atom:published', self.ns).text
            published_at = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
            
            # Extract URLs
            arxiv_url = id_url
            pdf_link_node = entry.find('atom:link[@title="pdf"]', self.ns)
            pdf_url = pdf_link_node.attrib['href'] if pdf_link_node is not None else f"{id_url}.pdf"

            # Map directly to our SQLAlchemy model schema
            return {
                "arxiv_id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "authors": authors_json,
                "category": category,
                "pdf_url": pdf_url,
                "arxiv_url": arxiv_url,
                "published_at": published_at
            }
        except AttributeError as e:
            print(f"Skipping a paper due to missing data: {e}")
            return None

# Simple test block: runs only if you execute this file directly
if __name__ == "__main__":
    client = ArxivClient()
    papers = client.fetch_papers()
    print(f"\nSuccessfully fetched {len(papers)} total papers.")
    if papers:
        print(f"Sample Title: {papers[0]['title']}")
        print(f"Sample Authors: {papers[0]['authors']}")