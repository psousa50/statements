
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path to import the GeminiPro class
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ai.gemini_pro import GeminiPro


async def test_single_prompt(gemini: GeminiPro):
    """Test generating a response from a single prompt."""
    prompt = "Explain the concept of technical debt in software development in 3 paragraphs."
    
    print("\n=== Testing Single Prompt Generation ===")
    print(f"Prompt: {prompt}")
    
    try:
        response = await gemini.generate(prompt)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")


async def test_chat_conversation(gemini: GeminiPro):
    """Test a multi-turn chat conversation."""
    messages = [
        {"role": "user", "content": "What are the top 3 programming languages for data science?"},
        {"role": "user", "content": "And what are their main advantages?"}
    ]
    
    print("\n=== Testing Chat Conversation ===")
    print("Messages:")
    for msg in messages:
        print(f"- {msg['role']}: {msg['content']}")
    
    try:
        response = await gemini.chat(messages)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")


async def test_config_update(gemini: GeminiPro):
    """Test updating the model configuration."""
    prompt = "Write a creative short story about a programmer who discovers AI."
    
    print("\n=== Testing Configuration Update ===")
    print("Original config:")
    print(f"- Temperature: {gemini.temperature}")
    print(f"- Top P: {gemini.top_p}")
    
    # Generate with original settings
    print("\nGenerating with original settings...")
    try:
        response1 = await gemini.generate(prompt)
        print("\nResponse with original settings:")
        print(response1[:200] + "..." if len(response1) > 200 else response1)
    except Exception as e:
        print(f"Error: {e}")
    
    # Update config to be more creative
    print("\nUpdating configuration to be more creative (higher temperature)...")
    gemini.update_config(temperature=1.0)
    print(f"- New Temperature: {gemini.temperature}")
    
    # Generate with new settings
    try:
        response2 = await gemini.generate(prompt)
        print("\nResponse with updated settings:")
        print(response2[:200] + "..." if len(response2) > 200 else response2)
    except Exception as e:
        print(f"Error: {e}")


async def main():
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if API key is available
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it by running: export GOOGLE_API_KEY='your-api-key'")
        return
    
    # Initialize GeminiPro
    gemini = GeminiPro(api_key=api_key)
    
    # Run tests
    await test_single_prompt(gemini)
    await test_chat_conversation(gemini)
    await test_config_update(gemini)


if __name__ == "__main__":
    asyncio.run(main())