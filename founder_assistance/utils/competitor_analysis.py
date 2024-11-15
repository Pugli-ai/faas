import os
import json
import re
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
        print("\nStarting competitor analysis...")
        result = crew.kickoff()
        print("\nAnalysis complete")
        
        # Get raw response
        raw_response = result.raw_output if hasattr(result, 'raw_output') else str(result)
        
        # Extract JSON from the result
        try:
            json_data = extract_json_from_text(raw_response)
            
            # Store both raw and JSON responses in the database
            project.ai_response_raw = raw_response
            project.ai_response_json = json_data
            project.save()
            
            # Print both responses to terminal
            print("\nRaw Response saved to database:")
            print("----------------------------------------")
            print(raw_response)
            print("----------------------------------------")
            print("\nJSON Response saved to database:")
            print("----------------------------------------")
            print(json.dumps(json_data, indent=2))
            print("----------------------------------------\n")
            
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
                        
                        # Print both responses to terminal
                        print("\nRaw Response saved to database:")
                        print("----------------------------------------")
                        print(raw_response)
                        print("----------------------------------------")
                        print("\nJSON Response saved to database:")
                        print("----------------------------------------")
                        print(json.dumps(json_data, indent=2))
                        print("----------------------------------------\n")
                        
                        return json_data
            except:
                pass
                
            # If all parsing attempts fail, store the error and raw response
            error_response = {
                "error": str(e),
                "market_overview": {"key_players": [], "market_share": "", "competitive_intensity": ""},
                "competitor_strategies": {"business_models": [], "marketing_approaches": [], "technology_stacks": []},
                "competitive_advantages": {"differentiators": [], "unique_features": [], "value_propositions": []},
                "market_gaps": {"underserved_segments": [], "opportunities": []}
            }
            project.ai_response_raw = raw_response
            project.ai_response_json = error_response
            project.save()
            
            # Print error state to terminal
            print("\nError processing response:")
            print("----------------------------------------")
            print(f"Error: {str(e)}")
            print("\nRaw Response saved to database:")
            print("----------------------------------------")
            print(raw_response)
            print("----------------------------------------")
            print("\nError Response saved to database:")
            print("----------------------------------------")
            print(json.dumps(error_response, indent=2))
            print("----------------------------------------\n")
            
            return error_response
            
    except Exception as e:
        error_response = {
            "error": str(e),
            "market_overview": {"key_players": [], "market_share": "", "competitive_intensity": ""},
            "competitor_strategies": {"business_models": [], "marketing_approaches": [], "technology_stacks": []},
            "competitive_advantages": {"differentiators": [], "unique_features": [], "value_propositions": []},
            "market_gaps": {"underserved_segments": [], "opportunities": []}
        }
        # Store error state in database
        project.ai_response_raw = str(e)
        project.ai_response_json = error_response
        project.save()
        
        # Print error to terminal
        print("\nError generating analysis:")
        print("----------------------------------------")
        print(f"Error: {str(e)}")
        print("----------------------------------------")
        print("\nError Response saved to database:")
        print("----------------------------------------")
        print(json.dumps(error_response, indent=2))
        print("----------------------------------------\n")
        
        return error_response
