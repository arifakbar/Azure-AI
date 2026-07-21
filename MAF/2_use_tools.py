import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential

import asyncio
from random import randint
from typing import Annotated
from pydantic import Field
import jsonref

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

@tool(approval_mode="never_require")
def get_weather_random(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main():

    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        credential = AzureCliCredential(),
        model=model
    )

    with open("./apis/weather_api.json", "r") as f:
        openapi_weather = jsonref.loads(f.read())
    
    # Initialize agent OpenApi tool using the read in OpenAPI spec
    weather_tool_api = {
            "type": "openapi",
            "openapi":{
                "name": "weather",
                "spec": openapi_weather,
                "auth": {
                    "type": "anonymous"
                },
            }
    }

    agent = Agent(
        client=client,
        name = "AgentFromCode",
        instructions="""
        You are an AI Assistant. Use both the get_weather_random and weather_tool_api tool whenever weather information is requested. And show result from both tools in your response.
        
        Format:
        Random: Output from get_weather_random tool
        API: Output from weather_tool_api tool
        """,
        tools = [get_weather_random, weather_tool_api]
    )

    result = await agent.run("What's the weather like in Pune?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
