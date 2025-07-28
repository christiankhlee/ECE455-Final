import sys
from fractions import Fraction

class Task:
    def __init__(self, execution_time, period, deadline, task_id):
        self.execution_time = float(execution_time)
        self.period = float(period)
        self.deadline = float(deadline)
        self.task_id = task_id
        self.preemption_count = 0

    def __repr__(self):
        return f"T{self.task_id}(e={self.execution_time}, P={self.period}, D={self.deadline})"

def gcd(a, b):
    """Calculate GCD."""
    frac_a = Fraction(a).limit_denominator(1000)
    frac_b = Fraction(b).limit_denominator(1000)
    
    while frac_b:
        frac_a, frac_b = frac_b, frac_a % frac_b
    return float(frac_a)

def lcm(a, b):
    """Calculate LCM of two numbers."""
    return abs(a * b) / gcd(a, b)

def calculate_hyperperiod(tasks):
    """Calculate the hyperperiod."""
    if not tasks:
        return 0
    
    hyperperiod = tasks[0].period
    for task in tasks[1:]:
        hyperperiod = lcm(hyperperiod, task.period)
    
    return hyperperiod

def get_task_arrivals(tasks, hyperperiod):
    """Generate all task arrivals within the hyperperiod."""
    arrivals = []
    
    for task in tasks:
        arrival_time = 0.0
        while arrival_time < hyperperiod:
            arrivals.append({
                'time': arrival_time,
                'task': task,
                'absolute_deadline': arrival_time + task.deadline
            })
            arrival_time += task.period
    
    # Sort by arrival time, then by deadline for tie-breaking
    arrivals.sort(key=lambda x: (x['time'], x['absolute_deadline']))
    return arrivals

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

    hyperperiod = calculate_hyperperiod(tasks)
    arrivals = get_task_arrivals(tasks, hyperperiod)

    # TODO: Implement scheduling simulation
    print("Tasks loaded successfully:")
    for task in tasks:
        print(f"  {task}")
    print(f"Hyperperiod: {hyperperiod}")
    print(f"Total arrivals in hyperperiod: {len(arrivals)}")
    
    print("\nTask arrivals:")
    for arrival in arrivals[:10]:  # Show first 10 arrivals
        print(f"  Time {arrival['time']}: {arrival['task']} (deadline: {arrival['absolute_deadline']})")
    if len(arrivals) > 10:
        print(f"  ... and {len(arrivals) - 10} more arrivals")

if __name__ == "__main__":
    main()