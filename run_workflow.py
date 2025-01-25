from praisonaiagents import Agent, Task, PraisonAIAgents, Tools
from praisonaiagents.tools import duckduckgo
from database import BlogPostDB
import os
import sys
import json
from datetime import datetime

def run_workflow(query, analysis_depth, api_key):
    # Set API key for the agent
    os.environ["ANTHROPIC_API_KEY"] = api_key

    # Initialize database client
    db = BlogPostDB()

    # LLM Configuration
    llm_config = {
        "model": "claude-3-5-sonnet-20241022",
        "api_key": api_key,
        "temperature": 0.7,
        "max_tokens": 8192
    }

    # Create agents
    research_agent = Agent(
        name="Research Explorer",
        role="Tech Research Friend",
        goal="Find interesting and practical insights about topics that make you go 'huh, that's cool!'",
        backstory="I'm that friend who loves exploring tech and sharing the cool stuff I find - no fancy jargon, just real experiences and useful insights",
        tools=[duckduckgo],
        llm=llm_config
    )

    analysis_agent = Agent(
        name="Pattern Connector",
        role="Insight Builder",
        goal="Connect ideas in unexpected ways and find the real value in what we've learned",
        backstory="I help piece together the puzzle, finding those 'aha!' moments that make complex topics click",
        llm=llm_config
    )

    writing_agent = Agent(
        name="Blog Crafter",
        role="Tech Storyteller",
        goal="Create engaging, conversational blog posts that feel like a coffee chat between friends",
        backstory="I turn tech insights into stories that flow naturally, using a casual but clear style that makes complex topics approachable",
        llm=llm_config
    )

    # Create tasks
    metadata_task = Task(
        name="metadata",
        description=f"""Hey--- let's create something awesome about {query}. I want this to be SUPER valuable for anyone exploring this stuff--- whether you're just starting out with AI, a fellow hacker figuring things out, or someone who's been in the game for a while.

IMPORTANT: Return ONLY this JSON with NO extra text or formatting:
{{
  "title": "A title that captures why this matters",
  "description": "A description that makes people think 'Yeah, I want to know more about this'",
  "tags": ["relevant", "tags", "here"],
  "type": "insight"
}}""",
        expected_output="JSON with title, description, tags, and type",
        agent=writing_agent
    )

    research_task = Task(
        name="research",
        description=f"""Hey--- let's find what makes {query} really interesting. What's the REAL value here? What got me excited enough to write about it?

STYLE GUIDE:
- Write like we're having a coffee chat--- casual but clear
- Use dashes (---) to break up thoughts and add emphasis
- CAPITALIZE things when they're exciting or important
- Share the learning journey--- no expert claims, just real experiences
- Keep it practical--- theory is cool but what can we actually DO with this?
- Be honest about what you're still figuring out
- Connect ideas in unexpected ways

WORD CHOICE:
- Use "explore" instead of "dive into"
- Use "improve" instead of "enhance"
- Use "find" instead of "discover"
- Use "show" instead of "unveil"
- Use "complete" instead of "comprehensive"
- Use "ask" instead of "inquire"
- Use "experience" instead of "journey"
- Use "use" instead of "leverage/utilize"
- Use "help" instead of "facilitate"
- Use "explain" instead of "elucidate"
- Use "combine" instead of "synthesize"
- Use "speed up" instead of "expedite"
- Use "develop" instead of "cultivate"
- Use "express" instead of "articulate"
- Use "spread" instead of "proliferate"
- Use "increase" instead of "augment"
- Use "show" instead of "manifest"
- Use "examine" instead of "scrutinize"
- Use "confirm" instead of "validate"

Remember:
- If something interesting comes up, explore it--- tangents can lead to cool insights
- Share what worked, what didn't, what surprised you
- Keep it real--- we're all learning here
- Connect ideas in unexpected ways
- Make it feel like a conversation between friends exploring tech together""",
        expected_output="Research findings with practical insights and real examples",
        agent=research_agent
    )

    analysis_task = Task(
        name="analyze",
        description=f"""Take our research about {query} and find those 'huh, interesting!' connections. What patterns jump out? What surprised you? Keep it practical--- what can we actually DO with this?

Follow the same style guide:
- Write like we're having a coffee chat--- casual but clear
- Use dashes (---) to break up thoughts and add emphasis
- CAPITALIZE things when they're exciting or important
- Share the learning journey--- no expert claims, just real experiences
- Keep it practical--- theory is cool but what can we actually DO with this?
- Be honest about what you're still figuring out
- Connect ideas in unexpected ways

Avoid these words:
- "dive into" (use "explore")
- "enhance" (use "improve")
- "discover" (use "find")
- "unveil" (use "show")
- "comprehensive" (use "complete")
- "inquire" (use "ask")
- "journey" (use "experience")
- "leverage/utilize" (use "use")
- "facilitate" (use "help")
- "elucidate" (use "explain")
- "synthesize" (use "combine")
- "expedite" (use "speed up")
- "cultivate" (use "develop")
- "articulate" (use "express")
- "proliferate" (use "spread")
- "augment" (use "increase")
- "manifest" (use "show")
- "scrutinize" (use "examine")
- "validate" (use "confirm")""",
        expected_output="Analysis highlighting key patterns and practical applications",
        agent=analysis_agent,
        context=[research_task]
    )

    writing_task = Task(
        name="write",
        description=f"""Time to craft our blog post about {query}! Write this exactly like we're having a coffee chat--- casual but clear, using dashes (---) for emphasis, and CAPITALIZING exciting points.

Here's how I write:
1. Like I'm talking to a friend--- casual but clear
2. Using dashes (---) to break up thoughts and add emphasis
3. CAPITALIZING things when I'm excited
4. Sharing what I'm learning--- no expert claims
5. Keeping it practical--- what can we actually DO?
6. Being honest about what I'm still figuring out
7. Connecting ideas in unexpected ways
8. Breaking rules when it feels natural
9. Mixing short, punchy statements with longer explanations
10. Making things ACTUALLY useful--- no fluff

IMPORTANT WORD CHOICES:
- Use "explore" not "dive into"
- Use "improve" not "enhance"
- Use "find" not "discover"
- Use "show" not "unveil"
- Use "complete" not "comprehensive"
- Use "ask" not "inquire"
- Use "experience" not "journey"
- Use "use" not "leverage/utilize"
- Use "help" not "facilitate"
- Use "explain" not "elucidate"
- Use "combine" not "synthesize"
- Use "speed up" not "expedite"
- Use "develop" not "cultivate"
- Use "express" not "articulate"
- Use "spread" not "proliferate"
- Use "increase" not "augment"
- Use "show" not "manifest"
- Use "examine" not "scrutinize"
- Use "confirm" not "validate"

Remember:
- Share interesting tangents
- Tell the story of what worked and what didn't
- Keep it real--- we're all learning
- Connect ideas in unexpected ways
- Make it feel like friends chatting about tech""",
        expected_output="Engaging blog post in markdown format",
        agent=writing_agent,
        context=[metadata_task, research_task, analysis_task]
    )

    # Initialize workflow
    workflow = PraisonAIAgents(
        agents=[research_agent, analysis_agent, writing_agent],
        tasks=[metadata_task, research_task, analysis_task, writing_task],
        process="sequential",
        verbose=True
    )

    print("🚀 Starting blog creation process...", flush=True)
    result = workflow.start()
    
    try:
        # Get metadata
        metadata = json.loads(metadata_task.result.raw) if metadata_task.result else {}
        
        # Get the final blog post content
        content = writing_task.result.raw if writing_task.result else ""
        
        # Prepare blog post data
        blog_post = {
            "title": metadata.get("title", f"Blog Post about {query}"),
            "description": metadata.get("description", ""),
            "content": content,
            "tags": metadata.get("tags", []),
            "type": metadata.get("type", "insight"),
            "published": False,  # Save as draft
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to database
        print("\n💾 Saving blog post as draft...", flush=True)
        saved_post = db.save_blog_post(blog_post)
        print(f"✅ Blog post saved with ID: {saved_post.get('id')}", flush=True)
        
    except Exception as e:
        print(f"❌ Error saving blog post: {str(e)}", flush=True)
    
    # Print results for each task
    print("\n📝 Metadata:", flush=True)
    if metadata_task.result:
        print(metadata_task.result.raw, flush=True)
    
    print("\n🔍 Research:", flush=True)
    if research_task.result:
        print(research_task.result.raw, flush=True)
    
    print("\n💡 Analysis:", flush=True)
    if analysis_task.result:
        print(analysis_task.result.raw, flush=True)
    
    print("\n✍️ Blog Post:", flush=True)
    if writing_task.result:
        print(writing_task.result.raw, flush=True)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run_workflow.py <query> <analysis_depth> <api_key>")
        sys.exit(1)
    
    query = sys.argv[1]
    analysis_depth = sys.argv[2]
    api_key = sys.argv[3]
    
    run_workflow(query, analysis_depth, api_key) 