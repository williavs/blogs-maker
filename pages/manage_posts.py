import streamlit as st
from datetime import datetime
from utils.auth import require_auth, init_auth
from database import DatabaseClient

# Initialize authentication
init_auth()

# Initialize database client with Supabase credentials from Streamlit secrets
db = DatabaseClient(
    url=st.secrets["SUPABASE_URL"],
    key=st.secrets["SUPABASE_KEY"]
)

@require_auth
def show_manage_posts():
    """Show the manage posts interface"""
    st.title("Manage Blog Posts")
    
    try:
        # Get the session from Streamlit's session state
        if not st.session_state.get("authenticated"):
            st.error("Please log in to view posts")
            return
            
        # Fetch all posts
        response = db.client.table("posts").select("*").order('created_at', desc=True).execute()
        posts = response.data
        
        # Debug: Show total posts
        st.write(f"Total posts found: {len(posts)}")
        
        # Debug: Show each post's published status
        with st.expander("🔍 Debug: Post Status"):
            for post in posts:
                st.write(f"Post '{post['title']}' - Published value: {post.get('published')} (Type: {type(post.get('published'))})")
        
        # Separate posts based on published status - using boolean conversion
        published_posts = [post for post in posts if bool(post.get('published'))]
        draft_posts = [post for post in posts if not bool(post.get('published'))]
        
        # Debug: Show counts
        st.write(f"Published posts found: {len(published_posts)}")
        st.write(f"Draft posts found: {len(draft_posts)}")
        
        # Create tabs for published and draft posts
        tab_published, tab_drafts = st.tabs([
            f"Published Posts ({len(published_posts)})", 
            f"Draft Posts ({len(draft_posts)})"
        ])
        
        # Display published posts
        with tab_published:
            for post in published_posts:
                with st.expander(f"📝 {post['title']}"):
                    # Display post metadata
                    st.write(f"**Description:** {post['description']}")
                    st.write(f"**Type:** {post['type']}")
                    if post.get('tags'):
                        st.write(f"**Tags:** {', '.join(post['tags'])}")
                    
                    # Handle dates safely
                    created_at = post.get('created_at', '').replace('Z', '+00:00')
                    updated_at = post.get('updated_at', '').replace('Z', '+00:00')
                    
                    if created_at:
                        st.write(f"**Created:** {datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M:%S')}")
                    if updated_at:
                        st.write(f"**Last Updated:** {datetime.fromisoformat(updated_at).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Display thumbnail if available
                    if post.get('thumbnail'):
                        st.image(post['thumbnail'], caption="Thumbnail", width=200)
                    
                    # Display content
                    if post.get('content'):
                        st.markdown("### Content Preview")
                        st.markdown(post['content'])
                    
                    # Add unpublish button
                    if st.button(f"Unpublish", key=f"unpub_{post['id']}"):
                        try:
                            db.toggle_publish_status(post['id'], False)
                            st.success("Post unpublished successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error unpublishing post: {str(e)}")
        
        # Display draft posts
        with tab_drafts:
            for post in draft_posts:
                with st.expander(f"📝 {post['title']}"):
                    # Display post metadata
                    st.write(f"**Description:** {post['description']}")
                    st.write(f"**Type:** {post['type']}")
                    if post.get('tags'):
                        st.write(f"**Tags:** {', '.join(post['tags'])}")
                    
                    # Handle dates safely
                    created_at = post.get('created_at', '').replace('Z', '+00:00')
                    updated_at = post.get('updated_at', '').replace('Z', '+00:00')
                    
                    if created_at:
                        st.write(f"**Created:** {datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M:%S')}")
                    if updated_at:
                        st.write(f"**Last Updated:** {datetime.fromisoformat(updated_at).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Display thumbnail if available
                    if post.get('thumbnail'):
                        st.image(post['thumbnail'], caption="Thumbnail", width=200)
                    
                    # Display content
                    if post.get('content'):
                        st.markdown("### Content Preview")
                        st.markdown(post['content'])
                    
                    # Add publish button
                    if st.button(f"Publish", key=f"pub_{post['id']}"):
                        try:
                            db.toggle_publish_status(post['id'], True)
                            st.success("Post published successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error publishing post: {str(e)}")
                    
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")
        if hasattr(e, 'response'):
            st.error(f"Response details: {e.response.text if hasattr(e.response, 'text') else e.response}")

# Add custom CSS
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .stExpander {
        background-color: #f0f2f6;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    show_manage_posts() 