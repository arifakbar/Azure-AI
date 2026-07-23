import asyncio
import os
from dotenv import load_dotenv
from agent_framework import Agent, AgentResponseUpdate, Message, WorkflowBuilder
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")

async def main():
    client = FoundryChatClient(
        project_endpoint=project_endpoint,
        model=model,
        credential=AzureCliCredential()
    )

    writer_agent = Agent(
        client=client,
        instructions="You are an excellent content writer. You create new content and edit contents based on the feedback.",
        name = "Writer"
    )

    reviewer_agent = Agent(
        client=client,
        instructions="""
            You are an excellent content reviewer.
            Provide actionable feedback to the writer about the provided content.
            Provide the feedback in the most concise manner possible.
        """,
        name="Reviewer"
    )

    workflow = WorkflowBuilder(start_executor=writer_agent, output_from="all").add_edge(writer_agent, reviewer_agent).build()

    last_author : str | None = None

    async for event in workflow.run(
        Message("user", ["Create a slogan for a Light Yagami in Naruto Anime"]),
        stream=True
    ): 
        if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
            update = event.data
            author = update.author_name
            if author != last_author:
                if last_author is not None:
                    print()
                print(f"{author}: {update.text}", end="", flush=True)
                last_author = author
            else:
                print(update.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())