#!/usr/bin/env python3
"""
Project task client with GUI input dialog for py-copilot VS Code extension
"""

import tkinter as tk
from tkinter import ttk, filedialog
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

class ProjectDialog:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Task Configuration")
        self.root.geometry("600x400")
        
        # Variables
        self.technology_name = tk.StringVar()
        self.benchmark_name = tk.StringVar()
        self.technology_path = tk.StringVar()
        self.benchmark_path = tk.StringVar()
        self.info_source = tk.StringVar()
        self.additional_info = tk.StringVar()
        
        # Set default info source options
        self.info_sources = [
            "the paper that proposed {technology}",
            "the paper that proposed {benchmark}",
            "the homepage of {technology}",
            "the homepage of {benchmark}",
            "custom source..."
        ]
        self.info_source.set(self.info_sources[0])
        
        # Create and pack widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Technology Name
        ttk.Label(main_frame, text="Technology Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.technology_name, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Benchmark Name
        ttk.Label(main_frame, text="Benchmark Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.benchmark_name, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Technology Path
        ttk.Label(main_frame, text="Technology Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.technology_path, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_path(self.technology_path)).grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Benchmark Path
        ttk.Label(main_frame, text="Benchmark Path:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.benchmark_path, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_path(self.benchmark_path)).grid(row=3, column=2, sticky=tk.W, pady=5)
        
        # Additional Information Frame
        info_frame = ttk.LabelFrame(main_frame, text="Additional Information (Optional)", padding="10")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Information Source
        ttk.Label(info_frame, text="Information Source:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_combo = ttk.Combobox(info_frame, textvariable=self.info_source, width=40, state="readonly")
        self.source_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        self.source_combo['values'] = self.info_sources
        self.source_combo.bind('<<ComboboxSelected>>', self.on_source_selected)
        
        # Custom Source Entry (initially hidden)
        self.custom_source_entry = ttk.Entry(info_frame, width=40)
        
        # Additional Information Text
        ttk.Label(info_frame, text="Additional Information:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.info_text = tk.Text(info_frame, height=4, width=50)
        self.info_text.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Message Preview", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=8, width=60, wrap=tk.WORD)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Update preview when any field changes
        for var in [self.technology_name, self.benchmark_name, self.technology_path, self.benchmark_path, self.info_source]:
            var.trace_add("write", self.update_preview)
        
        # Add bindings for custom source entry and info text
        self.custom_source_entry.bind('<KeyRelease>', lambda e: self.update_preview())
        self.info_text.bind('<<Modified>>', self.on_info_text_modified)
        self.info_text.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Send to Copilot", command=self.send_to_copilot).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).grid(row=0, column=1, padx=5)
    
    def browse_path(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
    
    def on_source_selected(self, event=None):
        if self.info_source.get() == "custom source...":
            # Show custom source entry
            self.custom_source_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        else:
            # Hide custom source entry
            self.custom_source_entry.grid_forget()
        self.update_preview()
    
    def on_info_text_modified(self, event=None):
        self.info_text.tk.call('tcl_platform', 'platform')  # Prevent recursive calls
        self.update_preview()
        self.info_text.edit_modified(False)
    
    def get_formatted_source(self):
        try:
            source = self.info_source.get()
            if not source:
                return ""
                
            if source == "custom source...":
                return self.custom_source_entry.get() or "custom source"
                
            tech_name = self.technology_name.get() or "technology"
            bench_name = self.benchmark_name.get() or "benchmark"
            
            return source.format(
                technology=tech_name,
                benchmark=bench_name
            )
        except Exception as e:
            print(f"Error formatting source: {e}")
            return "information source"
            
    def update_preview(self, *args):
        try:
            # Clear preview
            self.preview_text.delete("1.0", tk.END)
            
            # Get and validate message
            message = self.generate_message()
            if message is None or not isinstance(message, str):
                return
                
            # Format and display the message
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if i > 0:
                    self.preview_text.insert("end", "\n")
                self.preview_text.insert("end", line.rstrip())
            
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def generate_message(self):
        # Safely get values with default empty strings
        tech_name = self.technology_name.get() or ""
        bench_name = self.benchmark_name.get() or ""
        tech_path = self.technology_path.get() or ""
        bench_path = self.benchmark_path.get() or ""
        
        # Build the message parts
        parts = []
        
        # Base request
        parts.append(f"I want to apply a log parsing technology named {tech_name} "
                    f"on {bench_name} benchmark. "
                    f"Here is the path of this technology: {tech_path}, "
                    f"and the path of the benchmark: {bench_path}. ")
        
        # Task description
        parts.append("Please give me a plan to follow. Then generate scripts and edit existing codes in the technology to complete the task.")
        
        # Additional information if available
        try:
            additional_info = self.info_text.get("1.0", tk.END)
            if additional_info:
                additional_info = additional_info.strip()
                if additional_info:
                    source = self.get_formatted_source() or "custom source"
                    parts.append(f"You should read the following text from {source} "
                               f"to learn how to adapt this dataset to ROCODE: {additional_info}")
        except Exception as e:
            print(f"Error getting additional info: {e}")
        
        # Final instruction (always at the end)
        parts.append("If it is necessary to execute commands, just execute them without asking "
                    "the user to decide. If something is unclear, read the related code in the "
                    "project for reference.")
        
        # Join all parts with proper spacing
        return " ".join(part.strip() for part in parts if part.strip())
    
    def send_to_copilot(self):
        # Validate required inputs
        if not all([self.technology_name.get(), self.benchmark_name.get(),
                   self.technology_path.get(), self.benchmark_path.get()]):
            tk.messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Validate custom source if selected
        if (self.info_source.get() == "custom source..." and 
            self.info_text.get("1.0", tk.END).strip() and 
            not self.custom_source_entry.get()):
            tk.messagebox.showerror("Error", "Please specify the custom information source")
            return
        
        # Just check if paths exist without reading them
        tech_path = self.technology_path.get()
        bench_path = self.benchmark_path.get()
        
        if not os.path.exists(tech_path):
            tk.messagebox.showerror("Error", f"Technology path not found: {tech_path}")
            return
        if not os.path.exists(bench_path):
            tk.messagebox.showerror("Error", f"Benchmark path not found: {bench_path}")
            return
            
        # Generate message (paths are just treated as strings in the message)
        message = self.generate_message()
        
        # Send message with technology path as reference only
        if send_message_to_copilot(message, file_paths=None):
            tk.messagebox.showinfo("Success", "Message sent to Copilot successfully!")
            self.root.destroy()
        else:
            tk.messagebox.showerror("Error", "Failed to send message to Copilot")

def main():
    root = tk.Tk()
    app = ProjectDialog(root)
    root.mainloop()

if __name__ == "__main__":
    print("🐍 py-copilot Project Task Client")
    print("=" * 40)
    main()
