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

def simulate_dm_scheduling(tasks):
    """Simulate Deadline Monotonic scheduling."""
    if not tasks:
        return True, []
    
    # Handle very large hyperperiods (might indicate scheduling issues)
    hyperperiod = calculate_hyperperiod(tasks)
    if hyperperiod > 1000000:  # Reasonable upper bound
        return False, []
    
    # Reset task states
    for task in tasks:
        task.preemption_count = 0
    
    # Get all task arrivals
    arrivals = get_task_arrivals(tasks, hyperperiod)
    
    current_time = 0.0
    current_task = None
    ready_queue = []  # List of active task instances
    arrival_index = 0
    
    # Time resolution for simulation (handle floating point precision)
    time_step = 0.001
    
    while current_time < hyperperiod:
        # Process all arrivals at current time
        while (arrival_index < len(arrivals) and 
               abs(arrivals[arrival_index]['time'] - current_time) < time_step/2):
            arrival = arrivals[arrival_index]
            task_instance = {
                'task': arrival['task'],
                'remaining_time': arrival['task'].execution_time,
                'absolute_deadline': arrival['absolute_deadline'],
                'arrival_time': current_time
            }
            ready_queue.append(task_instance)
            arrival_index += 1
        
        # Remove completed tasks and check for deadline misses
        ready_queue = [instance for instance in ready_queue 
                      if instance['remaining_time'] > 0.001]  # Use small epsilon
        
        # Check for deadline violations
        for instance in ready_queue:
            if current_time >= instance['absolute_deadline']:
                return False, []
        
        if not ready_queue:
            # No ready tasks, advance to next arrival
            if arrival_index < len(arrivals):
                current_time = arrivals[arrival_index]['time']
            else:
                break
            continue
        
        # Sort ready queue by deadline (DM scheduling)
        ready_queue.sort(key=lambda x: x['absolute_deadline'])
        
        # Select highest priority task
        next_task_instance = ready_queue[0]
        
        # Check for preemption
        if (current_task is None or 
            current_task['task'] != next_task_instance['task'] or
            current_task['arrival_time'] != next_task_instance['arrival_time']):
            
            if current_task is not None:
                # Count preemption for the task being preempted
                current_task['task'].preemption_count += 1
            
            current_task = next_task_instance
        
        # Determine next event time
        next_event_time = current_time + time_step
        
        # Check for next arrival
        if arrival_index < len(arrivals):
            next_event_time = min(next_event_time, arrivals[arrival_index]['time'])
        
        # Check for task completion
        if current_task['remaining_time'] <= next_event_time - current_time + 0.0001:
            next_event_time = current_time + current_task['remaining_time']
        
        # Execute current task
        execution_time = next_event_time - current_time
        current_task['remaining_time'] -= execution_time
        
        # If task completes, remove it from current_task
        if current_task['remaining_time'] <= 0.001:
            current_task = None
        
        current_time = next_event_time
    
    # Check if all tasks completed successfully
    for instance in ready_queue:
        if instance['remaining_time'] > 0.001:
            return False, []
    
    # Collect preemption counts in task order
    preemption_counts = [task.preemption_count for task in tasks]
    
    return True, preemption_counts

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
    
    schedulable, preemption_counts = simulate_dm_scheduling(tasks)
    
    if schedulable:
        print("1")
        print(",".join(map(str, preemption_counts)))
    else:
        print("0")
        print()

if __name__ == "__main__":
    main()