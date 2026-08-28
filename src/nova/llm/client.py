import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def ask_llm(
        system_prompt: str,
        user_prompt: str
) -> str:

    if not LLM_MODEL:
        raise ValueError(
            "LLM_MODEL is not set in .env"
        )
    if not LLM_API_KEY:
        raise ValueError(
            "LLM_API_KEY is not set in .env"
        )

    response = completion(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role":"user",
                "content": user_prompt
            }
        ] 
    )

    return response.choices[0].message.content

#testing 
if __name__ == "__main__":

    response = ask_llm(
        system_prompt=(
            "You are a helpful business analyst."
        ),
        user_prompt=(
            "Explain what ROAS means in one sentence."
        )
    )

    print(response)