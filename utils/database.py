from supabase import create_client, Client
import os
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Union, BinaryIO, Any
from pydantic import BaseModel
from pathlib import Path

class MediaContent(BaseModel):
    """Model for media content in blog posts"""
    url: str
    type: str  # 'image' or 'gif'
    caption: Optional[str] = None
    alt_text: Optional[str] = None

class BlogPostDB:
    def __init__(self):
        """Initialize Supabase client with existing configuration"""
        self.supabase = create_client(
            supabase_url=st.secrets["SUPABASE_URL"],
            supabase_key=st.secrets["SUPABASE_KEY"]
        )

    def save_blog_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new blog post to the database
        
        Args:
            post_data: Dictionary containing blog post data
                - title: str
                - description: str
                - content: str
                - tags: List[str]
                - type: str
                - published: bool
                - created_at: str (ISO format)
                - updated_at: str (ISO format)
        
        Returns:
            Dict containing the saved blog post data with ID
        """
        try:
            response = self.supabase.table("posts").insert(post_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error saving blog post: {str(e)}")
            raise

    def get_blog_posts(self, published_only: bool = False) -> List[Dict[str, Any]]:
        """Get all blog posts, optionally filtered by published status
        
        Args:
            published_only: If True, return only published posts
        
        Returns:
            List of blog post dictionaries
        """
        try:
            query = self.supabase.table("posts")
            if published_only:
                query = query.eq("published", True)
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching blog posts: {str(e)}")
            return []

    def get_blog_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific blog post by ID
        
        Args:
            post_id: The ID of the blog post to retrieve
        
        Returns:
            Blog post dictionary if found, None otherwise
        """
        try:
            response = self.supabase.table("posts").select("*").eq("id", post_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching blog post: {str(e)}")
            return None

    def update_blog_post(self, post_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a blog post
        
        Args:
            post_id: The ID of the blog post to update
            updates: Dictionary containing fields to update
        
        Returns:
            Updated blog post dictionary if successful, None otherwise
        """
        try:
            response = self.supabase.table("posts").update(updates).eq("id", post_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating blog post: {str(e)}")
            return None

    def toggle_publish_status(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Toggle the published status of a blog post
        
        Args:
            post_id: The ID of the blog post to toggle
        
        Returns:
            Updated blog post dictionary if successful, None otherwise
        """
        try:
            # Get current post
            post = self.get_blog_post(post_id)
            if not post:
                return None
            
            # Toggle published status
            updates = {
                "published": not post.get("published", False),
                "updated_at": datetime.now().isoformat()
            }
            
            return self.update_blog_post(post_id, updates)
        except Exception as e:
            print(f"Error toggling publish status: {str(e)}")
            return None

class DatabaseClient:
    def __init__(self, url: str = None, key: str = None):
        """Initialize Supabase client with URL and key"""
        self.connection_status = "Initializing"
        self.storage_status = "Initializing"
        
        # Get credentials from Streamlit secrets
        self.url = url or st.secrets["SUPABASE_URL"]
        self.key = key or st.secrets["SUPABASE_KEY"]
        
        if not self.url or not self.key:
            self.connection_status = "Error: Missing credentials"
            raise ValueError("Supabase URL and key are required")
            
        try:
            self.client = create_client(self.url, self.key)
            self.connection_status = "Connecting"
            
            # Verify connection by trying to access the database
            try:
                # Try a simple query to verify connection
                self.client.table('posts').select("count", count='exact').execute()
                self.connection_status = "Connected"
            except Exception as db_e:
                self.connection_status = f"Warning: Connection issues - {str(db_e)}"
            
        except Exception as e:
            self.connection_status = f"Error: Failed to connect - {str(e)}"
            raise
        
        self._ensure_storage_bucket()

    def _ensure_storage_bucket(self):
        """Verify access to the blog-assets/blog-images storage path"""
        try:
            # Use from_ to access the bucket and list contents of the blog-images folder
            files = self.client.storage.from_('blog-assets').list('blog-images')
            self.storage_status = f"Storage accessible ({len(files)} files found)"
        except Exception as e:
            self.storage_status = f"Warning: Storage access issues - {str(e)}"

    def get_status(self):
        """Get the current status of database connections"""
        return {
            "connection": self.connection_status,
            "storage": self.storage_status
        }

    def upload_media(self, file: Union[BinaryIO, bytes, str, Path], file_path: str) -> str:
        """Upload media file to storage and return public URL"""
        try:
            # Ensure the file path includes the blog-images folder
            full_path = f"blog-images/{file_path}"
            
            # Upload the file
            response = self.client.storage.from_('blog-assets').upload(
                path=full_path,
                file=file,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
            
            # Get the public URL
            public_url = self.client.storage.from_('blog-assets').get_public_url(full_path)
            return public_url
        except Exception as e:
            raise Exception(f"Error uploading media: {str(e)}")

    def delete_media(self, file_path: str):
        """Delete media file from storage"""
        try:
            # Ensure the file path includes the blog-images folder
            full_path = f"blog-images/{file_path}"
            self.client.storage.from_('blog-assets').remove([full_path])
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
            
            response = (self.client.table("posts")
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
            query = self.client.table("posts").select("*")
            if published_only:
                query = query.eq("published", True)
            response = query.order("date", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            raise Exception(f"Error fetching blog posts: {str(e)}")

    def get_blog_post(self, post_id: str) -> Optional[Dict]:
        """Get a specific blog post by ID"""
        try:
            response = (self.client.table("posts")
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
            
            response = (self.client.table("posts")
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
                response = (self.client.table("posts")
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
            
            response = (self.client.table("posts")
                       .update({"media": new_media})
                       .eq("id", post_id)
                       .execute())
            
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error adding media to post: {str(e)}")

# Create a singleton instance
db = DatabaseClient(
    url=st.secrets["SUPABASE_URL"],
    key=st.secrets["SUPABASE_KEY"]
) 