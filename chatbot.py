import os
import sys
import json
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,

    CdpWalletProvider,
    CdpWalletProviderConfig,

    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools

# Configure a file to persist the agent's CDP API Wallet Data.
wallet_data_file = "wallet_data.txt"
print("wallet_data_file: ", wallet_data_file)

# Load environment variables from .env file
load_dotenv()

def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM
    # llm = ChatOpenAI(model="gpt-4o-mini")
    llm = ChatGroq(model="llama-3.3-70b-versatile") 

    # Initialize CDP Wallet Provider
    wallet_data = None
    print("wallet_data: ", wallet_data)

    if os.path.exists(wallet_data_file):
        print("Reading wallet data from file...")
        with open(wallet_data_file) as f:
            wallet_data = f.read()
            # wallet_data = json.loads(wallet_data)
            print("wallet_data: ", wallet_data)
    else:
        print("No wallet data file found.")
        wallet_data = None
    
    cdp_config = None
    print("cdp_config: ", cdp_config)

    print("CDP_API_KEY_NAME: ", os.getenv("CDP_API_KEY_NAME"))
    print("CDP_API_KEY_VALUE: ", os.getenv("CDP_API_KEY_PRIVATE_KEY"))
    print("CDP_API_SECRET_NAME: ", os.getenv("CDP_API_SECRET_NAME"))   
    print("CDP_API_SECRET_VALUE: ", os.getenv("CDP_API_SECRET_VALUE"))
    print("CDP_API_URL: ", os.getenv("CDP_API_URL"))
    print("CDP_API_VERSION: ", os.getenv("CDP_API_VERSION"))
    print("CDP_API_NETWORK: ", os.getenv("CDP_API_NETWORK"))
    print("CDP_API_CHAIN_ID: ", os.getenv("CDP_API_CHAIN_ID"))
    print("CDP_API_WALLET_ADDRESS: ", os.getenv("CDP_API_WALLET_ADDRESS"))
    print("CDP_API_WALLET_PRIVATE_KEY: ", os.getenv("CDP_API_WALLET_PRIVATE_KEY"))
    print("CDP_API_WALLET_PUBLIC_KEY: ", os.getenv("CDP_API_WALLET_PUBLIC_KEY"))
    print("CDP_API_WALLET_MNEMONIC: ", os.getenv("CDP_API_WALLET_MNEMONIC"))

    print("OPENAI_API_KEY: ", os.getenv("OPENAI_API_KEY"))
    print("GROQ_API_KEY: ", os.getenv("GROQ_API_KEY"))
    
    if wallet_data is not None:
        print("Creating CDP Wallet Provider with existing wallet data...")
        cdp_config = CdpWalletProviderConfig(api_key_name=os.getenv("CDP_API_KEY_NAME"), api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY"), wallet_data=wallet_data)
    else:
        print("Creating CDP Wallet Provider with new wallet data...")
        cdp_config = CdpWalletProviderConfig(api_key_name=os.getenv("CDP_API_KEY_NAME"), api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY"), wallet_data=wallet_data)
    
    print("cdp_config: ", cdp_config)

    wallet_provider = CdpWalletProvider(cdp_config)

    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            cdp_api_action_provider(),
            cdp_wallet_action_provider(),
            erc20_action_provider(),
            pyth_action_provider(),
            wallet_action_provider(),
            weth_action_provider(),
        ]
    ))

    wallet_data_json = json.dumps(wallet_provider.export_wallet().to_dict())

    with open(wallet_data_file, "w") as f:
        f.write(wallet_data_json)

    # use get_langchain_tools
    tools = get_langchain_tools(agentkit)

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),
    ), config


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            # Run agent in autonomous mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            # Wait before the next action
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
