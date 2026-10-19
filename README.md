# Maze Solver using A* Search

## 📌 Project Overview
A Python application that generates random mazes and solves them using the A* Search algorithm. The project includes a graphical interface that visualizes the search process in real time.

## ✨ Features
- Random maze generation.
- A* Search algorithm to find the shortest path.
- Real-time visualization of the search process.
- Interactive GUI built with Tkinter.
- Adjustable animation speed.
- Display of explored nodes and path length.
- Generate new mazes and reset the current search.

## 🛠️ Technologies Used
- Python
- Tkinter
- `heapq` for priority queue management.
- `random` for maze generation.
- `itertools.count` for priority queue tie-breaking.

## 🧠 Algorithm
The project uses **A* Search**, an informed search algorithm that finds the shortest path by evaluating:

`f(n) = g(n) + h(n)`

Where:
- `g(n)` is the cost from the start node to the current node.
- `h(n)` is the estimated cost from the current node to the goal, calculated using Manhattan distance.

The algorithm explores four possible directions: up, down, left, and right.

## 🚀 Getting Started

### Requirements
- Python 3.x
- Tkinter (usually included with Python)

No external libraries are required.

### Run the Project

1. Clone the repository:

   ```bash
   git clone <repository-url>
