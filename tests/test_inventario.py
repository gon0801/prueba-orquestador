import pytest

from inventario import Inventario
from inventario.cli import main


def test_agregar_suma_existencias_sin_distinguir_mayusculas():
    inv = Inventario()
    inv.agregar("Frijol", 5)
    inv.agregar("frijol", 3)
    assert inv.articulos["frijol"].existencias == 8


def test_cantidad_no_positiva_se_rechaza():
    inv = Inventario()
    with pytest.raises(ValueError):
        inv.agregar("Arroz", 0)


def test_quitar_resta_existencias():
    inv = Inventario()
    inv.agregar("Arroz", 10)
    assert inv.quitar("arroz", 4).existencias == 6


def test_quitar_un_articulo_que_no_existe_falla():
    with pytest.raises(KeyError):
        Inventario().quitar("Sal", 1)


def test_quitar_mas_de_lo_que_hay_falla_sin_cambiar_existencias():
    inv = Inventario()
    inv.agregar("Arroz", 4)
    with pytest.raises(ValueError) as error:
        inv.quitar("arroz", 9)
    assert "hay 4" in str(error.value)
    assert "se pidieron 9" in str(error.value)
    assert inv.articulos["arroz"].existencias == 4


def test_quitar_todas_las_existencias_deja_cero():
    inv = Inventario()
    inv.agregar("Arroz", 4)
    assert inv.quitar("arroz", 4).existencias == 0


def test_bajo_minimo_lista_lo_que_falta():
    inv = Inventario()
    inv.agregar("Aceite", 2, minimo=5)
    inv.agregar("Azúcar", 9, minimo=3)
    assert [a.nombre for a in inv.bajo_minimo()] == ["Aceite"]


def test_guardar_y_cargar_conserva_todo(tmp_path):
    ruta = tmp_path / "inv.json"
    inv = Inventario()
    inv.agregar("Café", 4, minimo=2)
    inv.guardar(ruta)
    otro = Inventario.cargar(ruta)
    assert otro.articulos["café"].existencias == 4
    assert otro.articulos["café"].minimo == 2


def test_cli_de_punta_a_punta(tmp_path, capsys):
    archivo = str(tmp_path / "inv.json")
    assert main(["--archivo", archivo, "agregar", "Leche", "3", "--minimo", "5"]) == 0
    assert main(["--archivo", archivo, "faltantes"]) == 0
    assert "Leche: 3 de 5" in capsys.readouterr().out


def test_cli_quitar_de_mas_falla_sin_tocar_el_archivo(tmp_path, capsys):
    archivo = tmp_path / "inventario.json"
    assert main(["--archivo", str(archivo), "agregar", "Leche", "3"]) == 0
    antes = archivo.read_bytes()
    capsys.readouterr()

    assert main(["--archivo", str(archivo), "quitar", "Leche", "5"]) == 1

    salida = capsys.readouterr()
    assert salida.out == ""
    assert salida.err.startswith("error: ")
    assert "hay 3" in salida.err
    assert "se pidieron 5" in salida.err
    assert archivo.read_bytes() == antes
