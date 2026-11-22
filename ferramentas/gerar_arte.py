"""Arte da Cripta de Bolso em 4 tons (Game Boy), toda desenhada em código.

Sprites: '.' transparente, 'w' claro, 'g' médio, 'k' escuro.
Fundos:  '0' claro, '1' médio-claro, '2' médio-escuro, '3' escuro.
"""
import json
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ARTE = RAIZ / "arte"

CORES_FUNDO = ["#E0F8CF", "#86C06C", "#306850", "#071821"]
CORES_SPRITE = ["#65FF00", "#E0F8CF", "#86C06C", "#071821"]
COR_SPRITE = {".": CORES_SPRITE[0], "w": CORES_SPRITE[1], "g": CORES_SPRITE[2], "k": CORES_SPRITE[3]}
COR_FUNDO = {str(i): c for i, c in enumerate(CORES_FUNDO)}
LARG, ALT = 20, 18
PORTAS = [(2, 1), (16, 1)]
NASCIMENTO = (9, 16)  # pé do jogador ao entrar na sala


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def folha(frames):
    for f in frames:
        assert len(f) == 16 and all(len(l) == 16 for l in f), f
    im = Image.new("RGB", (16 * len(frames), 16))
    for i, f in enumerate(frames):
        for y, l in enumerate(f):
            for x, c in enumerate(l):
                im.putpixel((16 * i + x, y), hex_rgb(COR_SPRITE[c]))
    return im


def espelhar(f):
    return [l[::-1] for l in f]


def subir(f, n=1):
    return f[n:] + ["." * 16] * n


# ------------------------------------------------------------------ herói (capuz e capa)
HEROI_BAIXO = [
    "................",
    "......kkkk......",
    ".....kggggk.....",
    "....kggggggk....",
    "....kgkwwkgk....",
    "....kgwkkwgk....",
    "....kgwwwwgk....",
    ".....kgwwgk.....",
    "....kkggggkk....",
    "...kwkggggkwk...",
    "...kwkkggkkwk...",
    "....kkggggkk....",
    ".....kggggk.....",
    ".....kk..kk.....",
    ".....kk..kk.....",
    "................",
]
HEROI_BAIXO_2 = HEROI_BAIXO[:12] + [".....kggggk.....", ".....kk...kk....", ".....kk.........", "................"]
HEROI_DIR = [
    "................",
    "......kkkk......",
    ".....kggggk.....",
    "....kgggggkk....",
    "....kggggwwk....",
    "....kgggwkwk....",
    "....kggggwwk....",
    ".....kggwwk.....",
    ".....kgggk......",
    ".....kgggkkkkk..",
    ".....kggwkwwwk..",
    ".....kgggkkkk...",
    ".....kgggk......",
    "......kkk.......",
    "......kkk.......",
    "................",
]
HEROI_DIR_2 = HEROI_DIR[:12] + [".....kgggk......", ".....kk.kk......", ".....kk..kk.....", "................"]
HEROI_CIMA = [
    "................",
    "......kkkk......",
    ".....kggggk.....",
    "....kggggggk....",
    "....kggggggk....",
    "....kggggggk....",
    "....kggggggk....",
    ".....kggggk.....",
    "....kkggggkk....",
    "...kgkggggkgk...",
    "...kgkggggkgk...",
    "....kkggggkk....",
    ".....kggggk.....",
    ".....kk..kk.....",
    ".....kk..kk.....",
    "................",
]
HEROI_CIMA_2 = HEROI_CIMA[:12] + [".....kggggk.....", "....kk...kk.....", ".........kk.....", "................"]

# ------------------------------------------------------------------ inimigos
MORCEGO = [
    "................", "................", "................", "................",
    "k......kk......k", "kk....kkkk....kk", "kgk..kwkkwk..kgk", "kggkkkkkkkkkkggk",
    "kgggkkwwwwkkgggk", "kgkgk.kkkk.kgkgk", "kk.k...kk...k.kk", "k...............",
    "................", "................", "................", "................",
]
MORCEGO_2 = [
    "................", "................", "................", "................",
    "................", ".......kk.......", "......kwkk......", "..kkkkkkkkkkkk..",
    ".kgggkwwwwkgggk.", "kggkk.kkkk.kkggk", "kgk.....kk...kgk", "kk............kk",
    "................", "................", "................", "................",
]
SLIME = [
    "................", "................", "................", "................",
    "................", "......kkkk......", "....kkwwggkk....", "...kwwggggggk...",
    "..kwgggggggggk..", "..kgkwgggkwggk..", "..kggkgggkgggk..", ".kggggggggggggk.",
    ".kgggkkkkkkgggk.", "..kkk......kkk..", "................", "................",
]
SLIME_2 = [
    "................", "................", "................", "................",
    "................", "................", "................", ".....kkkkkk.....",
    "...kkwwgggggkk..", "..kwgggggggggk..", ".kggkwgggkwgggk.", ".kgggkgggkggggk.",
    "kggggggggggggggk", "kkkkkkkkkkkkkkkk", "................", "................",
]
ESQUELETO = [
    ".....kkkkkk.....", "....kwwwwwwk....", "....kwkwwkwk....", "....kwkwwkwk....",
    "....kwwkkwwk....", ".....kwwwwk.....", "......kwwk......", "....kkkwwkkk....",
    "...kw.kwwk.wk...", "...kw.kkkk.wk...", "....k.kwwk.k....", "......kwwk......",
    ".....kw..wk.....", ".....kw..wk.....", "....kkk..kkk....", "................",
]
ESQUELETO_2 = ESQUELETO[:7] + [
    "..kkkkkwwkkkkk..", ".kw...kwwk...wk.", ".k....kkkk....k.", "......kwwk......", "......kwwk......",
    ".....kw..wk.....", ".....kw..wk.....", "....kkk..kkk....", "................"]
REI = [
    "...k.k.kk.k.k...", "...kgkgkkgkgk...", "...kggggggggk...", "....kwwwwwwk....",
    "....kwkwwkwk....", "....kwkwwkwk....", "....kwwkkwwk....", "..kkkkwwwwkkkk..",
    ".kggkkkwwkkkggk.", "kggkwkkwwkkwkggk", "kgkkwkkkkkkwkkgk", "kk.kwkkwwkkwk.kk",
    "....kgggggggk...", "....kgk...kgk...", "...kkk.....kkk..", "................",
]
REI_2 = subir(REI)

# ------------------------------------------------------------------ objetos 16x16
TIRO = ["." * 16] * 5 + [
    "......kkkk......", ".....kwwwwk.....", ".....kwwgwk.....", ".....kwggwk.....", "......kkkk......",
] + ["." * 16] * 6
TIRO_INIMIGO = ["." * 16] * 5 + [
    "......kkkk......", ".....kgkkgk.....", ".....kkggkk.....", ".....kgkkgk.....", "......kkkk......",
] + ["." * 16] * 6


def moldura_porta(miolo12):
    """porta: moldura escura 16x16 com miolo 12x12 (ícone)."""
    linhas = ["kkkkkkkkkkkkkkkk", "kgggggggggggggk."[:15] + "k"]
    for l in miolo12:
        linhas.append("kg" + l + "gk")
    linhas.append("kggggggggggggggk")
    linhas.append("kkkkkkkkkkkkkkkk")
    assert len(linhas) == 16
    return linhas


CAVEIRA12 = ["wwwwwwwwwwww", "wwwkkkkkkwww", "wwkwwwwwwkww", "wkwwwwwwwwkw", "wkwkkwwkkwkw", "wkwkkwwkkwkw",
             "wkwwwkkwwwkw", "wwkwwwwwwkww", "wwwkwkwkwwww", "wwwkwkwkwwww", "wwwwkkkwwwww", "wwwwwwwwwwww"]
BAU12 = ["wwwwwwwwwwww", "wwwwwwwwwwww", "wkkkkkkkkkkw", "kgggggggggk.", "kggggkkggggk", "kkkkkwwkkkkk",
         "kggggkkggggk", "kggggggggggk", "kggggggggggk", "kkkkkkkkkkkk", "wwwwwwwwwwww", "wwwwwwwwwwww"]
CORACAO12 = ["wwwwwwwwwwww", "wwkkwwwwkkww", "wkggkwwkggkw", "kgwggkkggggk", "kgwgggggggk.", "kggggggggggk",
             "wkggggggggkw", "wwkggggggkww", "wwwkggggkwww", "wwwwkggkwwww", "wwwwwkkwwwww", "wwwwwwwwwwww"]
GRADE12 = ["kwkwkwkwkwkw"] * 12


def cheio12(l):
    return [s.replace(".", "k") for s in l]


PORTA_COMBATE = moldura_porta(CAVEIRA12)
PORTA_TESOURO = moldura_porta(cheio12(BAU12))
PORTA_FONTE = moldura_porta(cheio12(CORACAO12))
PORTA_FECHADA = moldura_porta(GRADE12)

BAU = [
    "................", "................", "...kkkkkkkkkk...", "..kggggggggggk..", ".kggggggggggggk.",
    ".kkkkkkkkkkkkkk.", ".kgggggkkgggggk.", ".kgggggwwgggggk.", ".kkkkkkwwkkkkkk.", ".kgggggkkgggggk.",
    ".kggggggggggggk.", ".kggggggggggggk.", ".kkkkkkkkkkkkkk.", "................", "................", "................",
]
FONTE = [
    "................", ".......kk.......", "......kwwk......", ".....kwggwk.....", "......kwwk......",
    "..kkkkkkkkkkkk..", ".kwwwwwwwwwwwwk.", "kwgwgwgwgwgwgwwk", "kwwwwwwwwwwwwwwk", ".kkkkkkkkkkkkkk.",
    "...kggggggggk...", "...kgkkggkkgk...", "...kggggggggk...", "..kkkkkkkkkkkk..", "................", "................",
]
ITEM_FORTE = [  # espada
    "................", "............kk..", "...........kwk..", "..........kwk...", ".........kwk....",
    "........kwk.....", ".......kwk......", "..kk..kwk.......", "..kgkkwk........", "...kgkk.........",
    "...kkgk.........", "..kgkkgk........", ".kgk..kk........", ".kk.............", "................", "................",
]
ITEM_GATILHO = [  # raio
    "................", ".........kkkk...", "........kwwk....", ".......kwwk.....", "......kwwk......",
    ".....kwwkkkkk...", "....kwwwwwwk....", "...kkkkkwwk.....", ".......kwwk.....", "......kwwk......",
    ".....kwwk.......", "....kwk.........", "....kk..........", "................", "................", "................",
]
ITEM_CORACAO = [
    "................", "................", "...kkk...kkk....", "..kgggk.kgggk...", ".kgwwggkgggggk..",
    ".kgwgggggggggk..", ".kggggggggggggk.", "..kggggggggggk..", "...kgggggggk....", "....kgggggk.....",
    ".....kgggk......", "......kgk.......", ".......k........", "................", "................", "................",
]
ITEM_BOTAS = [
    "................", "................", "....kkkk........", "....kggk........", "....kggk...kk...",
    "....kggk..kwwk..", "....kggk...kk...", "....kggk........", "....kgggkkkk....", "...kggggggggk...",
    "...kgwgggggggk..", "...kkkkkkkkkkk..", "................", "................", "................", "................",
]
CORACAO_CHEIO = ["." * 16] * 3 + [
    "...kkk..kkk.....", "..kwggkkgggk....", "..kwgggggggk....", "..kggggggggk....", "...kgggggggk....",
    "....kgggggk.....", ".....kgggk......", "......kgk.......", ".......k........",
] + ["." * 16] * 4
CORACAO_VAZIO = ["." * 16] * 3 + [
    "...kkk..kkk.....", "..k...kk...k....", "..k.........k...", "..k.........k...", "...k.......k....",
    "....k.....k.....", ".....k...k......", "......k.k.......", ".......k........",
] + ["." * 16] * 4
for _f in (CORACAO_CHEIO, CORACAO_VAZIO):
    for _i, _l in enumerate(_f):
        _f[_i] = (_l + "." * 16)[:16]
CORACAO_VAZIO[6] = "..k.........k..."[:16]
CORACAO_VAZIO[5] = "..k.........k..."

# corações pequenos 7x7 para o HUD (dois por sprite 16x16)
MINI_CHEIO = [".kk.kk.", "kwgkggk", "kgggggk", "kgggggk", ".kgggk.", "..kgk..", "...k..."]
MINI_VAZIO = [".kk.kk.", "k..k..k", "k.....k", "k.....k", ".k...k.", "..k.k..", "...k..."]
MINI_NADA = ["......."] * 7


def par_coracoes(esq, dir_):
    f = ["." * 16 for _ in range(16)]
    for y in range(7):
        f[4 + y] = "." + esq[y] + "." + dir_[y]
    return [(l + "." * 16)[:16] for l in f]


HUD_ESTADOS = {  # estado -> (esq, dir)
    0: (MINI_CHEIO, MINI_CHEIO), 1: (MINI_CHEIO, MINI_VAZIO), 2: (MINI_VAZIO, MINI_VAZIO),
    3: (MINI_CHEIO, MINI_NADA), 4: (MINI_VAZIO, MINI_NADA),
}

# ------------------------------------------------------------------ fonte 5x7 (texto das telas e dígitos)
FONTE5 = {
    "A": [".kkk.", "k...k", "k...k", "kkkkk", "k...k", "k...k", "k...k"],
    "B": ["kkkk.", "k...k", "k...k", "kkkk.", "k...k", "k...k", "kkkk."],
    "C": [".kkk.", "k...k", "k....", "k....", "k....", "k...k", ".kkk."],
    "D": ["kkkk.", "k...k", "k...k", "k...k", "k...k", "k...k", "kkkk."],
    "E": ["kkkkk", "k....", "k....", "kkkk.", "k....", "k....", "kkkkk"],
    "F": ["kkkkk", "k....", "k....", "kkkk.", "k....", "k....", "k...."],
    "I": [".kkk.", "..k..", "..k..", "..k..", "..k..", "..k..", ".kkk."],
    "L": ["k....", "k....", "k....", "k....", "k....", "k....", "kkkkk"],
    "M": ["k...k", "kk.kk", "k.k.k", "k.k.k", "k...k", "k...k", "k...k"],
    "N": ["k...k", "kk..k", "k.k.k", "k..kk", "k...k", "k...k", "k...k"],
    "O": [".kkk.", "k...k", "k...k", "k...k", "k...k", "k...k", ".kkk."],
    "P": ["kkkk.", "k...k", "k...k", "kkkk.", "k....", "k....", "k...."],
    "R": ["kkkk.", "k...k", "k...k", "kkkk.", "k.k..", "k..k.", "k...k"],
    "S": [".kkkk", "k....", "k....", ".kkk.", "....k", "....k", "kkkk."],
    "T": ["kkkkk", "..k..", "..k..", "..k..", "..k..", "..k..", "..k.."],
    "U": ["k...k", "k...k", "k...k", "k...k", "k...k", "k...k", ".kkk."],
    "V": ["k...k", "k...k", "k...k", "k...k", "k...k", ".k.k.", "..k.."],
    " ": ["....."] * 7,
    "0": [".kkk.", "k...k", "k..kk", "k.k.k", "kk..k", "k...k", ".kkk."],
    "1": ["..k..", ".kk..", "..k..", "..k..", "..k..", "..k..", ".kkk."],
    "2": [".kkk.", "k...k", "....k", "...k.", "..k..", ".k...", "kkkkk"],
    "3": ["kkkk.", "....k", "....k", ".kkk.", "....k", "....k", "kkkk."],
    "4": ["...k.", "..kk.", ".k.k.", "k..k.", "kkkkk", "...k.", "...k."],
    "5": ["kkkkk", "k....", "kkkk.", "....k", "....k", "k...k", ".kkk."],
    "6": [".kkk.", "k....", "k....", "kkkk.", "k...k", "k...k", ".kkk."],
    "7": ["kkkkk", "....k", "...k.", "..k..", ".k...", ".k...", ".k..."],
    "8": [".kkk.", "k...k", "k...k", ".kkk.", "k...k", "k...k", ".kkk."],
    "9": [".kkk.", "k...k", "k...k", ".kkkk", "....k", "....k", ".kkk."],
}


def digito16(d):
    """dígito 5x7 ampliado 2x (10x14), centrado em 16x16, claro com contorno escuro."""
    g = FONTE5[str(d)]
    f = [["."] * 16 for _ in range(16)]
    for y, l in enumerate(g):
        for x, c in enumerate(l):
            if c == "k":
                for dy in (0, 1):
                    for dx in (0, 1):
                        f[1 + 2 * y + dy][3 + 2 * x + dx] = "w"
    # contorno
    for y in range(16):
        for x in range(16):
            if f[y][x] == "." and any(0 <= y + a < 16 and 0 <= x + b < 16 and f[y + a][x + b] == "w"
                                      for a in (-1, 0, 1) for b in (-1, 0, 1)):
                f[y][x] = "k"
    return ["".join(l) for l in f]


# ------------------------------------------------------------------ salas
CHAO_A = ["11111111", "11111111", "11121111", "11111111", "11111111", "11111121", "11111111", "11111111"]
CHAO_B = ["11111111", "12111111", "11111111", "11111211", "11111111", "11111111", "11211111", "11111111"]
PAREDE = ["32222223", "22222222", "22222222", "33333333", "22232222", "22232222", "22232222", "33333333"]
PILAR = ["3333333333333333", "3222222222222223", "3211111111111123", "3212222222222123",
         "3212222222222123", "3212222222222123", "3212222222222123", "3212222222222123",
         "3212222222222123", "3212222222222123", "3212222222222123", "3212222222222123",
         "3212222222222123", "3211111111111123", "3222222222222223", "3333333333333333"]
ESCURO = ["33333333"] * 8
VAO = ["30000003", "30000003", "30000003", "30000003", "30000003", "30000003", "30000003", "30000003"]
VAO = ["33333333", "31111113", "31111113", "31111113", "31111113", "31111113", "31111113", "31111113"]

OBSTACULOS = {
    "sala_1": [(5, 6), (13, 6), (5, 11), (13, 11)],
    "sala_2": [(6, 8), (8, 8), (10, 8), (12, 8)],
    "sala_3": [(6, 5), (6, 7), (6, 9), (12, 5), (12, 7), (12, 9)],
    "sala_4": [(3, 5), (15, 5), (9, 9), (3, 12), (15, 12)],
    "sala_tesouro": [],
    "sala_fonte": [],
    "sala_chefe": [(3, 4), (15, 4), (3, 12), (15, 12)],
}


def mapa_sala(nome):
    col = [[0] * LARG for _ in range(ALT)]
    grade = [["CHAO_A" if (x + y) % 3 else "CHAO_B" for x in range(LARG)] for y in range(ALT)]
    vaos = {(x + d, y) for (x, y) in PORTAS for d in (0, 1)}
    for y in range(ALT):
        for x in range(LARG):
            if y == 0:
                grade[y][x], col[y][x] = "ESCURO", 1
            elif y == 1 and (x, y) in vaos:
                grade[y][x] = "VAO"
            elif y in (1, ALT - 1) or x in (0, LARG - 1):
                grade[y][x], col[y][x] = "PAREDE", 1
    blocos = []
    for (x, y) in OBSTACULOS[nome]:
        blocos.append((x, y))
        for dy in (0, 1):
            for dx in (0, 1):
                col[y + dy][x + dx] = 1
                grade[y + dy][x + dx] = None
    return grade, col, blocos


def desenhar_sala(nome):
    grade, col, blocos = mapa_sala(nome)
    tiles = {"CHAO_A": CHAO_A, "CHAO_B": CHAO_B, "PAREDE": PAREDE, "ESCURO": ESCURO, "VAO": VAO}
    im = Image.new("RGB", (160, 144))
    for y in range(ALT):
        for x in range(LARG):
            if grade[y][x]:
                for yy, l in enumerate(tiles[grade[y][x]]):
                    for xx, c in enumerate(l):
                        im.putpixel((x * 8 + xx, y * 8 + yy), hex_rgb(COR_FUNDO[c]))
    for (x, y) in blocos:
        for yy, l in enumerate(PILAR):
            for xx, c in enumerate(l):
                im.putpixel((x * 8 + xx, y * 8 + yy), hex_rgb(COR_FUNDO[c]))
    return im, col


def tela_texto(linhas):
    """Tela escura com linhas de texto (texto, escala, linha_y)."""
    im = Image.new("RGB", (160, 144), hex_rgb(CORES_FUNDO[3]))
    for texto, esc, y0, cor in linhas:
        larg = len(texto) * 6 * esc - esc
        x0 = (160 - larg) // 2
        x0 -= x0 % 8 if esc == 1 else 0
        for i, ch in enumerate(texto):
            for y, l in enumerate(FONTE5[ch]):
                for x, c in enumerate(l):
                    if c == "k":
                        for dy in range(esc):
                            for dx in range(esc):
                                im.putpixel((x0 + (i * 6 + x) * esc + dx, y0 + y * esc + dy),
                                            hex_rgb(CORES_FUNDO[cor]))
    return im


def main():
    ARTE.mkdir(exist_ok=True)
    for nome in OBSTACULOS:
        im, col = desenhar_sala(nome)
        im.save(ARTE / f"{nome}.png")
        (ARTE / f"colisao_{nome}.json").write_text(json.dumps(col))
    tela_texto([("CRIPTA", 3, 24, 0), ("DE BOLSO", 2, 56, 1), ("APERTE A", 1, 104, 1)]).save(ARTE / "titulo.png")
    tela_texto([("FIM", 3, 16, 0), ("PROFUNDIDADE", 1, 56, 1), ("RECORDE", 1, 88, 1),
                ("APERTE A", 1, 128, 2)]).save(ARTE / "fim.png")
    tela_texto([("VITORIA", 3, 16, 0), ("RECORDE", 1, 88, 1), ("APERTE A", 1, 128, 2)]).save(ARTE / "vitoria.png")

    folha([HEROI_BAIXO, HEROI_BAIXO_2, HEROI_DIR, HEROI_DIR_2, HEROI_CIMA, HEROI_CIMA_2,
           espelhar(HEROI_DIR), espelhar(HEROI_DIR_2)]).save(ARTE / "jogador.png")
    um = {"tiro": TIRO, "tiro_inimigo": TIRO_INIMIGO, "porta_combate": PORTA_COMBATE,
          "porta_tesouro": PORTA_TESOURO, "porta_fonte": PORTA_FONTE, "porta_fechada": PORTA_FECHADA,
          "bau": BAU, "fonte": FONTE, "item_forte": ITEM_FORTE, "item_gatilho": ITEM_GATILHO,
          "item_coracao": ITEM_CORACAO, "item_botas": ITEM_BOTAS}
    for n, f in um.items():
        folha([f]).save(ARTE / f"{n}.png")
    dois = {"morcego": (MORCEGO, MORCEGO_2), "slime": (SLIME, SLIME_2), "esqueleto": (ESQUELETO, ESQUELETO_2),
            "rei": (REI, REI_2), "coracao": (CORACAO_CHEIO, CORACAO_VAZIO)}
    for n, fs in dois.items():
        folha(list(fs)).save(ARTE / f"{n}.png")
    folha([digito16(d) for d in range(10)]).save(ARTE / "digitos.png")
    for d in range(10):
        folha([digito16(d)]).save(ARTE / f"digito_{d}.png")
    for e, (l, r) in HUD_ESTADOS.items():
        folha([par_coracoes(l, r)]).save(ARTE / f"hud_{e}.png")

    nomes = ["jogador", "morcego", "slime", "esqueleto", "rei", "coracao", "digitos"] + list(um)
    ims = [Image.open(ARTE / f"{n}.png") for n in nomes]
    prev = Image.new("RGB", (max(i.width for i in ims) * 3 + 8, sum(i.height * 3 + 4 for i in ims)), (255, 255, 255))
    y = 0
    for i in ims:
        prev.paste(i.resize((i.width * 3, i.height * 3), Image.NEAREST), (4, y))
        y += i.height * 3 + 4
    prev.save(ARTE / "previa.png")


if __name__ == "__main__":
    main()
