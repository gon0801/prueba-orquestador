"""Veredicto de DeepSeek para un PR: 0 aprueba, 1 frena, 2 todavía no hay revisión de esta cabeza."""

import json
import re
import subprocess
import sys

BLOQUEAN = {"Medium", "High", "Critical"}
AUTOR = "github-actions[bot]"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main(repo: str, numero: str) -> int:
    cabeza = gh("api", f"repos/{repo}/pulls/{numero}", "--jq", ".head.sha").strip()
    cuerpos = json.loads(gh("api", "--paginate", "--slurp", f"repos/{repo}/issues/{numero}/comments"))
    # Solo cuenta el sticky que publica el revisor (github-actions[bot]): un comentario
    # de cualquier otra cuenta con el mismo marcador no es una revisión.
    sticky = next(
        (
            c["body"] for pagina in cuerpos for c in pagina
            if c["user"]["login"] == AUTOR and "<!-- ai-review:sticky -->" in c["body"]
        ),
        None,
    )
    if sticky is None:
        print("sin revisión de DeepSeek todavía")
        return 2
    # "partial" también es una revisión terminada de esa cabeza (por ejemplo, un
    # commit sin cambios); mientras revisa, el marcador no trae ninguno de los dos.
    if not re.search(rf"ai-review:completion={cabeza}:(complete|partial)\b", sticky):
        print(f"la revisión de DeepSeek no cubre todavía la cabeza {cabeza[:7]}")
        return 2
    marca = re.search(r"<!-- ai-review:findings=(\{.*?\}) -->", sticky)
    hallazgos = json.loads(marca.group(1))["findings"] if marca else []
    abiertos = [
        h for h in hallazgos
        if h.get("status", {}).get("kind") == "open" and h.get("severity") in BLOQUEAN
    ]
    if abiertos:
        print("abiertos: " + "; ".join(f"{h['id']} {h['severity']} {h['title']}" for h in abiertos))
        return 1
    print(f"DeepSeek sin hallazgos medios o mayores abiertos en {cabeza[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
