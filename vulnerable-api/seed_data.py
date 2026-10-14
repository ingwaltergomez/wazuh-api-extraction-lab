"""
Genera beneficiarios.json con datos 100% SINTÉTICOS mediante Faker.

Ningún dato aquí corresponde a una persona real. El DPI generado tiene
el formato numérico (13 dígitos) pero no es un algoritmo válido de DPI
guatemalteco real ni corresponde a ningún registro oficial.

Uso:
    pip install -r requirements.txt
    python seed_data.py --count 5000
"""

import argparse
import json
import random
from pathlib import Path

from faker import Faker

OUT_FILE = Path(__file__).parent / "beneficiarios.json"


def fake_dpi(fake: Faker) -> str:
    """13 dígitos con apariencia de DPI, sin validez real."""
    return "".join(str(random.randint(0, 9)) for _ in range(13))


def build_records(count: int) -> list[dict]:
    fake = Faker("es_MX")  # locale latinoamericano más cercano disponible
    Faker.seed(42)  # reproducible: útil para comparar corridas del lab
    random.seed(42)

    records = []
    for i in range(1, count + 1):
        records.append(
            {
                "id": i,
                "nombre_completo": fake.name(),
                "dpi": fake_dpi(fake),
                "telefono": fake.phone_number(),
                "direccion": fake.address().replace("\n", ", "),
                "municipio": fake.city(),
                "fecha_registro": fake.date_between(
                    start_date="-3y", end_date="today"
                ).isoformat(),
                "puesto_solicitado": fake.job(),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5000)
    args = parser.parse_args()

    records = build_records(args.count)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Generados {len(records)} registros sintéticos en {OUT_FILE}")


if __name__ == "__main__":
    main()
