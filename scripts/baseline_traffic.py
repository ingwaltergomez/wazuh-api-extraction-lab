"""
Genera tráfico "legítimo" de baja intensidad contra la API del
laboratorio, para que el dashboard de Wazuh muestre una línea base
antes del ataque (Fase 3 del plan).

Uso:
    python baseline_traffic.py --target http://<ip-victima>:8000 \
        --max-id 5000 --duration-min 5

Deja correr esto unos minutos ANTES de ejecutar attacker_script.py,
y para él (Ctrl+C) antes de lanzar el ataque, para que el contraste
en el gráfico de eventos sea claro.
"""

import argparse
import random
import time

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Ej: http://192.168.50.10:8000")
    parser.add_argument("--max-id", type=int, default=5000)
    parser.add_argument("--duration-min", type=float, default=5)
    parser.add_argument("--min-delay", type=float, default=5.0)
    parser.add_argument("--max-delay", type=float, default=10.0)
    args = parser.parse_args()

    end_time = time.time() + args.duration_min * 60
    session = requests.Session()
    count = 0

    print(f"Generando tráfico base contra {args.target} por {args.duration_min} min...")
    while time.time() < end_time:
        beneficiario_id = random.randint(1, args.max_id)
        url = f"{args.target}/api/v1/beneficiarios/{beneficiario_id}"
        try:
            resp = session.get(url, timeout=5)
            count += 1
            print(f"[{count}] GET /api/v1/beneficiarios/{beneficiario_id} -> {resp.status_code}")
        except requests.RequestException as exc:
            print(f"Error de conexión: {exc}")

        time.sleep(random.uniform(args.min_delay, args.max_delay))

    print(f"Listo. {count} peticiones de línea base enviadas.")


if __name__ == "__main__":
    main()
