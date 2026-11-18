"""Inventario de una tiendita: artículos, existencias y mínimos."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Articulo:
    nombre: str
    existencias: int
    minimo: int = 0


class Inventario:
    def __init__(self, articulos: dict[str, Articulo] | None = None) -> None:
        self.articulos: dict[str, Articulo] = articulos or {}

    def agregar(self, nombre: str, cantidad: int, minimo: int | None = None) -> Articulo:
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        clave = nombre.strip().lower()
        articulo = self.articulos.get(clave)
        if articulo is None:
            articulo = Articulo(nombre.strip(), 0, minimo or 0)
            self.articulos[clave] = articulo
        elif minimo is not None:
            articulo.minimo = minimo
        articulo.existencias += cantidad
        return articulo

    def quitar(self, nombre: str, cantidad: int) -> Articulo:
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        articulo = self.articulos.get(nombre.strip().lower())
        if articulo is None:
            raise KeyError(f"no existe el artículo {nombre!r}")
        articulo.existencias -= cantidad
        return articulo

    def bajo_minimo(self) -> list[Articulo]:
        return sorted(
            (a for a in self.articulos.values() if a.existencias < a.minimo),
            key=lambda a: a.nombre.lower(),
        )

    def reporte(self) -> str:
        if not self.articulos:
            return "Inventario vacío."
        lineas = []
        for articulo in sorted(self.articulos.values(), key=lambda a: a.nombre.lower()):
            marca = " (bajo mínimo)" if articulo.existencias < articulo.minimo else ""
            lineas.append(f"{articulo.nombre}: {articulo.existencias}{marca}")
        return "\n".join(lineas)

    def guardar(self, ruta: Path) -> None:
        datos = {clave: asdict(a) for clave, a in self.articulos.items()}
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def cargar(cls, ruta: Path) -> "Inventario":
        if not ruta.exists():
            return cls()
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        return cls({clave: Articulo(**valor) for clave, valor in datos.items()})
