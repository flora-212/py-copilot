#!/usr/bin/env python3
"""
Python client script for testing py-copilot VS Code extension
"""

import requests
import json
import time

def send_message_to_copilot(message, port=12345, file_path=None):
    """
    Send message to VS Code extension
    
    Args:
        message (str or dict): Message to send to Copilot. Can be a string or a dict with 'text' and 'file' keys
        port (int): Port number the VS Code extension is listening on
        file_path (str, optional): Path to file to attach to the message
    
    Returns:
        dict: Server response
    """
    url = f"http://localhost:{port}/message"
    
    # Handle dict message format
    if isinstance(message, dict):
        text = message['text']
        file_path = message.get('file', file_path)
    else:
        text = message
    
    data = {
        "text": text
    }
    
    # Add file if provided
    if file_path:
        import os
        if os.path.exists(file_path):
            data["file_path"] = os.path.abspath(file_path)
            data["file_name"] = os.path.basename(file_path)
            print(f"📎 Attached file: {file_path}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending message to VS Code: {message}")
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
            return result
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Unable to connect to VS Code extension")
        print("Please ensure:")
        print("1. VS Code is open")
        print("2. py-copilot extension is activated")
        print("3. Extension is listening on port 12345")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout error: Request timed out")
        return None
    except Exception as e:
        print(f"❌ Unknown error: {e}")
        return None

def interactive_mode():
    """Interactive mode - continuously receive user input and send to Copilot"""
    print("🚀 py-copilot Interactive mode started")
    print("💡 Instructions:")
    print("  - Type your message to send to Copilot")
    print("  - To attach a file, use format: message | file_path")
    print("    Example: 'Explain this code | src/main.py'")
    print("  - Type 'quit', 'exit', or 'q' to exit")
    print("  - Press Ctrl+C to force exit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Your message: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                print("⚠️  Message cannot be empty")
                continue
            
            # Check if user wants to attach a file
            if ' | ' in user_input:
                message, file_path = user_input.split(' | ', 1)
                message = message.strip()
                file_path = file_path.strip()
                send_message_to_copilot(message, file_path=file_path)
            else:
                send_message_to_copilot(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 User interrupted, exiting program")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Starting basic functionality test...")
    
    test_messages = [
        "Hello from Python! ",
        "Please help me explain this Python code: i += 1 ",
        "What does this error mean: IndexError: list index out of range",
        {"text": "Summarize the function of this file", "file": "test_code.py"}
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}/{len(test_messages)}")
        result = send_message_to_copilot(message)
        
        if result:
            print(f"✅ Test {i} passed")
        else:
            print(f"❌ Test {i} failed")
        
        # Wait a bit to avoid too rapid requests
        time.sleep(10)
    
    print("\n🎉 Basic functionality test complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("🐍 py-copilot Python Client")
    print("=" * 60)
    
    print("\nSelect run mode:")
    print("1. Interactive mode (send messages continuously)")
    print("2. Basic functionality test (automated test)")
    
    try:
        choice = input("\nPlease choose (1-2) or press Enter for interactive mode: ").strip()
        
        if choice == "2":
            test_basic_functionality()
        else:  # Default to interactive mode for choice "1" or empty input
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Program exited")
    except Exception as e:
        print(f"❌ Program error: {e}")
