import requests
import json
import re
from typing import Dict, Optional

class GroqService:
    """Service to generate blog content using Groq AI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
    
    def generate_blog_content(self, articles_data: Dict) -> Optional[Dict]:
        """Generate blog content from articles data"""
        try:
            prompt = self._create_blog_prompt(articles_data)
            response = self._call_groq_api(prompt)
            
            if response:
                return self._parse_blog_response(response)
            return None
            
        except Exception as e:
            print(f"Error generating blog content: {e}")
            return self._get_fallback_content()
    
    def _create_blog_prompt(self, articles_data: Dict) -> str:
        """Create the prompt for blog generation"""
        articles = articles_data.get('articles', [])
        search_date = articles_data.get('search_date', '')
        
        # Format articles for the prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"""
Paper {i}:
Title: {self._clean_text(article['title'])}
Authors: {self._clean_text(article['authors'])}
Published: {article['published']}
Description: {self._clean_text(article['description'])}
Categories: {self._clean_text(article['categories'])}
URL: {article['url']}

"""
        
        return f"""Create a comprehensive blog post about these latest AI research breakthroughs from arXiv published on {search_date}:

{articles_text}

IMPORTANT FORMATTING REQUIREMENTS:
1. Generate exactly 3 fields: title, subtitle, and content
2. Title: Create an attention-grabbing title about "Latest AI Research Breakthroughs"
3. Subtitle: Create a compelling subtitle that summarizes the key innovations
4. Content: Write comprehensive content (1200-1500 words) with clean HTML formatting

HTML FORMATTING RULES FOR CONTENT:
- Use <h2>Paper Name</h2> for each paper section
- Use <h3>Subsection</h3> for any subsections
- Use <p>paragraph text</p> for all paragraphs
- Use <strong>text</strong> for important terms
- Use <em>text</em> for emphasis
- NO line breaks outside of HTML tags
- NO special characters that need escaping
- Keep all HTML on single lines where possible

CONTENT STRUCTURE:
1. Introduction paragraph explaining the AI breakthroughs
2. One section per paper with <h2> heading
3. Each paper section should have 2-3 paragraphs explaining the innovation and impact
4. Conclusion paragraph about the future of AI research

Write in an informative yet engaging tone for tech enthusiasts.

Format your response as valid JSON with exactly these fields:
{{
  "title": "Your engaging blog post title",
  "subtitle": "Your compelling subtitle",
  "content": "Full blog post content with clean HTML formatting - no line breaks, properly escaped"
}}

CRITICAL: Ensure the content field contains clean HTML without line breaks or special characters that could break JSON parsing."""
    
    def _call_groq_api(self, prompt: str) -> Optional[Dict]:
        """Make API call to Groq"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI research blogger who writes engaging, informative blog posts about the latest AI research discoveries. You always respond with properly formatted JSON containing exactly 3 fields: title, subtitle, and content. The content field must contain clean HTML formatting without line breaks or special characters that could break JSON parsing. Always ensure the JSON is valid and properly escaped."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    def _parse_blog_response(self, response: Dict) -> Optional[Dict]:
        """Parse the response from Groq API"""
        try:
            message_content = response['choices'][0]['message']['content']
            
            # Clean the message content
            cleaned_content = message_content.strip()
            
            # Remove markdown code blocks if present
            if cleaned_content.startswith('```json'):
                cleaned_content = re.sub(r'^```json\s*', '', cleaned_content)
                cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
            elif cleaned_content.startswith('```'):
                cleaned_content = re.sub(r'^```\s*', '', cleaned_content)
                cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
            
            # Parse JSON
            blog_data = json.loads(cleaned_content)
            
            # Validate required fields
            if not all(key in blog_data for key in ['title', 'subtitle', 'content']):
                return self._extract_manually(cleaned_content)
            
            return {
                'title': blog_data['title'].strip(),
                'subtitle': blog_data['subtitle'].strip(),
                'content': self._clean_html_content(blog_data['content'])
            }
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error parsing Groq response: {e}")
            return self._extract_manually(message_content if 'message_content' in locals() else str(response))
    
    def _extract_manually(self, content: str) -> Optional[Dict]:
        """Manually extract blog data if JSON parsing fails"""
        try:
            title_match = re.search(r'"title"\s*:\s*"([^"]+)"', content, re.IGNORECASE)
            subtitle_match = re.search(r'"subtitle"\s*:\s*"([^"]+)"', content, re.IGNORECASE)
            content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.IGNORECASE)
            
            if title_match and subtitle_match and content_match:
                extracted_content = content_match.group(1)
                # Unescape the content
                extracted_content = extracted_content.replace('\\"', '"').replace('\\n', '').replace('\\r', '').replace('\\t', '').replace('\\\\', '\\')
                
                return {
                    'title': title_match.group(1),
                    'subtitle': subtitle_match.group(1),
                    'content': self._clean_html_content(extracted_content)
                }
        except Exception as e:
            print(f"Manual extraction failed: {e}")
        
        return self._get_fallback_content()
    
    def _clean_html_content(self, content: str) -> str:
        """Clean and format HTML content"""
        if not content:
            return "<p>No content available</p>"
        
        # Remove extra escaping
        cleaned = content.replace('\\"', '"').replace('\\n', '').replace('\\r', '').replace('\\t', '').replace('\\\\', '\\').strip()
        
        # Add proper formatting
        cleaned = (cleaned
                  .replace('</p>', '</p>\n')
                  .replace('</h1>', '</h1>\n')
                  .replace('</h2>', '</h2>\n')
                  .replace('</h3>', '</h3>\n')
                  .replace('</h4>', '</h4>\n')
                  .replace('</h5>', '</h5>\n')
                  .replace('</h6>', '</h6>\n')
                  .replace('</div>', '</div>\n')
                  .replace('<h1', '\n<h1')
                  .replace('<h2', '\n<h2')
                  .replace('<h3', '\n<h3')
                  .replace('<h4', '\n<h4')
                  .replace('<h5', '\n<h5')
                  .replace('<h6', '\n<h6'))
        
        # Clean up multiple newlines
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        cleaned = cleaned.strip()
        
        # Ensure proper HTML structure
        if not cleaned.startswith('<') or not any(tag in cleaned for tag in ['<p>', '<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>']):
            cleaned = f"<p>{cleaned}</p>"
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Clean text for prompt generation"""
        if not text:
            return ''
        return (text.replace('\\', '\\\\')
                   .replace('"', '\\"')
                   .replace('\n', ' ')
                   .replace('\r', ' ')
                   .replace('\t', ' ')
                   .strip())
    
    def _get_fallback_content(self) -> Dict:
        """Return fallback content if generation fails"""
        return {
            'title': "Latest AI Research Breakthroughs",
            'subtitle': "Exploring cutting-edge developments in artificial intelligence",
            'content': "<p>We encountered an issue processing the latest AI research papers. Please check back later for the latest updates on AI breakthroughs.</p>"
        }
