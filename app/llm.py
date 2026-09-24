"""deepseek api 调用"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = None


def get_llm() -> OpenAI:
    global client
    if client is None:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_URL"),
        )
    return client
