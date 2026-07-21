import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential

import asyncio
from agent_framework import Agent
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

    agent = Agent(
        client=client,
        name = agent_name,
        instructions="You are an AI Assistant"
    )

    return agent

agent = asyncio.run(main())

# async def non_streaming_example():
#     query = "Capital of India?"
#     result = await agent.run(query)
#     print("Agent Response:", result)

# asyncio.run(non_streaming_example())

async def streaming_example():
    async for chunk in agent.run("Tell me a one-sentence fun fact.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)

asyncio.run(streaming_example())