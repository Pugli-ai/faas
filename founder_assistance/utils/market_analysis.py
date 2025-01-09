import os
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Initialize the search tool
search_tool = SerperDevTool()

def create_market_analysis_crew(project_title, project_description, idea_description=None):
    """Create a crew AI system for market analysis"""
    
    # Create market analyst agent
    market_analyst = Agent(
        role='Market Analyst',
        goal='Analyze market opportunities and challenges',
        verbose=True,
        model='gpt-4',
        memory=True,
        backstory="An expert in market analysis and business strategy.",
        tools=[search_tool]
    )

    # Combine project and idea descriptions for context
    analysis_context = f"{project_title} - {project_description}"
    if idea_description:
        analysis_context += f"\nIdea Details: {idea_description}"

    # Create analysis task
    analysis_task = Task(
        description=(
            f"Analyze the market for: {analysis_context}\n"
            "Provide a detailed markdown report covering:\n"
            "# Market Analysis Report\n\n"
            "## Market Overview\n"
            "- Current market size and growth projections\n"
            "- Key market drivers\n\n"
            "## Market Segments\n"
            "- Major customer segments\n"
            "- Growth potential in each segment\n\n"
            "## Market Trends\n"
            "- Current industry trends\n"
            "- Emerging opportunities\n\n"
            "## Market Challenges\n"
            "- Entry barriers\n"
            "- Regulatory considerations\n"
            "- Potential risks\n"
        ),
        expected_output='A detailed markdown report analyzing the market.',
        tools=[search_tool],
        agent=market_analyst
    )

    # Create and return the crew
    crew = Crew(
        agents=[market_analyst],
        tasks=[analysis_task],
        process=Process.sequential
    )
    
    return crew

def format_market_analysis(result):
    """Format the market analysis results as markdown"""
    try:
        # If the result is already formatted as markdown, return it
        if isinstance(result, str) and '#' in result:
            return result
            
        # If it's a JSON string, parse it
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                return result

        # Format as markdown
        markdown_output = "# Market Analysis Report\n\n"
        
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

@retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
def generate_market_analysis(project):
    """Generate market analysis for a project"""
    try:
        # Create the crew
        crew = create_market_analysis_crew(
            project.title,
            project.description,
            project.related_idea.description if project.related_idea else None
        )
        
        # Run the analysis
        logger.info("Starting market analysis...")
        result = crew.kickoff()
        logger.info("Analysis complete")
        
        # Format and return results
        return format_market_analysis(result)
    except Exception as e:
        logger.error("Error in generate_market_analysis", exc_info=True)
        logger.error(f"Exception details: {str(e)}")
        return {
            "error": "Error generating market analysis",
            "details": str(e)
        }
