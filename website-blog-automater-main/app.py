from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
from models import db, Blog
from services.blog_service import BlogService
from datetime import datetime
import os

def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Initialize blog service
    blog_service = BlogService(app.config['GROQ_API_KEY'])
    
    class DateTimeWrapper:
        """A wrapper class that makes strings behave like datetime objects"""
        def __init__(self, value):
            self.original_value = value
            self.datetime_obj = None
            
            if isinstance(value, str):
                # Try to parse the string into a datetime object
                self.datetime_obj = self._parse_string_to_datetime(value)
            elif hasattr(value, 'strftime'):
                self.datetime_obj = value
            else:
                self.datetime_obj = None
        
        def _parse_string_to_datetime(self, date_string):
            """Try various formats to parse string to datetime"""
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%B %d, %Y',
                '%b %d, %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # Try ISO format
            try:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            except:
                pass
            
            return None
        
        def strftime(self, format_string):
            """Format the datetime or return formatted string"""
            if self.datetime_obj:
                return self.datetime_obj.strftime(format_string)
            else:
                # If we can't parse it, return a reasonable default
                return str(self.original_value)
        
        def __str__(self):
            if self.datetime_obj:
                return self.datetime_obj.strftime('%Y-%m-%d')
            return str(self.original_value)
        
        def __repr__(self):
            return f"DateTimeWrapper({self.original_value})"
    
    def ensure_datetime_compatibility(obj):
        """Recursively ensure all created_at fields are datetime-compatible"""
        if hasattr(obj, '__dict__'):
            # Handle objects with attributes
            if hasattr(obj, 'created_at'):
                obj.created_at = DateTimeWrapper(obj.created_at)
        elif isinstance(obj, dict):
            # Handle dictionaries
            if 'created_at' in obj:
                obj['created_at'] = DateTimeWrapper(obj['created_at'])
        elif isinstance(obj, list):
            # Handle lists
            for item in obj:
                ensure_datetime_compatibility(item)
        
        return obj
    
    @app.route('/')
    def index():
        """Home page showing latest blogs"""
        page = request.args.get('page', 1, type=int)
        blogs_data = blog_service.get_all_blogs(page=page, per_page=6)
        
        # Debug information
        print("DEBUG: blogs_data type:", type(blogs_data))
        print("DEBUG: blogs_data keys:", blogs_data.keys() if isinstance(blogs_data, dict) else "Not a dict")
        
        # Ensure all blog objects have datetime-compatible created_at
        if isinstance(blogs_data, dict) and 'blogs' in blogs_data:
            print("DEBUG: Found blogs in blogs_data")
            for i, blog in enumerate(blogs_data['blogs']):
                print(f"DEBUG: Blog {i} type: {type(blog)}")
                if hasattr(blog, 'created_at'):
                    print(f"DEBUG: Blog {i} created_at before: {blog.created_at} (type: {type(blog.created_at)})")
                    blog.created_at = DateTimeWrapper(blog.created_at)
                    print(f"DEBUG: Blog {i} created_at after: {blog.created_at}")
                else:
                    print(f"DEBUG: Blog {i} has no created_at attribute")
        else:
            print("DEBUG: No 'blogs' key found in blogs_data or blogs_data is not a dict")
        
        return render_template('index.html', **blogs_data)
    
    @app.route('/blog/<int:blog_id>')
    def view_blog(blog_id):
        """View a specific blog post"""
        blog = blog_service.get_blog_by_id(blog_id)
        if not blog:
            flash('Blog post not found', 'error')
            return redirect(url_for('index'))
        
        # Ensure created_at is datetime-compatible
        if hasattr(blog, 'created_at'):
            blog.created_at = DateTimeWrapper(blog.created_at)
        
        return render_template('blog_detail.html', blog=blog)
    
    @app.route('/generate', methods=['GET', 'POST'])
    def generate_blog():
        """Generate a new blog post"""
        if request.method == 'POST':
            try:
                blog = blog_service.generate_daily_blog()
                if blog:
                    flash('Blog post generated successfully!', 'success')
                    return redirect(url_for('view_blog', blog_id=blog.id))
                else:
                    flash('Failed to generate blog post. Please try again.', 'error')
            except Exception as e:
                flash(f'Error generating blog: {str(e)}', 'error')
        
        return render_template('generate.html')
    
    @app.route('/create', methods=['GET', 'POST'])
    def create_blog():
        """Create a blog post manually"""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            subtitle = request.form.get('subtitle', '').strip()
            content = request.form.get('content', '').strip()
            
            if not title or not content:
                flash('Title and content are required', 'error')
                return render_template('create.html', title=title, subtitle=subtitle, content=content)
            
            try:
                blog = blog_service.create_manual_blog(title, subtitle, content)
                if blog:
                    flash('Blog post created successfully!', 'success')
                    return redirect(url_for('view_blog', blog_id=blog.id))
                else:
                    flash('Failed to create blog post', 'error')
            except Exception as e:
                flash(f'Error creating blog: {str(e)}', 'error')
        
        return render_template('create.html')
    
    @app.route('/delete/<int:blog_id>', methods=['POST'])
    def delete_blog(blog_id):
        """Delete a blog post"""
        try:
            if blog_service.delete_blog(blog_id):
                flash('Blog post deleted successfully!', 'success')
            else:
                flash('Blog post not found', 'error')
        except Exception as e:
            flash(f'Error deleting blog: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/api/blogs')
    def api_blogs():
        """API endpoint to get blogs"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        blogs_data = blog_service.get_all_blogs(page=page, per_page=per_page)
        return jsonify(blogs_data)
    
    @app.route('/api/blog/<int:blog_id>')
    def api_blog(blog_id):
        """API endpoint to get a specific blog"""
        blog = blog_service.get_blog_by_id(blog_id)
        if not blog:
            return jsonify({'error': 'Blog not found'}), 404
        return jsonify(blog.to_dict())
    
    @app.route('/api/generate', methods=['POST'])
    def api_generate():
        """API endpoint to generate a blog"""
        try:
            blog = blog_service.generate_daily_blog()
            if blog:
                return jsonify({
                    'success': True,
                    'blog': blog.to_dict(),
                    'message': 'Blog generated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to generate blog'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)