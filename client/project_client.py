#!/usr/bin/env python3
"""
Simple adaptation client with GUI for py-copilot VS Code extension
Helps adapt methods to new datasets
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
import urllib.parse
import json
import os

def send_message_to_copilot(message, file_paths=None, port=12345):
    """
    Send message to VS Code extension with optional file attachments
    """
    url = f"http://localhost:{port}/message"
    
    data = {
        "text": message
    }
    
    # Handle file paths
    if file_paths and isinstance(file_paths, list):
        # Find first valid file path
        for path in file_paths:
            if path and os.path.exists(path):
                data["file_path"] = os.path.abspath(path)
                data["file_name"] = os.path.basename(path)
                print(f"📎 File attached: {path}")
                break
    
    json_data = json.dumps(data).encode('utf-8')
    
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

class SimpleAdaptationDialog:
    def __init__(self, root):
        self.root = root
        self.root.title("Method Adaptation Assistant")
        self.root.geometry("500x350")
        
        # Variables
        self.method_name = tk.StringVar()
        self.dataset_name = tk.StringVar()
        self.method_path = tk.StringVar()
        self.dataset_path = tk.StringVar()
        
        # Create and pack widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Method Name
        ttk.Label(main_frame, text="Method Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.method_name, width=40).grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Dataset Name
        ttk.Label(main_frame, text="Dataset Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dataset_name, width=40).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Method Path
        ttk.Label(main_frame, text="Method Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.method_path, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_path(self.method_path)).grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Dataset Path
        ttk.Label(main_frame, text="Dataset Path:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dataset_path, width=30).grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_path(self.dataset_path)).grid(row=3, column=2, sticky=tk.W, pady=5)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Message Preview", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=6, width=50, wrap=tk.WORD)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Update preview when any field changes
        for var in [self.method_name, self.dataset_name, self.method_path, self.dataset_path]:
            var.trace_add("write", self.update_preview)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Send to Copilot", command=self.send_to_copilot).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).grid(row=0, column=1, padx=5)
    
    def browse_path(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
    
    def update_preview(self, *args):
        try:
            # Clear preview
            self.preview_text.delete("1.0", tk.END)
            
            # Get and validate message
            message = self.generate_message()
            if message is None or not isinstance(message, str):
                return
                
            # Display the message
            self.preview_text.insert(tk.END, message)
            
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def generate_message(self):
        # Safely get values with default empty strings
        method_name = self.method_name.get() or ""
        dataset_name = self.dataset_name.get() or ""
        method_path = self.method_path.get() or ""
        dataset_path = self.dataset_path.get() or ""
        
        # Generate simple adaptation message
        message = f"I want to adapt the {method_name} method to the {dataset_name} dataset. "
        message += f"The method code is located at: {method_path}, "
        message += f"and the dataset is located at: {dataset_path}. "
        message += "Please help me adapt this method to work with the new dataset."
        
        return message
    
    def send_to_copilot(self):
        # Validate required inputs
        if not all([self.method_name.get(), self.dataset_name.get(),
                   self.method_path.get(), self.dataset_path.get()]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Check if paths exist
        method_path = self.method_path.get()
        dataset_path = self.dataset_path.get()
        
        if not os.path.exists(method_path):
            messagebox.showerror("Error", f"Method path not found: {method_path}")
            return
        if not os.path.exists(dataset_path):
            messagebox.showerror("Error", f"Dataset path not found: {dataset_path}")
            return
            
        # Generate message
        message = self.generate_message()
        
        # Send message with method path as reference
        if send_message_to_copilot(message, file_paths=[method_path]):
            messagebox.showinfo("Success", "Message sent to Copilot successfully!")
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to send message to Copilot")

def main():
    root = tk.Tk()
    app = SimpleAdaptationDialog(root)
    root.mainloop()

if __name__ == "__main__":
    print("🔄 py-copilot Method Adaptation Assistant")
    print("=" * 40)
    main()
