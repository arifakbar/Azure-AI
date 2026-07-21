import os
from dotenv import load_dotenv
# from agent_framework import AzureAICAlient
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")

async def create_agent():

    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        credential = AzureCliCredential(),
        model=model
    )

    agent = Agent(
        client=client,
        name = "AgentFromCode",
        instructions="You are an AI Assistant"
    )

    return agent

agent = asyncio.run(create_agent())

async def non_streaming_example():
    query = "Capital of India?"
    result = await agent.run(query)
    print("Agent Response:", result)

asyncio.run(non_streaming_example())