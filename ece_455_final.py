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

# def get_task_arrivals(tasks, hyperperiod):
#     """Generate all task arrivals within the hyperperiod."""
#     arrivals = []
    
#     for task in tasks:
#         arrival_time = 0.0
#         while arrival_time < hyperperiod:
#             arrivals.append({
#                 'time': arrival_time,
#                 'task': task,
#                 'absolute_deadline': arrival_time + task.deadline
#             })
#             arrival_time += task.period
    
#     # Sort by arrival time, then by deadline for tie-breaking
#     arrivals.sort(key=lambda x: (x['time'], x['absolute_deadline']))
#     return arrivals

def simulate_dm_scheduling(tasks):
    """Simulate Deadline Monotonic scheduling."""
    if not tasks:
        return True, []
    
    # Handle very large hyperperiods
    hyperperiod = calculate_hyperperiod(tasks)
    if hyperperiod > 1000000:
        return False, []
    
    # Reset task states
    for task in tasks:
        task.preemption_count = 0
    
    # Generate all task job releases
    jobs = []
    for task in tasks:
        release_time = 0.0
        job_id = 0
        while release_time < hyperperiod:
            jobs.append({
                'release_time': release_time,
                'task': task,
                'absolute_deadline': release_time + task.deadline,
                'remaining_time': task.execution_time,
                'job_id': job_id,
                'completed': False
            })
            release_time += task.period
            job_id += 1
    
    # Sort jobs by release time
    jobs.sort(key=lambda x: (x['release_time'], x['absolute_deadline']))
    
    # Simulation
    current_time = 0.0
    running_job = None
    
    # Create events list
    events = []
    for job in jobs:
        events.append(('release', job['release_time'], job))
        events.append(('deadline', job['absolute_deadline'], job))
    
    events.sort(key=lambda x: (x[1], x[0] == 'deadline'))  # Sort by time, deadlines first
    
    event_index = 0
    
    while event_index < len(events) or running_job is not None:
        # Process all events at current time
        while (event_index < len(events) and 
               events[event_index][1] <= current_time + 1e-9):
            event_type, event_time, job = events[event_index]
            
            if event_type == 'deadline' and not job['completed']:
                if job['remaining_time'] > 1e-9:
                    return False, []  # Deadline miss
            
            event_index += 1
        
        # Get all ready jobs
        ready_jobs = []
        for job in jobs:
            if (job['release_time'] <= current_time + 1e-9 and 
                job['remaining_time'] > 1e-9 and 
                not job['completed']):
                ready_jobs.append(job)
        
        # If no ready jobs, advance to next event
        if not ready_jobs:
            running_job = None
            if event_index < len(events):
                current_time = events[event_index][1]
                continue
            else:
                break
        
        # Sort by deadline (DM scheduling)
        ready_jobs.sort(key=lambda x: (x['absolute_deadline'], x['task'].task_id))
        highest_priority = ready_jobs[0]
        
        # Check for preemption
        if (running_job is not None and 
            running_job != highest_priority and 
            running_job['remaining_time'] > 1e-9):
            running_job['task'].preemption_count += 1
        
        running_job = highest_priority
        
        # Find next event time
        next_time = float('inf')
        
        # Next event
        if event_index < len(events):
            next_time = min(next_time, events[event_index][1])
        
        # Job completion
        if running_job['remaining_time'] > 1e-9:
            next_time = min(next_time, current_time + running_job['remaining_time'])
        
        # If no next time, we're stuck
        if next_time == float('inf'):
            break
        
        # Don't exceed hyperperiod
        next_time = min(next_time, hyperperiod)
        
        # Execute
        execution_time = next_time - current_time
        if execution_time > 0 and running_job['remaining_time'] > 1e-9:
            actual_execution = min(execution_time, running_job['remaining_time'])
            running_job['remaining_time'] -= actual_execution
            
            if running_job['remaining_time'] <= 1e-9:
                running_job['completed'] = True
                running_job = None
        
        current_time = next_time
        
        # Safety check to prevent infinite loops
        if current_time >= hyperperiod:
            break
    
    # Check all jobs completed
    for job in jobs:
        if job['remaining_time'] > 1e-9:
            return False, []
    
    return True, [task.preemption_count for task in tasks]

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