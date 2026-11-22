"""Anti-objetivos do design: nada de morte injusta nem partida travada."""
import random
import pytest
from caminhos import boot, virar, atirar


def andar_aleatorio(jogo, semente, frames=3000):
    """Anda mudando de direção a cada 20 frames; devolve o maior tempo seguido sem conseguir se mexer."""
    rnd = random.Random(semente)
    ult, parado, pior = None, 0, 0
    for f in range(frames):
        if f % 20 == 0:
            for x in ("up", "down", "left", "right"):
                jogo.pb.button_release(x)
            jogo.pb.button_press(rnd.choice(["up", "down", "left", "right"]))
        jogo.tick(1)
        p = jogo.pos_jogador()
        parado = parado + 1 if p == ult else 0
        ult = p
        pior = max(pior, parado)
    for x in ("up", "down", "left", "right"):
        jogo.pb.button_release(x)
    return pior


@pytest.mark.parametrize("sala,tipos", [("sala_4", (1, 0, 0, 0)), ("sala_1", (1, 1, 0, 0))])
def test_morcego_nao_prende_o_jogador(rom_jogo, sala, tipos):
    from emu import Emu
    for semente in range(1, 9):
        e = Emu(*rom_jogo)
        boot(e, sala, vida=999, vida_max=6, tipo_1=tipos[0], tipo_2=tipos[1], tipo_3=0, tipo_4=0)
        pior = andar_aleatorio(e, semente)
        e.fechar()
        assert pior < 200, (sala, semente, pior)


def test_tiro_acerta_morcego_colado(jogo):
    """Morcego encostado no jogador: atirando nas 4 direções, a sala tem que limpar."""
    boot(jogo, "sala_1", vida=999, vida_max=6, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0)
    jogo.tick(150)
    for _ in range(40):
        for d in ("up", "down", "left", "right"):
            virar(jogo, d)
            atirar(jogo, 1)
            jogo.tick(10)
        if jogo.var("vivos") == 0:
            break
    assert jogo.var("vivos") == 0
