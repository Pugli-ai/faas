import os
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

# Initialize the search tool
search_tool = SerperDevTool()

def create_competitor_search_crew(project_title, project_description, idea_description=None):
    """Create a crew AI system for searching competitor information"""
    
    # Create research agent
    competitor_finder = Agent(
        role='Startup Competitor Researcher',
        goal='Find and analyze startups with similar products, services, or business models',
        verbose=True,
        model='gpt-4',
        memory=True,
        backstory="An expert in startup research and competitive analysis, skilled at identifying similar companies and their key metrics.",
        tools=[search_tool]
    )

    # Create analysis agent
    competitor_analyzer = Agent(
        role='Competitor Data Analyzer',
        goal='Analyze and verify competitor information, extracting key business insights',
        verbose=True,
        memory=True,
        backstory="A specialist in analyzing startup data and extracting valuable business insights and metrics.",
    )

    # Combine project and idea descriptions for context
    search_context = f"{project_title} - {project_description}"
    if idea_description:
        search_context += f"\nIdea Details: {idea_description}"

    # Create search task
    finder_task = Task(
        description=(
            f"Research competitors for: {search_context}\n"
            "Find startups and companies with similar:\n"
            "- Products or services\n"
            "- Target market\n"
            "- Business model\n"
            "For each company found, gather:\n"
            "- Company name and website\n"
            "- Brief description\n"
            "- Funding information if available\n"
            "- Key differentiators\n"
            "- Target market"
        ),
        expected_output='A list of competitor companies with their key information and metrics.',
        tools=[search_tool],
        agent=competitor_finder
    )

    # Create analysis task
    analyzer_task = Task(
        description=(
            "Analyze the competitor data and provide insights:\n"
            "1. Verify each competitor's information\n"
            "2. Extract key business metrics and insights\n"
            "3. Identify market positioning and unique value propositions\n"
            "4. Analyze funding patterns and business model similarities\n"
            "Format the output as a structured markdown report with sections for each competitor"
        ),
        expected_output='A detailed markdown report analyzing the competitors and their key metrics.',
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

@retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
def generate_competitor_analysis(project):
    """Generate competitor analysis for a project"""
    try:
        # Create the crew
        crew = create_competitor_search_crew(
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
