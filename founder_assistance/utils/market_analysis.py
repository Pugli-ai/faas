import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import logging

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

def create_market_analysis_crew(project_title, project_description, idea_description=None):
    """Create a crew AI system for market analysis"""
    
    # Create research agent
    market_researcher = Agent(
        role='Market Research Specialist',
        goal='Analyze market size, trends, and opportunities for the business',
        verbose=True,
        model='gpt-4',  # Fixed model name
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
            "Analyze the following aspects and format as JSON:\n"
            "1. Market Size and Growth:\n"
            "   - Current market size (as a numeric value with currency)\n"
            "   - Growth projections (as a percentage)\n"
            "   - Key growth drivers (as a list)\n"
            "2. Market Segments:\n"
            "   - List of segments\n"
            "   - Growth potential for each segment\n"
            "3. Market Trends:\n"
            "   - Current trends\n"
            "   - Emerging opportunities\n"
            "4. Market Challenges:\n"
            "   - Entry barriers\n"
            "   - Regulatory challenges\n"
            "   - Market risks\n"
            "\nEnsure all numeric values are provided as numbers without text descriptions."
        ),
        expected_output='A comprehensive market analysis with key metrics and trends in JSON format.',
        tools=[search_tool],
        agent=market_researcher
    )

    # Create analysis task
    analyzer_task = Task(
        description=(
            "Analyze the market data and provide insights in JSON format with the following structure:\n"
            "{\n"
            '  "market_size_and_growth": {\n'
            '    "current_size": "50000000000",\n'
            '    "growth_projections": "15",\n'
            '    "key_drivers": ["driver1", "driver2"]\n'
            "  },\n"
            '  "market_segments": {\n'
            '    "segments": ["segment1", "segment2"],\n'
            '    "growth_potential": {"segment1": "20", "segment2": "15"}\n'
            "  },\n"
            '  "market_trends": {\n'
            '    "current_trends": ["trend1", "trend2"],\n'
            '    "emerging_opportunities": ["opportunity1", "opportunity2"]\n'
            "  },\n"
            '  "market_challenges": {\n'
            '    "entry_barriers": ["barrier1", "barrier2"],\n'
            '    "regulatory_challenges": ["challenge1", "challenge2"],\n'
            '    "risks": ["risk1", "risk2"]\n'
            "  }\n"
            "}\n"
            "\nEnsure all numeric values are clean numbers without currency symbols or text."
        ),
        expected_output='A detailed JSON object containing the market analysis.',
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
    """Format the market analysis results as JSON"""
    try:
        print("\nRaw Analysis Result:")
        print("-------------------")
        print(result)
        print("-------------------\n")

        # If the result is already a JSON string, parse it
        if isinstance(result, str):
            try:
                # Try to extract JSON from markdown code block if present
                if "```json" in result:
                    logger.info("Extracting JSON from markdown code block")
                    json_str = result.split("```json")[1].split("```")[0].strip()
                    parsed_result = json.loads(json_str)
                else:
                    logger.info("Attempting to parse raw JSON string")
                    parsed_result = json.loads(result)
                
                if isinstance(parsed_result, dict):
                    # Clean up the data structure if needed
                    if "market_analysis" in parsed_result:
                        parsed_result = parsed_result["market_analysis"]
                    
                    print("\nParsed JSON Result:")
                    print("-------------------")
                    print(json.dumps(parsed_result, indent=2))
                    print("-------------------\n")
                    
                    return parsed_result, json.dumps(parsed_result, indent=2)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                # If it's not valid JSON, convert the markdown/text to JSON structure
                sections = {}
                current_section = None
                content = []
                
                for line in result.split('\n'):
                    if line.startswith('##'):
                        if current_section and content:
                            sections[current_section] = '\n'.join(content).strip()
                            content = []
                        current_section = line.replace('#', '').strip()
                    elif line.strip() and current_section:
                        content.append(line.strip())
                
                if current_section and content:
                    sections[current_section] = '\n'.join(content).strip()
                
                print("\nConverted Markdown to JSON:")
                print("-------------------------")
                print(json.dumps(sections, indent=2))
                print("-------------------------\n")
                
                return sections, json.dumps(sections, indent=2)

        # If it's already a dict, format it as JSON
        if isinstance(result, dict):
            return result, json.dumps(result, indent=2)

        # If it's a list, convert to dict and format as JSON
        if isinstance(result, list):
            formatted = {"market_analysis": result}
            return formatted, json.dumps(formatted, indent=2)

        # Fallback for other types
        formatted = {"market_analysis": str(result)}
        return formatted, json.dumps(formatted, indent=2)

    except Exception as e:
        logger.error(f"Error formatting analysis: {str(e)}")
        error_result = {"error": f"Error formatting analysis: {str(e)}"}
        return error_result, json.dumps(error_result, indent=2)

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
        print("\nStarting market analysis...")
        logger.info(f"Starting market analysis for project: {project.title}")
        result = crew.kickoff()
        print("Analysis complete")
        logger.info("Market analysis complete")
        
        # Format results and get both dict and string versions
        json_dict, json_str = format_market_analysis(result)
        
        # Store both raw and JSON responses in the project
        project.ai_response_raw = result
        project.ai_response_json = json_dict
        project.save()
        logger.info("Analysis results saved to project")
        
        # Return the formatted string for display
        return json_str
        
    except Exception as e:
        logger.error(f"Error generating analysis: {str(e)}")
        error_result = {"error": f"Error generating analysis: {str(e)}"}
        return json.dumps(error_result, indent=2)
