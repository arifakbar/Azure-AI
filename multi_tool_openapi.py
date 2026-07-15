import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
import jsonref
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, Tool

load_dotenv()

foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")
mcp_server_name = os.getenv("MCP_SERVER_NAME")

project_client = AIProjectClient(
    endpoint=foundry_project_endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()


with open("./apis/weather_api.json", "r") as f:
        openapi_weather = jsonref.loads(f.read())

# Initialize agent OpenApi tool using the read in OpenAPI spec
weather_tool = {
        "type": "openapi",
        "openapi":{
            "name": "weather",
            "spec": openapi_weather,
            "auth": {
                "type": "anonymous"
            },
        }
}


connection_id = ""

for connection in project_client.connections.list():
    if connection.name == mcp_server_name:
        connection_id = connection.id
        break

print(f"The MCP Server Connection ID is: {connection_id}")

mcp_tool = MCPTool(
    server_label = "microsoft_learn_server",
    server_url="https://learn.microsoft.com/api/mcp",
    require_approval="never",
    project_connection_id=connection_id
)

agent = project_client.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=model_deployment_name,
        instructions="You are a helpful assistant that can use multiple tools to answer user queries.",
        tools=[weather_tool, mcp_tool],
    )
)

print(f"Created agent: {agent.name} with ID: {agent.id}")

user_query = "Let me know the weather in Mumbai and also find me a Microsoft Learn module on Microsoft Foundry."

response = openai_client.responses.create(
    extra_body = {
        "agent_reference": {
            "name": agent_name,
            "type": "agent_reference"
        }
    },
    input = user_query
)

print(f"Agent response: {response.output_text}")