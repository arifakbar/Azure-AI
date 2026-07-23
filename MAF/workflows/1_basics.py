import asyncio
import os

from agent_framework import (
    Agent, 
    AgentResponse,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryChatClient
from dotenv import load_dotenv
from typing_extensions import Never, cast

load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT_NAME")

#WorkflowContext[T_Out] is used for nodes that send messages to downstream nodes with ctx.send_message(T_Out).
#WorkflowContext[T_Out, T_W_Out] is used for nodes that also yield workflow output with ctx.yield_output(T_W_Out).

#The WorkflowContext is parameterized with two types:
#    - T_Out = Never: this node does not send messages to downstream nodes.
#    - T_W_Out = str: this node yields workflow output of type str.

@executor(id="uppercase_executor")
async def uppercase(text:str, ctx:WorkflowContext[str, str])->None:
    res = text.upper()
    await ctx.send_message(res) #send_message -> Send message to next node

@executor(id="reverse_text_executor")
async def reverse_text(text:str, ctx:WorkflowContext[str, str])->None:
    res = text[::-1]
    await ctx.send_message(res)

@executor(id="add_exclamation_executor")
async def add_exclamation(text:str, ctx:WorkflowContext[Never, str])->None:
    res = f"{text} !!!"
    await ctx.yield_output(res) #yield_output -> only emits workflow output.

#output_from="all" -> every executor's yield_output() to appear in events.get_outputs()
#output_from="add_exclamation" -> only care about the final result/specific node

def create_workflow() -> Workflow:
    return (
        WorkflowBuilder(start_executor=uppercase, output_from=[add_exclamation]) 
            .add_edge(uppercase, reverse_text)
            .add_edge(reverse_text,add_exclamation)
            .build()
    )

async def main():

    #=== Workflow without Agent ===
    workflow = create_workflow()
    events = await workflow.run("Hello Light")
    print("Reversed Output: ")
    print(events.get_outputs())
    print("Final output:", events.get_final_state())

    #=== Introducing Agent ===
    client = FoundryChatClient(
        project_endpoint= project_endpoint,
        model = model,
        credential= AzureCliCredential()
    )

    corrector_agent = Agent(
        client=client,
        instructions="You are provided with a reversed string in a workflow. As the last node of it, reverse it basck to it's original form.",
        name = "corrector"
    )

    workflow = WorkflowBuilder(
        start_executor=uppercase, output_from=[corrector_agent]
    ).add_edge(uppercase, reverse_text).add_edge(reverse_text,corrector_agent).build()

    print("Corrected Agent Output: ")
    events = await workflow.run("Hello Light")
    outputs = events.get_outputs()
    outputs = cast(list[AgentResponse], outputs) #outputs are expected to be a list of `AgentResponse` from the agents in the workflow.
    for output in outputs:
        print(f"{output.messages[0].author_name} : {output.text}")
    print("Final state:", events.get_final_state())

if __name__ == "__main__":
    asyncio.run(main())