import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
load_dotenv()

foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

#Foundry Client
project_client = AIProjectClient(
    endpoint=foundry_project_endpoint,
    credential=DefaultAzureCredential()
)

#OpenAPI Client
openAPI_client = project_client.get_openai_client()

response = openAPI_client.responses.create(
    model=model_deployment_name,
    instructions="You are a helpful AI assistant.",
    input = "What is difference between the project_client and openAPI_client in chat completion code?"
)

print(f"Response output: {response.output_text}")