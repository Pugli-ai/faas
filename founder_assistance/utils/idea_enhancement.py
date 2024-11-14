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
    As an experienced startup advisor, analyze this business idea and provide a comprehensive analysis. For each section, provide detailed, narrative responses that paint a complete picture of the business opportunity.

    Title: {title}
    Description: {description}

    Provide your analysis as a JSON object with the following structure and guidelines:

    {{
        "refined_idea": {{
            "enhanced_description": "Expand the original idea into a compelling narrative that clearly articulates the solution. Include the core technology or methodology, how it works, and its primary value drivers. Write this as a cohesive story that would engage potential investors.",
            "unique_selling_proposition": "Craft a powerful statement that captures why this solution is revolutionary. Focus on the intersection of market need and your unique approach. Explain what makes this truly different from existing solutions.",
            "core_innovation": "Describe the fundamental breakthrough or innovative approach that makes this idea possible. Explain the technical or methodological innovation in clear terms that highlight its significance."
        }},
        "market_analysis": {{
            "industry_sector": "Name the primary sector and any overlapping industries this operates in. Explain why this categorization matters for the business.",
            "market_size": "Provide a detailed market size analysis including TAM (Total Addressable Market), SAM (Serviceable Addressable Market), and SOM (Serviceable Obtainable Market). Include relevant growth trends and market dynamics.",
            "competitive_landscape": "Paint a comprehensive picture of the competitive environment. Include direct and indirect competitors, their strengths and weaknesses, and how this solution creates a unique position.",
            "market_trends": ["Identify key market trends that will impact this business. For each trend, explain its significance and how it creates opportunities or challenges."]
        }},
        "business_framework": {{
            "business_model_type": "Describe the core business model and explain why it's the most effective approach for this idea. Include how it enables scalability and profitability.",
            "revenue_streams": ["Detail each revenue stream, explaining how it works, its potential scale, and why customers would be willing to pay."],
            "cost_structure": ["Analyze major cost categories, explaining their strategic importance and how they scale with growth."],
            "key_partnerships": ["Identify critical partnerships needed, explaining each partner's role in enabling success."],
            "distribution_channels": ["Describe each channel's role in reaching customers, including why it's effective for this specific business."]
        }},
        "target_customer": {{
            "segments": ["Define each customer segment with rich detail about their characteristics, needs, and behaviors."],
            "demographics": {{"key": "value"}},
            "pain_points": ["Describe each pain point in detail, explaining its impact on customers and why current solutions fall short."],
            "acquisition_strategy": ["Detail specific strategies for reaching and converting each customer segment."]
        }},
        "value_proposition": {{
            "core_benefits": ["Explain each benefit in terms of customer value and competitive advantage."],
            "problem_solution_fit": "Provide a detailed analysis of how your solution addresses specific customer problems. Include real-world scenarios that demonstrate the fit.",
            "competitive_advantages": ["Detail each advantage and explain how it creates sustainable differentiation."],
            "customer_value": "Articulate the full value delivered to customers, including both tangible and intangible benefits. Explain how this translates to customer willingness to pay."
        }},
        "strategic_vision": {{
            "mission": "Craft a compelling mission statement that captures the core purpose and impact of the business.",
            "vision": "Paint a picture of the future state this business aims to create. Include both near-term and long-term transformation.",
            "long_term_goals": ["Define ambitious but achievable goals that align with the mission and vision."],
            "impact": {{
                "social": "Describe the positive social changes this business will create. Include both direct and indirect benefits to society.",
                "environmental": "Explain the environmental implications and any sustainability initiatives built into the business model."
            }}
        }},
        "implementation": {{
            "milestones": ["Define key milestones that mark significant progress points in the business journey."],
            "resources_needed": ["Detail critical resources required for success, including human capital, technology, and infrastructure."],
            "risks": ["Identify and analyze potential risks, including mitigation strategies."],
            "success_metrics": ["Define specific, measurable indicators that will track progress and success."]
        }},
        "financials": {{
            "initial_investment": "Provide a detailed breakdown of startup costs and initial capital requirements. Explain the allocation of funds.",
            "breakeven_timeline": "Analyze the path to breakeven, including key assumptions and variables that impact the timeline.",
            "potential_roi": "Project potential returns based on market analysis and business model. Include different scenarios and their likelihood.",
            "funding_requirements": "Detail the funding strategy, including amounts needed at different stages and how they align with milestones."
        }}
    }}

    For each field, provide rich, contextual information specific to this business idea. Write in clear, professional language that would be suitable for investors and stakeholders. Avoid generic responses - each answer should be tailored to this specific business opportunity. Focus on creating a cohesive narrative across all sections that builds a compelling case for the business.
    """
    
    try:
        print(f"Sending request to OpenAI for idea: {title}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an experienced startup advisor and business strategist with deep expertise in venture capital, market analysis, and business model innovation. Your analysis should be thorough, specific, and actionable, providing insights that would be valuable to both founders and investors."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        print("Received response from OpenAI")
        print(f"Response content: {response.choices[0].message.content}")
        
        # Parse the response to ensure it's valid JSON
        analysis = json.loads(response.choices[0].message.content)
        
        # Combine original description with analysis
        result = {
            "original_description": description,
            "analysis": analysis
        }
        
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return json.dumps({
            "error": "Failed to generate valid JSON analysis",
            "original_description": description
        })
    except Exception as e:
        print(f"Error during OpenAI request: {str(e)}")
        return json.dumps({
            "error": str(e),
            "original_description": description
        })
