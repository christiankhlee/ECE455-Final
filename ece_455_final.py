import sys

class Task:
    def __init__(self, execution_time, period, deadline, task_id):
        self.execution_time = float(execution_time)
        self.period = float(period)
        self.deadline = float(deadline)
        self.task_id = task_id

    def __repr__(self):
        return f"T{self.task_id}(e={self.execution_time}, P={self.period}, D={self.deadline})"

def read_tasks(filename):
    """Read tasks from input file."""
    tasks = []
    try:
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) != 3:
                        raise ValueError(f"Invalid format on line {i+1}")
                    execution_time, period, deadline = map(float, parts)
                    if execution_time <= 0 or period <= 0 or deadline <= 0:
                        raise ValueError(f"All values must be positive on line {i+1}")
                    tasks.append(Task(execution_time, period, deadline, i))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return tasks

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ece_455_final.py <input_file>", file=sys.stderr)
        sys.exit(1)
    
    filename = sys.argv[1]
    tasks = read_tasks(filename)
    
    # TODO: Implement scheduling simulation
    print("Tasks loaded successfully:")
    for task in tasks:
        print(f"  {task}")

if __name__ == "__main__":
    main()