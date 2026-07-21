import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

async def main():
    
    client = FoundryChatClient(
        project_endpoint = project_endpoint,
        model= model,
        credential=AzureCliCredential()
    )

    agent = Agent(
        client=client,
        name = agent_name,
        instructions="You are a friendly assistant."
    )

    session = agent.create_session()

    res = await agent.run("Hi, my name is Light. And I'm 6'2.", session=session)
    print(f"Agent: {res}\n")

    res = await agent.run("What do you remember about me?", session=session)
    print(f"Agent: {res}\n")

if __name__ == "__main__":
    asyncio.run(main())