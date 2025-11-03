import tkinter as tk
from queue import PriorityQueue
import random
import time
import threading

# Grid setup
ROWS, COLS = 20, 30
CELL_SIZE = 30

root = tk.Tk()
root.title("🚁 Delivery Drone Simulation (Color-Coded Smooth A* Pathfinding)")

canvas = tk.Canvas(root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE,
                   bg="#20232a", highlightthickness=0)
canvas.pack()

# Grid: 0 = empty, 1 = obstacle
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Random obstacles (like buildings)
for _ in range(100):
    r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
    grid[r][c] = 1

# Colors
COLOR_SETS = [
    {"drone": "#00FFFF", "start": "#A0FFFF", "target": "#007777"},  # Cyan set
    {"drone": "#FF69B4", "start": "#FFC0CB", "target": "#AA336A"},  # Pink set
    {"drone": "#00FF7F", "start": "#90EE90", "target": "#006B3C"},  # Green set
]

# Draw static grid once
for i in range(ROWS):
    for j in range(COLS):
        color = "#2f3136" if grid[i][j] == 0 else "#444c56"
        canvas.create_rectangle(j*CELL_SIZE, i*CELL_SIZE,
                                (j+1)*CELL_SIZE, (i+1)*CELL_SIZE,
                                fill=color, outline="#1f2428")

# Heuristic (Manhattan)
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# A* Pathfinding
def a_star(start, goal):
    pq = PriorityQueue()
    pq.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not pq.empty():
        _, current = pq.get()
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = current[0]+dx, current[1]+dy
            neighbor = (nx, ny)
            if 0 <= nx < ROWS and 0 <= ny < COLS and grid[nx][ny] != 1:
                temp_g = g_score[current] + 1
                if temp_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g
                    f_score[neighbor] = temp_g + heuristic(neighbor, goal)
                    pq.put((f_score[neighbor], neighbor))
    return None

# Drone setup
drones = []
for i in range(3):
    start = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
    target = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
    while grid[start[0]][start[1]] == 1 or grid[target[0]][target[1]] == 1:
        start = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
        target = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
    drones.append({
        "pos": start,
        "target": target,
        "path": [],
        "color_set": COLOR_SETS[i],
        "oval": None,
        "trail": []
    })

# Draw start & target indicators (unique for each drone)
for i, d in enumerate(drones, 1):
    sx, sy = d["pos"][1]*CELL_SIZE, d["pos"][0]*CELL_SIZE
    tx, ty = d["target"][1]*CELL_SIZE, d["target"][0]*CELL_SIZE

    # Start point (lighter tone)
    canvas.create_rectangle(sx+6, sy+6, sx+CELL_SIZE-6, sy+CELL_SIZE-6,
                            fill=d["color_set"]["start"], outline="#20232a", width=2)
    # Target point (darker tone)
    canvas.create_rectangle(tx+8, ty+8, tx+CELL_SIZE-8, ty+CELL_SIZE-8,
                            fill=d["color_set"]["target"], outline="#20232a", width=2)

# Dashboard label
status_label = tk.Label(root, text="Ready", bg="#181a1f", fg="white",
                        font=("Consolas", 12), justify="left")
status_label.pack(fill="x", padx=10, pady=5)

# Animation logic
def move_drones():
    for d in drones:
        d["path"] = a_star(d["pos"], d["target"]) or []
        # Draw initial drone
        x, y = d["pos"][1]*CELL_SIZE, d["pos"][0]*CELL_SIZE
        d["oval"] = canvas.create_oval(x+6, y+6, x+CELL_SIZE-6, y+CELL_SIZE-6,
                                       fill=d["color_set"]["drone"], outline="white")

    step = 0
    while True:
        all_reached = True
        for d in drones:
            if d["path"]:
                next_pos = d["path"].pop(0)
                d["pos"] = next_pos
                all_reached = False

                # Update drone position smoothly
                x, y = next_pos[1]*CELL_SIZE, next_pos[0]*CELL_SIZE
                canvas.coords(d["oval"], x+6, y+6, x+CELL_SIZE-6, y+CELL_SIZE-6)

                # Draw persistent trail
                trail_rect = canvas.create_rectangle(
                    x+12, y+12, x+CELL_SIZE-12, y+CELL_SIZE-12,
                    fill=d["color_set"]["drone"], outline=""
                )
                d["trail"].append(trail_rect)

        update_dashboard(step)
        root.update_idletasks()
        root.update()
        time.sleep(0.25)

        if all_reached:
            break
        step += 1

    status_label.config(text=status_label.cget("text") + "\nAll deliveries complete! ✅")

def update_dashboard(step):
    info = f"Step: {step}\nActive Drones: {len(drones)}"
    for i, d in enumerate(drones, 1):
        dist = heuristic(d["pos"], d["target"])
        info += f"\nDrone {i}: Dist → {dist}"
    status_label.config(text=info)

def start_simulation():
    threading.Thread(target=move_drones, daemon=True).start()

# Control buttons
control_frame = tk.Frame(root, bg="#181a1f")
control_frame.pack(fill="x", pady=5)
tk.Button(control_frame, text="▶ Start Simulation", command=start_simulation,
           bg="#00BFFF", fg="white", font=("Arial", 12, "bold"), padx=10).pack(side="left", padx=10)
tk.Button(control_frame, text="🔁 Reset", command=lambda: root.destroy(),
           bg="#FF4040", fg="white", font=("Arial", 12, "bold"), padx=10).pack(side="left", padx=10)

root.mainloop()
