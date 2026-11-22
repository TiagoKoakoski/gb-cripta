import pytest
from caminhos import boot, boot_sorteado, limpar_sala


def test_sorteio_por_profundidade(rom_jogo):
    from emu import Emu
    vistos_raso, vistos_fundo, n_raso, n_fundo = set(), set(), [], []
    for semente in range(1, 13):
        for prof, tipos, ns in ((1, vistos_raso, n_raso), (5, vistos_fundo, n_fundo)):
            e = Emu(*rom_jogo)
            boot_sorteado(e, profundidade=prof, semente=semente)
            t = [e.var(f"tipo_{k}") for k in (1, 2, 3, 4)]
            assert 1 <= e.var("cena") <= 4
            tipos.update(x for x in t if x)
            ns.append(sum(1 for x in t if x))
            e.fechar()
    assert vistos_raso <= {1, 2} and max(n_raso) <= 2 and min(n_raso) >= 1
    assert 3 in vistos_fundo and min(n_fundo) >= 3 and max(n_fundo) <= 4


def test_slots_longe_da_entrada():
    from gerar_projeto import POS_SLOTS
    from gerar_arte import NASCIMENTO
    for sala, slots in POS_SLOTS.items():
        for (x, y) in slots:
            assert abs(x - NASCIMENTO[0]) + abs(y + 1 - NASCIMENTO[1]) >= 5, (sala, x, y)


def andou(jogo, k, frames):
    a = (jogo.var(f"ex_{k}"), jogo.var(f"ey_{k}"))
    jogo.tick(frames)
    return a != (jogo.var(f"ex_{k}"), jogo.var(f"ey_{k}"))


def test_slime_anda(jogo):
    boot(jogo, tipo_1=2, tipo_2=0, tipo_3=0, tipo_4=0)
    jogo.tick(30)
    assert andou(jogo, 1, 300)


def test_morcego_persegue(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=6, vida_max=6)
    jogo.tick(10)
    px, py = jogo.pos_jogador()
    d0 = abs(jogo.var("ex_1") / 8 - px) + abs(jogo.var("ey_1") / 8 - py)
    jogo.tick(60)
    d1 = abs(jogo.var("ex_1") / 8 - px) + abs(jogo.var("ey_1") / 8 - py)
    assert d1 < d0


def test_esqueleto_atira_e_tira_vida(jogo):
    boot(jogo, tipo_1=3, tipo_2=0, tipo_3=0, tipo_4=0)
    for _ in range(600):
        jogo.tick(1)
        if jogo.var("vida") < 3:
            break
    assert jogo.var("vida") == 2


@pytest.mark.parametrize("sala", ["sala_1", "sala_2", "sala_3", "sala_4"])
def test_layouts_limpam_e_abrem(jogo, sala):
    boot(jogo, sala, tipo_1=1, tipo_2=2, tipo_3=3, tipo_4=1, vida=99, vida_max=6, dano=3, cadencia=1)
    assert jogo.var("vivos") == 4
    assert limpar_sala(jogo)
    jogo.tick(15)   # portas abrem no fim do mesmo script
    assert jogo.var("porta_esq") in (1, 2, 3)


def test_morcego_nao_gruda(jogo):
    """Morcego encostado recua: o jogador parado consegue acertá-lo atirando pra baixo/cima."""
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=99, vida_max=6)
    jogo.tick(200)
    grudado = 0
    for _ in range(300):
        jogo.tick(1)
        px, py = jogo.pos_jogador()
        if abs(jogo.var("ex_1") / 8 - px) < 1 and abs(jogo.var("ey_1") / 8 - py) < 1:
            grudado += 1
    assert grudado < 100   # não pode passar a maior parte do tempo em cima do jogador
