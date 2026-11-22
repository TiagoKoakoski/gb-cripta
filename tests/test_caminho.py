import pytest
from caminhos import boot, ir_porta, ir_eixo

VAZIA = dict(tipo_1=0, tipo_2=0, tipo_3=0, tipo_4=0)


def entrar(jogo, tipo, lado="esq", **extra):
    boot(jogo, **VAZIA, **extra)
    jogo.set_var("porta_esq" if lado == "esq" else "porta_dir", tipo)
    ir_porta(jogo, lado)


@pytest.mark.parametrize("tipo,cenas", [(1, {1, 2, 3, 4}), (2, {5}), (3, {6})])
def test_porta_leva_ao_tipo(jogo, tipo, cenas):
    entrar(jogo, tipo, "dir")
    assert jogo.var("cena") in cenas


def test_profundidade_sobe(jogo):
    entrar(jogo, 1)
    assert jogo.var("profundidade") == 2


def test_sala_8_e_chefe(jogo):
    entrar(jogo, 2, profundidade=7)
    assert jogo.var("cena") == 7


def pegar_centro(jogo):
    """Sobe até o objeto do centro (item ou fonte)."""
    ir_eixo(jogo, 1, 11.0)
    jogo.tick(20)


def sair_centro(jogo):
    ir_eixo(jogo, 1, 15.0)
    jogo.tick(10)


@pytest.mark.parametrize("item", [1, 2, 3, 4])
def test_itens_tem_efeito(jogo, item):
    entrar(jogo, 2)
    jogo.set_var("item_sala", item)
    antes = {v: jogo.var(v) for v in ("dano", "cadencia", "vida_max", "vida", "rapido")}
    pegar_centro(jogo)
    d = {v: jogo.var(v) for v in antes}
    if item == 1:
        assert d["dano"] == antes["dano"] + 1
    elif item == 2:
        assert d["cadencia"] < antes["cadencia"]
    elif item == 3:
        assert d["vida_max"] == antes["vida_max"] + 1 and d["vida"] == antes["vida"] + 1
    else:
        assert d["rapido"] == 1
        y0 = jogo.pos_jogador()[1]
        jogo.pb.button_press("down"); jogo.tick(16); jogo.pb.button_release("down")
        assert jogo.pos_jogador()[1] - y0 > 2.5   # mais que 2 tiles em 16 frames (normal = 2)


def test_item_uma_vez(jogo):
    entrar(jogo, 2)
    jogo.set_var("item_sala", 1)
    pegar_centro(jogo)
    sair_centro(jogo)
    pegar_centro(jogo)
    assert jogo.var("dano") == 2


def test_fonte_uma_vez(jogo):
    entrar(jogo, 3, vida=1)
    pegar_centro(jogo)
    assert jogo.var("vida") == 3
    sair_centro(jogo)
    jogo.set_var("vida", 1)
    pegar_centro(jogo)
    assert jogo.var("vida") == 1


def test_fonte_nao_passa_do_maximo(jogo):
    entrar(jogo, 3, vida=3)
    pegar_centro(jogo)
    assert jogo.var("vida") == jogo.var("vida_max") == 3


def test_ids_e_simbolos_unicos(rom_jogo):
    """GB Studio funde recursos com o mesmo símbolo: tesouro e fonte chegaram a dividir um gatilho."""
    import json
    from pathlib import Path
    ids, simbolos = [], []
    for f in (Path(__file__).resolve().parent.parent / "projeto/project/scenes").rglob("*.gbsres"):
        d = json.loads(f.read_text())
        ids.append(d["id"]); simbolos.append(d["symbol"])
    assert len(ids) == len(set(ids))
    assert len(simbolos) == len(set(simbolos))


def test_ids_de_evento_unicos(rom_jogo):
    import json
    from pathlib import Path
    ids = []

    def walk(o):
        if isinstance(o, dict):
            if "command" in o:
                ids.append(o["id"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in (Path(__file__).resolve().parent.parent / "projeto/project/scenes").rglob("*.gbsres"):
        walk(json.loads(f.read_text()))
    assert len(ids) == len(set(ids))


def test_morto_nao_passa_pela_porta(jogo):
    from caminhos import andar_ate
    boot(jogo, **VAZIA)
    andar_ate(jogo, (2, 3))
    jogo.set_var("vida", 0)
    jogo.set_var("invencivel", 255)   # estado durante a espera da morte
    cena0 = jogo.var("cena")
    for _ in range(60):
        jogo.pb.button_press("up"); jogo.tick(1)
    jogo.pb.button_release("up")
    jogo.tick(30)
    assert jogo.var("cena") == cena0
