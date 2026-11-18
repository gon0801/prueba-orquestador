# inventario

Herramienta chica para llevar el inventario de una tiendita desde la terminal.

```
python -m inventario agregar Frijol 10 --minimo 3
python -m inventario quitar Frijol 2
python -m inventario reporte
python -m inventario faltantes
python -m inventario buscar azucar
```

`reporte` lista cada artículo con sus existencias y termina con una línea `Total: N artículos` que
cuenta los artículos distintos (no la suma de existencias; con uno solo dice `Total: 1 artículo`).
Una línea en blanco separa ese total de la lista, para que no se confunda con un artículo que se
llame "Total". Si el inventario está vacío, solo dice `Inventario vacío.`.

`buscar` encuentra los artículos que contienen el texto en su nombre, sin importar mayúsculas ni
acentos (`azucar` encuentra `Azúcar`, y `nino` encuentra `Niño`), y muestra sus existencias.

Los datos se guardan en `inventario.json`.

## Pruebas

```
python -m pytest
```

Este repo es una prueba de orquestadores de agentes de código. Un PR se mergea solo cuando pasan
las pruebas y la revisión automática no tiene hallazgos medios o mayores abiertos.
