import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from mcp_use import MCPAgent, MCPClient
import boto3
from datetime import datetime
import traceback
import shutil
import tempfile
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="MCP Agent Chat",
    page_icon="??",
    layout="wide"
)

def clean_browser_profile():
    """Clean up browser profile directory to fix launch issues"""
    try:
        profile_dir = Path.home() / ".config" / "browseruse" / "profiles" / "default"
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
            st.info("Cleaned browser profile directory")
        return True
    except Exception as e:
        st.warning(f"Could not clean browser profile: {e}")
        return False

def create_browser_config():
    """Create a clean browser configuration"""
    try:
        # Create a temporary directory for browser profile
        temp_dir = tempfile.mkdtemp(prefix="mcp_browser_")
        
        # Set environment variables for browser configuration
        os.environ["BROWSERUSE_USER_DATA_DIR"] = temp_dir
        os.environ["BROWSERUSE_HEADLESS"] = "true"  # Run in headless mode for server environments
        
        return temp_dir
    except Exception as e:
        st.error(f"Failed to create browser config: {e}")
        return None

@st.cache_resource
def initialize_agent():
    """Initialize the MCP agent (cached to avoid recreation)"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Clean browser profile and create new config
        clean_browser_profile()
        browser_dir = create_browser_config()
        
        if not browser_dir:
            st.error("Failed to create browser configuration")
            return None
        
        # Create MCPClient from configuration file with browser settings
        try:
            client = MCPClient.from_config_file("browser_mcp.json")
        except FileNotFoundError:
            st.error("browser_mcp.json configuration file not found")
            return None
        except Exception as e:
            st.error(f"Failed to load MCP configuration: {e}")
            return None
        
        # Create Bedrock client (uses IAM role from EC2 instance)
        try:
            bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name='us-east-1'  # Change to your preferred region
            )
        except Exception as e:
            st.error(f"Failed to create Bedrock client: {e}")
            return None
        
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
        
        st.success("MCP Agent initialized successfully")
        return agent
        
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.error(f"Full traceback: {traceback.format_exc()}")
        return None

async def get_agent_response(agent, query):
    """Get response from the MCP agent"""
    try:
        result = await agent.run(query)
        return result
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
        st.error(f"Agent execution failed: {str(e)}")
        return error_msg

def reset_agent():
    """Reset the agent and clear cache"""
    try:
        # Clear the cached agent
        if "agent" in st.session_state:
            del st.session_state.agent
        
        # Clear streamlit cache
        st.cache_resource.clear()
        
        # Clean browser profile
        clean_browser_profile()
        
        st.success("Agent reset successfully")
        return True
    except Exception as e:
        st.error(f"Failed to reset agent: {e}")
        return False

def main():
    st.title("?? MCP Agent Chat Interface")
    st.markdown("Ask questions and get responses from the MCP Agent powered by Claude")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar with configuration and controls
    with st.sidebar:
        st.header("Configuration")
        
        # Agent status
        if "agent" not in st.session_state or st.session_state.agent is None:
            st.warning("?? Agent not initialized")
            if st.button("Initialize Agent", use_container_width=True):
                with st.spinner("Initializing MCP Agent..."):
                    st.session_state.agent = initialize_agent()
                st.rerun()
        else:
            st.success("? MCP Agent Ready")
        
        st.header("Controls")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("Reset Agent", use_container_width=True):
                if reset_agent():
                    st.rerun()
        
        # Troubleshooting section
        st.header("Troubleshooting")
        if st.button("Clean Browser Profile", use_container_width=True):
            if clean_browser_profile():
                st.success("Browser profile cleaned")
            st.rerun()
        
        # Display browser configuration
        st.subheader("Browser Config")
        browser_dir = os.environ.get("BROWSERUSE_USER_DATA_DIR", "Not set")
        st.text(f"Profile Dir: {browser_dir}")
        st.text(f"Headless: {os.environ.get('BROWSERUSE_HEADLESS', 'Not set')}")
        
        st.header("Chat Statistics")
        st.metric("Total Messages", len(st.session_state.messages))
        
        st.header("Example Questions")
        example_questions = [
            "What's the current time?",
            "Search for information about Python",
            "Find news about artificial intelligence",
            "What are the top programming languages?",
            "Search for weather information"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}", use_container_width=True):
                # Add the example question to chat
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    
    # Main chat interface
    st.header("Chat")
    
    # Check if agent is ready
    if "agent" not in st.session_state or st.session_state.agent is None:
        st.warning("Please initialize the MCP Agent using the sidebar controls.")
        st.stop()
    
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
                try:
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
                    
                except Exception as e:
                    error_msg = f"Failed to get response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
        
        # Rerun to update the display
        st.rerun()

if __name__ == "__main__":
    main()