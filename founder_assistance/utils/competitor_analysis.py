import os
import json
import re
import logging
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found in environment variables")

# Initialize the search tool with API key from environment
search_tool = SerperDevTool()

def extract_json_from_text(text):
    """Extract valid JSON from text, handling CrewAI response format"""
    # Convert CrewOutput to string if needed
    if hasattr(text, 'raw_output'):
        text = text.raw_output
    elif not isinstance(text, str):
        text = str(text)
    
    # First try to parse the entire text as JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict) and any(key in data for key in ['market_overview', 'competitors']):
            return data
    except json.JSONDecodeError:
        pass
    
    # If that fails, try to find JSON objects in the text
    json_pattern = r'\{[\s\S]*?\}'
    matches = re.finditer(json_pattern, text)
    
    # Try each match to find valid JSON
    for match in matches:
        try:
            json_str = match.group()
            data = json.loads(json_str)
            # Check if this is the analysis JSON we want
            if isinstance(data, dict) and any(key in data for key in ['market_overview', 'competitors']):
                return data
        except json.JSONDecodeError:
            continue
    
    raise ValueError("No valid analysis JSON found in the response")

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

    # Create search task with JSON structure requirement
    finder_task = Task(
        description=(
            f"Research competitors for: {search_context}\n"
            "Return ONLY a JSON object with the following structure for each competitor. Do not include any text before or after the JSON:\n"
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
        expected_output='ONLY the JSON object containing competitor information, with no additional text',
        tools=[search_tool],
        agent=competitor_finder
    )

    # Create analysis task with JSON structure requirement
    analyzer_task = Task(
        description=(
            "Analyze the competitor data and provide ONLY a JSON object with the following structure. Do not include any text before or after the JSON:\n"
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
        expected_output='ONLY the JSON object containing market analysis insights, with no additional text',
        agent=competitor_analyzer
    )

    # Create and return the crew
    crew = Crew(
        agents=[competitor_finder, competitor_analyzer],
        tasks=[finder_task, analyzer_task],
        process=Process.sequential
    )
    
    return crew

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
        logger.info("Starting competitor analysis for project: %s", project.title)
        result = crew.kickoff()
        logger.info("Analysis complete for project: %s", project.title)
        
        # Get raw response
        raw_response = result.raw_output if hasattr(result, 'raw_output') else str(result)
        
        # Extract JSON from the result
        try:
            json_data = extract_json_from_text(raw_response)
            
            # Store both raw and JSON responses in the database
            project.ai_response_raw = raw_response
            project.ai_response_json = json_data
            project.save()
            
            logger.info("Successfully saved analysis data for project: %s", project.title)
            return json_data
            
        except Exception as e:
            # Try to parse raw response directly if it looks like JSON
            try:
                if raw_response.strip().startswith('{') and raw_response.strip().endswith('}'):
                    json_data = json.loads(raw_response)
                    if isinstance(json_data, dict) and any(key in json_data for key in ['market_overview', 'competitors']):
                        # Store both raw and JSON responses in the database
                        project.ai_response_raw = raw_response
                        project.ai_response_json = json_data
                        project.save()
                        
                        logger.info("Successfully saved analysis data for project: %s (fallback parsing)", project.title)
                        return json_data
            except:
                pass
                
            # If all parsing attempts fail, return error response
            logger.error("Failed to parse analysis response for project %s: %s", project.title, str(e))
            error_response = {
                "error": "Failed to process market analysis data. Please try again.",
                "details": str(e)
            }
            project.ai_response_raw = raw_response
            project.ai_response_json = error_response
            project.save()
            
            return error_response
            
    except Exception as e:
        logger.error("Failed to generate analysis for project %s: %s", project.title, str(e))
        error_response = {
            "error": "Failed to generate market analysis. Please try again.",
            "details": str(e)
        }
        project.ai_response_raw = str(e)
        project.ai_response_json = error_response
        project.save()
        
        return error_response
