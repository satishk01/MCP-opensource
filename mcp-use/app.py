import asyncio
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from mcp_use import MCPAgent, MCPClient
import boto3

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create MCPClient from configuration dictionary
    ####client = MCPClient.from_dict(config)
    client = MCPClient.from_config_file("browser_mcp.json")
    
    # Create Bedrock client (uses IAM role from EC2 instance)
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'  # Change to your preferred region
    )
    
    # Create LLM using ChatBedrock
    llm = ChatBedrock(
        client=bedrock_client,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
        }
    )
    
    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    
    # Run the query
    result = await agent.run(
        "Find the best restaurant in San Francisco",
    )
    
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())