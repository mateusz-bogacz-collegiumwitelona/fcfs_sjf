import csv
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tabulate import tabulate

file_path = 'data.cve'
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

n = len(process_data)
if n == 0:
    print("Błąd: Plik nie zawiera danych.")
    exit(1)

mat = [[0 for j in range(5)] for i in range(n)]

for i, process in enumerate(process_data):
    mat[i][0] = process["Process"]
    mat[i][1] = process["ArrivalTime"]
    mat[i][2] = process["BurstTime"]

print("Dane procesów:")
for process in process_data:
    print(f"Proces P{process['Process']} ma czas przybycia: {process['ArrivalTime']} oraz czas trwania: {process['BurstTime']}")

# Sortowanie procesów według czasu przybycia (FCFS)
mat.sort(key=lambda x: x[1])

def plot_processes(mat, title, current_time):
    processes = [f"P{int(row[0])}" for row in mat]
    burst_times = [row[2] for row in mat]
    completion_times = [row[3] for row in mat]

    plt.bar(processes, burst_times, color='skyblue', label="Czas trwania")
    plt.plot(processes, completion_times, marker='o', color='orange', label="Czas zakończenia")
    plt.axvline(x=current_time, color='red', linestyle='--', label='Czas bieżący')
    plt.title(title)
    plt.xlabel("Proces")
    plt.ylabel("Czas")
    plt.legend()
    plt.pause(1)
    plt.clf()

plt.ion()

# FCFS - Obliczanie czasu oczekiwania i zakończenia
current_time = 0
mat[0][3] = mat[0][1] + mat[0][2]  # Czas zakończenia pierwszego procesu
current_time = mat[0][3]
total_wait_time = 0
total_tatime = 0

# Animacja
plot_processes(mat, "Początkowa kolejność procesów", current_time)

for i in range(1, n):
    mat[i][3] = mat[i-1][3] + mat[i][2]  # Czas zakończenia procesu
    mat[i][4] = mat[i][3] - mat[i][1]  # Czas oczekiwania (Czas zakończenia - Czas przybycia)
    total_wait_time += mat[i][4]
    total_tatime += mat[i][3]
    current_time = mat[i][3]
    
    # Animacja dla każdego procesu
    plot_processes(mat, f"Krok {i}", current_time)

avg_wtime = total_wait_time / n
avg_tatime = total_tatime / n

# Formatowanie tabeli w terminalu
headers = ["Proces", "Czas_Przebywania", "Czas_Trwania", "Czas_Zakończenia", "Czas_Oczekiwania"]
table_data = [[mat[i][0], mat[i][1], mat[i][2], mat[i][3], mat[i][4]] for i in range(n)]
print(tabulate(table_data, headers, tablefmt="grid"))

# Wizualizacja
plot_processes(mat, "Końcowa kolejność procesów (FCFS)", current_time)
plt.ioff()

def show_table(data, columns, title):
    root = tk.Tk()
    root.title(title)

    tree = ttk.Treeview(root, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for row in data:
        tree.insert('', tk.END, values=row)

    tree.pack(expand=True, fill='both')
    root.mainloop()

# Dane tabelaryczne
columns = ["Proces", "Czas_Przebywania", "Czas_Trwania", "Czas_Zakończenia", "Czas_Oczekiwania"]
show_table(mat, columns, "Wyniki procesów FCFS")

# Wyświetlenie wyników
print(f"Średni czas oczekiwania dla wszystkich procesów wynosi = {avg_wtime}")
print(f"Średni czas zakończenia dla procesów wynosi = {avg_tatime}")
