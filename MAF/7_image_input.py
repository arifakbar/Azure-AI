import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import Content, Message
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")
agent_name = os.getenv("AGENT_NAME")

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

def load_pdf():
        pdf = ASSETS_DIR / "sample.pdf"
        return pdf.read_bytes()

def create_img(): # This is a tiny yellow pixel in PNG format
        png_data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        return f"data:image/png;base64,{png_data}"

async def test_img(client):
        image_uri = create_img()
        message = Message(
                role="user",
                contents=[
                        Content.from_text(text="What is this image"),
                        Content.from_uri(uri=image_uri, media_type="image/png")
                ],
        )
        res = await client.get_response([message])
        print(f"Image Response: {res}")

async def test_pdf(client):
        pdf_byte = load_pdf()
        message = Message(
                role="user",
                contents=[
                        Content.from_text(text="What is in this PDF?"),
                        Content.from_data(
                                data=pdf_byte,
                                media_type="application/pdf",
                                additional_properties={"filename":"sample.pdf"}
                        )
                ]
        )
        res = await client.get_response([message])
        print(f"PDF response: {res}")

async def main():
        
        client = FoundryChatClient(
                project_endpoint=project_endpoint,
                model=model,
                credential=AzureCliCredential()
        )

        await test_img(client)
        await test_pdf(client)


if __name__ == "__main__":
        asyncio.run(main())