import os
from openai import OpenAI
from dotenv import load_dotenv

def test_api():
    """Test the OpenAI API connection and agent retrieval"""
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Test API key by making a simple completion request
        print("Testing API key...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✅ API key is valid")
        
        # Test agent retrieval
        print("\nTesting agent retrieval...")
        agent_id = os.getenv("agent_id")
        if not agent_id:
            print("❌ agent_id not found in environment variables")
            return
            
        assistant = client.beta.assistants.retrieve(agent_id)
        print(f"✅ Successfully retrieved assistant: {assistant.id}")
        print(f"Assistant name: {assistant.name}")
        print(f"Assistant model: {assistant.model}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api() 