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


def nombres(articulos):
    return [a.nombre for a in articulos]


def test_buscar_sin_acento_encuentra_con_acento():
    inv = Inventario()
    inv.agregar("Azúcar", 9)
    assert nombres(inv.buscar("azucar")) == ["Azúcar"]


def test_buscar_con_acento_y_mayusculas_encuentra_sin_acento():
    inv = Inventario()
    inv.agregar("Azucar", 9)
    assert nombres(inv.buscar("AZÚCAR")) == ["Azucar"]


def test_buscar_encuentra_parte_del_nombre_en_medio():
    inv = Inventario()
    inv.agregar("Azúcar", 9)
    inv.agregar("Arroz", 4)
    assert nombres(inv.buscar("úca")) == ["Azúcar"]


def test_buscar_regresa_varios_ordenados_por_nombre_con_existencias():
    inv = Inventario()
    inv.agregar("Pan dulce", 6)
    inv.agregar("Empanada", 2)
    inv.agregar("Arroz", 4)
    inv.agregar("pan blanco", 3)
    encontrados = inv.buscar("PAN")
    assert [(a.nombre, a.existencias) for a in encontrados] == [
        ("Empanada", 2),
        ("pan blanco", 3),
        ("Pan dulce", 6),
    ]


def test_buscar_sin_coincidencias_regresa_lista_vacia():
    inv = Inventario()
    inv.agregar("Arroz", 4)
    assert inv.buscar("sal") == []


@pytest.mark.parametrize("texto", ["", "   "])
def test_buscar_texto_vacio_o_de_espacios_se_rechaza(texto):
    inv = Inventario()
    inv.agregar("Arroz", 4)
    with pytest.raises(ValueError):
        inv.buscar(texto)


def test_buscar_sin_acentos_tambien_ignora_la_tilde_de_la_enie():
    # Decisión: quitar diacríticos hace que la ñ cuente como n, para buscar con tolerancia.
    inv = Inventario()
    inv.agregar("Niño envuelto", 2)
    assert nombres(inv.buscar("nino")) == ["Niño envuelto"]


def test_cli_buscar_muestra_existencias_de_cada_resultado(tmp_path, capsys):
    archivo = str(tmp_path / "inv.json")
    assert main(["--archivo", archivo, "agregar", "Azúcar morena", "3"]) == 0
    assert main(["--archivo", archivo, "agregar", "Arroz", "4"]) == 0
    assert main(["--archivo", archivo, "agregar", "Azúcar", "9"]) == 0
    capsys.readouterr()

    assert main(["--archivo", archivo, "buscar", "azucar"]) == 0

    assert capsys.readouterr().out == "Azúcar: 9\nAzúcar morena: 3\n"


def test_cli_buscar_sin_coincidencias_lo_dice_y_termina_bien(tmp_path, capsys):
    archivo = str(tmp_path / "inv.json")
    assert main(["--archivo", archivo, "agregar", "Arroz", "4"]) == 0
    capsys.readouterr()

    assert main(["--archivo", archivo, "buscar", "sal"]) == 0

    assert capsys.readouterr().out == "Sin coincidencias.\n"


def test_cli_buscar_texto_vacio_es_error(tmp_path, capsys):
    archivo = str(tmp_path / "inv.json")
    assert main(["--archivo", archivo, "agregar", "Arroz", "4"]) == 0
    capsys.readouterr()

    assert main(["--archivo", archivo, "buscar", "  "]) == 1

    salida = capsys.readouterr()
    assert salida.out == ""
    assert salida.err.startswith("error: ")


def test_buscar_ordena_sin_importar_acentos():
    inv = Inventario()
    inv.agregar("Zapote", 5)
    inv.agregar("Ámbar", 1)
    assert nombres(inv.buscar("a")) == ["Ámbar", "Zapote"]


@pytest.mark.parametrize("consulta", [["buscar", "sal"], ["reporte"], ["faltantes"]])
def test_cli_las_consultas_no_crean_el_archivo(tmp_path, consulta):
    archivo = tmp_path / "inventario.json"

    assert main(["--archivo", str(archivo), *consulta]) == 0

    assert not archivo.exists()


def test_cli_buscar_no_reescribe_el_archivo(tmp_path, capsys):
    archivo = tmp_path / "inventario.json"
    # Sin la sangría que deja guardar(): si buscar lo reescribiera, los bytes cambiarían.
    archivo.write_text('{"arroz": {"nombre": "Arroz", "existencias": 4, "minimo": 0}}', encoding="utf-8")
    antes = archivo.read_bytes()

    assert main(["--archivo", str(archivo), "buscar", "arroz"]) == 0

    assert capsys.readouterr().out == "Arroz: 4\n"
    assert archivo.read_bytes() == antes


def test_reporte_termina_con_total_de_articulos_distintos_no_de_existencias():
    inv = Inventario()
    inv.agregar("Frijol", 5)
    inv.agregar("frijol", 3)
    inv.agregar("Arroz", 2)
    # Dos artículos distintos (Frijol se juntó), aunque haya 10 piezas en total.
    assert inv.reporte() == "Arroz: 2\nFrijol: 8\nTotal: 2 artículos"


def test_reporte_total_cuenta_los_articulos_que_quedaron_en_cero():
    inv = Inventario()
    inv.agregar("Arroz", 3)
    inv.agregar("Frijol", 5)
    inv.quitar("arroz", 3)
    assert inv.reporte() == "Arroz: 0\nFrijol: 5\nTotal: 2 artículos"


def test_reporte_total_con_un_solo_articulo_va_en_singular():
    # Decisión: "Total: 1 artículo", porque "1 artículos" se lee como error.
    inv = Inventario()
    inv.agregar("Sal", 1)
    assert inv.reporte() == "Sal: 1\nTotal: 1 artículo"


def test_reporte_vacio_queda_igual_sin_total():
    assert Inventario().reporte() == "Inventario vacío."


def test_cli_reporte_pone_el_total_en_la_ultima_linea(tmp_path, capsys):
    archivo = str(tmp_path / "inv.json")
    assert main(["--archivo", archivo, "agregar", "Leche", "3", "--minimo", "5"]) == 0
    assert main(["--archivo", archivo, "agregar", "Azúcar", "9"]) == 0
    assert main(["--archivo", archivo, "agregar", "Arroz", "4"]) == 0
    capsys.readouterr()

    assert main(["--archivo", archivo, "reporte"]) == 0

    assert capsys.readouterr().out == "Arroz: 4\nAzúcar: 9\nLeche: 3 (bajo mínimo)\nTotal: 3 artículos\n"


def test_cli_reporte_de_inventario_vacio_no_agrega_total(tmp_path, capsys):
    assert main(["--archivo", str(tmp_path / "inv.json"), "reporte"]) == 0

    assert capsys.readouterr().out == "Inventario vacío.\n"
