from openai import OpenAI
from django.conf import settings
import json

def augment_idea_with_ai(title, description):
    """
    Use OpenAI to augment the idea description with additional insights and suggestions.
    Returns a JSON structure with the analysis.
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""
    Analyze the following business idea and provide a comprehensive business analysis in JSON format:
    
    Title: {title}
    Description: {description}

    Return the analysis as a valid JSON object with the following structure:

    {{
        "refined_idea": {{
            "enhanced_description": "",
            "unique_selling_proposition": "",
            "core_innovation": ""
        }},
        "market_analysis": {{
            "industry_sector": "",
            "market_size": "",
            "competitive_landscape": "",
            "market_trends": []
        }},
        "business_framework": {{
            "business_model_type": "",
            "revenue_streams": [],
            "cost_structure": [],
            "key_partnerships": [],
            "distribution_channels": []
        }},
        "target_customer": {{
            "segments": [],
            "demographics": {{}},
            "pain_points": [],
            "acquisition_strategy": []
        }},
        "value_proposition": {{
            "core_benefits": [],
            "problem_solution_fit": "",
            "competitive_advantages": [],
            "customer_value": ""
        }},
        "strategic_vision": {{
            "mission": "",
            "vision": "",
            "long_term_goals": [],
            "impact": {{
                "social": "",
                "environmental": ""
            }}
        }},
        "implementation": {{
            "milestones": [],
            "resources_needed": [],
            "risks": [],
            "success_metrics": []
        }},
        "financials": {{
            "initial_investment": "",
            "breakeven_timeline": "",
            "potential_roi": "",
            "funding_requirements": ""
        }}
    }}

    Ensure all values are meaningful and specific to the business idea. The output must be valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced business strategist and startup advisor. You always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response to ensure it's valid JSON
        analysis = json.loads(response.choices[0].message.content)
        
        # Combine original description with analysis
        result = {
            "original_description": description,
            "analysis": analysis
        }
        
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": "Failed to generate valid JSON analysis",
            "original_description": description
        })
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "original_description": description
        })
