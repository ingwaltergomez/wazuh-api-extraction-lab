# Cómo usar este paquete

Contenido:

```
vulnerable-api/     → Fase 2 (víctima): API sintética sin autenticación
scripts/            → Fases 3 y 5 (línea base y ataque simulado)
wazuh/               → Fase 4 (detección): decoder, reglas, config del agente
```

## Orden de ejecución (resumen; el detalle de cada paso está en la
## conversación donde se definió el plan completo)

1. **VM víctima:** sigue `vulnerable-api/README.md` para instalar y
   arrancar la API. Verifica con `curl` que responde.
2. **Manager de Wazuh:**
   - Copia `wazuh/local_decoder.xml` a `/var/ossec/etc/decoders/local_decoder.xml`
     (o fusiónalo si ya tienes contenido ahí).
   - Copia `wazuh/local_rules.xml` a `/var/ossec/etc/rules/local_rules.xml`
     (o fusiónalo).
   - `systemctl restart wazuh-manager`
   - Valida con `/var/ossec/bin/wazuh-logtest` pegando una línea de
     prueba como:
     `api_access: ip:192.168.50.20 method:GET path:/api/v1/beneficiarios/42 status:200`
     Deberías ver que dispara el decoder `api-access-log-fields` y,
     si repites la prueba 20+ veces seguidas, la regla 100101.
3. **VM víctima (agente):** agrega el bloque de
   `wazuh/ossec_localfile_snippet.conf` a `/var/ossec/etc/ossec.conf`
   y reinicia el agente.
4. **Captura la línea base:** desde la VM atacante (o tu propia
   máquina, apuntando a la IP de la víctima), corre:
   ```bash
   pip install requests
   python scripts/baseline_traffic.py --target http://<ip-victima>:8000 --duration-min 5
   ```
5. **Ejecuta el ataque simulado:**
   ```bash
   python scripts/attacker_script.py --target http://<ip-victima>:8000 \
       --start-id 1 --end-id 5000 --threads 10
   ```
   Anota la hora de inicio que imprime el script.
6. **En el dashboard de Wazuh:** busca las alertas de la regla 100101
   en la ventana de tiempo del ataque. Anota la hora de la primera
   alerta y réstala a la hora de inicio del ataque — ese es tu dato
   de "tiempo de detección".

## Checklist de capturas de pantalla (coincide con el plan)

- [ ] 1. Diagrama de topología de red (lo haces tú, no es una captura del sistema)
- [ ] 2. Agente "Active" en el dashboard de Wazuh
- [ ] 3. Dashboard con tráfico base (bajo y estable)
- [ ] 4. Salida de `wazuh-logtest` mostrando el decoder y la regla disparando
- [ ] 5. Terminal del atacante corriendo `attacker_script.py`
- [ ] 6. Dashboard mostrando el pico de alertas durante el ataque
- [ ] 7. Detalle de una alerta expandida, con el campo MITRE ATT&CK
- [ ] 8. Tabla de eventos crudos (Discover) filtrada por la IP atacante

## Advertencias que van en el artículo, tal cual

- Todos los datos son sintéticos (Faker), generados por el autor.
- El laboratorio corre en una red aislada, sin salida a Internet.
- No se usó, consultó ni tocó ningún sistema real del Estado.
- La regla 100101 detecta el ataque por **volumen**, no por el patrón
  de enumeración secuencial — ver la nota al final de
  `wazuh/local_rules.xml`.
