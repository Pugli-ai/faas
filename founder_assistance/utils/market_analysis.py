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

def create_market_analysis_crew(project_title, project_description, idea_description=None):
    """Create a crew AI system for market analysis"""
    
    # Create research agent
    market_researcher = Agent(
        role='Market Research Specialist',
        goal='Analyze market size, trends, and opportunities for the business',
        verbose=True,
        model='gpt-4',
        memory=True,
        backstory="An expert in market research and analysis, skilled at identifying market opportunities and trends.",
        tools=[search_tool]
    )

    # Create analysis agent
    market_analyzer = Agent(
        role='Market Data Analyzer',
        goal='Analyze market data and extract valuable insights',
        verbose=True,
        memory=True,
        backstory="A specialist in analyzing market data and extracting actionable business insights.",
    )

    # Combine project and idea descriptions for context
    search_context = f"{project_title} - {project_description}"
    if idea_description:
        search_context += f"\nIdea Details: {idea_description}"

    # Create search task
    researcher_task = Task(
        description=(
            f"Research market details for: {search_context}\n"
            "Analyze the following aspects:\n"
            "- Total market size and growth rate\n"
            "- Market segments and their characteristics\n"
            "- Key market trends and drivers\n"
            "- Market challenges and opportunities\n"
            "- Regulatory environment\n"
            "- Geographic distribution\n"
            "- Customer behavior and preferences"
        ),
        expected_output='A comprehensive market analysis with key metrics and trends.',
        tools=[search_tool],
        agent=market_researcher
    )

    # Create analysis task
    analyzer_task = Task(
        description=(
            "Analyze the market data and provide insights:\n"
            "1. Market Size and Growth:\n"
            "   - Current market size\n"
            "   - Growth projections\n"
            "   - Key growth drivers\n"
            "2. Market Segments:\n"
            "   - Major segments and their sizes\n"
            "   - Growth potential by segment\n"
            "3. Market Trends:\n"
            "   - Current trends\n"
            "   - Emerging opportunities\n"
            "4. Market Challenges:\n"
            "   - Entry barriers\n"
            "   - Regulatory challenges\n"
            "   - Market risks\n"
            "Format the output as a structured markdown report"
        ),
        expected_output='A detailed markdown report analyzing the market landscape.',
        agent=market_analyzer
    )

    # Create and return the crew
    crew = Crew(
        agents=[market_researcher, market_analyzer],
        tasks=[researcher_task, analyzer_task],
        process=Process.sequential
    )
    
    return crew

def format_market_analysis(result):
    """Format the market analysis results as markdown"""
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
        print("Starting market analysis...")
        result = crew.kickoff()
        print("Analysis complete")
        
        # Format and return results
        return format_market_analysis(result)
    except Exception as e:
        return f"Error generating analysis: {str(e)}"
