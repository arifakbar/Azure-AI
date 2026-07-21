import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential

import asyncio
from agent_framework import Agent
from azure.ai.projects.models import OpenApiTool
from agent_framework.foundry import FoundryChatClient

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

async def main():

    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        credential = AzureCliCredential(),
        model=model
    )

    weather_tool = OpenApiTool(
        name="weather_api",
        specification_path="../apis/weather_api.json",
    )

    agent = Agent(
        client=client,
        name = "AgentFromCode",
        instructions="You are an AI Assistant. Use the weather_api tool whenever weather information is requested.",
        tools = [weather_tool]
    )

    result = await agent.run("What's the weather like in Seattle?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
