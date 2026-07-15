import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

#Foundry Client
project_client = AIProjectClient(
    endpoint=foundry_project_endpoint,
    credential=DefaultAzureCredential()
)

openai_client = project_client.get_openai_client()

agent = project_client.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=model_deployment_name,
        instructions="You are a helpful AI Assistant"
    ),
)

# printing the agent id
print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
     
response = openai_client.responses.create(
    input = "Hi",
    extra_body = {
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference"
        }
    }
)

print(f"Response completed: {response.output_text}")