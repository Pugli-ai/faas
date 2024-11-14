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
    """Extract valid JSON from text, handling potential markdown or extra text"""
    # Remove markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1]
    if "```" in text:
        text = text.split("```")[0]
    
    # Try to find JSON object in the text
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # Try each match until we find valid JSON
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    raise ValueError("No valid JSON found in the text")

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

def format_competitor_analysis(result):
    """Format the competitor analysis results as clean JSON"""
    try:
        # Store the original result as raw response
        raw_response = str(result)
        
        # If the result is already a dictionary, use it directly
        if isinstance(result, dict):
            return raw_response, result
            
        # Try to extract and parse JSON from the text
        try:
            cleaned_json = extract_json_from_text(result)
            # Merge competitor data with market analysis if both are present
            if isinstance(cleaned_json, dict):
                if 'competitors' in cleaned_json or 'market_overview' in cleaned_json:
                    return raw_response, cleaned_json
                else:
                    return raw_response, {
                        "error": "Invalid JSON structure",
                        "market_overview": {"key_players": [], "market_share": "", "competitive_intensity": ""},
                        "competitor_strategies": {"business_models": [], "marketing_approaches": [], "technology_stacks": []},
                        "competitive_advantages": {"differentiators": [], "unique_features": [], "value_propositions": []},
                        "market_gaps": {"underserved_segments": [], "opportunities": []}
                    }
        except ValueError:
            return raw_response, {
                "error": "Could not parse valid JSON from response",
                "market_overview": {"key_players": [], "market_share": "", "competitive_intensity": ""},
                "competitor_strategies": {"business_models": [], "marketing_approaches": [], "technology_stacks": []},
                "competitive_advantages": {"differentiators": [], "unique_features": [], "value_propositions": []},
                "market_gaps": {"underserved_segments": [], "opportunities": []}
            }
            
    except Exception as e:
        return str(result), {
            "error": str(e),
            "market_overview": {"key_players": [], "market_share": "", "competitive_intensity": ""},
            "competitor_strategies": {"business_models": [], "marketing_approaches": [], "technology_stacks": []},
            "competitive_advantages": {"differentiators": [], "unique_features": [], "value_propositions": []},
            "market_gaps": {"underserved_segments": [], "opportunities": []}
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
        
        # Format results to ensure clean JSON and get both raw and structured responses
        raw_response, formatted_json = format_competitor_analysis(result)
        
        # Store both raw and JSON responses in the database
        project.ai_response_raw = raw_response
        project.ai_response_json = formatted_json
        project.save()
        
        return formatted_json
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
        return error_response
