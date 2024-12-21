import csv
import time
from prettytable import PrettyTable

def findWaitingTime(processes, n, bt, wt):
    wt[0] = 0
    for i in range(1, n):
        wt[i] = bt[i - 1] + wt[i - 1]

def findTurnAroundTime(processes, n, bt, wt, tat):
    for i in range(n):
        tat[i] = bt[i] + wt[i]

def animate_process(process, burst_time):
    print(f"Proces {process} wykonuje się przez {burst_time} jednostek czasu.")
    time.sleep(burst_time * 0.5) 
    print(f"Proces {process} zakończony.")

def findavgTime(processes, n, bt):
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    findWaitingTime(processes, n, bt, wt)
    findTurnAroundTime(processes, n, bt, wt, tat)

    for i in range(n):
        total_wt += wt[i]
        total_tat += tat[i]

        animate_process(processes[i], bt[i])
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
    
if __name__ == "__main__":
    input_file = "data.cve"

    try:
        with open(input_file, "r") as file:
            reader = csv.DictReader(file)
            processes = []
            burst_time = []

            for row in reader:
                processes.append(row['Process'])
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