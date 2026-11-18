# inventario

Herramienta chica para llevar el inventario de una tiendita desde la terminal.

```
python -m inventario agregar Frijol 10 --minimo 3
python -m inventario quitar Frijol 2
python -m inventario reporte
python -m inventario faltantes
```

Los datos se guardan en `inventario.json`.

## Pruebas

```
python -m pytest
```

Este repo es una prueba de orquestadores de agentes de código. Un PR se mergea solo cuando pasan
las pruebas y la revisión automática no tiene hallazgos medios o mayores abiertos.
