# API Beneficiarios — laboratorio vulnerable (Fase 2 del plan)

API sintética, deliberadamente sin autenticación, para reproducir el
patrón descrito en la Parte 1 del artículo. Todos los datos son
generados con Faker; ninguno corresponde a una persona real.

## Instalación en la VM "víctima"

Ejecutar como el usuario que correrá el servicio (crea uno dedicado,
no uses root):

```bash
sudo useradd -r -s /usr/sbin/nologin labapi
sudo mkdir -p /opt/vulnerable-api
sudo chown "$(whoami)":"$(whoami)" /opt/vulnerable-api
```

Copia `app.py`, `seed_data.py` y `requirements.txt` a `/opt/vulnerable-api`,
luego:

```bash
cd /opt/vulnerable-api
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python seed_data.py --count 5000
```

> Las versiones en `requirements.txt` son una referencia al momento de
> escribir esto. Si `pip install` falla por versiones no disponibles,
> quita el `==x.y.z` de cada línea e instala la última compatible.

Crea el archivo de log con permisos del usuario del servicio:

```bash
sudo touch /var/log/api_access.log
sudo chown labapi:labapi /var/log/api_access.log
```

Instala y arranca el servicio:

```bash
sudo chown -R labapi:labapi /opt/vulnerable-api
sudo cp api-beneficiarios.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now api-beneficiarios
sudo systemctl status api-beneficiarios
```

## Prueba rápida

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/beneficiarios/1
```

Debe responder sin pedir ningún token ni credencial — esa es, a
propósito, la vulnerabilidad que el laboratorio reproduce.

## Verifica que el log se está escribiendo

```bash
sudo tail -f /var/log/api_access.log
```

Cada línea debe verse así:

```
api_access: ip:127.0.0.1 method:GET path:/api/v1/beneficiarios/1 status:200
```

Este es el formato exacto que el decoder de Wazuh (`wazuh/local_decoder.xml`)
espera. Si cambias el formato aquí, ajusta el regex del decoder.
