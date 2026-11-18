"""Línea de comandos: python -m inventario <comando>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import Inventario

ARCHIVO = Path("inventario.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inventario")
    parser.add_argument("--archivo", type=Path, default=ARCHIVO)
    sub = parser.add_subparsers(dest="comando", required=True)

    agregar = sub.add_parser("agregar", help="suma existencias de un artículo")
    agregar.add_argument("nombre")
    agregar.add_argument("cantidad", type=int)
    agregar.add_argument("--minimo", type=int)

    quitar = sub.add_parser("quitar", help="resta existencias de un artículo")
    quitar.add_argument("nombre")
    quitar.add_argument("cantidad", type=int)

    sub.add_parser("reporte", help="muestra todas las existencias")
    sub.add_parser("faltantes", help="muestra lo que está bajo su mínimo")

    args = parser.parse_args(argv)
    inventario = Inventario.cargar(args.archivo)
    try:
        if args.comando == "agregar":
            articulo = inventario.agregar(args.nombre, args.cantidad, args.minimo)
            print(f"{articulo.nombre}: {articulo.existencias}")
        elif args.comando == "quitar":
            articulo = inventario.quitar(args.nombre, args.cantidad)
            print(f"{articulo.nombre}: {articulo.existencias}")
        elif args.comando == "reporte":
            print(inventario.reporte())
        elif args.comando == "faltantes":
            faltan = inventario.bajo_minimo()
            print("\n".join(f"{a.nombre}: {a.existencias} de {a.minimo}" for a in faltan) or "Nada bajo mínimo.")
    except (KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    inventario.guardar(args.archivo)
    return 0
