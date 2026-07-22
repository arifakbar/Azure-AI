import asyncio
import os
from dotenv import load_dotenv

from agent_framework import Message
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

async def main() -> None:

    client = FoundryChatClient(
          project_endpoint=project_endpoint,
          credential=AzureCliCredential(),
          model=model
    )   

    async def llm_response():
          await client.get_response(messages=[Message(role="user",contents=["Tell a poem"])])
    
    try:
          task = asyncio.create_task(llm_response())
          await asyncio.sleep(1) #Cancelling a chat request after 1 second.
          task.cancel()
          await task
    except asyncio.CancelledError:
          print("Request was cancelled")

if __name__ == "__main__":
        asyncio.run(main())