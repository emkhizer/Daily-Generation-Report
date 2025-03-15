import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os
import csv

class DailyGenerationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Generation Calculator")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        # Data storage
        self.data = {}
        self.current_date = datetime.date.today()
        self.data_file = "generation_data.csv"

        # Load existing data if available
        self.load_data()

        # Create the main UI
        self.create_widgets()

    def create_widgets(self):
        # Main input frame
        self.input_frame = ttk.LabelFrame(self.root, text="Daily Input")
        self.input_frame.pack(fill="x", expand=False, padx=10, pady=10)

        # Diesel, Gas Engine, HFO input fields
        ttk.Label(self.input_frame, text="Diesel (L):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.diesel_entry = ttk.Entry(self.input_frame, width=15)
        self.diesel_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Gas Engine (kWh):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.gas_entry = ttk.Entry(self.input_frame, width=15)
        self.gas_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.input_frame, text="HFO (L):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hfo_entry = ttk.Entry(self.input_frame, width=15)
        self.hfo_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.add_btn = ttk.Button(button_frame, text="Add Entry", command=self.add_entry)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_entries)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Report frame
        self.report_frame = ttk.LabelFrame(self.root, text="Generation Reports")
        self.report_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook for table, chart, and summary
        self.notebook = ttk.Notebook(self.report_frame)
        self.notebook.pack(fill="both", expand=True)

        # Table frame
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Data Table")

        # Chart frame
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Chart View")

        # Summary frame
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")

        # Export/Import buttons
        self.export_btn = ttk.Button(self.report_frame, text="Export Report", command=self.export_report)
        self.export_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        self.import_btn = ttk.Button(self.report_frame, text="Import Data", command=self.import_data)
        self.import_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # Initialize table and chart
        self.create_table()
        self.create_chart()
        self.update_summary()

    def create_table(self):
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Create treeview
        columns = ("date", "diesel", "gas", "hfo")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")

        # Define headings
        self.tree.heading("date", text="Date")
        self.tree.heading("diesel", text="Diesel (L)")
        self.tree.heading("gas", text="Gas Engine (kWh)")
        self.tree.heading("hfo", text="HFO (L)")

        # Define columns
        self.tree.column("date", width=100)
        self.tree.column("diesel", width=100)
        self.tree.column("gas", width=100)
        self.tree.column("hfo", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Populate table with data
        self.update_table()

    def create_chart(self):
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not self.data:
            ttk.Label(self.chart_frame, text="No data available to display").pack(pady=50)
            return

        # Create a figure and plot
        fig, ax = plt.subplots(figsize=(8, 5))

        # Convert data to DataFrame for easier plotting
        df = pd.DataFrame(self.data.values())
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Plot diesel, gas, and HFO
        ax.plot(df['date'], df['diesel'].astype(float), marker='o', label="Diesel (L)")
        ax.plot(df['date'], df['gas'].astype(float), marker='o', label="Gas Engine (kWh)")
        ax.plot(df['date'], df['hfo'].astype(float), marker='o', label="HFO (L)")

        # Format the plot
        ax.set_title("Daily Generation Report")
        ax.set_xlabel("Date")
        ax.set_ylabel("Generation")
        ax.legend()
        fig.autofmt_xdate()

        # Create a canvas to display the plot
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_summary(self):
        # Clear existing summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        if not self.data:
            ttk.Label(self.summary_frame, text="No data available to display").pack(pady=50)
            return

        # Convert data to DataFrame for analysis
        df = pd.DataFrame(self.data.values())
        df['diesel'] = df['diesel'].astype(float)
        df['gas'] = df['gas'].astype(float)
        df['hfo'] = df['hfo'].astype(float)

        # Create summary frame
        summary_container = ttk.Frame(self.summary_frame)
        summary_container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Calculate statistics
        ttk.Label(summary_container, text="Summary Statistics", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10, sticky="w")

        ttk.Label(summary_container, text="Total Diesel (L):").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Label(summary_container, text=f"{df['diesel'].sum()}").grid(row=1, column=1, sticky="w")

        ttk.Label(summary_container, text="Total Gas Engine (kWh):").grid(row=2, column=0, sticky="w", padx=20)
        ttk.Label(summary_container, text=f"{df['gas'].sum()}").grid(row=2, column=1, sticky="w")

        ttk.Label(summary_container, text="Total HFO (L):").grid(row=3, column=0, sticky="w", padx=20)
        ttk.Label(summary_container, text=f"{df['hfo'].sum()}").grid(row=3, column=1, sticky="w")

    def add_entry(self):
        try:
            diesel = self.diesel_entry.get()
            gas = self.gas_entry.get()
            hfo = self.hfo_entry.get()

            # Validate inputs
            if not diesel or not gas or not hfo:
                messagebox.showerror("Error", "All fields are required")
                return

            try:
                # Validate numeric values
                float(diesel)
                float(gas)
                float(hfo)
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values")
                return

            # Create a unique ID for this entry
            entry_id = f"{self.current_date.strftime('%Y-%m-%d')}_{len(self.data)}"

            # Add to data dictionary
            self.data[entry_id] = {
                "date": self.current_date.strftime('%Y-%m-%d'),
                "diesel": diesel,
                "gas": gas,
                "hfo": hfo
            }

            # Update displays
            self.update_table()
            self.create_chart()
            self.update_summary()
            self.save_data()

            # Clear inputs
            self.clear_entries()

            messagebox.showinfo("Success", "Entry added successfully")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_entries(self):
        self.diesel_entry.delete(0, tk.END)
        self.gas_entry.delete(0, tk.END)
        self.hfo_entry.delete(0, tk.END)

    def update_table(self):
        # Clear existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort data by date
        sorted_data = sorted(self.data.values(), key=lambda x: x['date'], reverse=True)

        # Add entries to table
        for entry in sorted_data:
            self.tree.insert("", tk.END, values=(
                entry['date'],
                entry['diesel'],
                entry['gas'],
                entry['hfo']
            ))

    def save_data(self):
        with open(self.data_file, mode='w', newline='') as file:
            fieldnames = ["date", "diesel", "gas", "hfo"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data.values():
                writer.writerow(entry)

    def load_data(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entry_id = f"{row['date']}_{len(self.data)}"
                self.data[entry_id] = {
                    "date": row['date'],
                    "diesel": row['diesel'],
                    "gas": row['gas'],
                    "hfo": row['hfo']
                }

    def export_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        with open(file_path, mode='w', newline='') as file:
            fieldnames = ["date", "diesel", "gas", "hfo"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data.values():
                writer.writerow(entry)

        messagebox.showinfo("Success", f"Report exported to {file_path}")

    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entry_id = f"{row['date']}_{len(self.data)}"
                self.data[entry_id] = {
                    "date": row['date'],
                    "diesel": row['diesel'],
                    "gas": row['gas'],
                    "hfo": row['hfo']
                }

        # Update displays
        self.update_table()
        self.create_chart()
        self.update_summary()
        self.save_data()

        messagebox.showinfo("Success", "Data imported successfully")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DailyGenerationApp(root)
    root.mainloop()