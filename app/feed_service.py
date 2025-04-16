import feedparser
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from .models import Post
import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInFeedService:
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = BackgroundScheduler()
        self.job_roles = {}  # Dictionary to store job roles and their RSS feeds

    def add_job_role(self, role_name: str, rss_url: str):
        """Add a new job role and its RSS feed URL to monitor"""
        self.job_roles[role_name] = rss_url
        logger.info(f"Added job role: {role_name} with RSS URL: {rss_url}")

    def fetch_feed(self, role_name: str) -> List[Dict]:
        """Fetch and parse RSS feed for a specific job role"""
        if role_name not in self.job_roles:
            logger.error(f"Job role {role_name} not found")
            return []

        try:
            feed = feedparser.parse(self.job_roles[role_name])
            posts = []
            
            for entry in feed.entries:
                post = {
                    'title': entry.get('title', ''),
                    'content': entry.get('description', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'role': role_name
                }
                posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching feed for {role_name}: {str(e)}")
            return []

    def save_posts(self, posts: List[Dict]):
        """Save fetched posts to the database"""
        for post_data in posts:
            try:
                post = Post(
                    title=post_data['title'],
                    content=post_data['content'],
                    created_at=datetime.now(),
                    author_id=1  # Default system user
                )
                self.db.add(post)
            except Exception as e:
                logger.error(f"Error saving post: {str(e)}")
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error committing posts: {str(e)}")

    def fetch_all_feeds(self):
        """Fetch feeds for all registered job roles"""
        for role_name in self.job_roles:
            posts = self.fetch_feed(role_name)
            self.save_posts(posts)
            logger.info(f"Fetched {len(posts)} posts for role: {role_name}")

    def start_scheduler(self):
        """Start the scheduler to fetch feeds daily at 8 AM"""
        self.scheduler.add_job(
            self.fetch_all_feeds,
            CronTrigger(hour=8, minute=0),
            id='linkedin_feed_fetcher',
            name='Fetch LinkedIn feeds daily',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped") 