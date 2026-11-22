from PIL import Image, ImageChops
from caminhos import boot, virar, atirar


def foto(jogo, p):
    jogo.foto(p)
    return Image.open(p).convert("RGB")


def test_jogador_atira(jogo, tmp_path):
    boot(jogo, tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0)
    virar(jogo, "up")
    a = foto(jogo, tmp_path / "a.png")
    atirar(jogo)
    jogo.tick(6)
    b = foto(jogo, tmp_path / "b.png")
    assert jogo.var("tiros") == 1
    assert ImageChops.difference(a, b).getbbox() is not None


def test_recarga(jogo):
    boot(jogo, tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0)
    virar(jogo, "up")
    for _ in range(60):
        atirar(jogo, 1)
    # cadência padrão: 1 tiro a cada ~20 frames => 60 apertos (~120 frames) dão no máx. ~7
    assert 2 <= jogo.var("tiros") <= 8


def test_morcego_morre(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0)
    assert jogo.var("vivos") == 1
    virar(jogo, "up")
    for _ in range(200):
        atirar(jogo, 1)
        if jogo.var("vivos") == 0:
            break
    assert jogo.var("vivos") == 0


def test_portas_abrem(jogo, tmp_path):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0)
    antes = foto(jogo, tmp_path / "a.png").crop((24, 0, 136, 24))
    virar(jogo, "up")
    for _ in range(200):
        atirar(jogo, 1)
        if jogo.var("vivos") == 0:
            break
    jogo.tick(20)
    depois = foto(jogo, tmp_path / "b.png").crop((24, 0, 136, 24))
    assert jogo.var("porta_esq") in (1, 2, 3)
    assert jogo.var("porta_dir") in (1, 2, 3)
    assert ImageChops.difference(antes, depois).getbbox() is not None


def test_sala_vazia_ja_abre(jogo):
    boot(jogo, tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0)
    assert jogo.var("vivos") == 0
    assert jogo.var("porta_esq") in (1, 2, 3)


def test_cadencia_padrao(jogo):
    boot(jogo, tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0)
    virar(jogo, "up")
    for _ in range(100):
        atirar(jogo, 1)          # 2 frames por aperto => ~200 frames
    assert 8 <= jogo.var("tiros") <= 12, jogo.var("tiros")
