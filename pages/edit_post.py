import streamlit as st
import os
from datetime import datetime
from utils.database import db

def show_edit_post():
    st.title("✏️ Edit Post")
    
    # Get list of posts for selection using existing method
    posts = db.get_blog_posts()
    post_titles = {post['id']: post['title'] for post in posts}
    
    # Post selection
    selected_post_id = st.selectbox(
        "Select Post to Edit",
        options=list(post_titles.keys()),
        format_func=lambda x: post_titles[x]
    )
    
    if selected_post_id:
        post = db.get_blog_post(selected_post_id)
        
        with st.form("edit_post_form"):
            # Basic post info
            title = st.text_input("Title", value=post['title'])
            description = st.text_area("Description", value=post['description'])
            content = st.text_area("Content", value=post['content'], height=300)
            
            # Tags
            tags = st.text_input("Tags (comma separated)", 
                               value=','.join(post['tags']) if post['tags'] else '')
            
            # Image upload
            st.write("### Post Image")
            if post.get('thumbnail'):
                try:
                    st.image(post['thumbnail'], caption="Current thumbnail", width=200)
                except Exception as e:
                    st.warning(f"Could not load current image: {str(e)}")
            
            uploaded_file = st.file_uploader("Upload new image", type=['png', 'jpg', 'jpeg'])
            
            # Published status
            published = st.checkbox("Published", value=post.get('published', False))
            
            # Submit button
            submitted = st.form_submit_button("Update Post")
        
        if submitted:
            try:
                # Prepare updates
                updates = {
                    'title': title,
                    'description': description,
                    'content': content,
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
                    'published': published,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Handle image upload if new file
                if uploaded_file:
                    file_ext = os.path.splitext(uploaded_file.name)[1]
                    file_path = f"blog-images/{selected_post_id}{file_ext}"
                    
                    # Upload image and get URL using existing method
                    image_url = db.upload_media(uploaded_file.getvalue(), file_path)
                    updates['thumbnail'] = f"{selected_post_id}{file_ext}"
                
                # Update post using existing method
                updated_post = db.update_blog_post(selected_post_id, updates)
                
                if updated_post:
                    st.success("Post updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update post")
                    
            except Exception as e:
                st.error(f"Error updating post: {str(e)}")

if __name__ == "__main__":
    show_edit_post() 