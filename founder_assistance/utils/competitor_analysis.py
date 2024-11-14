import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found in environment variables")

# Initialize the search tool with API key from environment
search_tool = SerperDevTool()

def create_competitor_analysis_crew(project_title, project_description, idea_description=None):
    """Create a crew AI system for competitor analysis"""
    
    # Create research agent
    competitor_finder = Agent(
        role='Competitor Research Specialist',
        goal='Find and analyze direct and indirect competitors in the market',
        verbose=True,
        model='gpt-4',
        memory=True,
        backstory="An expert in competitive analysis, skilled at identifying and analyzing competitor companies.",
        tools=[search_tool]
    )

    # Create analysis agent
    competitor_analyzer = Agent(
        role='Competitor Strategy Analyst',
        goal='Analyze competitor strategies and extract valuable insights',
        verbose=True,
        memory=True,
        backstory="A specialist in analyzing competitor strategies and business models.",
    )

    # Combine project and idea descriptions for context
    search_context = f"{project_title} - {project_description}"
    if idea_description:
        search_context += f"\nIdea Details: {idea_description}"

    # Create search task
    finder_task = Task(
        description=(
            f"Research competitors for: {search_context}\n"
            "For each competitor found, gather:\n"
            "- Company name and website\n"
            "- Brief description\n"
            "- Business model\n"
            "- Target market\n"
            "- Key products/services\n"
            "- Funding information\n"
            "- Strengths and weaknesses\n"
            "- Market positioning\n"
            "- Unique selling propositions"
        ),
        expected_output='A comprehensive list of competitors with detailed information about each.',
        tools=[search_tool],
        agent=competitor_finder
    )

    # Create analysis task
    analyzer_task = Task(
        description=(
            "Analyze the competitor data and provide insights:\n"
            "1. Competitor Overview:\n"
            "   - Key players in the market\n"
            "   - Market share distribution\n"
            "   - Competitive intensity\n"
            "2. Competitor Strategies:\n"
            "   - Business models\n"
            "   - Marketing approaches\n"
            "   - Technology stacks\n"
            "3. Competitive Advantages:\n"
            "   - Key differentiators\n"
            "   - Unique features\n"
            "   - Value propositions\n"
            "4. Market Gaps:\n"
            "   - Underserved segments\n"
            "   - Opportunity areas\n"
            "Format the output as a structured markdown report with sections for each competitor"
        ),
        expected_output='A detailed markdown report analyzing the competitive landscape.',
        agent=competitor_analyzer
    )

    # Create and return the crew
    crew = Crew(
        agents=[competitor_finder, competitor_analyzer],
        tasks=[finder_task, analyzer_task],
        process=Process.sequential
    )
    
    return crew

def format_competitor_analysis(result):
    """Format the competitor analysis results as markdown"""
    try:
        # If the result is already formatted as markdown, return it
        if isinstance(result, str) and "##" in result:
            return result
            
        # If it's a JSON string, parse it
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                return result

        # Format as markdown
        markdown_output = "# Competitor Analysis Report\n\n"
        
        if isinstance(result, (list, dict)):
            items = result if isinstance(result, list) else [result]
            for item in items:
                if isinstance(item, str):
                    markdown_output += f"{item}\n\n"
                else:
                    for key, value in item.items():
                        markdown_output += f"## {key}\n{value}\n\n"
        else:
            markdown_output += str(result)

        return markdown_output
    except Exception as e:
        return f"Error formatting analysis: {str(e)}"

def generate_competitor_analysis(project):
    """Generate competitor analysis for a project"""
    try:
        # Create the crew
        crew = create_competitor_analysis_crew(
            project.title,
            project.description,
            project.related_idea.description if project.related_idea else None
        )
        
        # Run the analysis
        print("Starting competitor analysis...")
        result = crew.kickoff()
        print("Analysis complete")
        
        # Format and return results
        return format_competitor_analysis(result)
    except Exception as e:
        return f"Error generating analysis: {str(e)}"
