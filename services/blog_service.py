from models import Blog, db
from services.arxiv_service import ArxivService
from services.groq_service import GroqService
from datetime import datetime
from typing import Optional, List, Dict

class BlogService:
    """Service to manage blog operations"""
    
    def __init__(self, groq_api_key: str):
        self.arxiv_service = ArxivService()
        self.groq_service = GroqService(groq_api_key)
    
    def generate_daily_blog(self) -> Optional[Blog]:
        """Generate a daily blog post from arXiv papers"""
        try:
            # Fetch papers from arXiv
            papers = self.arxiv_service.fetch_papers()
            if not papers:
                print("No papers found from arXiv")
                return None
            
            # Format papers for blog generation
            articles_data = self.arxiv_service.format_for_blog(papers)
            
            # Generate blog content using Groq
            blog_content = self.groq_service.generate_blog_content(articles_data)
            if not blog_content:
                print("Failed to generate blog content")
                return None
            
            # Create and save blog post
            blog = Blog(
                title=blog_content['title'],
                subtitle=blog_content['subtitle'],
                content=blog_content['content'],
                created_at=datetime.utcnow()
            )
            
            db.session.add(blog)
            db.session.commit()
            
            print(f"Successfully created blog: {blog.title}")
            return blog
            
        except Exception as e:
            print(f"Error generating daily blog: {e}")
            db.session.rollback()
            return None
    
    def get_all_blogs(self, page: int = 1, per_page: int = 10) -> Dict:
        """Get paginated list of all blogs"""
        try:
            blogs = Blog.query.order_by(Blog.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'blogs': [blog.to_dict() for blog in blogs.items],
                'total': blogs.total,
                'pages': blogs.pages,
                'current_page': page,
                'has_next': blogs.has_next,
                'has_prev': blogs.has_prev
            }
        except Exception as e:
            print(f"Error fetching blogs: {e}")
            return {
                'blogs': [],
                'total': 0,
                'pages': 0,
                'current_page': 1,
                'has_next': False,
                'has_prev': False
            }
    
    def get_blog_by_id(self, blog_id: int) -> Optional[Blog]:
        """Get a specific blog by ID"""
        try:
            return Blog.query.get(blog_id)
        except Exception as e:
            print(f"Error fetching blog {blog_id}: {e}")
            return None
    
    def delete_blog(self, blog_id: int) -> bool:
        """Delete a blog by ID"""
        try:
            blog = Blog.query.get(blog_id)
            if blog:
                db.session.delete(blog)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting blog {blog_id}: {e}")
            db.session.rollback()
            return False
    
    def create_manual_blog(self, title: str, subtitle: str, content: str) -> Optional[Blog]:
        """Create a blog post manually"""
        try:
            blog = Blog(
                title=title,
                subtitle=subtitle,
                content=content,
                created_at=datetime.utcnow()
            )
            
            db.session.add(blog)
            db.session.commit()
            
            return blog
        except Exception as e:
            print(f"Error creating manual blog: {e}")
            db.session.rollback()
            return None
