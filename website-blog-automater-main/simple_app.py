#!/usr/bin/env python3
"""
Simple Flask Blog App - Minimal Dependencies Version
This version uses only built-in Python libraries where possible
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import re

# Try to import Flask, if not available, provide instructions
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for
except ImportError:
    print("Flask is not installed. Please install it with:")
    print("pip install flask")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subtitle TEXT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

# ArXiv Service (simplified)
def fetch_arxiv_papers():
    """Fetch papers from arXiv API"""
    try:
        params = {
            'search_query': 'cat:cs.AI OR cat:cs.LG OR cat:cs.CL',
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
            'max_results': '10'
        }
        
        url = f"https://export.arxiv.org/api/query?{urlencode(params)}"
        req = Request(url)
        
        with urlopen(req, timeout=30) as response:
            xml_data = response.read().decode('utf-8')
        
        return parse_arxiv_xml(xml_data)
    except Exception as e:
        print(f"Error fetching arXiv papers: {e}")
        return []

def parse_arxiv_xml(xml_data):
    """Simple XML parsing for arXiv response"""
    papers = []
    
    # Extract entry blocks
    entries = re.findall(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
    
    for entry in entries[:5]:  # Limit to 5 papers
        try:
            title_match = re.search(r'<title[^>]*?>(.*?)</title>', entry, re.DOTALL)
            summary_match = re.search(r'<summary[^>]*?>(.*?)</summary>', entry, re.DOTALL)
            
            if title_match and summary_match:
                title = re.sub(r'\n\s+', ' ', title_match.group(1).strip())
                summary = re.sub(r'\n\s+', ' ', summary_match.group(1).strip())
                
                # Check if it's AI/ML related
                content = (title + ' ' + summary).lower()
                ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning']
                
                if any(keyword in content for keyword in ai_keywords):
                    papers.append({
                        'title': title,
                        'summary': summary[:300] + '...' if len(summary) > 300 else summary
                    })
        except Exception as e:
            continue
    
    return papers

# Simple blog generation (without Groq)
def generate_blog_content(papers):
    """Generate blog content from papers (simplified version)"""
    if not papers:
        return {
            'title': 'Latest AI Research Update',
            'subtitle': 'No new papers found today',
            'content': '<p>We could not find any new AI research papers today. Please check back later.</p>'
        }
    
    title = f"Latest AI Research Breakthroughs - {datetime.now().strftime('%B %d, %Y')}"
    subtitle = f"Exploring {len(papers)} cutting-edge developments in artificial intelligence"
    
    content = f"""
    <p>Today we're exploring {len(papers)} exciting new developments in artificial intelligence research from arXiv. These papers represent the latest thinking in AI, machine learning, and computer science.</p>
    
    <h2>Research Highlights</h2>
    """
    
    for i, paper in enumerate(papers, 1):
        content += f"""
        <h3>{i}. {paper['title']}</h3>
        <p>{paper['summary']}</p>
        """
    
    content += """
    <h2>Looking Forward</h2>
    <p>These research developments continue to push the boundaries of what's possible in artificial intelligence. Each paper contributes to our growing understanding of how AI systems can be made more capable, efficient, and beneficial for society.</p>
    
    <p>Stay tuned for more updates as we continue to track the latest developments in AI research!</p>
    """
    
    return {
        'title': title,
        'subtitle': subtitle,
        'content': content
    }

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Research Blog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .blog-card { border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; border-radius: 5px; }
        .blog-title { color: #333; text-decoration: none; font-size: 18px; font-weight: bold; }
        .blog-subtitle { color: #666; font-size: 14px; margin: 5px 0; }
        .blog-date { color: #999; font-size: 12px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .no-blogs { text-align: center; color: #666; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 AI Research Blog</h1>
            <p>Latest breakthroughs in artificial intelligence research</p>
            <a href="/generate" class="btn">Generate New Blog</a>
            <a href="/create" class="btn">Create Manual Blog</a>
        </div>
        
        {% if blogs %}
            {% for blog in blogs %}
            <div class="blog-card">
                <a href="/blog/{{ blog.id }}" class="blog-title">{{ blog.title }}</a>
                {% if blog.subtitle %}
                <div class="blog-subtitle">{{ blog.subtitle }}</div>
                {% endif %}
                <div class="blog-date">{{ blog.created_at }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-blogs">
                <h3>No blog posts yet</h3>
                <p>Generate your first AI research blog post!</p>
                <a href="/generate" class="btn">Generate First Blog</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

BLOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ blog.title }} - AI Research Blog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { margin-bottom: 30px; }
        .title { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 10px; }
        .date { color: #999; font-size: 14px; margin-bottom: 20px; }
        .content { line-height: 1.6; }
        .content h2 { color: #333; margin-top: 30px; }
        .content h3 { color: #555; margin-top: 20px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px 5px 20px 0; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="btn">← Back to Home</a>
        <div class="header">
            <h1 class="title">{{ blog.title }}</h1>
            {% if blog.subtitle %}
            <h2 class="subtitle">{{ blog.subtitle }}</h2>
            {% endif %}
            <div class="date">Published: {{ blog.created_at }}</div>
        </div>
        <div class="content">
            {{ blog.content | safe }}
        </div>
    </div>
</body>
</html>
'''

GENERATE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Generate Blog - AI Research Blog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; border: none; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Generate AI Blog Post</h1>
        <p>Automatically generate a blog post from the latest AI research papers on arXiv.</p>
        
        <div class="info">
            <strong>How it works:</strong>
            <ol>
                <li>Fetch latest AI research papers from arXiv</li>
                <li>Process and filter relevant papers</li>
                <li>Generate comprehensive blog content</li>
            </ol>
        </div>
        
        <form method="POST">
            <button type="submit" class="btn">Generate Blog Post</button>
        </form>
        
        <a href="/" class="btn" style="background: #6c757d;">Cancel</a>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blogs ORDER BY created_at DESC LIMIT 10').fetchall()
    conn.close()
    return render_template_string(HOME_TEMPLATE, blogs=blogs)

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blogs WHERE id = ?', (blog_id,)).fetchone()
    conn.close()
    
    if not blog:
        return "Blog not found", 404
    
    return render_template_string(BLOG_TEMPLATE, blog=blog)

@app.route('/generate', methods=['GET', 'POST'])
def generate_blog():
    if request.method == 'POST':
        try:
            # Fetch papers from arXiv
            papers = fetch_arxiv_papers()
            
            # Generate blog content
            blog_data = generate_blog_content(papers)
            
            # Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO blogs (title, subtitle, content) VALUES (?, ?, ?)',
                (blog_data['title'], blog_data['subtitle'], blog_data['content'])
            )
            blog_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return redirect(url_for('view_blog', blog_id=blog_id))
            
        except Exception as e:
            return f"Error generating blog: {str(e)}", 500
    
    return render_template_string(GENERATE_TEMPLATE)

@app.route('/api/blogs')
def api_blogs():
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blogs ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return jsonify([dict(blog) for blog in blogs])

if __name__ == '__main__':
    init_db()
    print("Starting AI Research Blog...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
