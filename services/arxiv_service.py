import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ArxivService:
    """Service to fetch and parse arXiv research papers"""
    
    BASE_URL = "https://export.arxiv.org/api/query"
    
    def __init__(self, max_results: int = 20):
        self.max_results = max_results
    
    def fetch_papers(self, search_query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL") -> List[Dict]:
        """Fetch papers from arXiv API"""
        params = {
            'search_query': search_query,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
            'max_results': self.max_results
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_arxiv_xml(response.text)
        except requests.RequestException as e:
            print(f"Error fetching arXiv papers: {e}")
            return []
    
    def _parse_arxiv_xml(self, xml_data: str) -> List[Dict]:
        """Parse XML response from arXiv API"""
        papers = []
        
        # Extract all entry blocks
        entry_regex = r'<entry>(.*?)</entry>'
        entry_matches = re.findall(entry_regex, xml_data, re.DOTALL)
        
        for i, entry_xml in enumerate(entry_matches[:8]):  # Limit to 8 papers
            paper = self._extract_paper_details(entry_xml)
            if paper and self._is_relevant_paper(paper):
                papers.append(paper)
        
        return papers[:5]  # Return top 5 relevant papers
    
    def _extract_paper_details(self, entry_xml: str) -> Optional[Dict]:
        """Extract paper details from entry XML"""
        try:
            # Extract basic fields
            title_match = re.search(r'<title[^>]*?>(.*?)</title>', entry_xml, re.DOTALL)
            summary_match = re.search(r'<summary[^>]*?>(.*?)</summary>', entry_xml, re.DOTALL)
            published_match = re.search(r'<published[^>]*?>(.*?)</published>', entry_xml, re.DOTALL)
            id_match = re.search(r'<id[^>]*?>(.*?)</id>', entry_xml, re.DOTALL)
            
            if not all([title_match, summary_match, published_match, id_match]):
                return None
            
            title = self._clean_text(title_match.group(1))
            summary = self._clean_text(summary_match.group(1))
            published = published_match.group(1).strip()
            paper_id = id_match.group(1).strip()
            
            # Extract authors
            authors = re.findall(r'<name[^>]*?>(.*?)</name>', entry_xml)
            authors = [self._clean_text(author) for author in authors[:3]]
            
            # Extract categories
            categories = re.findall(r'<category[^>]*?term=[\'"]([^\'"]*?)[\'"][^>]*?>', entry_xml)
            categories = categories[:3]
            
            return {
                'title': title,
                'summary': summary,
                'authors': authors,
                'published_date': published.split('T')[0],
                'arxiv_id': paper_id.split('/')[-1],
                'categories': categories,
                'pdf_link': paper_id.replace('abs', 'pdf') + '.pdf',
                'paper_link': paper_id
            }
        except Exception as e:
            print(f"Error extracting paper details: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        return re.sub(r'\n\s+', ' ', text.strip())
    
    def _is_relevant_paper(self, paper: Dict) -> bool:
        """Check if paper is relevant to AI/ML"""
        ai_keywords = [
            'llm', 'large language model', 'transformer', 'neural network',
            'deep learning', 'machine learning', 'artificial intelligence',
            'generative', 'reinforcement learning', 'computer vision',
            'natural language', 'gpt', 'bert', 'diffusion', 'gan'
        ]
        
        content = (paper['title'] + ' ' + paper['summary']).lower()
        return any(keyword in content for keyword in ai_keywords)
    
    def format_for_blog(self, papers: List[Dict]) -> Dict:
        """Format papers for blog generation"""
        formatted_articles = []
        
        for paper in papers:
            formatted_articles.append({
                'title': paper['title'],
                'description': paper['summary'][:300] + '...' if len(paper['summary']) > 300 else paper['summary'],
                'authors': ', '.join(paper['authors']),
                'published': paper['published_date'],
                'source': 'arXiv',
                'url': paper['paper_link'],
                'pdf_url': paper['pdf_link'],
                'categories': ', '.join(paper['categories'])
            })
        
        return {
            'articles': formatted_articles,
            'article_count': len(formatted_articles),
            'blog_date': datetime.now().strftime('%Y-%m-%d'),
            'search_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        }
