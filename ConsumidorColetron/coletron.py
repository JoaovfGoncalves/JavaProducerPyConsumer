import subprocess
import os
import sys
from run_consumers import run_consumers
from src.audit_consumer import run_audit
from src.selective_consumer import run_selective
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main_menu():
    print("\n=== Menu Principal ===")
    print("1. Executar Produtor (Java)")
    print("2. Executar Consumidor (Standard)")
    print("3. Executar Auditoria")
    print("4. Executar Consumidor Seletivo")
    print("0. Sair")
    escolha = input("Escolha uma opção: ")
    return escolha

def main_producer():

    jar_path = os.path.join(
        BASE_DIR, "..", "MonitorColetron", "target", "coletron-producer-1.0.0.jar"
    )

    jar_path_encoded = os.path.normpath(jar_path)

    try:
        subprocess.run(["java", "-jar", jar_path_encoded], check=True)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar o produtor Java:", e)

def main_consumer(mode="standard"):
    try:
        workers = int(input("Quantos consumidores deseja iniciar? "))
        run_consumers(workers=workers, mode=mode)
    except Exception as e:
        print(f"Erro ao executar consumidor ({mode}):", e)

def main_selective():
    try:
        run_selective()
    except Exception as e:
        print("Erro ao executar o consumidor seletivo:", e)

def main_audit():
    try:
        run_audit()
    except Exception as e:
        print("Erro ao executar auditoria:", e)

if __name__ == "__main__":
    while True:
        opcao = main_menu()

        if opcao == "1":
            main_producer()
        elif opcao == "2":
            main_consumer("standard")
        elif opcao == "3":
            main_audit()
        elif opcao == "4":
            main_selective()
        elif opcao == "0":
            print("Encerrando aplicação.")
            break
        else:
            print("Opção inválida. Tente novamente.")
