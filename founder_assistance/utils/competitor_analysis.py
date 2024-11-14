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
        model='gpt-4o',
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

    # Create search task with JSON structure requirement
    finder_task = Task(
        description=(
            f"Research competitors for: {search_context}\n"
            "Return the data as a JSON object with the following structure for each competitor and do not include any trailing text:\n"
            "{\n"
            '  "competitors": [\n'
            "    {\n"
            '      "name": "Company name",\n'
            '      "website": "Company website",\n'
            '      "description": "Brief description",\n'
            '      "business_model": "Business model details",\n'
            '      "target_market": "Target market details",\n'
            '      "products_services": ["Key product 1", "Key service 1"],\n'
            '      "funding": "Funding information",\n'
            '      "strengths": ["Strength 1", "Strength 2"],\n'
            '      "weaknesses": ["Weakness 1", "Weakness 2"],\n'
            '      "market_position": "Market positioning details",\n'
            '      "unique_selling_points": ["USP 1", "USP 2"]\n'
            "    }\n"
            "  ]\n"
            "}"
        ),
        expected_output='A JSON object containing detailed competitor information',
        tools=[search_tool],
        agent=competitor_finder
    )

    # Create analysis task with JSON structure requirement
    analyzer_task = Task(
        description=(
            "Analyze the competitor data and provide insights in the following JSON structure:\n"
            "{\n"
            '  "market_overview": {\n'
            '    "key_players": ["Player 1", "Player 2"],\n'
            '    "market_share": "Distribution details",\n'
            '    "competitive_intensity": "Analysis of competition level"\n'
            "  },\n"
            '  "competitor_strategies": {\n'
            '    "business_models": ["Model 1", "Model 2"],\n'
            '    "marketing_approaches": ["Approach 1", "Approach 2"],\n'
            '    "technology_stacks": ["Tech 1", "Tech 2"]\n'
            "  },\n"
            '  "competitive_advantages": {\n'
            '    "differentiators": ["Diff 1", "Diff 2"],\n'
            '    "unique_features": ["Feature 1", "Feature 2"],\n'
            '    "value_propositions": ["Value 1", "Value 2"]\n'
            "  },\n"
            '  "market_gaps": {\n'
            '    "underserved_segments": ["Segment 1", "Segment 2"],\n'
            '    "opportunities": ["Opportunity 1", "Opportunity 2"]\n'
            "  }\n"
            "}"
        ),
        expected_output='A JSON object containing market analysis insights',
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
    """Format the competitor analysis results as JSON"""
    try:
        # If the result is already a JSON string, parse it
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                # If it's not valid JSON, try to extract JSON-like content
                import re
                json_pattern = r'\{[\s\S]*\}'
                matches = re.findall(json_pattern, result)
                if matches:
                    try:
                        result = json.loads(matches[0])
                    except json.JSONDecodeError:
                        # If still not valid JSON, create a basic structure
                        result = {"raw_response": result}
                else:
                    result = {"raw_response": result}

        # Ensure we have a proper dictionary
        if not isinstance(result, dict):
            result = {"raw_response": str(result)}

        return {
            "raw_response": str(result),  # Store original response
            "structured_data": result if isinstance(result, dict) else {}  # Store structured data
        }
    except Exception as e:
        return {
            "error": str(e),
            "raw_response": str(result)
        }

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
        
        # Format results
        formatted_result = format_competitor_analysis(result)
        
        # Update project with results
        project.ai_response_raw = formatted_result.get("raw_response", "")
        project.ai_response_json = formatted_result.get("structured_data", {})
        project.save()
        
        return formatted_result
    except Exception as e:
        error_response = {
            "error": str(e),
            "raw_response": None,
            "structured_data": None
        }
        return error_response
