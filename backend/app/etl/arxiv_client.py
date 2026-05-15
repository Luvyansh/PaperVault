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
    Extracts AI/ML research papers from the arXiv API using polite pagination.
    This handles the 'E' (Extract) phase of the ETL pipeline.
    """
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "http://export.arxiv.org/api/query"
        self.ns = {'atom': 'http://www.w3.org/2005/Atom'}

    def fetch_papers(self) -> list[dict]:
        """Iterates through configured categories and fetches papers in safe chunks."""
        all_papers = []
        CHUNK_SIZE = 50  # Safe limit to avoid 429s

        for category in self.settings.category_list:
            total_target = self.settings.arxiv_max_results_per_category
            print(f"\n📥 Fetching up to {total_target} papers for {category}...")
            
            # Pagination loop
            for start_index in range(0, total_target, CHUNK_SIZE):
                # Calculate how many papers to request in this specific chunk
                current_chunk_size = min(CHUNK_SIZE, total_target - start_index)
                print(f"  -> Requesting papers {start_index} to {start_index + current_chunk_size - 1}...")
                
                # 1. Construct the API request with pagination
                params = {
                    "search_query": f"cat:{category}",
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                    "start": start_index,
                    "max_results": current_chunk_size
                }
                query_string = urllib.parse.urlencode(params)
                url = f"{self.base_url}?{query_string}"
                
                # 2. Inject Custom Identity
                headers = {
                    'User-Agent': 'PaperVaultDev/1.0 (anurag.test.dev@gmail.com)'
                }
                req = urllib.request.Request(url, headers=headers)
                
                # 3. Call the API
                try:
                    with urllib.request.urlopen(req) as response:
                        xml_data = response.read()
                        
                    # 4. Parse the XML response
                    root = ET.fromstring(xml_data)
                    entries = root.findall('atom:entry', self.ns)
                    
                    # If arXiv returns no entries, we have exhausted this category
                    if not entries:
                        print(f"  -> No more papers available for {category}. Moving to next category.")
                        break
                    
                    # 5. Extract each paper from the feed
                    for entry in entries:
                        paper_data = self._parse_entry(entry, category)
                        if paper_data:
                            all_papers.append(paper_data)
                            
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        print(f"⚠️ 429 Rate Limit Hit at index {start_index}! Backing off for 60 seconds...")
                        time.sleep(60)
                        # We break the chunk loop here to let the system recover and move to the next category
                        break 
                    else:
                        print(f"❌ HTTP Error fetching category {category}: {e.code} {e.reason}")
                        break
                except Exception as e:
                    print(f"❌ Error fetching category {category}: {e}")
                    break
                
                # --- POLITE THROTTLING ---
                # Only sleep if we have more chunks to fetch for this category
                if start_index + current_chunk_size < total_target:
                    time.sleep(4) 
            
            # Rest for a few seconds before hammering the API with a completely new category
            time.sleep(4)
                
        return all_papers

    def _parse_entry(self, entry: ET.Element, category: str) -> dict:
        """Transforms a raw XML entry into a dictionary matching our Database Model."""
        try:
            id_url = entry.find('atom:id', self.ns).text
            arxiv_id = id_url.split('/')[-1]
            
            title = entry.find('atom:title', self.ns).text.strip().replace('\n', ' ')
            abstract = entry.find('atom:summary', self.ns).text.strip().replace('\n', ' ')
            
            authors = [author.find('atom:name', self.ns).text for author in entry.findall('atom:author', self.ns)]
            authors_json = json.dumps(authors)
            
            published_str = entry.find('atom:published', self.ns).text
            published_at = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
            
            arxiv_url = id_url
            pdf_link_node = entry.find('atom:link[@title="pdf"]', self.ns)
            pdf_url = pdf_link_node.attrib['href'] if pdf_link_node is not None else f"{id_url}.pdf"

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

if __name__ == "__main__":
    client = ArxivClient()
    papers = client.fetch_papers()
    print(f"\n✅ Successfully fetched {len(papers)} total papers.")