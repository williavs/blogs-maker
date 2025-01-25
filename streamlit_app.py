import streamlit as st
import os
import traceback
import sys
import json
import re
from urllib.parse import urlparse
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO
from blog_agents import main, PraisonAIAgents, researcher, writer, initial_research, analysis_task, metadata_task, writing_task, save_task
from database import db, BlogPostDB
from utils.auth import require_auth, init_auth, is_authenticated, get_user

# Configure page - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Blog Post Generator",
    page_icon="📝",
    layout="wide"
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
        topic = st.text_input("What would you like to write about?", 
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
        if topic:
            try:
                # Display agent info with custom styling at the top
                st.markdown(f"""
                <div class="terminal">
                    <div class="agent-info">
                        <span class="agent-name">👤 Agent: Researcher</span><br>
                        <span class="agent-role">Role: Tech Explorer</span><br>
                        <span class="agent-tools">Tools: internet_search</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Create placeholders for each step
                research_placeholder = st.empty()
                analysis_placeholder = st.empty()
                metadata_placeholder = st.empty()
                writing_placeholder = st.empty()
                
                
                
                # Initialize progress tracking
                progress = st.progress(0)
                
                with st.spinner("🔍 Researching your topic..."):
                    # Create and start the agent workflow with progress tracking
                    agents = PraisonAIAgents(
                        agents=[researcher, writer],
                        tasks=[initial_research, analysis_task, metadata_task, writing_task, save_task],
                        process="sequential",
                        verbose=True
                    )
                    
                    # Track task completion
                    completed_tasks = []
                    
                    def task_callback(task_output):
                        task_name = task_output.task_name
                        completed_tasks.append(task_name)
                        
                        # Update progress bar
                        progress.progress(len(completed_tasks) / 5)
                        
                        # Update appropriate placeholder based on task with custom styling
                        if task_name == "initial_research":
                            with research_placeholder.container():
                                st.markdown('<div class="terminal-header">🔬 Research Findings</div>', unsafe_allow_html=True)
                                display_json_with_links(task_output.json_dict, research_placeholder)
                        
                        elif task_name == "analysis":
                            with analysis_placeholder.container():
                                st.markdown('<div class="terminal-header">🧮 Analysis Results</div>', unsafe_allow_html=True)
                                display_json_with_links(task_output.json_dict, analysis_placeholder)
                        
                        elif task_name == "metadata":
                            with metadata_placeholder.container():
                                st.markdown('<div class="terminal-header">📋 Blog Metadata</div>', unsafe_allow_html=True)
                                display_json_with_links(task_output.json_dict, metadata_placeholder)
                        
                        elif task_name == "writing":
                            with writing_placeholder.container():
                                st.markdown('<div class="terminal-header">✍️ Generated Blog Post</div>', unsafe_allow_html=True)
                                processed_content = process_json_urls(task_output.raw)
                                writing_placeholder.markdown(processed_content, unsafe_allow_html=True)
                        # Create a placeholder for terminal output (moved to bottom)
                    terminal_output = st.empty()
                    
                    # Run the workflow with terminal output capture
                    with st_capture(terminal_output.markdown):
                        # Update writing task description with length control
                        length_instructions = {
                            'quick': 'Keep this focused and punchy- - - around 500-750 words. Hit the key points that\'ll make someone go "aha!"',
                            'standard': 'Give us a solid exploration- - - about 1000-1500 words. Enough space to really share some good insights.',
                            'deep': 'This is a deep exploration- - - 2500-3000 words. Really explore the nuances and share detailed examples.',
                            'complete': 'This is a complete guide- - - 4000-5000 words. Cover everything someone needs to know, from fundamentals to advanced concepts.'
                        }
                        
                        writing_task.description = writing_task.description + f"\n\nLength Control: {length_instructions[length]}"
                        result = agents.start({"topic": topic})
                    
                    # Show final blog post
                    if os.path.exists("outputs/ai_blog_post.md"):
                        with open("outputs/ai_blog_post.md", "r") as f:
                            blog_content = f.read()
                            st.markdown('<div class="terminal-header">📝 Final Blog Post</div>', unsafe_allow_html=True)
                            st.markdown(blog_content)
                    
                    st.markdown('<div class="success-message">✅ Blog post generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Save to database
                    if os.path.exists("outputs/ai_blog_post.md"):
                        with open("outputs/ai_blog_post.md", "r") as f:
                            blog_content = f.read()
                            if result and hasattr(result, 'pydantic'):
                                db_result = save_to_database(result.pydantic, blog_content)
                                if db_result:
                                    st.success(f"Blog post saved to database! View it in the Manage Posts page.")
                                    st.markdown(f"Post ID: `{db_result['id']}`")
                    
            except Exception as e:
                st.markdown('<div class="error-message">❌ An error occurred during execution</div>', unsafe_allow_html=True)
                
                # Create an expander for the full error details
                with st.expander("See detailed error message"):
                    st.markdown(f'<div class="error-message">Error message: {str(e)}</div>', unsafe_allow_html=True)
                    st.code(traceback.format_exc(), language="python")
                    
                    if 'terminal_output' in locals():
                        st.markdown('<div class="terminal-header">Terminal Output at Time of Error</div>', unsafe_allow_html=True)
                        terminal_output.markdown('<div class="error-message">Terminal output unavailable</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic first!")

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