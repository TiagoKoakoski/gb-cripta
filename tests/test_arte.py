import json, subprocess, sys
from collections import deque
from pathlib import Path
import pytest
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ARTE = RAIZ / "arte"
SALAS = ["sala_1", "sala_2", "sala_3", "sala_4", "sala_tesouro", "sala_fonte", "sala_chefe"]
TELAS = ["titulo", "fim", "vitoria"]
SPRITES_1 = ["tiro", "tiro_inimigo", "porta_combate", "porta_tesouro", "porta_fonte", "porta_fechada",
             "bau", "fonte", "item_forte", "item_gatilho", "item_coracao", "item_botas"]
SPRITES_2 = ["morcego", "slime", "esqueleto", "rei", "coracao"]
PORTAS = [(4, 1), (14, 1)]   # (coluna, linha) do canto esquerdo de cada vão de 2 tiles
ENTRADA = (9, 16)            # onde o jogador nasce (pé), coluna 9-10


@pytest.fixture(scope="module", autouse=True)
def gerar():
    subprocess.run([sys.executable, str(RAIZ / "ferramentas/gerar_arte.py")], check=True)


def cores(p):
    return {"#%02X%02X%02X" % c for c in Image.open(p).convert("RGB").getdata()}


def test_cores():
    from gerar_arte import CORES_FUNDO, CORES_SPRITE
    for n in SALAS + TELAS:
        assert cores(ARTE / f"{n}.png") <= set(CORES_FUNDO), n
    for n in SPRITES_1 + SPRITES_2 + ["jogador", "digitos"]:
        assert cores(ARTE / f"{n}.png") <= set(CORES_SPRITE), n


def test_tamanhos():
    tam = lambda n: Image.open(ARTE / f"{n}.png").size
    for n in SALAS + TELAS:
        assert tam(n) == (160, 144), n
    assert tam("jogador") == (128, 16)
    for n in SPRITES_1:
        assert tam(n) == (16, 16), n
    for n in SPRITES_2:
        assert tam(n) == (32, 16), n
    assert tam("digitos") == (160, 16)


def test_tiles_unicos():
    for n in SALAS + TELAS:
        im = Image.open(ARTE / f"{n}.png").convert("RGB")
        t = {im.crop((x, y, x + 8, y + 8)).tobytes() for x in range(0, 160, 8) for y in range(0, 144, 8)}
        assert len(t) <= 192, (n, len(t))


def col(n):
    c = json.loads((ARTE / f"colisao_{n}.json").read_text())
    assert len(c) == 18 and all(len(l) == 20 for l in c)
    return c


def test_borda_fechada_menos_portas():
    for n in SALAS:
        c = col(n)
        vaos = {(x + d, y) for (x, y) in PORTAS for d in (0, 1)}
        for x in range(20):
            assert c[0][x] == 1 and c[17][x] == 1, (n, x)
            assert c[1][x] == (0 if (x, 1) in vaos else 1), (n, x)
        for y in range(18):
            assert c[y][0] == 1 and c[y][19] == 1, (n, y)


def livre(c, x, y):
    return 0 <= x < 19 and 0 <= y < 17 and all(c[yy][xx] == 0 for xx in (x, x + 1) for yy in (y,))


def test_caminho_livre_entrada_portas():
    """jogador ocupa 2 tiles de largura (pé numa fileira): busca em largura do nascimento às portas."""
    for n in SALAS:
        c = col(n)
        ini = ENTRADA
        vistos, fila = {ini}, deque([ini])
        while fila:
            x, y = fila.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p not in vistos and livre(c, *p):
                    vistos.add(p); fila.append(p)
        for (px, py) in PORTAS:
            assert (px, py) in vistos, (n, px)
