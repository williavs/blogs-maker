from praisonaiagents import Agent, Task, PraisonAIAgents, Tools
import os
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

# Get current date for research context
current_date = datetime.now().strftime("%B %Y")  # e.g., "March 2024"

# Define output structures
class ResearchFindings(BaseModel):
    main_trends: List[str]
    key_developments: List[Dict[str, str]]
    impact_analysis: str
    sources: List[Dict[str, str]]

class BlogMetadata(BaseModel):
    title: str
    description: str
    tags: List[str]
    type: str

class BlogPost(BaseModel):
    metadata: BlogMetadata
    introduction: str
    main_content: List[str]
    conclusion: str
    references: List[str]

# LLM Configuration
llm_config = {
    "model": "claude-3-5-sonnet-20241022",
    "api_key": os.getenv("ANTHROPIC_API_KEY"),
    "temperature": 0.7,
    "max_tokens": 8192
}

def save_blog_post(content: str) -> str:
    """Save the blog post to a markdown file"""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/ai_blog_post.md", "w") as f:
        f.write(content)
    return "Blog post saved successfully"

# Create Research Agent
researcher = Agent(
    name="Researcher",
    role="Tech Explorer",
    goal="Find the most interesting and valuable insights about our topic",
    backstory="""You're a curious tech explorer who loves finding those 'aha!' moments that make complex topics click. 
    You don't just gather info- - - you find the stories, examples, and unexpected connections that make things interesting.""",
    verbose=True,
    llm=llm_config,
    markdown=True,
    tools=[Tools.internet_search],
    min_reflect=2,
    max_reflect=4
)

# Create Writer Agent
writer = Agent(
    name="Writer",
    role="Tech Storyteller",
    goal="Create content that makes people think 'wow, I never thought about it that way!'",
    backstory="""You're a tech enthusiast who loves making complex topics feel like an exciting coffee chat between friends.
    You write like you're sharing cool discoveries, not lecturing- - - keeping it casual but clear, with plenty of real examples.AI SOUNDING WORKDS TO AVOID AT ALL COSTS

Dive – Instead, go for "delve into" or "explore."
Dazzling – Opt for "impressive" or "striking."
Enhance – Instead, go for "improve" or "boost."
Discover – Use "find" instead.
Divine – Choose "predict" or "foresee."
Unveiling – Use "revealing" or "showing."
Comprehensive – Opt for "complete" or "detailed."
Inquire – Go with "ask."
Discern – Choose "identify" or "recognize."
Vigilance – Use "alertness" or "watchfulness."
In conclusion – Instead, say "to sum up" or "finally."
Embark – Use "begin" or "start."
Journey – Opt for "trip" or "experience."
Elevate – Go with "raise" or "lift."
Evolution – Choose "development" or "progress."
Shift – Use "change" or "move."
Prevailing – Go with "common" or "widespread."
Unleash – Opt for "release" or "let loose."
Let us embark on a journey of – Say "let's begin exploring" or "start our exploration of."
Facilitate – Instead, use "help" or "aid."
Unveil – Go with "reveal" or "show."
Elucidate – Opt for "explain" or "clarify."
Leverage – Instead, go for "use" or "utilize."
Utilize – Opt for "use" or "employ."
Strategize – Instead, say "plan" or "accomplish."
Innovate – Use "create" or "invent."
Synthesize – Go with "combine" or "blend."
Expedite – Opt for "speed up" or "accelerate."
Cultivate – Use "develop" or "foster."
Delineate – Choose "outline" or "describe."
Articulate – Instead, say "express" or "state."
Navigate – Go with "guide" or "direct."
Proliferate – Use "expand" or "spread."
Augment – Opt for "increase."
Diversify – Instead, go for "broaden" or "vary."
Conceptualize – Use "envision" or "imagine."
Manifest – Go with "show" or "demonstrate."
Ponder – Opt for "think about" or "consider."
Scrutinize – Use "examine" or "inspect."
Elicit – Choose "bring out" or "provoke."
Enumerate – Instead, say "list" or "count."
Empower – Go with "enable" or "strengthen."
Disseminate – Use "spread" or "distribute."
Culminate – Opt for "conclude" or "end."
Harness – Instead, go for "control" or "use."
Perceive – Use "see" or "notice."
Actualize – Go with "realize" or "achieve."
Harmonize – Opt for "align" or "coordinate."
Accentuate – Use "highlight" or "emphasize."
Illuminate – Instead, say "light up" or "clarify."
Reiterate – Go with "repeat" or "restate."
Mitigate – Use "reduce" or "alleviate."
Galvanize – Opt for "inspire" or "motivate."
Transcend – Instead, go for "surpass" or "exceed."
Advocate – Use "support" or "promote."
Exemplify – Go with "illustrate" or "represent."
Validate – Opt for "confirm" or "verify."
Consolidate – Instead, say "combine" or "unite."
Mediate – Use "intervene" or "arbitrate."
Conjecture – Go with "guess" or "speculate."
Ascertain – Opt for "find out" or "determine."
Contextualize – Instead, use "place in context" or "relate."
Amplify – Go with "increase" or "magnify."
Elaborate – Use "expand on" or "explain."
Synergize – Instead, say "combine" or "work together."
Correlate – Use "relate" or "associate."
Quantify – Go with "measure" or "calculate."
Extrapolate – Use "infer" or "predict."
Substantiate – Opt for "prove" or "validate."
Deconstruct – Use "break down" or "analyze."
Engage – Go with "involve" or "participate."
Envision – Opt for "imagine" or "foresee."
Speculate – Use "guess" or "hypothesize."
Expound – Go with "explain" or "elaborate."
Interpret – Opt for "explain" or "translate."
Juxtapose – Instead, say "compare" or "contrast."
Encompass – Use "include" or "cover."
Revitalize – Go with "rejuvenate" or "refresh."
Assimilate – Opt for "integrate" or "absorb."
Collaborate – Instead, go for "work together" or "cooperate."
Deliberate – Use "consider" or "think over."
Aggregate – Go with "combine" or "total."
Fortify – Use "strengthen" or "reinforce."
Acclimate – Opt for "adapt" or "adjust."
Differentiate – Instead, say "distinguish" or "separate."
Reconcile – Go with "resolve" or "settle."
Decipher – Use "decode" or "figure out."
Theorize – Opt for "speculate" or "hypothesize."
Alleviate – Instead, go for "ease" or "reduce."
Align – Use "arrange" or "line up."
Dissect – Go with "analyze" or "examine."
Formulate – Opt for "develop" or "create."
Evaluate – Instead, say "assess" or "review."
Converge – Use "meet" or "join."
Introspect – Go with "reflect" or "contemplate."
Scaffold – Opt for "support" or "framework."
Emulate – Use "imitate" or "copy."
Reconfigure – Instead, go for "rearrange" or "adjust."
Incubate – Use "develop" or "nurture."
Permeate – Go with "spread through" or "pervade."
Benchmark – Opt for "standard" or "measure."
Calibrate – Use "adjust" or "fine-tune."
Recapitulate – Go with "summarize" or "recap."
Orchestrate – Opt for "arrange" or "coordinate."
Retrofit – Instead, say "update" or "modernize."
Transmute – Use "transform" or "change.""",
    llm=llm_config,
    markdown=True,
    tools=[save_blog_post]
)

# Define Research Tasks
initial_research = Task(
    name="initial_research",
    description="""Hey- - - let's find what makes {topic} SUPER interesting! I want you to:

    Focus on the LATEST developments (as of {current_date}):
    1. Find the core concepts we NEED to understand
    2. Look for recent examples of how people are using this RIGHT NOW
    3. Dig up those "wait, what?" moments that make you think differently
    4. Find recent stories of what worked, what didn't, and why
    5. Spot connections to other cool stuff people might not expect
    6. Show where this is heading- - - the possibilities that get people excited

    Make sure to include recent developments and current state of the art!
    Don't just list facts- - - find the stuff that makes someone go "aha!"
    If you spot something interesting, chase it- - - tangents often lead to the best insights!""",
    expected_output="A collection of the most interesting findings, stories, and connections that make this topic exciting",
    agent=researcher,
    output_json=ResearchFindings
)

analysis_task = Task(
    name="analysis",
    description="""Alright, let's break down what makes {topic} REALLY valuable (as of {current_date}):

    1. What's the ACTUAL cool stuff happening RIGHT NOW? The things that made you go "wow"?
    2. Where are the unexpected connections in today's tech landscape?
    3. What current problems does this help solve?
    4. What are people still figuring out in {current_date}?
    5. What possibilities get you excited about the immediate future?

    Remember- - - we want those "I never thought about it that way" moments!
    Focus on what's happening NOW and what's coming NEXT!""",
    expected_output="An analysis that reveals why this topic matters and what makes it exciting",
    agent=researcher,
    context=[initial_research]
)

metadata_task = Task(
    name="metadata",
    description="""Create metadata that makes people think "Yeah, I want to know more about {topic}!"
    Focus on what makes this topic exciting and valuable.
    
    Return ONLY this JSON structure with NO additional text:
    {{
        "title": "A title that captures why {topic} matters",
        "description": "A description that makes people think 'Yeah, I want to know more about this'",
        "tags": ["relevant", "tags", "here"],
        "type": "insight"
    }}""",
    expected_output="Blog post metadata in JSON format",
    agent=writer,
    context=[initial_research, analysis_task],
    output_json=BlogMetadata
)

writing_task = Task(
    name="writing",
    description="""Let's create something AWESOME about {topic}! Make it valuable for everyone- - - 
    whether they're just starting out, a fellow hacker figuring things out, or someone who's been in the game for a while.

    Remember:
    - Write like we're having a coffee chat- - - casual but clear
    - Use dashes (- - -) to break up thoughts and add emphasis
    - CAPITALIZE things when they're exciting or important
    - Share the learning journey- - - no expert claims, just real experiences
    - Keep it practical- - - theory is cool but what can we actually DO with this?
    - Be honest about what you're still figuring out
    - Connect ideas in unexpected ways

    Structure it naturally, but make sure we cover:
    1. An intro that hooks people in
    2. The core concepts they need to know
    3. The interesting stuff you found
    4. Real examples and stories
    5. Unexpected connections
    6. What's possible and what's next

    Make it feel like a friend sharing cool discoveries!""",
    expected_output="An engaging blog post that makes complex topics feel accessible and exciting",
    agent=writer,
    context=[initial_research, analysis_task, metadata_task],
    output_json=BlogPost
)

save_task = Task(
    name="save_output",
    description="Save the final blog post as a markdown file",
    expected_output="Confirmation of saved file",
    agent=writer,
    context=[writing_task],
    tools=[save_blog_post],
    output_file='outputs/ai_blog_post.md',
    create_directory=True
)

def update_task_progress(task_results, task_id, status, step_name=None, step_result=None):
    """Update the task progress in the shared task_results dictionary"""
    if step_name and step_result:
        task_results[task_id]["steps"].append({
            "name": step_name,
            "result": step_result
        })
    task_results[task_id]["status"] = status

def main(topic, length="standard"):
    """
    Main function to run the blog generation workflow.
    Args:
        topic (str): The topic to write about
        length (str): The desired length of the blog post ("quick", "standard", "deep", or "complete")
    """
    # Update writing task description with length-specific instructions
    length_instructions = {
        'quick': 'Keep this focused and punchy- - - around 500-750 words. Hit the key points that\'ll make someone go "aha!"',
        'standard': 'Give us a solid exploration- - - about 1000-1500 words. Enough space to really share some good insights.',
        'deep': 'This is a deep exploration- - - 2500-3000 words. Really explore the nuances and share detailed examples.',
        'complete': 'This is a complete guide- - - 4000-5000 words. Cover everything someone needs to know, from fundamentals to advanced concepts.'
    }

    # Update the writing task description with length control
    writing_task.description = writing_task.description + f"\n\nLength Control: {length_instructions[length]}"

    # Create and start the agent workflow
    agents = PraisonAIAgents(
        agents=[researcher, writer],
        tasks=[initial_research, analysis_task, metadata_task, writing_task, save_task],
        process="sequential",
        verbose=True
    )
    
    result = agents.start({"topic": topic})
    return result

if __name__ == "__main__":
    main("AI Developments in 2024")
    
    # Or you can run it with a different topic:
    # main("The Future of Large Language Models")
    # main("Building Multi-Agent Systems")
    # etc. 