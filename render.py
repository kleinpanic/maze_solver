# render.py

import tkinter as tk
from tkinter import messagebox, ttk

from maze_solver.algorithms import ALGORITHM_REGISTRY
from maze_solver.generation import GENERATION_REGISTRY

PALETTE = {
    "bg": "#0b1117",
    "panel": "#101a25",
    "panel_2": "#121d29",
    "border": "#263546",
    "text": "#e8eef6",
    "muted": "#9fb0c3",
    "accent": "#35d0c7",
    "path": "#d84fd6",
    "frontier": "#f0b84d",
    "visited": "#79d6f2",
    "start": "#45e08e",
    "goal": "#ef5454",
    "wall": "#091017",
    "open": "#edf3f8",
}


class Render:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=PALETTE["bg"])
        self.configure_style()

        # Configure root window's grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        # Left sidebar frame
        self.sidebar = ttk.Frame(self.root, padding="16", style="Panel.TFrame")
        self.sidebar.grid(row=0, column=0, sticky="NSWE")

        # Main canvas frame
        self.main_frame = ttk.Frame(self.root, padding="16", style="Panel.TFrame")
        self.main_frame.grid(row=0, column=1, sticky="NSWE")

        # Canvas for maze visualization
        self.canvas = tk.Canvas(
            self.main_frame,
            width=680,
            height=680,
            bg=PALETTE["wall"],
            highlightthickness=1,
            highlightbackground=PALETTE["border"],
        )
        self.canvas.pack(fill="both", expand=True)

        # Populate sidebar with controls
        self.create_sidebar_controls()

    def configure_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=PALETTE["bg"], foreground=PALETTE["text"], fieldbackground=PALETTE["panel_2"])
        style.configure("Panel.TFrame", background=PALETTE["panel"])
        style.configure(
            "Section.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"], font=("Helvetica", 10, "bold")
        )
        style.configure(
            "Title.TLabel", background=PALETTE["panel"], foreground=PALETTE["text"], font=("Helvetica", 16, "bold")
        )
        style.configure("Body.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"], font=("Helvetica", 10))
        style.configure(
            "Metric.TLabel", background=PALETTE["panel"], foreground=PALETTE["text"], font=("Helvetica", 13, "bold")
        )
        style.configure("TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"])
        style.configure("TButton", background=PALETTE["panel_2"], foreground=PALETTE["text"], padding=8)
        style.map("TButton", background=[("active", PALETTE["accent"])], foreground=[("active", PALETTE["bg"])])
        style.configure("Accent.TButton", background=PALETTE["accent"], foreground=PALETTE["bg"], padding=9)
        style.configure("TEntry", fieldbackground=PALETTE["panel_2"], foreground=PALETTE["text"])
        style.configure("TCombobox", fieldbackground=PALETTE["panel_2"], foreground=PALETTE["text"])

    def create_sidebar_controls(self):
        # Maze Parameters Label
        ttk.Label(self.sidebar, text="Maze Solver Lab", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.sidebar,
            text="Generate, inspect, and solve graph mazes with the shared algorithm catalog.",
            style="Body.TLabel",
            wraplength=260,
        ).pack(anchor="w", pady=(4, 18))

        params_label = ttk.Label(self.sidebar, text="Maze Parameters", style="Section.TLabel")
        params_label.pack(anchor="w", pady=(0, 10))

        # Rows Entry
        ttk.Label(self.sidebar, text="Rows:").pack(anchor="w")
        self.rows_entry = ttk.Entry(self.sidebar)
        self.rows_entry.insert(0, "31")  # Default value
        self.rows_entry.pack(fill="x", pady=5)

        # Columns Entry
        ttk.Label(self.sidebar, text="Columns:").pack(anchor="w")
        self.cols_entry = ttk.Entry(self.sidebar)
        self.cols_entry.insert(0, "31")  # Default value
        self.cols_entry.pack(fill="x", pady=5)

        # Dead Ends Scale
        ttk.Label(self.sidebar, text="Dead Ends:").pack(anchor="w")
        self.dead_ends_scale = ttk.Scale(self.sidebar, from_=1, to=10, orient="horizontal")
        self.dead_ends_scale.set(10)  # Default value
        self.dead_ends_scale.pack(fill="x", pady=5)

        # Branching Factor Scale
        ttk.Label(self.sidebar, text="Branching Factor:").pack(anchor="w")
        self.branching_factor_scale = ttk.Scale(
            self.sidebar, from_=1, to=10, orient="horizontal"
        )  # Adjust max as needed
        self.branching_factor_scale.set(3)  # Default value
        self.branching_factor_scale.pack(fill="x", pady=5)

        # Connectedness Scale
        ttk.Label(self.sidebar, text="Connectedness (%):").pack(anchor="w")
        self.connectedness_scale = ttk.Scale(
            self.sidebar, from_=1, to=9.9, orient="horizontal"
        )  # Scale ranges from 1 to 9 for 10% to 90%
        self.connectedness_scale.set(7)  # Default value is 7, representing 70%
        self.connectedness_scale.pack(fill="x", pady=5)

        # Maze Generation Algorithm Dropdown
        ttk.Label(self.sidebar, text="Generation Algorithm:").pack(anchor="w", pady=(10, 0))
        self.gen_algorithm_var = tk.StringVar()
        self.gen_algorithm_combobox = ttk.Combobox(self.sidebar, textvariable=self.gen_algorithm_var, state="readonly")
        self.gen_algorithm_combobox["values"] = tuple(GENERATION_REGISTRY)
        self.gen_algorithm_combobox.current(0)
        self.gen_algorithm_combobox.pack(fill="x", pady=5)

        # Seed Entry
        ttk.Label(self.sidebar, text="Seed (optional):").pack(anchor="w", pady=(10, 0))
        self.seed_entry = ttk.Entry(self.sidebar)
        self.seed_entry.pack(fill="x", pady=5)

        # Wall Density Scale
        ttk.Label(self.sidebar, text="Wall Density:").pack(anchor="w", pady=(10, 0))
        self.density_scale = ttk.Scale(self.sidebar, from_=0, to=1, orient="horizontal")
        self.density_scale.set(0.3)  # Default value
        self.density_scale.pack(fill="x", pady=5)

        # Generate Maze Button
        self.generate_button = ttk.Button(
            self.sidebar, text="Generate Maze", command=self.app.generate_maze, style="Accent.TButton"
        )
        self.generate_button.pack(fill="x", pady=(10, 10))

        # Algorithm Selection Dropdown for Solving
        ttk.Label(self.sidebar, text="Select Algorithm:").pack(anchor="w")
        self.algorithm_var = tk.StringVar()
        self.algorithm_combobox = ttk.Combobox(self.sidebar, textvariable=self.algorithm_var, state="readonly")
        self.algorithm_combobox["values"] = tuple(ALGORITHM_REGISTRY)
        self.algorithm_combobox.current(0)
        self.algorithm_combobox.pack(fill="x", pady=5)
        self.algorithm_combobox.bind("<<ComboboxSelected>>", lambda _event: self.update_algorithm_panel())

        self.algorithm_info_var = tk.StringVar()
        self.algorithm_info = ttk.Label(
            self.sidebar,
            textvariable=self.algorithm_info_var,
            style="Body.TLabel",
            wraplength=260,
            justify="left",
        )
        self.algorithm_info.pack(fill="x", pady=(2, 8))

        # Start Button
        self.start_button = ttk.Button(self.sidebar, text="Start", command=self.app.solve_maze, style="Accent.TButton")
        self.start_button.pack(fill="x", pady=(20, 5))

        # Stop Button
        self.stop_button = ttk.Button(self.sidebar, text="Stop", command=self.app.stop_solving)
        self.stop_button.pack(fill="x", pady=5)

        # Timer Label
        ttk.Label(self.sidebar, text="Runtime", style="Section.TLabel").pack(anchor="w", pady=(16, 0))
        self.timer_label = ttk.Label(self.sidebar, text="00:00", style="Metric.TLabel")
        self.timer_label.pack(pady=(20, 0))
        ttk.Label(
            self.sidebar,
            text="Legend: green start, red goal, cyan visited, amber frontier, magenta final path.",
            style="Body.TLabel",
            wraplength=260,
        ).pack(anchor="w", pady=(12, 0))
        self.update_algorithm_panel()

    def update_algorithm_panel(self):
        algorithm = self.algorithm_combobox.get()
        if algorithm not in ALGORITHM_REGISTRY:
            algorithm = next(iter(ALGORITHM_REGISTRY))
            self.algorithm_var.set(algorithm)
        info = ALGORITHM_REGISTRY[algorithm]
        self.algorithm_info_var.set(
            f"{info.name}\n{info.family}\nTime {info.time_complexity} | Space {info.space_complexity}\n{info.notes}"
        )

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
            if abs(rows / cols - 1) < abs((rows / (cols * 2)) - 1) and abs(rows / cols - 1) < abs(
                ((rows * 2) / cols) - 1
            ):
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
                messagebox.showinfo(
                    "Adjusted Dimensions",
                    f"The row-to-column ratio was adjusted to match the closest ratio (1:1, 1:2, or 2:1).\n\n"
                    f"New Dimensions: {rows} rows, {cols} columns.",
                )

            return {
                "rows": rows,
                "cols": cols,
                "dead_ends": dead_ends,
                "branching_factor": branching_factor,
                "connectedness": connectedness,
                "generation_algorithm": generation_algorithm,
                "seed": seed,
                "wall_density": wall_density,
            }
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid values for all parameters.\n\n"
                "Ensure that Rows and Columns are integers.\n"
                "Seed (if provided) should be an integer.",
            )
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
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["wall"], outline="")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["open"], outline="")

        # Mark start and end points
        self.canvas.create_rectangle(
            1 * cell_width, 1 * cell_height, 2 * cell_width, 2 * cell_height, fill=PALETTE["start"], outline=""
        )
        self.canvas.create_rectangle(
            (cols - 2) * cell_width,
            (rows - 2) * cell_height,
            (cols - 1) * cell_width,
            (rows - 1) * cell_height,
            fill=PALETTE["goal"],
            outline="",
        )

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
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

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
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["path"], outline="")

        # Re-mark start and end to ensure their colors remain
        self.canvas.create_rectangle(
            1 * cell_width, 1 * cell_height, 2 * cell_width, 2 * cell_height, fill=PALETTE["start"], outline=""
        )
        self.canvas.create_rectangle(
            (cols - 2) * cell_width,
            (rows - 2) * cell_height,
            (cols - 1) * cell_width,
            (rows - 1) * cell_height,
            fill=PALETTE["goal"],
            outline="",
        )

    def mark_visited(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["visited"], outline="")

    def mark_frontier(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["frontier"], outline="")

    def mark_path(self, cell):
        rows, cols = self.app.maze.shape
        cell_width = self.canvas.winfo_width() / cols
        cell_height = self.canvas.winfo_height() / rows
        r, c = cell
        x0 = c * cell_width
        y0 = r * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PALETTE["path"], outline="")
