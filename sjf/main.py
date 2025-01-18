import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from prettytable import PrettyTable

class Process:
    def __init__(self, id, arrival_time, burst_time):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.start_time = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.remaining_time = burst_time

def load_process_data(file_path):
    processes = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                processes.append(Process(
                    int(row["Process"].strip()),
                    int(row["ArrivalTime"].strip()),
                    int(row["BurstTime"].strip())
                ))
        return sorted(processes, key=lambda x: x.arrival_time)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku '{file_path}'.")
        exit(1)
    except KeyError as e:
        print(f"Błąd: Brak wymaganej kolumny {e} w pliku CSV.")
        exit(1)

def sjf_algorithm(processes):
    n = len(processes)
    current_time = 0
    completed_processes = 0
    total_wait_time = 0
    total_turnaround_time = 0
    completed = [False] * n
    execution_steps = []
    milestones = []
    
    while completed_processes < n:
        available_processes = [
            i for i, p in enumerate(processes) 
            if not completed[i] and p.arrival_time <= current_time
        ]
        
        if available_processes:
            shortest_idx = min(
                available_processes, 
                key=lambda i: processes[i].burst_time
            )
            process = processes[shortest_idx]
            
            process.start_time = current_time
            current_time += process.burst_time
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
            milestones.append({
                'time': current_time,
                'process_id': process.id,
                'event': 'Zakończenie',
                'waiting_time': process.waiting_time,
                'turnaround_time': process.turnaround_time
            })
            
            total_wait_time += process.waiting_time
            total_turnaround_time += process.turnaround_time
            
            completed[shortest_idx] = True
            completed_processes += 1
            
            execution_steps.append(process)
            
        else:
            current_time += 1
    
    avg_wait_time = total_wait_time / n
    avg_turnaround_time = total_turnaround_time / n
    cpu_utilization = sum(p.burst_time for p in processes) / current_time * 100
    
    return processes, execution_steps, milestones, {
        'avg_wait_time': avg_wait_time,
        'avg_turnaround_time': avg_turnaround_time,
        'cpu_utilization': cpu_utilization,
        'total_time': current_time
    }

def generate_report(all_processes, execution_steps, milestones, metrics):
    current_time = datetime.now()
    filename = f"sjf_raport_{current_time.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
    
    table = PrettyTable()
    table.field_names = [
        "Proces", 
        "Czas Przybycia", 
        "Czas Przetwarzania", 
        "Czas Rozpoczęcia", 
        "Czas Zakończenia", 
        "Czas Oczekiwania", 
        "Czas Realizacji"
    ]
    
    sorted_processes = sorted(all_processes, key=lambda p: p.id)
    
    for process in sorted_processes:
        table.add_row([
            process.id,
            process.arrival_time,
            process.burst_time,
            process.start_time,
            process.completion_time,
            process.waiting_time,
            process.turnaround_time
        ])
    
    report_content = f"""Raport Algorytmu Shortest Job First (SJF)
Wygenerowany: {current_time.strftime('%d.%m.%Y %H:%M:%S')}

Szczegóły procesów:
{table}

Metryki wydajności:
- Średni czas oczekiwania: {metrics['avg_wait_time']:.2f} jednostek
- Średni czas realizacji: {metrics['avg_turnaround_time']:.2f} jednostek
- Wykorzystanie CPU: {metrics['cpu_utilization']:.2f}%
- Całkowity czas wykonania: {metrics['total_time']} jednostek

Szczegóły kroków wykonania:
"""
    
    for step in execution_steps:
        report_content += (
            f"Proces {step.id}: "
            f"Czas rozpoczęcia = {step.start_time}, "
            f"Czas zakończenia = {step.completion_time}\n"
        )
    
    with open(filename, 'w') as report_file:
        report_file.write(report_content)
    
    print(f"Raport został zapisany do pliku: {filename}")

def create_animated_sjf_visualization(processes, execution_steps, milestones, metrics):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                   gridspec_kw={'height_ratios': [2, 1]})
    fig.suptitle('Wizualizacja Algorytmu Szeregowania Shortest Job First (SJF)', fontsize=16)
    
    y_ticks = list(range(len(execution_steps)))
    y_labels = [f'Proces {p.id}' for p in execution_steps]
    
    ax1.set_yticks(y_ticks)
    ax1.set_yticklabels(y_labels)
    ax1.set_xlabel('Jednostki czasu')
    ax1.set_title('Diagram Gannta Wykonania Procesów')
    ax1.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    metrics_text = (
        f"Metryki wydajności:\n"
        f"Średni czas oczekiwania: {metrics['avg_wait_time']:.2f} jednostek\n"
        f"Średni czas realizacji: {metrics['avg_turnaround_time']:.2f} jednostek\n"
        f"Wykorzystanie CPU: {metrics['cpu_utilization']:.2f}%\n"
        f"Całkowity czas wykonania: {metrics['total_time']} jednostek"
    )
    ax2.text(0.5, 0.5, metrics_text, 
             horizontalalignment='center', 
             verticalalignment='center', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=10)
    ax2.axis('off')
    
    def init():
        return []
    
    def update(frame):
        ax1.clear()
        ax1.set_yticks(y_ticks)
        ax1.set_yticklabels(y_labels)
        ax1.set_xlabel('Jednostki czasu')
        ax1.set_title('Diagram Gannta Wykonania Procesów')
        ax1.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        current_milestones = [m for m in milestones if m['time'] <= execution_steps[frame].completion_time]
        
        for i, proc in enumerate(execution_steps[:frame+1]):
            bar = ax1.barh(i, proc.burst_time, left=proc.start_time, 
                     height=0.5, color='skyblue', edgecolor='black', alpha=0.6)
            ax1.text(proc.start_time + proc.burst_time/2, i, 
                     f'P{proc.id}', ha='center', va='center')
        
        for milestone in current_milestones:
            proc_idx = next(i for i, p in enumerate(execution_steps) if p.id == milestone['process_id'])
            ax1.scatter(milestone['time'], proc_idx, color='red', s=100, 
                        marker='*', zorder=3, label=f'Kamień milowy Procesu {milestone["process_id"]}')
            ax1.annotate(f'Zakończony\nOczekiwanie: {milestone["waiting_time"]:.2f}\nCzas realizacji: {milestone["turnaround_time"]:.2f}', 
                         (milestone['time'], proc_idx), 
                         xytext=(10, 0), 
                         textcoords='offset points',
                         fontsize=8,
                         bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.7))
        
        if current_milestones:
            ax1.legend(loc='best', fontsize=8)
        
        return []
    
    anim = animation.FuncAnimation(
        fig, 
        update, 
        frames=len(execution_steps), 
        init_func=init, 
        interval=1000,
        repeat_delay=2000
    )
    
    plt.tight_layout()
    plt.show()

def main():
    processes = load_process_data('data.csv')
    
    all_processes, execution_steps, milestones, metrics = sjf_algorithm(processes)
    
    create_animated_sjf_visualization(processes, execution_steps, milestones, metrics)
    
    generate_report(all_processes, execution_steps, milestones, metrics)

if __name__ == "__main__":
    main()