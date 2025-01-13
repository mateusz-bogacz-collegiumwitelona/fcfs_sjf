import csv
import time
from datetime import datetime
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def findWaitingTime(processes, n, bt, wt):
    wt[0] = 0
    for i in range(1, n):
        wt[i] = bt[i - 1] + wt[i - 1]

def findTurnAroundTime(processes, n, bt, wt, tat):
    for i in range(n):
        tat[i] = bt[i] + wt[i]

def animate_process(process, burst_time, report_file):
    start_time = time.time()
    print(f"Proces {process} wykonuje się przez {burst_time} jednostek czasu.")
    try:
        report_file.write(f"\nRozpoczęto proces {process} o czasie {datetime.now().strftime('%H:%M:%S')}\n")
        time.sleep(burst_time * 0.5)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Proces {process} zakończony.")
        report_file.write(f"Zakończono proces {process} o czasie {datetime.now().strftime('%H:%M:%S')}\n")
        report_file.write(f"Rzeczywisty czas wykonania: {execution_time:.2f} sekund\n")
    except IOError as e:
        print(f"Błąd podczas zapisu do pliku raportu: {e}")

def create_fcfs_animation(processes, burst_times):
    n = len(processes)
    wait_times = [0] * n
    for i in range(1, n):
        wait_times[i] = wait_times[i-1] + burst_times[i-1]
    
    completion_times = [wait_times[i] + burst_times[i] for i in range(n)]
    total_time = sum(burst_times)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Wizualizacja algorytmu FCFS', fontsize=16)
    
    def init():
        ax1.clear()
        ax2.clear()
        return []

    def animate(frame):
        ax1.clear()
        ax2.clear()
        
        current_time = frame / 10 * total_time if frame < 10 else total_time
        
        ax1.set_xlim(0, total_time)
        ax1.set_ylim(0, n + 1)
        ax1.set_title('Harmonogram procesów')
        ax1.set_xlabel('Czas')
        ax1.set_ylabel('Procesy')
        
        for i in range(n):
            if current_time > wait_times[i]:
                progress = min(current_time - wait_times[i], burst_times[i])
                ax1.barh(i + 1, progress, left=wait_times[i], color='skyblue', alpha=0.8)
            ax1.text(-0.5, i + 1, f'P{processes[i]}', ha='right', va='center')
        
        ax1.axvline(x=current_time, color='red', linestyle='--', alpha=0.5)
        
        ax2.set_title('Statystyki procesów')
        ax2.set_xlim(0, max(completion_times))
        ax2.set_ylim(0, n + 1)
        
        for i in range(n):
            if current_time > wait_times[i]:
                ax2.barh(i + 1, wait_times[i], color='lightgray', alpha=0.5)
            
            if current_time > wait_times[i]:
                progress = min(current_time - wait_times[i], burst_times[i])
                ax2.barh(i + 1, progress, left=wait_times[i], color='skyblue', alpha=0.8)
            
            ax2.text(-0.5, i + 1, f'P{processes[i]}', ha='right', va='center')
        
        ax2.set_xlabel('Czas')
        ax2.set_ylabel('Procesy')
        
        plt.tight_layout()
        return []

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                 frames=12, interval=500, blit=True)
    
    return fig, anim

def visualize_fcfs(processes, burst_times):
    try:
        fig, anim = create_fcfs_animation(processes, burst_times)
        anim.save('fcfs_animation.gif', writer='pillow')
        plt.show()
    except Exception as e:
        print(f"Błąd podczas tworzenia animacji: {e}")

def generate_detailed_report(processes, n, bt, wt, tat, report_file):
    try:
        avg_wt = sum(wt) / n
        max_wt = max(wt)
        min_wt = min(wt)
        avg_tat = sum(tat) / n
        max_tat = max(tat)
        min_tat = min(tat)
        total_execution_time = sum(bt)
        
        report_file.write("\n=== SZCZEGÓŁOWY RAPORT SYMULACJI ===\n")
        report_file.write(f"\nData i czas symulacji: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        report_file.write("\n--- STATYSTYKI OGÓLNE ---\n")
        report_file.write(f"Liczba procesów: {n}\n")
        report_file.write(f"Całkowity czas wykonania: {total_execution_time} jednostek\n")
        
        report_file.write("\n--- CZASY OCZEKIWANIA ---\n")
        report_file.write(f"Średni czas oczekiwania: {avg_wt:.2f} jednostek\n")
        report_file.write(f"Maksymalny czas oczekiwania: {max_wt} jednostek\n")
        report_file.write(f"Minimalny czas oczekiwania: {min_wt} jednostek\n")
        
        report_file.write("\n--- CZASY ZAKOŃCZENIA ---\n")
        report_file.write(f"Średni czas zakończenia: {avg_tat:.2f} jednostek\n")
        report_file.write(f"Maksymalny czas zakończenia: {max_tat} jednostek\n")
        report_file.write(f"Minimalny czas zakończenia: {min_tat} jednostek\n")
        
        report_file.write("\n--- SZCZEGÓŁY PROCESÓW ---\n")
        table = PrettyTable()
        table.field_names = ["Proces", "Czas trwania", "Czas oczekiwania", "Czas zakończenia"]
        for i in range(n):
            table.add_row([processes[i], bt[i], wt[i], tat[i]])
        report_file.write(str(table))
        
        report_file.write("\n\n--- ANALIZA WYDAJNOŚCI ---\n")
        report_file.write(f"Wykorzystanie CPU: {(sum(bt)/max(tat))*100:.2f}%\n")
        report_file.write(f"Średni throughput: {n/max(tat):.2f} procesów na jednostkę czasu\n")
    except Exception as e:
        print(f"Błąd podczas generowania raportu: {e}")

def findavgTime(processes, n, bt):
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0
    
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    report_filename = os.path.join(reports_dir, f"fcfs_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    try:
        print(f"Próba utworzenia pliku raportu: {report_filename}")
        with open(report_filename, "w", encoding='utf-8') as report_file:
            report_file.write("=== ROZPOCZĘCIE SYMULACJI ===\n")
            report_file.write(f"Liczba procesów: {n}\n")
            report_file.write("Procesy wejściowe:\n")
            for i in range(n):
                report_file.write(f"Proces {processes[i]}: czas wykonania = {bt[i]}\n")
            
            findWaitingTime(processes, n, bt, wt)
            findTurnAroundTime(processes, n, bt, wt, tat)
            
            for i in range(n):
                total_wt += wt[i]
                total_tat += tat[i]
                animate_process(processes[i], bt[i], report_file)
                print()
            
            avg_wt = total_wt / n
            avg_tat = total_tat / n
            
            print(f"Średni czas oczekiwania = {avg_wt:.2f}\n")  
            print(f"Średni czas zakończenia = {avg_tat:.2f}\n")  
            
            table = PrettyTable()
            table.field_names = ["Proces", "Czas trwania", "Czas oczekiwania", "Czas zakończenia"]
            
            for i in range(n):
                table.add_row([i + 1, bt[i], wt[i], tat[i]])
            
            print("\nPodsumowanie:")
            print(table)
            
            generate_detailed_report(processes, n, bt, wt, tat, report_file)
            
            print(f"\nSzczegółowy raport został zapisany do pliku: {report_filename}")

        visualize_fcfs(processes, bt)
            
    except PermissionError:
        print(f"Błąd: Brak uprawnień do utworzenia pliku w lokalizacji: {report_filename}")
        print("Spróbuj uruchomić program z odpowiednimi uprawnieniami lub zmień lokalizację zapisu.")
    except IOError as e:
        print(f"Błąd przy tworzeniu pliku raportu: {e}")
        print(f"Próbowano utworzyć plik w: {report_filename}")

if __name__ == "__main__":
    input_file = "./data.csv"
    
    try:
        with open(input_file, "r") as file:
            reader = csv.DictReader(file)
            processes = []
            burst_time = []
            
            for row in reader:
                processes.append(int(row['Process']))
                burst_time.append(int(row['BurstTime']))
            
            n = len(processes)
            
            if n == 0:
                print("Brak danych do przetworzenia.")
            else:
                print(f"Wczytane procesy: {processes}")
                print(f"Wczytane czasy trwania: {burst_time}\n")
                findavgTime(processes, n, burst_time)
                
    except FileNotFoundError:
        print(f"Błąd: Plik '{input_file}' nie został znaleziony.")
    except KeyError:
        print("Błąd: Plik CSV nie zawiera wymaganych nagłówków.")
    except ValueError:
        print("Błąd: Nieprawidłowy format danych w pliku.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")