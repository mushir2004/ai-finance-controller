from openai import OpenAI
import os

# Point the base_url to the NVIDIA API Gateway
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

def resolve_financial_exception(record_data: dict, is_hard_exception: bool = False):
    messages = [
        {"role": "system", "content": "You are a financial reconciliation agent. Output valid JSON mapping the exception root cause."},
        {"role": "user", "content": f"Analyze this unstructured settlement data: {record_data}"}
    ]

    kwargs = {
        "model": "deepseek-ai/deepseek-v4-flash-0731",
        "messages": messages,
        "response_format": {"type": "json_object"}
    }

    # Dynamically apply 'Think High' reasoning for complex chargebacks and memos
    if is_hard_exception:
        kwargs["extra_body"] = {
            "chat_template_kwargs": {
                "thinking": True,
                "reasoning_effort": "high"
            }
        }

    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message.content