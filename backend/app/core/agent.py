import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Ensure dotenv locates the .env file in the backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(backend_dir, ".env"))

# Fallback to prevent startup crashes if the key is completely missing
api_key = os.getenv("NVIDIA_API_KEY", "missing_key")

client = OpenAI(
    api_key=api_key,
    base_url="https://integrate.api.nvidia.com/v1"
)

def resolve_exception_with_ai(exception_data: dict) -> dict:
    if api_key == "missing_key" or not api_key:
        return {
            "root_cause_analysis": "System Error: NVIDIA_API_KEY is missing or empty in the .env file.",
            "recommended_action": "Add a valid API key and restart the server.",
            "confidence_score": 0.0,
            "requires_human_escalation": True
        }

    prompt = f"""
    You are an AI Finance Controller agent handling settlement exceptions.
    Analyze the following failed reconciliation record:
    {json.dumps(exception_data, indent=2)}

    Determine the root cause and propose a financial operations resolution.
    Respond ONLY in valid JSON matching this schema:
    {{
      "root_cause_analysis": "string",
      "recommended_action": "string",
      "confidence_score": 0.0 to 1.0,
      "requires_human_escalation": boolean
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/deepseek-v4-flash-0731",
            messages=[
                {"role": "system", "content": "You are a precise JSON-only financial operations agent."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        # Catch 401 Unauthorized, timeouts, or rate limits and pass them to the UI
        return {
            "root_cause_analysis": f"AI API Connection Failed: {str(e)}",
            "recommended_action": "Check API key validity, network connection, or provider status.",
            "confidence_score": 0.0,
            "requires_human_escalation": True
        }