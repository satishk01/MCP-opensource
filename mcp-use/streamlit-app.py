import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from mcp_use import MCPAgent, MCPClient
import boto3
from datetime import datetime
import traceback

# Page configuration
st.set_page_config(
    page_title="MCP Agent Chat",
    page_icon="??",
    layout="wide"
)

@st.cache_resource
def initialize_agent():
    """Initialize the MCP agent (cached to avoid recreation)"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create MCPClient from configuration file
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
        
        return agent
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return None

async def get_agent_response(agent, query):
    """Get response from the MCP agent"""
    try:
        result = await agent.run(query)
        return result
    except Exception as e:
        return f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def main():
    st.title("?? MCP Agent Chat Interface")
    st.markdown("Ask questions and get responses from the MCP Agent powered by Claude")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        with st.spinner("Initializing MCP Agent..."):
            st.session_state.agent = initialize_agent()
    
    # Check if agent initialization was successful
    if st.session_state.agent is None:
        st.error("Failed to initialize the MCP Agent. Please check your configuration.")
        st.stop()
    
    # Sidebar with configuration and controls
    with st.sidebar:
        st.header("Configuration")
        st.success("? MCP Agent Initialized")
        
        st.header("Controls")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.header("Chat Statistics")
        st.metric("Total Messages", len(st.session_state.messages))
        
        st.header("Example Questions")
        example_questions = [
            "Find the best restaurant in San Francisco",
            "What's the weather like today?",
            "Search for recent news about AI",
            "Find information about Python programming",
            "What are the top tourist attractions in Paris?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question[:20]}", use_container_width=True):
                # Add the example question to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    
    # Main chat interface
    st.header("Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "timestamp" in message:
                    st.caption(f"Time: {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"Time: {timestamp}")
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(
                        get_agent_response(st.session_state.agent, prompt)
                    )
                finally:
                    loop.close()
                
                st.write(response)
                response_timestamp = datetime.now().strftime("%H:%M:%S")
                st.caption(f"Time: {response_timestamp}")
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": response_timestamp
        })
        
        # Rerun to update the display
        st.rerun()

if __name__ == "__main__":
    main()