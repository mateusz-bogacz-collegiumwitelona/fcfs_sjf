import csv
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from prettytable import PrettyTable
import os
import sys

class ProcessState:
    NEW = "Nowy"
    READY = "Gotowy"
    RUNNING = "Aktywny"
    WAITING = "Czekający"
    TERMINATED = "Zakończony"

class Process:
    def __init__(self, pid, burst_time, arrival_time=0):
        self.pid = pid
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0
        self.response_time = 0
        self.start_time = 0
        self.state = ProcessState.NEW
        self.progress = 0 

class FCFSScheduler:
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.performance_metrics = {
            'avg_waiting_time': 0,
            'avg_turnaround_time': 0,
            'cpu_utilization': 0,
            'throughput': 0
        }
        
    def add_process(self, process):
        self.processes.append(process)
        
    def calculate_times(self):
        if not self.processes:
            return
            
        current_time = 0
        for process in self.processes:
            process.start_time = current_time
            process.waiting_time = current_time - process.arrival_time
            current_time += process.burst_time
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.response_time = process.waiting_time

        self._calculate_performance_metrics()

    def _calculate_performance_metrics(self):
        n = len(self.processes)
        total_burst_time = sum(p.burst_time for p in self.processes)
        max_completion = max(p.completion_time for p in self.processes)
        
        self.performance_metrics['avg_waiting_time'] = sum(p.waiting_time for p in self.processes) / n
        self.performance_metrics['avg_turnaround_time'] = sum(p.turnaround_time for p in self.processes) / n
        self.performance_metrics['cpu_utilization'] = (total_burst_time / max_completion) * 100
        self.performance_metrics['throughput'] = n / max_completion

    def generate_report(self):
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        filename = f"fcfs_report_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=== Raport z wykonania algorytmu FCFS ===\n")
            f.write(f"Data wygenerowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("1. Informacje o procesach:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'PID':<5} {'Czas wykonania':<15} {'Czas oczekiwania':<15} "
                   f"{'Czas przetwarzania':<15} {'Czas odpowiedzi':<15}\n")
            
            for p in self.processes:
                f.write(f"{p.pid:<5} {p.burst_time:<15} {p.waiting_time:<15} "
                       f"{p.turnaround_time:<15} {p.response_time:<15}\n")
            
            f.write("\n2. Metryki wydajności:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Średni czas oczekiwania: {self.performance_metrics['avg_waiting_time']:.2f}\n")
            f.write(f"Średni czas przetwarzania: {self.performance_metrics['avg_turnaround_time']:.2f}\n")
            f.write(f"Wykorzystanie CPU: {self.performance_metrics['cpu_utilization']:.2f}%\n")
            f.write(f"Przepustowość: {self.performance_metrics['throughput']:.2f} procesów/jednostkę czasu\n")
            
            f.write("\n3. Szczegóły wykonania:\n")
            f.write("-" * 50 + "\n")
            for p in self.processes:
                f.write(f"\nProces P{p.pid}:\n")
                f.write(f"- Czas rozpoczęcia: {p.start_time}\n")
                f.write(f"- Czas zakończenia: {p.completion_time}\n")
                f.write(f"- Całkowity czas wykonania: {p.burst_time}\n")
            
            f.write("\n4. Podsumowanie:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Całkowita liczba procesów: {len(self.processes)}\n")
            f.write(f"Całkowity czas wykonania: {max(p.completion_time for p in self.processes)}\n")
            
    def _update_process_states(self, current_time):
        for process in self.processes:
            if current_time < process.start_time:
                process.state = ProcessState.NEW
            elif current_time >= process.completion_time:
                process.state = ProcessState.TERMINATED
                process.progress = 100
            elif current_time >= process.start_time:
                process.state = ProcessState.RUNNING
                process.progress = ((current_time - process.start_time) / process.burst_time) * 100
            else:
                process.state = ProcessState.READY
                process.progress = 0

    def create_animation(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), height_ratios=[2, 2, 1])
        fig.suptitle('Wizualizacja algorytmu FCFS (First-Come-First-Served)', fontsize=16)
        
        total_time = sum(p.burst_time for p in self.processes)
        
        def init():
            ax1.clear()
            ax2.clear()
            ax3.clear()
            return []

        def animate(frame):
            ax1.clear()
            ax2.clear()
            ax3.clear()
            
            current_time = frame / 10 * total_time if frame < 10 else total_time
            
            self._update_process_states(current_time)
            
            ax1.set_xlim(0, total_time)
            ax1.set_ylim(0, len(self.processes) + 1)
            ax1.set_title('Harmonogram procesów FCFS')
            ax1.set_xlabel('Czas')
            ax1.set_ylabel('Procesy')
            
            colors = {
                ProcessState.NEW: 'lightgray',
                ProcessState.READY: 'yellow',
                ProcessState.RUNNING: 'lightgreen',
                ProcessState.TERMINATED: 'lightblue'
            }
            
            for i, process in enumerate(self.processes):
                if current_time > process.start_time:
                    progress = min(current_time - process.start_time, process.burst_time)
                    ax1.barh(i + 1, progress, left=process.start_time, 
                            color=colors[process.state], alpha=0.8)
                    ax1.text(process.start_time + progress/2, i + 1, 
                            f'P{process.pid} ({process.state}\n{process.progress:.0f}%)',
                            ha='center', va='center')
                ax1.text(-0.5, i + 1, f'P{process.pid}', ha='right', va='center')

            ax1.axvline(x=current_time, color='red', linestyle='--', alpha=0.5)
            
            ax2.set_title('Metryki procesów')
            ax2.set_xlim(0, max(p.completion_time for p in self.processes))
            ax2.set_ylim(0, len(self.processes) + 1)
            
            for i, process in enumerate(self.processes):
                if current_time > process.start_time:

                    ax2.barh(i + 1, process.waiting_time, color='pink', alpha=0.5,
                            label='Czas oczekiwania')
                    
                    progress = min(current_time - process.start_time, process.burst_time)
                    ax2.barh(i + 1, progress, left=process.waiting_time, 
                            color='lightgreen', alpha=0.8, label='Czas wykonania')
                    
                    ax2.text(0, i + 1, f'Oczekiwanie: {process.waiting_time}',
                            ha='left', va='bottom')
                    ax2.text(process.waiting_time + progress, i + 1, 
                            f'Wykonanie: {progress:.1f}',
                            ha='right', va='bottom')
                            
                ax2.text(-0.5, i + 1, f'P{process.pid}', ha='right', va='center')
            
            ax3.axis('off')
            status_text = (
                f"Czas systemowy: {current_time:.1f}\n"
                f"Średni czas oczekiwania: {self.performance_metrics['avg_waiting_time']:.2f}\n"
                f"Wykorzystanie CPU: {self.performance_metrics['cpu_utilization']:.1f}%\n"
                f"Przepustowość: {self.performance_metrics['throughput']:.2f} proc/jedn\n"
                "\nKamienie milowe:\n"
            )
            
            milestones = []
            for p in self.processes:
                if current_time >= p.start_time and p.state != ProcessState.NEW:
                    milestones.append(f"P{p.pid}: {p.state} ({p.progress:.0f}%)")
            
            status_text += "\n".join(milestones)
            ax3.text(0.02, 0.98, status_text, ha='left', va='top', 
                    transform=ax3.transAxes, fontfamily='monospace')
            
            plt.tight_layout()
            return []

        anim = animation.FuncAnimation(fig, animate, init_func=init,
                                     frames=12, interval=500, blit=True)
        
        def on_close(event):
            plt.close('all')
            
        fig.canvas.mpl_connect('close_event', on_close)
        plt.show(block=True)
        plt.close('all')

def main():
    scheduler = FCFSScheduler()
    
    try:
        with open("data.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                process = Process(
                    int(row['Process']),
                    int(row['BurstTime'])
                )
                scheduler.add_process(process)
    except FileNotFoundError:
        print("Błąd: Plik data.csv nie został znaleziony")
        return
        
    scheduler.calculate_times()
    scheduler.generate_report()  
    scheduler.create_animation()
    sys.exit(0)  

if __name__ == "__main__":
    main()