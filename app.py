import streamlit as st

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import subprocess
import os
from pages.manage_posts import show_manage_posts
from pages.invoice_generator import show_invoice_generator
from pages.edit_post import show_edit_post

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    .title-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .terminal {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Courier New', Courier, monospace;
        padding: 1rem;
        border-radius: 5px;
        min-height: 1000px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.selectbox(
    "Select Page",
    ["Blog Generator", "Manage Posts", "Edit Post", "Invoice Generator"]
)

if page == "Blog Generator":
    # Title section
    st.markdown("""
    <div class="title-container">
        <h1>✍️ AI Blog Generator</h1>
        <p style="font-size: 1.2em; color: #666;">Transform your ideas into engaging blog posts with AI assistance</p>
    </div>
    """, unsafe_allow_html=True)

    # Create columns for input fields
    col1, col2 = st.columns([3, 1])

    with col1:
        # Topic input with placeholder
        topic = st.text_input(
            "What's your blog topic?",
            placeholder="e.g., The future of AI in healthcare",
            help="Enter the main topic or subject you want to write about"
        )

    with col2:
        # Analysis depth slider
        analysis_depth = st.select_slider(
            "Analysis Depth",
            options=["Basic", "Detailed", "Comprehensive"],
            value="Detailed",
            help="Choose how deep you want the analysis to be"
        )

    # Info box about the process
    with st.expander("ℹ️ How it works", expanded=False):
        st.markdown("""
        1. **Research**: AI explores your topic using web searches
        2. **Analysis**: Connects ideas and finds valuable insights
        3. **Writing**: Creates an engaging blog post in a conversational style
        4. **Saving**: Automatically saves as a draft in your database
        
        The generated post will be casual but informative, perfect for tech enthusiasts!
        """)

    # Generate button
    if st.button("✨ Generate Blog Post", help="Click to start generating your blog post"):
        if not topic:
            st.error("Please enter a topic first!")
        else:
            try:
                # Make the shell script executable
                script_path = os.path.join(os.path.dirname(__file__), "run.sh")
                os.chmod(script_path, 0o755)
                
                # Create a placeholder for output
                output_placeholder = st.empty()
                
                # Run the shell script with topic and analysis depth
                process = subprocess.Popen(
                    [script_path, topic, analysis_depth, st.secrets["ANTHROPIC_API_KEY"]],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Initialize output lines list
                output_lines = []
                
                # Read and display output in real-time
                for line in process.stdout:
                    output_lines.append(line)
                    output_placeholder.markdown(
                        f'<div class="terminal">{"".join(output_lines)}</div>',
                        unsafe_allow_html=True
                    )
                
                # Wait for the process to complete
                process.wait()
                
                if process.returncode == 0:
                    st.success("✅ Blog post generated and saved as draft!")
                else:
                    st.error("❌ An error occurred during generation")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

elif page == "Manage Posts":
    show_manage_posts()
elif page == "Edit Post":
    show_edit_post()
elif page == "Invoice Generator":
    show_invoice_generator()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;">
    <p>Made with ❤️ using PraisonAI Agents</p>
</div>
""", unsafe_allow_html=True)