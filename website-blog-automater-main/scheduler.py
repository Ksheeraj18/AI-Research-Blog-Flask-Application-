from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.blog_service import BlogService
import os
import atexit

class BlogScheduler:
    """Scheduler for automated blog generation"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.blog_service = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
        # Initialize blog service with app context
        with app.app_context():
            groq_api_key = app.config.get('GROQ_API_KEY')
            if groq_api_key:
                self.blog_service = BlogService(groq_api_key)
                
                # Schedule daily blog generation at 9 AM
                self.scheduler.add_job(
                    func=self.generate_daily_blog,
                    trigger=CronTrigger(hour=9, minute=0),
                    id='daily_blog_generation',
                    name='Generate Daily AI Blog Post',
                    replace_existing=True
                )
                
                # Start the scheduler
                self.scheduler.start()
                
                # Shutdown scheduler when app exits
                atexit.register(lambda: self.scheduler.shutdown())
                
                print("Blog scheduler initialized - Daily posts will be generated at 9:00 AM")
            else:
                print("Warning: GROQ_API_KEY not found. Scheduler not started.")
    
    def generate_daily_blog(self):
        """Generate daily blog post (called by scheduler)"""
        if not self.blog_service or not self.app:
            print("Error: Blog service or app not initialized")
            return
        
        try:
            with self.app.app_context():
                blog = self.blog_service.generate_daily_blog()
                if blog:
                    print(f"Successfully generated scheduled blog: {blog.title}")
                else:
                    print("Failed to generate scheduled blog post")
        except Exception as e:
            print(f"Error in scheduled blog generation: {e}")
    
    def add_custom_job(self, func, trigger, job_id, name):
        """Add a custom scheduled job"""
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True
        )
    
    def remove_job(self, job_id):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            print(f"Error removing job {job_id}: {e}")
            return False
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Blog scheduler shutdown")
