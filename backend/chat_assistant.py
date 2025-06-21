from langchain_openai import ChatOpenAI
from langchain.schema import message_to_dict, messages_from_dict
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
import os
import json

load_dotenv()

class LLM:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize chat_history.json if it doesn't exist
        if not os.path.exists("chat_history.json"):
            with open("chat_history.json", "w") as f:
                json.dump([], f)
        
        # Load chat history only if the file has valid data
        try:
            if os.path.exists("chat_history.json"):
                recalled_messages = []
                with open("chat_history.json", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:  # Skip empty lines
                            try:
                                message_dict = json.loads(line)
                                recalled_messages.append(message_dict)
                            except json.JSONDecodeError:
                                continue  # Skip invalid lines
                
                # Guard: Only update memory if we have valid, non-empty data
                if recalled_messages and len(recalled_messages) > 0:
                    try:
                        self.memory.chat_memory.messages = messages_from_dict(recalled_messages)
                        print(f"Loaded {len(recalled_messages)} messages from chat history")
                    except Exception as e:
                        print(f"Error loading messages from history: {e}")
                        # If there's an error loading, start with empty memory
                        self.memory.chat_memory.messages = []
                else:
                    print("Chat history is empty or invalid, starting with fresh memory")
            else:
                print("No chat history file found, starting with fresh memory")
        except Exception as e:
            print(f"Error reading chat history: {e}, starting with fresh memory")
            # If there's an error reading the file, start with empty memory
            self.memory.chat_memory.messages = []

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            openai_api_key=openai_api_key
        )

        self.chatter = ConversationChain(llm=self.llm, memory=self.memory, verbose=True)

    def generate_response(self, prompt: str) -> str:
        prev_len = len(self.memory.chat_memory.messages)
        result = self.chatter.predict(input=prompt)
        new_len = len(self.memory.chat_memory.messages)

        # Only save if we have new messages
        if new_len > prev_len:
            new_messages = self.memory.chat_memory.messages[prev_len:]
            try:
                # Convert new messages to dict format
                new_messages_dict = []
                for message in new_messages:
                    new_messages_dict.append(message_to_dict(message))
                
                # Append new messages to file without loading existing ones
                with open("chat_history.json", "a") as f:
                    for message_dict in new_messages_dict:
                        f.write(json.dumps(message_dict) + '\n')
                
                print(f"Appended {len(new_messages)} new messages to chat history")
            except Exception as e:
                print(f"Error saving chat history: {e}")
        
        return result
    

    
