import csv
import matplotlib.pyplot as plt
from tabulate import tabulate
from datetime import datetime

def load_process_data(file_path):
    process_data = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                process_data.append({
                    "Process": int(row["Process"].strip()),
                    "ArrivalTime": int(row["ArrivalTime"].strip()),
                    "BurstTime": int(row["BurstTime"].strip())
                })
    except FileNotFoundError:
        print(f"Błąd: Plik '{file_path}' nie został znaleziony.")
        exit(1)
    except KeyError as e:
        print(f"Błąd: Brakuje oczekiwanej kolumny {e} w pliku CSV.")
        exit(1)
    return process_data

def sjf_algorithm(process_data):
    n = len(process_data)
    process_data.sort(key=lambda x: x["ArrivalTime"])

    current_time = 0
    completed_processes = 0
    total_wait_time = 0
    total_tatime = 0
    completed = [False] * n
    results = []

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))

    while completed_processes < n:
        available_processes = [
            process for i, process in enumerate(process_data)
            if not completed[i] and process["ArrivalTime"] <= current_time
        ]

        if available_processes:
            shortest_process = min(available_processes, key=lambda x: x["BurstTime"])
            idx = process_data.index(shortest_process)

            start_time = current_time
            end_time = start_time + shortest_process["BurstTime"]
            wait_time = start_time - shortest_process["ArrivalTime"]
            tatime = end_time - shortest_process["ArrivalTime"]

            results.append({
                "Process": shortest_process["Process"],
                "ArrivalTime": shortest_process["ArrivalTime"],
                "BurstTime": shortest_process["BurstTime"],
                "StartTime": start_time,
                "CompletionTime": end_time,
                "WaitTime": wait_time,
                "TurnaroundTime": tatime
            })

            current_time = end_time
            completed_processes += 1
            total_wait_time += wait_time
            total_tatime += tatime
            completed[idx] = True

            update_gantt_chart(ax, results, current_time)
        else:
            current_time += 1

    plt.ioff()
    return results, total_wait_time, total_tatime, n

def update_gantt_chart(ax, results, current_time):
    ax.clear()
    ax.barh(
        [f"P{result['Process']}" for result in results],
        [result["BurstTime"] for result in results],
        left=[result["StartTime"] for result in results],
        color="skyblue",
        edgecolor="black"
    )
    ax.axvline(current_time, color="red", linestyle="--", label="Czas bieżący")
    ax.set_xlabel("Czas")
    ax.set_ylabel("Procesy")
    ax.set_title("Algorytm SJF")
    ax.legend(loc="upper right")
    plt.pause(1)

def generate_report(results, total_wait_time, total_tatime, n):
    headers = ["Process", "ArrivalTime", "BurstTime", "StartTime", "CompletionTime", "WaitTime", "TurnaroundTime"]
    table_data = [
        [result["Process"], result["ArrivalTime"], result["BurstTime"], result["StartTime"], 
         result["CompletionTime"], result["WaitTime"], result["TurnaroundTime"]]
        for result in results
    ]

    print(tabulate(table_data, headers, tablefmt="grid"))

    avg_wtime = total_wait_time / n
    avg_tatime = total_tatime / n
    max_wtime = max(result["WaitTime"] for result in results)
    min_wtime = min(result["WaitTime"] for result in results)
    max_tatime = max(result["TurnaroundTime"] for result in results)
    min_tatime = min(result["TurnaroundTime"] for result in results)

    print(f"\nŚredni czas oczekiwania: {avg_wtime:.2f}")
    print(f"Średni czas zakończenia: {avg_tatime:.2f}")

    report_filename = f"sjf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, "w", encoding="utf-8") as file:
        file.write("=== RAPORT SYMULACJI ALGORYTMU SJF ===\n\n")
        file.write(f"Data i czas generowania raportu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Liczba procesów: {n}\n\n")
        file.write("Szczegóły procesów:\n")
        file.write(tabulate(table_data, headers, tablefmt="grid"))
        file.write("\n\n=== STATYSTYKI ===\n")
        file.write(f"Średni czas oczekiwania: {avg_wtime:.2f} jednostek\n")
        file.write(f"Średni czas zakończenia: {avg_tatime:.2f} jednostek\n")
        file.write(f"Maksymalny czas oczekiwania: {max_wtime} jednostek\n")
        file.write(f"Minimalny czas oczekiwania: {min_wtime} jednostek\n")
        file.write(f"Maksymalny czas zakończenia: {max_tatime} jednostek\n")
        file.write(f"Minimalny czas zakończenia: {min_tatime} jednostek\n")

    print(f"\nSzczegółowy raport został zapisany do pliku: {report_filename}")

# Główna funkcja programu
def main():
    file_path = 'data.csv'
    process_data = load_process_data(file_path)

    if not process_data:
        print("Błąd: Plik nie zawiera danych.")
        exit(1)

    results, total_wait_time, total_tatime, n = sjf_algorithm(process_data)
    generate_report(results, total_wait_time, total_tatime, n)
    plt.show()

if __name__ == "__main__":
    main()