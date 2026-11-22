"""Ajudas pros testes: boot controlado, posição, mira, caminho (busca em largura no mapa da sala)."""
import json
from collections import deque
from pathlib import Path

ARTE = Path(__file__).resolve().parent.parent / "arte"
NOME_CENA = {1: "sala_1", 2: "sala_2", 3: "sala_3", 4: "sala_4", 5: "sala_tesouro", 6: "sala_fonte", 7: "sala_chefe"}

SALAS = {"sala_1": 1, "sala_2": 2, "sala_3": 3, "sala_4": 4, "tesouro": 5, "fonte": 6, "chefe": 7}


def boot(jogo, sala="sala_1", **vars_):
    """Liga o jogo, ajusta variáveis na janela do boot e espera a sala carregar."""
    for _ in range(400):            # espera o motor ligar e o boot iniciar a partida
        jogo.tick(1)
        if jogo.var("vida") == 3:
            break
    jogo.tick(2)
    jogo.set_var("ir_para", SALAS[sala])
    for k, v in vars_.items():
        jogo.set_var(k, v)
    jogo.tick(80)


def ir_eixo(jogo, eixo, destino, limite=600):
    for _ in range(limite):
        d = destino - jogo.pos_jogador()[eixo]
        if abs(d) < 0.2:
            return
        b = ("right" if d > 0 else "left") if eixo == 0 else ("down" if d > 0 else "up")
        jogo.pb.button_press(b); jogo.tick(1); jogo.pb.button_release(b)
    raise AssertionError(f"preso no eixo {eixo} indo a {destino}: {jogo.pos_jogador()}")


def virar(jogo, direcao):
    jogo.pb.button_press(direcao); jogo.tick(1); jogo.pb.button_release(direcao); jogo.tick(2)


def atirar(jogo, frames=2):
    jogo.pb.button_press("a"); jogo.tick(frames); jogo.pb.button_release("a"); jogo.tick(1)


def ate_titulo(jogo):
    for _ in range(600):
        jogo.tick(1)
        if jogo.var("cena") == 10:
            jogo.tick(40)
            return
    raise AssertionError("não chegou ao título")


def boot_sorteado(jogo, **vars_):
    """Caminho normal: título -> A -> o jogo sorteia sala e inimigos. vars_ vale antes do A
    (use prof_inicial para começar mais fundo)."""
    ate_titulo(jogo)
    for k, v in vars_.items():
        jogo.set_var(k, v)
    jogo.pb.button_press("a"); jogo.tick(3); jogo.pb.button_release("a")
    jogo.tick(90)


def mirar(jogo, k, secundario=False):
    """Vira o jogador para o inimigo do slot k (lê ex_k/ey_k, em pixels).
    secundario=True usa o eixo de menor distância (pega inimigo na diagonal)."""
    px, py = jogo.pos_jogador()
    dx = jogo.var(f"ex_{k}") / 8 - px
    dy = jogo.var(f"ey_{k}") / 8 - py
    if (abs(dx) > abs(dy)) != secundario:
        virar(jogo, "right" if dx > 0 else "left")
    else:
        virar(jogo, "down" if dy > 0 else "up")


def limpar_sala(jogo, limite=900):
    """Mira e atira no primeiro inimigo vivo até a sala abrir (para se a cena mudar, ex.: morreu)."""
    cena0 = jogo.var("cena")
    for i in range(limite):
        if jogo.var("vivos") == 0:
            return True
        if jogo.var("cena") != cena0:
            return False
        vivo = next((k for k in (1, 2, 3, 4) if jogo.var(f"tipo_{k}") != 0), None)
        if vivo:
            mirar(jogo, vivo, secundario=bool(i % 2))
        atirar(jogo, 1)
    return jogo.var("vivos") == 0


def caminho(jogo, destino):
    """Lista de tiles (x, y do pé) do jogador até destino, evitando paredes (herói tem 2 tiles de largura)."""
    col = json.loads((ARTE / f"colisao_{NOME_CENA[jogo.var('cena')]}.json").read_text())
    livre = lambda x, y: 0 <= x < 19 and 0 < y < 18 and col[y][x] == 0 and col[y][x + 1] == 0
    px, py = jogo.pos_jogador()
    ini = (round(px), round(py))
    ant, fila = {ini: None}, deque([ini])
    while fila:
        p = fila.popleft()
        if p == destino:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (p[0] + dx, p[1] + dy)
            if q not in ant and livre(*q):
                ant[q] = p
                fila.append(q)
    if destino not in ant:
        raise AssertionError(f"sem caminho de {ini} até {destino}")
    rota, p = [], destino
    while p is not None:
        rota.append(p)
        p = ant[p]
    return rota[::-1]


def andar_ate(jogo, destino):
    cena0 = jogo.var("cena")
    for (x, y) in caminho(jogo, destino)[1:]:
        if jogo.var("cena") != cena0:
            return
        ir_eixo(jogo, 0, float(x))
        ir_eixo(jogo, 1, float(y))


def ir_porta(jogo, lado, limite=900):
    """Vai (por busca de caminho) até logo abaixo do vão da porta e entra; volta quando a cena muda."""
    cena0 = jogo.var("cena")
    andar_ate(jogo, (2 if lado == "esq" else 16, 3))
    for _ in range(limite):
        if jogo.var("cena") != cena0:
            jogo.tick(60)
            return
        jogo.pb.button_press("up"); jogo.tick(1); jogo.pb.button_release("up")
    raise AssertionError(f"não entrou na porta {lado}: {jogo.pos_jogador()}")
