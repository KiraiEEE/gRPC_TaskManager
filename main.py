import tkinter as tk
from tkinter import messagebox, ttk
import grpc
from datetime import datetime
from tkcalendar import DateEntry
import sys
import os

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
        self.root = tk.Tk()
        self.root.title("Task Manager")
        self.root.geometry("600x700")
        
        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = taskmanager_pb2_grpc.TaskManagerStub(self.channel)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to gRPC server: {str(e)}")
            self.root.destroy()
            return
        
        self.create_widgets()

    def create_widgets(self):
        # Task Form
        self.form_frame = tk.LabelFrame(self.root, text="Task Details", padx=10, pady=10)
        self.form_frame.pack(pady=10, padx=10, fill="x")
        
        # Title
        tk.Label(self.form_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(self.form_frame, width=40)
        self.title_entry.grid(row=0, column=1, pady=5)
        
        # Description
        tk.Label(self.form_frame, text="Description:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_text = tk.Text(self.form_frame, width=30, height=3)
        self.desc_text.grid(row=1, column=1, pady=5)
        
        # Status
        tk.Label(self.form_frame, text="Status:").grid(row=2, column=0, sticky="w", pady=5)
        self.status_combo = ttk.Combobox(self.form_frame, 
                                       values=["Not Started", "In Progress", "Completed"],
                                       state="readonly")
        self.status_combo.set("Not Started")
        self.status_combo.grid(row=2, column=1, pady=5, sticky="w")
        
        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)
        
        tk.Button(self.button_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="List Tasks", command=self.list_tasks).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Delete Task", command=self.delete_selected_task).pack(side=tk.LEFT, padx=5)
        
        # Task list with Treeview
        self.tree = ttk.Treeview(self.root, columns=("ID", "Title", "Description", "Status"), 
                                show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=150)
        self.tree.column("Description", width=250)
        self.tree.column("Status", width=100)
        
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

    def add_task(self):
        title = self.title_entry.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        status = self.status_combo.get()
        
        if title and description:
            try:
                request = taskmanager_pb2.Task(
                    title=title,
                    description=description,
                    status=status
                )
                response = self.stub.AddTask(request)
                messagebox.showinfo("Success", "Task added successfully!")
                self.clear_form()
                self.list_tasks()  # Refresh the list
            except grpc.RpcError as e:
                messagebox.showerror("Error", f"Failed to add task: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please fill in both title and description!")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.status_combo.set("Not Started")

    def delete_selected_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
            
        try:
            task_id = self.tree.item(selected_item[0])['values'][0]
            request = taskmanager_pb2.TaskRequest(taskId=task_id)
            self.stub.DeleteTask(request)
            self.list_tasks()  # Refresh the list
            messagebox.showinfo("Success", "Task deleted successfully!")
        except grpc.RpcError as e:
            messagebox.showerror("Error", f"Failed to delete task: {str(e)}")

    def list_tasks(self):
        try:
            response = self.stub.ListTasks(taskmanager_pb2.Empty())
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Add new items
            for task in response.tasks:
                self.tree.insert("", tk.END, values=(
                    task.id,
                    task.title,
                    task.description,
                    task.status
                ))
        except grpc.RpcError as e:
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
