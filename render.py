# render.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Render:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Configure root window's grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        # Left sidebar frame
        self.sidebar = ttk.Frame(self.root, padding="10")
        self.sidebar.grid(row=0, column=0, sticky="NSWE")

        # Main canvas frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=1, sticky="NSWE")

        # Canvas for maze visualization
        self.canvas = tk.Canvas(self.main_frame, width=600, height=600, bg='white')
        self.canvas.pack(fill="both", expand=True)

        # Populate sidebar with controls
        self.create_sidebar_controls()

    def create_sidebar_controls(self):
        # Maze Parameters Label
        params_label = ttk.Label(self.sidebar, text="Maze Parameters", font=("Helvetica", 12, "bold"))
        params_label.pack(pady=(0, 10))

        # Rows Entry
        ttk.Label(self.sidebar, text="Rows:").pack(anchor='w')
        self.rows_entry = ttk.Entry(self.sidebar)
        self.rows_entry.insert(0, "31")  # Default value
        self.rows_entry.pack(fill='x', pady=5)

        # Columns Entry
        ttk.Label(self.sidebar, text="Columns:").pack(anchor='w')
        self.cols_entry = ttk.Entry(self.sidebar)
        self.cols_entry.insert(0, "31")  # Default value
        self.cols_entry.pack(fill='x', pady=5)

        # Dead Ends Scale
        ttk.Label(self.sidebar, text="Dead Ends:").pack(anchor='w')
        self.dead_ends_scale = ttk.Scale(self.sidebar, from_=1, to=10, orient='horizontal')
        self.dead_ends_scale.set(10)  # Default value
        self.dead_ends_scale.pack(fill='x', pady=5)

        # Branching Factor Scale
        ttk.Label(self.sidebar, text="Branching Factor:").pack(anchor='w')
        self.branching_factor_scale = ttk.Scale(self.sidebar, from_=1, to=10, orient='horizontal')  # Adjust max as needed
        self.branching_factor_scale.set(3)  # Default value
        self.branching_factor_scale.pack(fill='x', pady=5)

        # Connectedness Scale 
        ttk.Label(self.sidebar, text="Connectedness (%):").pack(anchor='w')
        self.connectedness_scale = ttk.Scale(self.sidebar, from_=1, to=9.9, orient='horizontal')  # Scale ranges from 1 to 9 for 10% to 90%
        self.connectedness_scale.set(7)  # Default value is 7, representing 70%
        self.connectedness_scale.pack(fill='x', pady=5)

        # Maze Generation Algorithm Dropdown
        ttk.Label(self.sidebar, text="Generation Algorithm:").pack(anchor='w', pady=(10, 0))
        self.gen_algorithm_var = tk.StringVar()
        self.gen_algorithm_combobox = ttk.Combobox(self.sidebar, textvariable=self.gen_algorithm_var, state="readonly")
        self.gen_algorithm_combobox['values'] = ("Recursive Backtracker", "Prim's")
        self.gen_algorithm_combobox.current(0)
        self.gen_algorithm_combobox.pack(fill='x', pady=5)

        # Seed Entry
        ttk.Label(self.sidebar, text="Seed (optional):").pack(anchor='w', pady=(10, 0))
        self.seed_entry = ttk.Entry(self.sidebar)
        self.seed_entry.pack(fill='x', pady=5)

        # Wall Density Scale
        ttk.Label(self.sidebar, text="Wall Density:").pack(anchor='w', pady=(10, 0))
        self.density_scale = ttk.Scale(self.sidebar, from_=0, to=1, orient='horizontal')
        self.density_scale.set(0.3)  # Default value
        self.density_scale.pack(fill='x', pady=5)

        # Generate Maze Button
        self.generate_button = ttk.Button(self.sidebar, text="Generate Maze", command=self.app.generate_maze)
        self.generate_button.pack(fill='x', pady=(10, 10))

        # Algorithm Selection Dropdown for Solving
        ttk.Label(self.sidebar, text="Select Algorithm:").pack(anchor='w')
        self.algorithm_var = tk.StringVar()
        self.algorithm_combobox = ttk.Combobox(self.sidebar, textvariable=self.algorithm_var, state="readonly")
        self.algorithm_combobox['values'] = ("BFS", "DFS", "A*")
        self.algorithm_combobox.current(0)
        self.algorithm_combobox.pack(fill='x', pady=5)

        # Start Button
        self.start_button = ttk.Button(self.sidebar, text="Start", command=self.app.solve_maze)
        self.start_button.pack(fill='x', pady=(20, 5))

        # Stop Button
        self.stop_button = ttk.Button(self.sidebar, text="Stop", command=self.app.stop_solving)
        self.stop_button.pack(fill='x', pady=5)

        # Timer Label
        self.timer_label = ttk.Label(self.sidebar, text="00:00", font=("Helvetica", 14))
        self.timer_label.pack(pady=(20, 0))

    def update_timer_label(self, time_str):
        self.timer_label.config(text=time_str)

    def get_maze_parameters(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            dead_ends = int(self.dead_ends_scale.get())
            branching_factor = int(self.branching_factor_scale.get())
            generation_algorithm = self.gen_algorithm_var.get()
            connectedness = int(self.connectedness_scale.get()) * 10  # Convert the scale to percentage (e.g., 7 => 70%)
            seed_input = self.seed_entry.get()
            if seed_input == "":
                seed = None
            else:
                seed = int(seed_input)
            wall_density = float(self.density_scale.get())

            # Ensure rows and cols are odd numbers
            if rows % 2 == 0:
                rows += 1
            if cols % 2 == 0:
                cols += 1
        
            # Store original values to check for changes
            original_rows = rows
            original_cols = cols

            # Strict 1:1 or 1:2/2:1 ratio enforcement
            if abs(rows / cols - 1) < abs((rows / (cols * 2)) - 1) and abs(rows / cols - 1) < abs(((rows * 2) / cols) - 1):
                # Enforce 1:1 ratio
                cols = rows
            elif abs((rows / (cols * 2)) - 1) < abs(((rows * 2) / cols) - 1):
                # Enforce 1:2 ratio (rows:cols)
                cols = max(1, rows * 2)
            else:
                # Enforce 2:1 ratio (rows:cols)
                rows = max(1, cols * 2)

            # Update the row and column input fields only if changes were made
            if rows != original_rows or cols != original_cols:
                self.rows_entry.delete(0, tk.END)
                self.rows_entry.insert(0, str(rows))
                self.cols_entry.delete(0, tk.END)
                self.cols_entry.insert(0, str(cols))

                # Display message only when adjustments were made
                messagebox.showinfo("Adjusted Dimensions", 
                    f"The row-to-column ratio was adjusted to match the closest ratio (1:1, 1:2, or 2:1).\n\n"
                    f"New Dimensions: {rows} rows, {cols} columns.")

            return {
                'rows': rows,
                'cols': cols,
                'dead_ends': dead_ends,
                'branching_factor': branching_factor,
                'connectedness': connectedness,
                'generation_algorithm': generation_algorithm,
                'seed': seed,
                'wall_density': wall_density
            }
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid values for all parameters.\n\n"
                                                 "Ensure that Rows and Columns are integers.\n"
                                                 "Seed (if provided) should be an integer.")
            return None

    def update_algorithm_selection(self):
        return self.algorithm_var.get()

    def draw_maze(self, maze):
        self.canvas.delete("all")
        rows, cols = maze.shape

        # Calculate cell size and allow small margins for separation
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows

        for r in range(rows):
            for c in range(cols):
                x0 = c * cell_width
                y0 = r * cell_height
                x1 = x0 + cell_width - 1  # Slightly reduce size to restore previous look
                y1 = y0 + cell_height - 1  # Slightly reduce size to restore previous look
                if maze[r][c] == 1:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="black", outline="")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="")

        # Mark start and end points
        self.canvas.create_rectangle(1 * cell_width, 1 * cell_height,
                                     2 * cell_width, 2 * cell_height, fill="green", outline="")
        self.canvas.create_rectangle((cols - 2) * cell_width, (rows - 2) * cell_height,
                                     (cols - 1) * cell_width, (rows - 1) * cell_height, fill="red", outline="")

    def highlight_cell(self, cell, color):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell

        # Skip start and end
        if (r, c) == (1, 1) or (r, c) == (rows - 2, cols - 2):
            return

        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height

        # Overlay the cell with the specified color
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

    def draw_path(self, path):
        if not path:
            return
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows

        for cell in path:
            r, c = cell
            x0 = c * cell_width
            y0 = r * cell_height
            x1 = x0 + cell_width
            y1 = y0 + cell_height
            # Avoid overwriting start and end
            if cell != (1, 1) and cell != (rows - 2, cols - 2):
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")

        # Re-mark start and end to ensure their colors remain
        self.canvas.create_rectangle(1 * cell_width, 1 * cell_height,
                                     2 * cell_width, 2 * cell_height, fill="green", outline="")
        self.canvas.create_rectangle((cols - 2) * cell_width, (rows - 2) * cell_height,
                                     (cols - 1) * cell_width, (rows - 1) * cell_height, fill="red", outline="")


    def mark_visited(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="lightblue", outline="")

    def mark_frontier(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="orange", outline="")

    def mark_path(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")

