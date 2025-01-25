import streamlit as st
import os
import traceback
import sys
import json
import re
from urllib.parse import urlparse
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO
from blog_agents import (
    main as generate_blog,  # Rename to avoid confusion
    PraisonAIAgents, 
    researcher, 
    writer, 
    initial_research, 
    analysis_task, 
    metadata_task, 
    writing_task, 
    save_task
)
from database import db, BlogPostDB
from utils.auth import require_auth, init_auth, is_authenticated, get_user
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(
    page_title="Blog Maker",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set API key from Streamlit secrets
os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

# Add URL styling to CSS
st.markdown("""
<style>
    .terminal {
        background-color: #1E1E1E;
        color: #D4D4D4;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        margin: 1rem 0;
        border: 1px solid #333;
    }
    .terminal-header {
        color: #569CD6;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #333;
    }
    .agent-info {
        background-color: #252526;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.5rem 0;
    }
    .agent-name {
        color: #C586C0;
    }
    .agent-role {
        color: #4EC9B0;
    }
    .agent-tools {
        color: #9CDCFE;
    }
    .task-output {
        color: #CE9178;
        white-space: pre-wrap;
    }
    .success-message {
        color: #6A9955;
    }
    .error-message {
        color: #F44747;
    }
    .url-link {
        color: #4EC9B0;
        text-decoration: underline;
    }
    .url-link:hover {
        color: #569CD6;
    }
</style>
""", unsafe_allow_html=True)

# Display database status
status = db.get_status()
if status["connection"] == "Connected":
    st.sidebar.success("✅ Database Connected")
elif "Warning" in status["connection"]:
    st.sidebar.warning(f"⚠️ {status['connection']}")
else:
    st.sidebar.error(f"❌ {status['connection']}")

if status["storage"] == "Storage accessible":
    st.sidebar.success("✅ Storage Connected")
elif "Warning" in status["storage"]:
    st.sidebar.warning(f"⚠️ {status['storage']}")
else:
    st.sidebar.error(f"❌ {status['storage']}")

def is_valid_url(url):
    """Check if a URL is valid and properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_url(url):
    """Format URL to ensure it's valid and has proper scheme."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def process_json_urls(data):
    """Recursively process JSON data to format URLs."""
    if isinstance(data, dict):
        return {k: process_json_urls(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [process_json_urls(item) for item in data]
    elif isinstance(data, str):
        # Check if the string looks like a URL
        if any(domain in data.lower() for domain in ['.com', '.org', '.net', '.edu', '.gov', '.io', '.ai']):
            # Extract URLs from text using a more robust regex pattern
            url_pattern = r'(?:https?:\/\/)?(?:[\w-]+\.)+[\w-]+(?:\/[^\s]*)?'
            urls = re.findall(url_pattern, data)
            for url in urls:
                if url and is_valid_url(format_url(url)):
                    formatted_url = format_url(url)
                    # Use a more specific replacement to avoid partial matches
                    data = re.sub(re.escape(url), f'<a href="{formatted_url}" class="url-link" target="_blank">{url}</a>', data)
        return data
    return data

def display_json_with_links(data, container):
    """Display JSON data with clickable links."""
    processed_data = process_json_urls(data)
    if isinstance(processed_data, (dict, list)):
        # Format JSON with proper indentation
        formatted_json = json.dumps(processed_data, indent=2)
        # Convert the formatted JSON to HTML with preserved formatting
        html_content = f'<pre class="terminal">{formatted_json}</pre>'
        container.markdown(html_content, unsafe_allow_html=True)
    else:
        container.markdown(processed_data, unsafe_allow_html=True)

@contextmanager
def st_capture(output_func):
    """Capture stdout/stderr and redirect to a Streamlit element."""
    with StringIO() as stdout, redirect_stdout(stdout), redirect_stderr(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            # Process URLs in the output
            processed_output = process_json_urls(string)
            formatted_output = f"""
            <div class="terminal">
                <div class="terminal-header">🖥️ Terminal Output</div>
                <div class="task-output">{processed_output}</div>
            </div>
            """
            output_func(formatted_output, unsafe_allow_html=True)
            return ret
        
        stdout.write = new_write
        yield stdout

# Initialize authentication
init_auth()

def new_write(data):
    """Custom write function that handles URLs and Streamlit output"""
    if data is None:
        return
    try:
        # Process URLs if the data is a string
        if isinstance(data, str):
            url_pattern = r'(?:https?:\/\/)?(?:[\w-]+\.)+[\w-]+(?:\/[^\s]*)?'
            urls = re.findall(url_pattern, data)
            processed_data = data
            for url in urls:
                if url and is_valid_url(format_url(url)):
                    formatted_url = format_url(url)
                    processed_data = processed_data.replace(url, f'<a href="{formatted_url}" class="url-link" target="_blank">{url}</a>')
            st.markdown(processed_data, unsafe_allow_html=True)
        else:
            st.write(data)
    except Exception as e:
        st.error(f"Error processing output: {str(e)}")

@require_auth
def show_blog_generator():
    """Show the blog generator interface"""
    # Title and description
    st.title("📝 AI Blog Post Generator")
    st.markdown("""
    Generate engaging blog posts about any topic using AI agents! 
    Watch the process unfold as our agents research, analyze, and write your content.
    """)

    # Input section with length control
    col1, col2 = st.columns([3, 1])
    with col1:
        user_topic = st.text_input("What would you like to write about?", 
                             placeholder="Enter a topic (e.g., 'The Future of AI in Healthcare')")
    with col2:
        length = st.selectbox(
            "Post Length",
            options=["quick", "standard", "deep", "complete"],
            format_func=lambda x: {
                "quick": "Quick (500-750 words)",
                "standard": "Standard (1000-1500 words)",
                "deep": "Deep Dive (2500-3000 words)",
                "complete": "Complete Guide (4000-5000 words)"
            }[x],
            help="Select the desired length of your blog post"
        )

    if st.button("Generate Blog Post"):
        if not user_topic:
            st.error("Please enter a topic to write about.")
            return
            
        # Validate topic length and content
        if len(user_topic.strip()) < 5:
            st.error("Topic is too short. Please provide a more specific topic.")
            return
            
        if len(user_topic.strip()) > 200:
            st.error("Topic is too long. Please make it more concise.")
            return

        try:
            # Create placeholders for output
            output_placeholder = st.empty()
            progress = st.progress(0)
            
            # Store topic in session state to maintain context
            if 'current_topic' not in st.session_state:
                st.session_state.current_topic = user_topic
            
            # Create generation context
            generation_context = {
                'topic': user_topic,
                'length': length,
                'date': datetime.now().strftime("%B %Y")
            }
            
            # Redirect stdout to our custom writer
            with st_capture(new_write):
                # Run the workflow with the user's topic and context
                result = generate_blog(user_topic)
                
                if result:
                    # Display final blog post
                    if os.path.exists("outputs/ai_blog_post.md"):
                        with open("outputs/ai_blog_post.md", "r") as f:
                            blog_content = f.read()
                            
                            # Verify content matches topic
                            if user_topic.lower() not in blog_content.lower():
                                st.error("Generated content may have deviated from the requested topic. Please try again.")
                                return
                                
                            st.markdown("## 📝 Final Blog Post")
                            st.markdown(blog_content)
                            
                            # Save to database if available
                            if hasattr(result, 'pydantic'):
                                db_result = save_to_database(result.pydantic, blog_content)
                                if db_result:
                                    st.success("✅ Blog post saved to database!")
            
        except Exception as e:
            st.error("❌ An error occurred")
            with st.expander("See error details"):
                st.error(str(e))
                st.code(traceback.format_exc())

def save_to_database(blog_post, content):
    """Save the generated blog post to the database"""
    try:
        post = BlogPostDB(
            title=blog_post.metadata.title,
            description=blog_post.metadata.description,
            content=content,
            tags=blog_post.metadata.tags,
            type=blog_post.metadata.type,
            published=False  # Start as draft
        )
        result = db.save_blog_post(post)
        return result
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return None

def main():
    if not is_authenticated():
        st.warning("Please log in to access the blog generator.")
        st.stop()
    else:
        show_blog_generator()

if __name__ == "__main__":
    main() 