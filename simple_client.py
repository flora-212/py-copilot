#!/usr/bin/env python3
"""
Simple Python client - using standard library only
For testing py-copilot VS Code extension
"""

import urllib.request
import urllib.parse
import json
import sys

def send_message_simple(message, port=12345, file_path=None):
    """
    Send message to VS Code extension using standard library
    Optionally attach a file
    """
    url = f"http://localhost:{port}/message"
    
    data = {
        "text": message
    }
    
    # If file path is provided, add it to the data
    if file_path:
        import os
        if os.path.exists(file_path):
            data["file_path"] = os.path.abspath(file_path)
            data["file_name"] = os.path.basename(file_path)
            print(f"📎 Attached file: {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Prepare data
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Content-Length': str(len(json_data))
        },
        method='POST'
    )
    
    try:
        print(f"📤 Sending message: {message}")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Response status: {result.get('status')}")
                print(f"📝 Original message: {result.get('message')}")
                
                if 'copilot_reply' in result:
                    print(f"🤖 Copilot reply: {result.get('copilot_reply')}")
                else:
                    print(f"📋 Processing result: {result.get('result')}")
                
                return True
            else:
                print(f"❌ HTTP error: {response.status}")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        print("Please ensure VS Code and py-copilot extension are running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🐍 py-copilot Simple Test Client")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Command line argument mode
        message = sys.argv[1]
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        send_message_simple(message, file_path=file_path)
    else:
        # Interactive mode
        print("Enter message to send to Copilot (type 'quit' to exit):")
        print("Format: message text [file path]")
        
        while True:
            try:
                user_input = input("\n💬 Message: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye")
                    break
                    
                if user_input:
                    # Parse message and optional file path
                    parts = user_input.split(' ', 1)
                    if len(parts) == 2 and parts[1].startswith('/') or parts[1].startswith('.') or '\\' in parts[1]:
                        # Looks like a file path
                        message = parts[0]
                        file_path = parts[1]
                    else:
                        message = user_input
                        file_path = None
                    
                    send_message_simple(message, file_path=file_path)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye")
                break
