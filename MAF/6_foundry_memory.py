import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

from agent_framework import Agent, InMemoryHistoryProvider
from agent_framework.foundry import FoundryChatClient, FoundryMemoryProvider
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemoryStoreDefaultOptions,
)
from azure.identity import AzureCliCredential

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")
embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")

async def main():
        
        client = AIProjectClient(
                credential=AzureCliCredential(),
                model=model,
                endpoint=project_endpoint
        )

        memory_store_name = f"foundry_memory_{datetime.now(timezone.utc).strftime('%Y%m%d')}"

        options = MemoryStoreDefaultOptions(
                chat_summary_enabled=False,
                user_profile_enabled=True,
                user_profile_details="Avoid irrelevant or sensitive data, such as age, financials, precise location, and credentials"
        )

        memory_store_definition = MemoryStoreDefaultDefinition(
                chat_model=model,
                embedding_model=embedding_model,
                options=options
        )

        print(f"Creating memory store '{memory_store_name}'...")

        try:
                memory_store = await client.beta.memory_stores.create(
                        name = memory_store_name,
                        description = "Memory store for Agent Framework with FoundryMemoryProvider",
                        definition = memory_store_definition
                )
        except Exception as e:
                print(f"Failed creating memory store: {e}")
        
        print(f"Memory store created: {memory_store.name} with ID: {memory_store.id}")

        memory_context_provider = FoundryMemoryProvider(
                project_client = client,
                memory_store_name = memory_store.name,
                scope = "Light", ## Scope memories to a specific user
                update_delay=0# Do not wait to update memories after each interaction (for demo purposes) In production, consider setting a delay to batch updates and reduce costs.
        )

        chat_client = FoundryChatClient(
               model=model,
               credential=AzureCliCredential(),
               project_endpoint=project_endpoint
        )

        agent = Agent(
                name = agent_name,
                client = chat_client,
                description="""
                You are a helpful assistant that remembers past conversations.
                The memories from previous interactions are automatically provided to you.
                """,
                context_providers=[memory_context_provider, InMemoryHistoryProvider(load_messages=False)] #use the service side storage, nor load messsages from the history provider
        )

        try:
                session = agent.create_session()
                print("===First===")
                print("User: I prefer dark roast coffee and I'm allergic to nuts.")
                res = await agent.run("I prefer dark roast coffee and I'm allergic to nuts",session=session)
                print(f"Agent: {res}")

                print("Waiting for memories to be stored...")
                await asyncio.sleep(8)

                print("===Second===")
                print("User: Can you recommend a coffee and snack for me?")
                res = await agent.run("Can you recommend a coffee and snack for me?",session=session)
                print(f"Agent: {res}")

                print("===Third===")
                res = await agent.run("User: What do you remember about my preferences??",session=session)
                print(f"Agent: {res}")

                print(f"Stored memories from: {memory_store.name} ({memory_store.id})")

                res = await client.beta.memory_stores.search_memories(name=memory_store.name, scope="Light")

                for memory in res.memories:
                    print(f"Memory: {memory.memory_item.content}")
            
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
               await client.beta.memory_stores.delete(memory_store_name)
               print("==========================================")
               print("Memory store deleted")

if __name__ == "__main__":
        asyncio.run(main())