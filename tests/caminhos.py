"""Ajudas pros testes: boot controlado, posição, mira."""

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


def boot_sorteado(jogo, **vars_):
    """Boot normal (ir_para=0): o próprio jogo sorteia sala e inimigos."""
    for _ in range(400):
        jogo.tick(1)
        if jogo.var("vida") == 3:
            break
    jogo.tick(2)
    for k, v in vars_.items():
        jogo.set_var(k, v)
    jogo.tick(80)


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
    """Mira e atira no primeiro inimigo vivo até a sala abrir."""
    for i in range(limite):
        if jogo.var("vivos") == 0:
            return True
        vivo = next((k for k in (1, 2, 3, 4) if jogo.var(f"tipo_{k}") != 0), None)
        if vivo:
            mirar(jogo, vivo, secundario=bool(i % 2))
        atirar(jogo, 1)
    return jogo.var("vivos") == 0
