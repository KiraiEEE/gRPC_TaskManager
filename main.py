import tkinter as tk
from tkinter import messagebox
import grpc
from datetime import datetime
import sys
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

# Add the generated directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
generated_path = os.path.join(current_dir, 'generated', 'python')
sys.path.append(generated_path)

try:
    import taskmanager_pb2
    import taskmanager_pb2_grpc
except ImportError:
    print("Error: Could not import gRPC generated files. Please ensure they exist in the generated/python directory.")
    sys.exit(1)

class TaskManagerClient:
    def __init__(self):
        self.root = ttk.Window(
            title="Task Manager",
            themename="litera",  # Options: cosmo, flatly, journal, litera, lumen, minty, pulse, sandstone, united, yeti, etc.
            size=(800, 700),
            resizable=(True, True),
            iconphoto=""
        )
        self.root.place_window_center()
        
        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = taskmanager_pb2_grpc.TaskManagerStub(self.channel)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to gRPC server: {str(e)}")
            self.root.destroy()
            return
        
        self.create_widgets()
        self.setup_styles()

    def setup_styles(self):
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        style.configure("Treeview.Heading", font=(None, 10, "bold"))

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        # Header with app name and icon
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            header_frame, 
            text="Task Manager", 
            font=("TkDefaultFont", 16, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        
        # Task Form in a Card-like container
        form_frame = ttk.LabelFrame(
            main_frame, 
            text="Task Details", 
            padding=15, 
            bootstyle="default"
        )
        form_frame.pack(fill=X, pady=10)
        
        # Create a two-column grid
        form_frame.columnconfigure(1, weight=1)
        
        # Title
        ttk.Label(form_frame, text="Title:", font=(None, 10)).grid(row=0, column=0, sticky="w", pady=8, padx=(0, 10))
        self.title_entry = ttk.Entry(form_frame, width=50)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=8)
        
        # Description
        ttk.Label(form_frame, text="Description:", font=(None, 10)).grid(row=1, column=0, sticky="nw", pady=8, padx=(0, 10))
        self.desc_text = ScrolledText(form_frame, width=50, height=3, autohide=True)
        self.desc_text.grid(row=1, column=1, sticky="ew", pady=8)
        
        # Status
        ttk.Label(form_frame, text="Status:", font=(None, 10)).grid(row=2, column=0, sticky="w", pady=8, padx=(0, 10))
        self.status_combo = ttk.Combobox(
            form_frame,
            values=["Not Started", "In Progress", "Completed"],
            state="readonly",
            bootstyle="default"
        )
        self.status_combo.current(0)
        self.status_combo.grid(row=2, column=1, sticky="ew", pady=8)
        
        # Action Buttons in a separate frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Add Task", 
            command=self.add_task,
            bootstyle="success",
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Update Task",
            command=self.update_selected_task,
            bootstyle="info",
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Delete Task",
            command=self.delete_selected_task,
            bootstyle="danger",
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame, 
            text="Refresh",
            command=self.list_tasks,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT, padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=X, pady=(10, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_tasks())
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, fill=X, expand=YES)
        
        # Filter by status
        ttk.Label(search_frame, text="Filter:").pack(side=LEFT, padx=(10, 5))
        self.filter_combo = ttk.Combobox(
            search_frame,
            values=["All", "Not Started", "In Progress", "Completed"],
            state="readonly",
            bootstyle="default",
            width=15
        )
        self.filter_combo.current(0)
        self.filter_combo.pack(side=LEFT, padx=(0, 5))
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_tasks())
        
        # Task list with Treeview in a separate frame with border
        tree_frame = ttk.Frame(main_frame, bootstyle="default")
        tree_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Create scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
        tree_scroll_x.pack(side=BOTTOM, fill=X)
        
        # Add the Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Title", "Description", "Status"),
            show="headings",
            height=10,
            bootstyle="default",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        # Configure column widths and headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50, minwidth=50)
        self.tree.column("Title", width=150, minwidth=100)
        self.tree.column("Description", width=350, minwidth=200)
        self.tree.column("Status", width=100, minwidth=100)
        
        # Pack the Treeview and configure scrollbars
        self.tree.pack(fill=BOTH, expand=YES)
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W, 
            padding=(10, 2)
        )
        status_bar.pack(side=BOTTOM, fill=X)
        
        # Initially populate the task list
        self.list_tasks()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, values[1])
            
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", values[2])
            
            self.status_combo.set(values[3])

    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        status = self.status_combo.get()
        
        if title and description:
            try:
                self.status_var.set("Adding task...")
                request = taskmanager_pb2.Task(
                    title=title,
                    description=description,
                    status=status
                )
                response = self.stub.AddTask(request)
                self.status_var.set(f"Task added successfully: {title}")
                self.clear_form()
                self.list_tasks()  # Refresh the list
            except grpc.RpcError as e:
                self.status_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to add task: {str(e)}")
        else:
            self.status_var.set("Warning: Missing information")
            messagebox.showwarning("Warning", "Please fill in both title and description!")

    def update_selected_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to update")
            return
            
        try:
            task_id = self.tree.item(selected_item[0])['values'][0]
            title = self.title_entry.get()
            description = self.desc_text.get("1.0", tk.END).strip()
            status = self.status_combo.get()
            
            if title and description:
                request = taskmanager_pb2.Task(
                    id=task_id,
                    title=title,
                    description=description,
                    status=status
                )
                self.stub.UpdateTask(request)
                self.status_var.set(f"Task updated successfully: {title}")
                self.list_tasks()  # Refresh the list
                self.clear_form()
            else:
                messagebox.showwarning("Warning", "Please fill in both title and description!")
                
        except grpc.RpcError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to update task: {str(e)}")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.status_combo.current(0)

    def delete_selected_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
            
        try:
            task_id = self.tree.item(selected_item[0])['values'][0]
            task_title = self.tree.item(selected_item[0])['values'][1]
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Deletion", 
                f"Are you sure you want to delete task: {task_title}?"
            )
            
            if confirm:
                request = taskmanager_pb2.TaskRequest(taskId=task_id)
                self.stub.DeleteTask(request)
                self.list_tasks()  # Refresh the list
                self.clear_form()
                self.status_var.set(f"Task deleted successfully: {task_title}")
        except grpc.RpcError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete task: {str(e)}")

    def filter_tasks(self):
        search_text = self.search_var.get().lower()
        status_filter = self.filter_combo.get()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            title = str(values[1]).lower()
            desc = str(values[2]).lower()
            status = values[3]
            
            # Check if the item matches both search text and status filter
            match_search = search_text == "" or search_text in title or search_text in desc
            match_status = status_filter == "All" or status == status_filter
            
            if match_search and match_status:
                self.tree.item(item, tags=())
            else:
                self.tree.detach(item)  # Hide items that don't match

    def list_tasks(self):
        try:
            self.status_var.set("Retrieving tasks...")
            response = self.stub.ListTasks(taskmanager_pb2.Empty())
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Add new items with status-based styling
            for task in response.tasks:
                item_id = self.tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.description,
                    task.status
                ))
                
                # Apply different styles based on status
                if task.status == "Completed":
                    self.tree.item(item_id, tags=("completed",))
                elif task.status == "In Progress":
                    self.tree.item(item_id, tags=("in_progress",))
            
            # Configure tag styles
            self.tree.tag_configure("completed", background="#e8f0fe")
            self.tree.tag_configure("in_progress", background="#fff8e1")
            
            self.status_var.set(f"Found {len(response.tasks)} task(s)")
            
        except grpc.RpcError as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to list tasks: {str(e)}")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            if hasattr(self, 'channel'):
                self.channel.close()

if __name__ == "__main__":
    try:
        client = TaskManagerClient()
        client.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)