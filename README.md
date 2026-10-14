# Wazuh API Extraction Lab

Laboratorio sintético que reproduce, de forma controlada, el patrón de **extracción masiva de datos vía una API sin autenticación** — el mismo patrón descrito públicamente en el caso de Mintrab (Guatemala, abril de 2026) — y documenta cómo detectarlo con [Wazuh](https://wazuh.com/) como SIEM.

Es el material complementario de una serie de dos artículos:

- **[Parte 1 — Abril de 2026 en Guatemala: anatomía de una cadena de incidentes en el sector público](https://medium.com/@waltgomez/abril-de-2026-en-guatemala-anatomía-de-una-cadena-de-incidentes-en-el-sector-público-d94a802a4a3f)** — análisis del incidente real, a partir de fuentes públicas.
- **[Parte 2 — Reproduciendo el patrón de extracción masiva en un laboratorio con Wazuh](https://medium.com/@waltgomez/abril-de-2026-parte-2-así-se-ve-una-extracción-masiva-vía-api-dentro-de-un-siem-c8003eea4372)** — este laboratorio, con resultados y capturas.

## ⚠️ Aviso importante

- **Todos los datos son sintéticos**, generados con [Faker](https://faker.readthedocs.io/). Ningún registro corresponde a una persona real.
- El laboratorio corre en una **red aislada, sin salida a Internet**. No se usó, consultó ni tocó ningún sistema real de ninguna institución.
- Este código existe con fines educativos y de documentación defensiva. **No lo apuntes a ningún sistema que no sea tuyo.**

## Qué hay aquí

```
vulnerable-api/     API en FastAPI, deliberadamente sin autenticación (la "víctima")
scripts/            Generador de tráfico base y script de extracción masiva (el "ataque")
wazuh/               Decoder y reglas de detección personalizadas para Wazuh
INSTRUCCIONES.md    Guía paso a paso de orquestación completa del laboratorio
```

## Resultados obtenidos

En la corrida documentada en la Parte 2:

| Métrica | Valor |
|---|---|
| Registros extraídos | 5,000 |
| Duración del ataque | 4 segundos |
| Tiempo hasta la primera alerta | ≈ 1 segundo |
| Alertas generadas (regla de volumen) | 151 |
| Errores durante la extracción | 0 |

## Inicio rápido

1. Monta la topología de dos redes descrita en `INSTRUCCIONES.md` (una de gestión con salida a Internet, otra aislada para el laboratorio).
2. Instala la API siguiendo `vulnerable-api/README.md`.
3. Carga `wazuh/local_decoder.xml` y `wazuh/local_rules.xml` en tu manager de Wazuh.
4. Agrega el bloque de `wazuh/ossec_localfile_snippet.conf` al agente de la VM víctima.
5. Corre `scripts/baseline_traffic.py` para la línea base, y `scripts/attacker_script.py` para el ataque simulado.

El detalle completo, con cada comando, está en [`INSTRUCCIONES.md`](./INSTRUCCIONES.md).

## Una nota honesta sobre el bug que encontré

Durante la construcción de este laboratorio, mi primera versión de la regla de detección **falló en silencio** — sin ningún error de sintaxis, pero sin generar jamás una alerta. La causa fue un desajuste entre el nombre de un decoder padre y su decoder hijo en Wazuh. Quedó documentado con detalle en la Parte 2 del artículo, porque me pareció un hallazgo tan útil como el resultado final: una regla de Wazuh puede estar sintácticamente perfecta y aun así no disparar nunca, por una razón que no salta a la vista sin depurar paso a paso.

## Limitación metodológica

La regla de detección incluida dispara por **volumen** (muchas peticiones en poco tiempo desde el mismo origen), no por la secuencialidad de los IDs consultados. Un atacante que distribuyera la misma extracción por debajo del umbral de frecuencia, o desde múltiples orígenes, no sería detectado por esta regla tal como está escrita. Más detalle en `wazuh/local_rules.xml` y en la Parte 2 del artículo.

## Autor

**Walter Gómez** — [LinkedIn](#) · [Medium](https://medium.com/@waltgomez)

## Licencia

MIT. Úsalo, modifícalo y reprodúcelo libremente, citando la fuente si te es útil.
