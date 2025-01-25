from supabase import create_client, Client
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, BinaryIO
from pydantic import BaseModel
from pathlib import Path

class MediaContent(BaseModel):
    """Model for media content in blog posts"""
    url: str
    type: str  # 'image' or 'gif'
    caption: Optional[str] = None
    alt_text: Optional[str] = None

class BlogPostDB(BaseModel):
    """Database model for blog posts"""
    title: str
    description: str
    content: str
    tags: List[str]
    type: str = "insight"
    published: bool = False
    thumbnail: Optional[str] = None
    media: Optional[List[MediaContent]] = None

class DatabaseClient:
    def __init__(self, url: str, key: str):
        """Initialize Supabase client"""
        if not url or not key:
            raise Exception("Supabase URL and key are required")
        
        print(f"Initializing Supabase client...")
        print(f"URL provided: {'Yes' if url else 'No'}")
        print(f"Key provided: {'Yes' if key else 'No'}")
        
        try:
            self.supabase: Client = create_client(
                supabase_url=url,
                supabase_key=key
            )
            print("Successfully initialized Supabase client")
            
            # Verify connection by trying to access the database
            try:
                # Try a simple query to verify connection
                self.supabase.table('posts').select("count", count='exact').execute()
                print("Successfully connected to database")
            except Exception as db_e:
                print(f"Warning: Could not verify database connection: {str(db_e)}")
            
        except Exception as e:
            print(f"Error initializing Supabase client: {str(e)}")
            raise
        
        self._ensure_storage_bucket()

    def _ensure_storage_bucket(self):
        """Verify access to the blog-assets/blog-images storage path"""
        try:
            print("Attempting to access blog-assets/blog-images...")
            # Use from_ to access the bucket and list contents of the blog-images folder
            files = self.supabase.storage.from_('blog-assets').list('blog-images')
            print(f"Successfully accessed blog-assets/blog-images. Found {len(files)} files.")
        except Exception as e:
            print(f"Warning: Could not access storage path. Error details: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response details: {e.response.text if hasattr(e.response, 'text') else e.response}")

    def upload_media(self, file: Union[BinaryIO, bytes, str, Path], file_path: str) -> str:
        """Upload media file to storage and return public URL"""
        try:
            # Ensure the file path includes the blog-images folder
            full_path = f"blog-images/{file_path}"
            
            # Upload the file
            response = self.supabase.storage.from_('blog-assets').upload(
                path=full_path,
                file=file,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
            
            # Get the public URL
            public_url = self.supabase.storage.from_('blog-assets').get_public_url(full_path)
            return public_url
        except Exception as e:
            raise Exception(f"Error uploading media: {str(e)}")

    def delete_media(self, file_path: str):
        """Delete media file from storage"""
        try:
            # Ensure the file path includes the blog-images folder
            full_path = f"blog-images/{file_path}"
            self.supabase.storage.from_('blog-assets').remove([full_path])
        except Exception as e:
            raise Exception(f"Error deleting media: {str(e)}")

    def save_blog_post(self, post: BlogPostDB) -> Dict:
        """Save a new blog post to the database"""
        try:
            data = {
                "title": post.title,
                "description": post.description,
                "content": post.content,
                "tags": post.tags,
                "type": post.type,
                "published": post.published,
                "thumbnail": post.thumbnail,
                "media": [media.dict() for media in post.media] if post.media else []
            }
            
            response = (self.supabase.table("posts")
                       .insert(data)
                       .execute())
            
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error saving blog post: {str(e)}")

    def get_blog_posts(self, published_only: bool = False) -> List[Dict]:
        """Get all blog posts
        
        Args:
            published_only (bool): If True, only return published posts. If False, return all posts.
        """
        try:
            query = self.supabase.table("posts").select("*")
            if published_only:
                query = query.eq("published", True)
            response = query.order("date", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            raise Exception(f"Error fetching blog posts: {str(e)}")

    def get_blog_post(self, post_id: str) -> Optional[Dict]:
        """Get a specific blog post by ID"""
        try:
            response = (self.supabase.table("posts")
                       .select("*")
                       .eq("id", post_id)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching blog post: {str(e)}")

    def update_blog_post(self, post_id: str, updates: Dict) -> Dict:
        """Update a blog post"""
        try:
            # Ensure post exists
            existing_post = self.get_blog_post(post_id)
            if not existing_post:
                raise Exception(f"Blog post with ID {post_id} not found")
            
            # If updating media content, ensure proper format
            if "media" in updates and updates["media"]:
                if isinstance(updates["media"], list):
                    updates["media"] = [
                        media.dict() if isinstance(media, MediaContent) else media 
                        for media in updates["media"]
                    ]
            
            response = (self.supabase.table("posts")
                       .update(updates)
                       .eq("id", post_id)
                       .execute())
            
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating blog post: {str(e)}")

    def toggle_publish_status(self, post_id: str, publish: bool) -> Dict:
        """Toggle the published status of a blog post"""
        try:
            # Get existing post
            existing_post = self.get_blog_post(post_id)
            if not existing_post:
                raise Exception(f"Blog post with ID {post_id} not found")
            
            # Only update if status is different
            if existing_post.get("published") != publish:
                response = (self.supabase.table("posts")
                           .update({"published": publish})
                           .eq("id", post_id)
                           .execute())
                
                return response.data[0] if response.data else None
            
            return existing_post
        except Exception as e:
            raise Exception(f"Error toggling publish status: {str(e)}")

    def add_media_to_post(self, post_id: str, media: Union[MediaContent, List[MediaContent]]) -> Dict:
        """Add media content to a blog post"""
        try:
            existing_post = self.get_blog_post(post_id)
            if not existing_post:
                raise Exception(f"Blog post with ID {post_id} not found")
            
            current_media = existing_post.get("media", [])
            
            # Convert single media to list
            if isinstance(media, MediaContent):
                media = [media]
            
            # Add new media
            new_media = current_media + [m.dict() for m in media]
            
            response = (self.supabase.table("posts")
                       .update({"media": new_media})
                       .eq("id", post_id)
                       .execute())
            
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error adding media to post: {str(e)}")

# Create a singleton instance
db = DatabaseClient(
    url=os.getenv("SUPABASE_URL"),
    key=os.getenv("SUPABASE_KEY")) 