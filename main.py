
import tkinter as tk
import random
import heapq
from itertools import count


# ===================== CONFIGURATION =====================

ROWS = 21
COLS = 31

BG = "#0B1120"
PANEL = "#111B2E"
CARD = "#17243A"
GRID_LINE = "#334155"
EMPTY = "#E2E8F0"
WALL = "#29364B"
START_COLOR = "#22C55E"
GOAL_COLOR = "#F43F5E"
EXPLORED_COLOR = "#38BDF8"
PATH_COLOR = "#FBBF24"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
ACCENT = "#818CF8"


# ===================== MAZE GENERATOR =====================

def generate_maze():
    maze = [["#" for _ in range(COLS)] for _ in range(ROWS)]

    start = (1, 1)
    goal = (ROWS - 2, COLS - 2)

    maze[start[0]][start[1]] = "."

    stack = [start]
    visited = {start}

    while stack:
        r, c = stack[-1]
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)

        neighbors = []

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if (
                1 <= nr < ROWS - 1
                and 1 <= nc < COLS - 1
                and (nr, nc) not in visited
            ):
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = neighbors[0]

            maze[r + dr // 2][c + dc // 2] = "."
            maze[nr][nc] = "."

            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    maze[start[0]][start[1]] = "S"
    maze[goal[0]][goal[1]] = "G"

    return maze


MAZE = generate_maze()
START_POS = (1, 1)
GOAL_POS = (ROWS - 2, COLS - 2)


# ===================== A* SEARCH =====================

def heuristic(position):
    r, c = position
    gr, gc = GOAL_POS
    return abs(r - gr) + abs(c - gc)


def get_neighbors(position):
    r, c = position

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc

        if (
            0 <= nr < ROWS
            and 0 <= nc < COLS
            and MAZE[nr][nc] != "#"
        ):
            yield (nr, nc)


def run_astar():
    sequence = count()

    frontier = [
        (heuristic(START_POS), next(sequence), START_POS)
    ]

    g_score = {START_POS: 0}
    parents = {}
    closed = set()
    explored = []

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current in closed:
            continue

        if current == GOAL_POS:
            path = [current]

            while current in parents:
                current = parents[current]
                path.append(current)

            path.reverse()
            return explored, path

        closed.add(current)
        explored.append(current)

        for neighbor in get_neighbors(current):
            if neighbor in closed:
                continue

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                parents[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = tentative_g + heuristic(neighbor)

                heapq.heappush(
                    frontier,
                    (f_score, next(sequence), neighbor)
                )

    return explored, None


# ===================== APPLICATION =====================

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Pathfinder | AI Lab")
        self.root.geometry("1200x900")
        self.root.minsize(760, 650)
        self.root.configure(bg=BG)

        self.explored = set()
        self.path = set()
        self.animation_events = []

        self.after_id = None
        self.running = False
        self.finished = False
        self.cell_size = 20

        self.explored_count = 0
        self.path_length = 0

        self.build_interface()
        self.draw_maze()

    # ===================== UI =====================

    def build_interface(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(18, 12))

        tk.Label(
            header,
            text="AI LAB  /  PATHFINDING",
            font=("Segoe UI", 10, "bold"),
            fg=ACCENT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="A* Maze Pathfinder",
            font=("Segoe UI", 25, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w", pady=(3, 0))

        tk.Label(
            header,
            text="Random mazes • Live exploration • Shortest path",
            font=("Segoe UI", 11),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=(3, 0))

        stats = tk.Frame(self.root, bg=BG)
        stats.pack(fill="x", padx=28, pady=(0, 12))

        self.explored_var = tk.StringVar(value="0")
        self.path_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(value="Ready to explore")

        self.create_stat(
            stats, "CELLS EXPLORED", self.explored_var, EXPLORED_COLOR
        )
        self.create_stat(
            stats, "PATH LENGTH", self.path_var, PATH_COLOR
        )
        self.create_stat(
            stats, "STATUS", self.status_var, START_COLOR
        )

        board = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground="#26354C",
            highlightthickness=1
        )
        board.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 12)
        )

        self.canvas = tk.Canvas(
            board,
            bg=PANEL,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", self.on_resize)

        legend = tk.Frame(self.root, bg=BG)
        legend.pack(fill="x", padx=28, pady=(0, 12))

        self.create_legend(legend, START_COLOR, "Start")
        self.create_legend(legend, GOAL_COLOR, "Goal")
        self.create_legend(legend, WALL, "Wall")
        self.create_legend(legend, EXPLORED_COLOR, "Explored")
        self.create_legend(legend, PATH_COLOR, "Shortest path")

        controls = tk.Frame(self.root, bg=PANEL)
        controls.pack(fill="x", padx=28, pady=(0, 20))

        button_frame = tk.Frame(controls, bg=PANEL)
        button_frame.pack(side="left", padx=12, pady=12)

        self.start_button = tk.Button(
            button_frame,
            text="▶  Start Search",
            command=self.start_search,
            bg=ACCENT,
            fg="#FFFFFF",
            activebackground="#6366F1",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2"
        )
        self.start_button.pack(side="left", padx=(0, 7))

        self.reset_button = tk.Button(
            button_frame,
            text="↻  Reset",
            command=self.reset,
            bg=CARD,
            fg=TEXT,
            activebackground="#26354C",
            activeforeground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2"
        )
        self.reset_button.pack(side="left", padx=(0, 7))

        self.new_maze_button = tk.Button(
            button_frame,
            text="✦  New Maze",
            command=self.new_maze,
            bg="#0F766E",
            fg="#FFFFFF",
            activebackground="#115E59",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2"
        )
        self.new_maze_button.pack(side="left")

        speed_frame = tk.Frame(controls, bg=PANEL)
        speed_frame.pack(side="right", padx=14, pady=8)

        tk.Label(
            speed_frame,
            text="ANIMATION SPEED",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(anchor="w")

        self.speed = tk.IntVar(value=100)

        tk.Scale(
            speed_frame,
            from_=20,
            to=400,
            orient="horizontal",
            variable=self.speed,
            bg=PANEL,
            fg=TEXT,
            troughcolor=CARD,
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            length=160,
            showvalue=False
        ).pack()

    def create_stat(self, parent, title, variable, color):
        card = tk.Frame(parent, bg=CARD, padx=14, pady=8)
        card.pack(side="left", fill="both", expand=True, padx=(0, 7))

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(anchor="w")

        tk.Label(
            card,
            textvariable=variable,
            font=("Segoe UI", 17, "bold"),
            fg=color,
            bg=CARD
        ).pack(anchor="w", pady=(2, 0))

    def create_legend(self, parent, color, label):
        item = tk.Frame(parent, bg=BG)
        item.pack(side="left", padx=(0, 16))

        marker = tk.Canvas(
            item,
            width=12,
            height=12,
            bg=BG,
            highlightthickness=0
        )
        marker.pack(side="left", padx=(0, 5))

        marker.create_rectangle(
            1, 1, 11, 11,
            fill=color,
            outline=color
        )

        tk.Label(
            item,
            text=label,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG
        ).pack(side="left")

    # ===================== DRAWING =====================

    def on_resize(self, event=None):
        if not self.running:
            self.draw_maze()

    def draw_maze(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 50 or height < 50:
            return

        padding = 8

        self.cell_size = max(
            1,
            min(
                (width - 2 * padding) / COLS,
                (height - 2 * padding) / ROWS
            )
        )

        grid_width = self.cell_size * COLS
        grid_height = self.cell_size * ROWS

        x_offset = (width - grid_width) / 2
        y_offset = (height - grid_height) / 2

        for r in range(ROWS):
            for c in range(COLS):
                x1 = x_offset + c * self.cell_size
                y1 = y_offset + r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                position = (r, c)
                cell = MAZE[r][c]

                if position == START_POS:
                    color = START_COLOR
                elif position == GOAL_POS:
                    color = GOAL_COLOR
                elif cell == "#":
                    color = WALL
                elif position in self.path:
                    color = PATH_COLOR
                elif position in self.explored:
                    color = EXPLORED_COLOR
                else:
                    color = EMPTY

                inset = max(0.7, self.cell_size * 0.06)

                self.canvas.create_rectangle(
                    x1 + inset,
                    y1 + inset,
                    x2 - inset,
                    y2 - inset,
                    fill=color,
                    outline=color
                )

                if self.cell_size >= 19 and cell in ("S", "G"):
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=cell,
                        fill="#FFFFFF",
                        font=(
                            "Segoe UI",
                            max(8, int(self.cell_size * 0.35)),
                            "bold"
                        )
                    )

    # ===================== SEARCH ANIMATION =====================

    def start_search(self):
        if self.running:
            return

        if self.finished:
            self.reset()

        self.running = True
        self.finished = False

        self.explored.clear()
        self.path.clear()

        self.explored_count = 0
        self.path_length = 0

        explored, path = run_astar()

        self.animation_events = [
            ("explored", position)
            for position in explored
        ]

        if path:
            self.animation_events.extend(
                ("path", position)
                for position in path
                if position not in (START_POS, GOAL_POS)
            )

            self.path_length = len(path) - 1
            self.path_var.set(str(self.path_length))
            self.status_var.set("Searching...")
        else:
            self.path_var.set("No path")
            self.status_var.set("No solution")

        self.explored_var.set("0")
        self.start_button.configure(state="disabled")

        self.animate_step()

    def animate_step(self):
        self.after_id = None

        if not self.animation_events:
            self.running = False
            self.finished = True

            self.start_button.configure(state="normal")

            if self.path_var.get() != "No path":
                self.status_var.set("Path found!")
            else:
                self.status_var.set("No solution")

            self.draw_maze()
            return

        event_type, position = self.animation_events.pop(0)

        if event_type == "explored":
            self.explored.add(position)
            self.explored_count += 1
            self.explored_var.set(str(self.explored_count))

        elif event_type == "path":
            self.path.add(position)

        self.draw_maze()

        delay = max(1, 100 - self.speed.get())

        self.after_id = self.root.after(
            delay,
            self.animate_step
        )

    # ===================== CONTROLS =====================

    def reset(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.running = False
        self.finished = False
        self.animation_events.clear()

        self.explored.clear()
        self.path.clear()

        self.explored_count = 0
        self.path_length = 0

        self.explored_var.set("0")
        self.path_var.set("—")
        self.status_var.set("Ready to explore")

        self.start_button.configure(state="normal")
        self.draw_maze()

    def new_maze(self):
        global MAZE, START_POS, GOAL_POS

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.running = False
        self.finished = False
        self.animation_events.clear()

        MAZE = generate_maze()
        START_POS = (1, 1)
        GOAL_POS = (ROWS - 2, COLS - 2)

        self.explored.clear()
        self.path.clear()

        self.explored_count = 0
        self.path_length = 0

        self.explored_var.set("0")
        self.path_var.set("—")
        self.status_var.set("New maze generated")

        self.start_button.configure(state="normal")
        self.draw_maze()


# ===================== RUN =====================

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
