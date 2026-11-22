from PIL import Image
from caminhos import boot, virar, atirar

CENA_FIM = 8


def esperar(jogo, cond, frames):
    for _ in range(frames):
        jogo.tick(1)
        if cond():
            return True
    return False


def test_encostar_tira_vida(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0)
    assert esperar(jogo, lambda: jogo.var("vida") < 3, 600)
    assert jogo.var("vida") == 2


def test_invencibilidade(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0)
    assert esperar(jogo, lambda: jogo.var("vida") < 3, 600)
    for _ in range(45):           # morcego continua encostado
        jogo.tick(1)
        assert jogo.var("vida") == 2


def test_morte_vai_pro_fim(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=1)
    assert esperar(jogo, lambda: jogo.var("cena") == CENA_FIM, 900)


def test_vivos_nunca_negativo_e_abre(jogo):
    boot(jogo, tipo_1=1, tipo_2=1, tipo_3=0, tipo_4=0, vida=6, vida_max=6, cadencia=1)
    virar(jogo, "up")
    for _ in range(300):
        atirar(jogo, 1)
        assert jogo.var("vivos") >= 0
        if jogo.var("vivos") == 0:
            break
    jogo.tick(10)
    assert jogo.var("vivos") == 0
    assert jogo.var("porta_esq") in (1, 2, 3)


def coracoes(jogo, tmp_path):
    """Lê os 6 corações do HUD (pares em x = 7,9,11 tiles): conta pixels de miolo de cada um."""
    jogo.foto(tmp_path / "h.png")
    im = Image.open(tmp_path / "h.png").convert("RGB")
    out = []
    for j in range(3):
        x0 = (7 + 2 * j) * 8
        for dx in (1, 9):
            reg = list(im.crop((x0 + dx + 1, 5, x0 + dx + 6, 10)).getdata())
            out.append(reg)
    return out


def test_hud_coracoes(jogo, tmp_path):
    boot(jogo, tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0, vida=2, vida_max=5)
    jogo.tick(10)
    r = coracoes(jogo, tmp_path)
    assert r[0] == r[1]                       # 1º e 2º cheios
    assert r[2] == r[3] == r[4]               # 3º, 4º e 5º vazios
    assert r[0] != r[2]                       # cheio != vazio
    assert r[5] != r[4]                       # 6º: nada (só o muro)


def test_invencibilidade_dura_cerca_de_1s(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=6, vida_max=6)
    assert esperar(jogo, lambda: jogo.var("vida") < 6, 600)
    n = 0
    while jogo.var("invencivel") != 0 and n < 400:
        jogo.tick(1); n += 1
    assert 45 <= n <= 90, n
