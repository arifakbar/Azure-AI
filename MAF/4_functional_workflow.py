import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Agent, workflow
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

    novice_writer = Agent(
        client=client,
        name="novice_writer_agent",
        instructions="You are a novice poem writer. Write poem on theme of only 4 lines."
    )

    experienced_writer = Agent(
        client=client,
        name="experienced_writer_agent",
        instructions="You are an experienced writer, review the poem (good/bad/avg) and provide a better version of 4 lines."
    )

    @workflow
    async def poem_workflow(theme: str) -> str:
        poem =(await novice_writer.run(f"Write a poem about : {theme}")).text
        review_poem =(await experienced_writer.run(f"Review the following poem and provide a better version:\n{poem}")).text
        return f"Poem:\n{poem}\n\nReview: {review_poem}"
    
    res = await poem_workflow.run("Anime over Movies")
    print(f"{res.get_outputs()[0]}\n")

if __name__ == "__main__":
        asyncio.run(main())


    