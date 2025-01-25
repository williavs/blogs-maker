from praisonaiagents import Agent, Task, PraisonAIAgents
from praisonaiagents.tools import duckduckgo
import os
import streamlit as st
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import requests


# Get current date for research context
current_date = datetime.now().strftime("%B %Y")  # e.g., "March 2024"

# Define output structures
class ResearchFindings:
    def __init__(self):
        self.original_request = ""  # Store the exact user request
        self.findings = {
            "main_points": [],      # Key findings that directly answer the request
            "examples": [],         # Real examples that match their needs
            "solutions": [],        # Solutions to their specific problems
            "opportunities": []     # Opportunities relevant to their request
        }
        self.sources = []

class BlogMetadata:
    def __init__(self):
        self.original_request = ""  # Store the exact user request
        self.title = ""
        self.description = ""
        self.tags = []
        self.type = "insight"

class BlogPost:
    def __init__(self):
        self.original_request = ""  # Store the exact user request
        self.title = ""
        self.content = ""
        self.metadata = None

# LLM Configuration
llm_config = {
    "model": "claude-3-5-sonnet-20241022",
    "api_key": st.secrets["ANTHROPIC_API_KEY"],
    "temperature": 0.7,
    "max_tokens": 8192,
    "stream": True,  # Enable streaming for Streamlit
    "verbose": False  # Disable verbose output
}

def save_blog_post(content: str) -> str:
    """Save the blog post to a markdown file"""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/ai_blog_post.md", "w") as f:
        f.write(content)
    return "Blog post saved successfully"

# Create specialized agents
researcher = Agent(
    name="ResearchAssistant",
    role="Research Specialist",
    goal="""Conduct comprehensive research and analysis ONLY about the specific topic provided.
    You must NEVER deviate from the exact topic or include generic content.""",
    backstory="""You are a hyper-focused research specialist who excels at finding precise, 
    topic-specific information. You have a strict policy of never including generic content 
    or straying from the exact topic requested. You constantly verify that all your research 
    and analysis stays precisely on topic.""",
    tools=[duckduckgo],
    llm=llm_config,
    self_reflect=True,
    verbose=False
)

writer = Agent(
    name="ContentWriter",
    role="Content Specialist",
    goal="""Create engaging and informative blog content STRICTLY about the provided topic.
    You must NEVER include generic content or deviate from the exact topic.""",
    backstory="""You are a specialized content writer who excels at creating laser-focused articles
    that stay precisely on topic. You have a strict policy of never including generic content
    or expanding beyond the specific topic requested. You constantly verify that every sentence
    you write directly relates to the original topic.""",
    tools=[save_blog_post],
    llm=llm_config,
    self_reflect=True,
    verbose=False
)

# Define Research Tasks
request_analysis = Task(
    name="analyze_request",
    description="""WRITE ONLY ABOUT THIS EXACT TOPIC: {topic}

    DO NOT write a general technology article!
    
    1. What is the SPECIFIC topic being requested?
    2. What EXACT aspects need to be covered?
    3. What SPECIFIC information is needed?
    
    STAY FOCUSED on this exact topic - no generic content!""",
    expected_output="Specific topic analysis",
    agent=researcher
)

initial_research = Task(
    name="research",
    description="""RESEARCH ONLY THIS EXACT TOPIC: {topic}

    DO NOT write a general technology article!
    
    Find SPECIFIC information about:
    1. Latest news and developments about THIS topic
    2. Actual features and capabilities of THIS product/service
    3. Real-world examples of THIS specific topic
    4. Expert opinions about THIS exact topic
    
    Date: {current_date}
    
    STAY FOCUSED - no generic tech content!""",
    expected_output="Topic-specific research",
    agent=researcher,
    context=[request_analysis]
)

analysis_task = Task(
    name="analyze",
    description="""ANALYZE ONLY THIS EXACT TOPIC: {topic}

    DO NOT write a general technology article!
    
    Analyze SPECIFICALLY:
    1. What makes THIS topic unique?
    2. How does THIS specific thing impact its industry?
    3. What are the SPECIFIC benefits/challenges of THIS topic?
    
    Date: {current_date}
    
    STAY FOCUSED on the exact topic!""",
    expected_output="Topic-specific analysis",
    agent=researcher,
    context=[request_analysis, initial_research]
)

metadata_task = Task(
    name="metadata",
    description="""CREATE METADATA FOR THIS EXACT TOPIC: {topic}

    DO NOT use generic technology titles or descriptions!
    
    1. Title must be SPECIFIC to this topic
    2. Description must focus on THIS exact subject
    3. Tags must be relevant to THIS topic only
    
    Date: {current_date}""",
    expected_output="Topic-specific metadata",
    agent=writer,
    context=[request_analysis, initial_research, analysis_task]
)

writing_task = Task(
    name="write",
    description="""WRITE ONLY ABOUT THIS EXACT TOPIC: {topic}

    DO NOT write a general technology article!
    
    Write SPECIFICALLY about:
    1. What THIS topic/product/service is
    2. How THIS specific thing works
    3. Why THIS topic matters
    4. What makes THIS unique
    
    Date: {current_date}
    
    STAY FOCUSED - no generic content!""",
    expected_output="Topic-specific blog post",
    agent=writer,
    context=[request_analysis, initial_research, analysis_task, metadata_task]
)

save_task = Task(
    name="save",
    description="""Save the blog post about THIS SPECIFIC topic: {topic}

    Verify the content stays focused on the exact topic.""",
    expected_output="Saved topic-specific post",
    agent=writer,
    context=[writing_task],
    tools=[save_blog_post]
)

def main(topic: str) -> dict:
    """
    Run the blog generation workflow
    Args:
        topic (str): Topic to write about
    Returns:
        dict: Results from the workflow
    """
    if not topic:
        raise ValueError("Topic cannot be empty")
    
    # Initialize workflow with agents and tasks
    workflow = PraisonAIAgents(
        agents=[researcher, writer],
        tasks=[request_analysis, initial_research, analysis_task, metadata_task, writing_task, save_task],
        process="sequential",
        verbose=True
    )
    
    # Create simple context with topic
    context = {
        "topic": topic,
        "current_date": current_date
    }
    
    # Run workflow and return result
    return workflow.start(context)

if __name__ == "__main__":
    # Example usage
    topic = "The Future of AI in Healthcare"
    result = main(topic)
    print(f"Generated blog post about: {topic}")
    
    # Or you can run it with a different topic:
    # main("The Future of Large Language Models")
    # main("Building Multi-Agent Systems")
    # etc. 