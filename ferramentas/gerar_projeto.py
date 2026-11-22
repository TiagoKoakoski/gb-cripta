"""Gera o projeto GB Studio 4.3.2 da Cripta de Bolso em projeto/ (abre no GB Studio).

IDs determinísticos (uuid5 por nome). Lógica em funções nomeadas por regra do jogo.
"""
import hashlib
import json
import shutil
import uuid
from pathlib import Path

from PIL import Image

import gerar_arte as A

RAIZ = Path(__file__).resolve().parent.parent
PROJ = RAIZ / "projeto"
TEMPLATE = Path.home() / "Projetos/jogos/_ferramentas/gb-studio/appData/templates/blank"
NS = uuid.UUID("2b7e9c41-5d0a-4f6e-9a3b-8c1d2e4f6a70")

SLOTS = [1, 2, 3, 4]
COMBATE = ["sala_1", "sala_2", "sala_3", "sala_4"]
# posição (tile, canto sup. esq. do sprite 16x16) de cada slot de inimigo por sala
POS_SLOTS = {
    "sala_1": [(3, 3), (16, 3), (9, 6), (9, 10)],
    "sala_2": [(3, 3), (16, 3), (9, 4), (3, 11)],
    "sala_3": [(3, 3), (16, 3), (9, 5), (9, 10)],
    "sala_4": [(6, 3), (13, 3), (9, 6), (16, 9)],
}
TIPOS = {1: "morcego", 2: "slime", 3: "esqueleto"}
VIDA_TIPO = {1: 1, 2: 2, 3: 3}
IR_PARA = {1: "sala_1", 2: "sala_2", 3: "sala_3", 4: "sala_4", 5: "sala_tesouro", 6: "sala_fonte", 7: "sala_chefe"}
CENA_NUM = {"boot": 0, "sala_1": 1, "sala_2": 2, "sala_3": 3, "sala_4": 4, "sala_tesouro": 5,
            "sala_fonte": 6, "sala_chefe": 7, "fim": 8, "vitoria": 9, "titulo": 10}
PARES_HUD = 3  # cada ator mostra 2 corações (limite de 10 sprites por linha do Game Boy)
PORTA_SPRITE = {1: "porta_combate", 2: "porta_tesouro", 3: "porta_fonte"}

VARIAVEIS = (["vida", "vida_max", "dano", "cadencia", "rapido", "profundidade", "vivos", "porta_esq",
              "porta_dir", "recarga", "invencivel", "recorde", "venceu", "item_sala", "fonte_usada",
              "ir_para", "tiros", "sorte", "cena", "fio_pisca", "semente", "qtd", "sala_sorteada", "hp_chefe", "rajadas", "prof_inicial"] +
             [f"tipo_{k}" for k in SLOTS] + [f"hp_{k}" for k in SLOTS] +
             [f"{p}{e}_{k}" for k in SLOTS for p in ("e", "p") for e in ("x", "y")])
VAR = {n: str(i) for i, n in enumerate(VARIAVEIS)}


def ID(nome):
    return str(uuid.uuid5(NS, nome))


# ------------------------------------------------------------------ eventos

def ev(comando, children=None, **args):
    ev.n += 1
    e = {"command": comando, "args": args, "id": ID(f"ev-{ev.n}")}
    if children is not None:
        e["children"] = children
    return e


ev.n = 0


def renovar_ids(eventos):
    """Cópia profunda com IDs de evento novos (o mesmo script usado em dois lugares)."""
    import copy
    novo = copy.deepcopy(eventos)

    def walk(o):
        if isinstance(o, dict):
            if "command" in o:
                ev.n += 1
                o["id"] = ID(f"ev-{ev.n}")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(novo)
    return novo


def num(v):
    return {"type": "number", "value": v}


def var(nome):
    return {"type": "variable", "value": VAR[nome]}


def op(tipo, a, b):
    return {"type": tipo, "valueA": a, "valueB": b}


def igual(nome, valor):
    return op("eq", var(nome), num(valor))


def se(cond, entao, senao=None):
    return ev("EVENT_IF", children={"true": entao + [ev("EVENT_END")], "false": (senao or []) + [ev("EVENT_END")]},
              condition=cond, __collapseElse=senao is None, __disableElse=senao is None)


def setar(nome, valor):
    return ev("EVENT_SET_VALUE", variable=VAR[nome], value=num(valor) if isinstance(valor, int) else valor)


def somar(nome):
    return ev("EVENT_INC_VALUE", variable=VAR[nome])


def tirar(nome):
    return ev("EVENT_DEC_VALUE", variable=VAR[nome])


def sorteio(n):
    """0..n-1"""
    return {"type": "rnd", "value": num(n)}


def som(tipo="beep", pitch=4, frequency=200, duration=0.2):
    return ev("EVENT_SOUND_PLAY_EFFECT", type=tipo, pitch=pitch, frequency=frequency, duration=duration,
              wait=False, priority="medium")


def esperar(frames):
    return ev("EVENT_WAIT", time=num(frames / 60), frames=num(frames), units="frames")


CENA_ATUAL = [""]  # cena sendo montada: IDs e símbolos de atores/gatilhos são únicos por cena


def a(nome):
    return ID(f"ator-{CENA_ATUAL[0]}-{nome}")


def esconder(nome):
    return ev("EVENT_ACTOR_HIDE", actorId=a(nome))


def mostrar(nome):
    return ev("EVENT_ACTOR_SHOW", actorId=a(nome))


def sem_colisao(nome):
    return ev("EVENT_ACTOR_COLLISIONS_DISABLE", actorId=a(nome))


def trocar_sprite(ator_id, sprite):
    return ev("EVENT_ACTOR_SET_SPRITE", actorId=ator_id, spriteSheetId=ID(f"sprite-{sprite}"))


def ir_cena(cena, x=A.NASCIMENTO[0], y=A.NASCIMENTO[1]):
    return ev("EVENT_SWITCH_SCENE", sceneId=ID(f"cena-{cena}"), x=num(x), y=num(y), direction="up", fadeSpeed="1")


# ------------------------------------------------------------------ recursos

def sprite_res(nome, frames, tipo="fixed"):
    png = A.ARTE / f"{nome}.png"
    w, h = Image.open(png).size

    def quadro(i):
        sx = 16 * i
        return {"id": ID(f"{nome}-q{i}"), "tiles": [
            {"id": ID(f"{nome}-q{i}-t{k}"), "x": 8 * k, "y": 0, "sliceX": sx + 8 * k, "sliceY": 0,
             "flipX": False, "flipY": False, "palette": 0, "paletteIndex": 0, "objPalette": "OBP0",
             "priority": False} for k in (0, 1)]}

    if tipo == "multi_movement":
        mapa = [[2], [], [4], [0], [3, 2], [], [5, 4], [1, 0]]
    else:
        mapa = [list(range(frames))] + [[]] * 7
    anims = [{"id": ID(f"{nome}-a{i}"), "frames": [quadro(q) for q in idx] or
              [{"id": ID(f"{nome}-a{i}-v"), "tiles": []}]} for i, idx in enumerate(mapa)]
    return {
        "_resourceType": "sprite", "id": ID(f"sprite-{nome}"), "name": nome, "symbol": f"sprite_{nome}",
        "numTiles": 2 * frames, "canvasOriginX": 0, "canvasOriginY": 0, "canvasWidth": 16, "canvasHeight": 16,
        "boundsX": 2, "boundsY": -6, "boundsWidth": 12, "boundsHeight": 12, "animSpeed": 15,
        "filename": png.name, "width": w, "height": h, "checksum": hashlib.sha1(png.read_bytes()).hexdigest(),
        "states": [{"id": ID(f"{nome}-estado"), "name": "", "animationType": tipo,
                    "flipLeft": tipo == "multi_movement", "animations": anims}],
    }


def colisoes_str(col):
    plano = [0x0F if c else 0 for linha in col for c in linha]
    out, ultimo, n = "", -1, 0

    def fechar():
        return "!" if n == 1 else (f"{n:x}+" if n > 0 else "")
    for v in plano:
        if v != ultimo:
            out += fechar()
            n, ultimo = 0, v
            out += f"{v:02x}"
        n += 1
    return out + fechar()


def ator(nome, sprite, x, y, idx, grupo="", script=None, start=None, update=None, hit2=None, animar=False):
    return {
        "_resourceType": "actor", "id": a(nome), "_index": idx, "symbol": f"actor_{CENA_ATUAL[0]}_{nome}",
        "prefabId": "",
        "name": nome, "coordinateType": "tiles", "x": x, "y": y + 1, "frame": 0, "animate": animar,
        "spriteSheetId": ID(f"sprite-{sprite}"), "paletteId": "", "direction": "down", "moveSpeed": 1,
        "animSpeed": 15, "isPinned": False, "persistent": False, "collisionGroup": grupo,
        "collisionExtraFlags": [], "prefabScriptOverrides": {}, "script": script or [],
        "startScript": start or [], "updateScript": update or [],
        "hit1Script": [], "hit2Script": hit2 or [], "hit3Script": [],
    }


def gatilho(nome, x, y, w, h, idx, script):
    return {"_resourceType": "trigger", "id": ID(f"gat-{CENA_ATUAL[0]}-{nome}"), "_index": idx,
            "symbol": f"trigger_{CENA_ATUAL[0]}_{nome}",
            "prefabId": "", "name": nome, "x": x, "y": y, "width": w, "height": h,
            "prefabScriptOverrides": {}, "script": script, "leaveScript": []}


# ------------------------------------------------------------------ regras

def iniciar_partida():
    return [setar("vida", 3), setar("vida_max", 3), setar("dano", 1), setar("cadencia", 5), setar("rapido", 0),
            setar("profundidade", 1), setar("venceu", 0), setar("recarga", 0), setar("invencivel", 0),
            setar("tiros", 0), setar("ir_para", 0), setar("rajadas", 0)] + [setar(f"tipo_{k}", 0) for k in SLOTS]


def tiro_do_jogador():
    return [se(igual("recarga", 0), [
        ev("EVENT_LAUNCH_PROJECTILE", spriteSheetId=ID("sprite-tiro"), spriteStateId="", actorId="player",
           x=0, y=0, directionType="actor", otherActorId="player", direction="up", angle=0,
           speed=3, animSpeed=15, lifeTime=0.8, initialOffset=14, loopAnim=True, destroyOnHit=True,
           collisionGroup="2", collisionMask=["1"]),
        somar("tiros"),
        ev("EVENT_SET_VALUE", variable=VAR["recarga"], value=var("cadencia")),
        som("beep", pitch=7, duration=0.05),
    ])]


def relogio_recarga():
    """A cada 4 frames: recarga do tiro e invencibilidade piscando o herói."""
    return [se(op("gt", var("recarga"), num(0)), [tirar("recarga")]),
            se(op("gt", var("invencivel"), num(0)), [
                se(op("lt", var("invencivel"), num(255)), [tirar("invencivel")]),
                se(op("eq", op("mod", var("invencivel"), num(2)), num(1)),
                   [ev("EVENT_ACTOR_HIDE", actorId="player")], [ev("EVENT_ACTOR_SHOW", actorId="player")]),
            ])]


def abrir_portas():
    """Sorteia o tipo de cada porta (combate mais provável) e troca grade por ícone."""
    def tipo_porta(nome):
        # sorte 0..5: 0-2 combate, 3-4 tesouro, 5 fonte
        return [setar("sorte", sorteio(6)),
                setar(nome, 1),
                se(op("gte", var("sorte"), num(3)), [setar(nome, 2)]),
                se(op("gte", var("sorte"), num(5)), [setar(nome, 3)])]
    acoes = tipo_porta("porta_esq") + tipo_porta("porta_dir")
    for lado in ("esq", "dir"):
        for t, spr in PORTA_SPRITE.items():
            acoes.append(se(igual(f"porta_{lado}", t), [trocar_sprite(a(f"icone_{lado}"), spr)]))
        acoes += [ev("EVENT_ACTOR_DEACTIVATE", actorId=a(f"grade_{lado}")), mostrar(f"icone_{lado}")]
    return acoes + [som("tone", frequency=700, duration=0.15)]


def inimigo_morreu(k):
    return [setar(f"tipo_{k}", 0), ev("EVENT_ACTOR_DEACTIVATE", actorId="$self$"), tirar("vivos"),
            som("noise" if False else "crash", pitch=4, duration=0.1),
            se(igual("vivos", 0), abrir_portas())]


def acerto_no_inimigo(k):
    return [ev("EVENT_SET_VALUE", variable=VAR[f"hp_{k}"], value=op("sub", var(f"hp_{k}"), var("dano"))),
            se(op("lte", var(f"hp_{k}"), num(0)), inimigo_morreu(k))]


def ia_inimigo(k):
    """update do slot k: comportamento conforme tipo_k. Sempre publica a posição em ex_k/ey_k."""
    ex, ey, px, py = f"ex_{k}", f"ey_{k}", f"px_{k}", f"py_{k}"
    passo = lambda e, p, d: setar(e, op("add", var(e), op("max", num(-d), op("min", num(d), op("sub", var(p), var(e))))))
    onde = ev("EVENT_ACTOR_GET_POSITION", actorId="$self$", vectorX=VAR[ex], vectorY=VAR[ey], units="pixels")
    perto = op("and", op("lt", {"type": "abs", "value": op("sub", var(px), var(ex))}, num(12)),
               op("lt", {"type": "abs", "value": op("sub", var(py), var(ey))}, num(12)))
    def fugir(e, p, centro):
        """RECUO px para longe do jogador; alinhado com ele, foge para o centro da sala."""
        return se(op("gt", var(e), var(p)), [setar(p, op("add", var(e), num(RECUO)))], [
            se(op("lt", var(e), var(p)), [setar(p, op("sub", var(e), num(RECUO)))], [
                se(op("lt", var(e), num(centro)), [setar(p, op("add", var(e), num(RECUO)))],
                   [setar(p, op("sub", var(e), num(RECUO)))])])])
    recuar = [
        fugir(ex, px, 80), fugir(ey, py, 72),
        ev("EVENT_ACTOR_MOVE_TO", actorId="$self$", x=var(px), y=var(py), moveType="diagonal",
           useCollisions=True, collideWith=["walls"], units="pixels"),
        ev("EVENT_ACTOR_GET_POSITION", actorId="$self$", vectorX=VAR[ex], vectorY=VAR[ey], units="pixels"),
        esperar(30),
    ]
    perseguir = [
        ev("EVENT_ACTOR_GET_POSITION", actorId="player", vectorX=VAR[px], vectorY=VAR[py], units="pixels"),
        se(perto, recuar, [
            passo(ex, px, 8), passo(ey, py, 8),
            ev("EVENT_ACTOR_MOVE_TO", actorId="$self$", x=var(ex), y=var(ey), moveType="diagonal",
               useCollisions=True, collideWith=["walls"], units="pixels")]),
    ]
    mover = lambda dx, dy: ev("EVENT_ACTOR_MOVE_RELATIVE", actorId="$self$", x=num(dx), y=num(dy),
                              moveType="horizontal" if dx else "vertical", useCollisions=True,
                              collideWith=["walls", "actors"], units="pixels")
    vagar = [setar(px, sorteio(4)),
             se(igual(px, 0), [mover(16, 0)]), se(igual(px, 1), [mover(-16, 0)]),
             se(igual(px, 2), [mover(0, 16)]), se(igual(px, 3), [mover(0, -16)]),
             esperar(40)]
    atirar = [esperar(60), setar(px, sorteio(60)), ev("EVENT_WAIT", time=num(0.5), frames=var(px), units="frames"),
              se(op("ne", var(f"tipo_{k}"), num(0)), [
                  ev("EVENT_LAUNCH_PROJECTILE", spriteSheetId=ID("sprite-tiro_inimigo"), spriteStateId="",
                     actorId="$self$", x=0, y=0, directionType="target", targetActorId="player",
                     otherActorId="$self$", direction="down", angle=0, speed=1, animSpeed=15, lifeTime=2,
                     initialOffset=8, loopAnim=True, destroyOnHit=True, collisionGroup="3",
                     collisionMask=["player"]),
                  som("beep", pitch=2, duration=0.08)])]
    return [onde, se(igual(f"tipo_{k}", 1), perseguir, [
        se(igual(f"tipo_{k}", 2), vagar, [se(igual(f"tipo_{k}", 3), atirar, [esperar(10)])])])]


def sortear_inimigos():
    """Quantidade e tipos pela profundidade. raso (1-2): 1-2 inimigos, morcego/slime;
    meio (3-4): 2-3, qualquer; fundo (5+): 3-4, qualquer."""
    acoes = [setar("qtd", op("add", num(1), sorteio(2))),
             se(op("gte", var("profundidade"), num(3)), [setar("qtd", op("add", num(2), sorteio(2)))]),
             se(op("gte", var("profundidade"), num(5)), [setar("qtd", op("add", num(3), sorteio(2)))])]
    for k in SLOTS:
        acoes.append(se(op("gte", var("qtd"), num(k)), [
            se(op("gte", var("profundidade"), num(3)),
               [setar(f"tipo_{k}", op("add", num(1), sorteio(3)))],
               [setar(f"tipo_{k}", op("add", num(1), sorteio(2)))]),
        ], [setar(f"tipo_{k}", 0)]))
    return acoes


def ir_combate_sorteado():
    acoes = [setar("sala_sorteada", op("add", num(1), sorteio(4)))]
    for n in (1, 2, 3, 4):
        acoes.append(se(igual("sala_sorteada", n), [ir_cena(f"sala_{n}")]))
    return acoes


def embaralhar():
    """Semeia pelo relógio e avança 'semente' passos (testes usam pra variar o sorteio)."""
    return [ev("EVENT_RNG_SEED"),
            ev("EVENT_LOOP_WHILE", children={"true": [tirar("semente"), setar("sorte", sorteio(7))]},
               condition=op("gt", var("semente"), num(0)))]


def preparar_slot(k):
    acoes = [se(igual(f"tipo_{k}", 0), [ev("EVENT_ACTOR_DEACTIVATE", actorId=a(f"inimigo_{k}"))], [somar("vivos")])]
    for t, nome in TIPOS.items():
        acoes.append(se(igual(f"tipo_{k}", t), [trocar_sprite(a(f"inimigo_{k}"), nome), setar(f"hp_{k}", VIDA_TIPO[t])]))
    return acoes


def atualizar_hud():
    """Par j mostra corações 2j-1 e 2j. Estados: 0 cheio+cheio, 1 cheio+vazio, 2 vazio+vazio,
    3 cheio+nada, 4 vazio+nada; some se vida_max < 2j-1."""
    acoes = []
    for j in range(1, PARES_HUD + 1):
        p, s2 = 2 * j - 1, 2 * j
        nome = f"hud_{j}"
        spr = lambda e: trocar_sprite(a(nome), f"hud_{e}")
        dois = [se(op("gte", var("vida"), num(s2)), [spr(0)],
                   [se(op("gte", var("vida"), num(p)), [spr(1)], [spr(2)])])]
        um = [se(op("gte", var("vida"), num(p)), [spr(3)], [spr(4)])]
        acoes.append(se(op("gte", var("vida_max"), num(p)), [
            mostrar(nome), se(op("gte", var("vida_max"), num(s2)), dois, um)], [esconder(nome)]))
    return acoes


RECUO = 24  # px que o morcego recua depois de mergulhar
INVENCIVEL_TICKS = 15  # x4 frames = ~1 s


def jogador_levou_dano():
    """invencivel conta para baixo no relógio de 4 frames (sem threads: thread disparada dentro do
    script de colisão corrompia o estado do motor)."""
    return [se(igual("invencivel", 0), [
        setar("invencivel", INVENCIVEL_TICKS),
        tirar("vida"),
        som("crash", pitch=2, duration=0.2),
    ] + atualizar_hud() + [
        se(op("lte", var("vida"), num(0)), [setar("invencivel", 255), esperar(30), ir_cena("fim")]),
    ])]


def init_sala_combate(nome):
    return init_sala_comum(nome) + [setar("vivos", 0)] + [x for k in SLOTS for x in preparar_slot(k)] + \
        [se(igual("vivos", 0), abrir_portas())]


ITENS = {1: "item_forte", 2: "item_gatilho", 3: "item_coracao", 4: "item_botas"}
SALAS_ATE_CHEFE = 7


def entrar_porta(lado):
    """Profundidade +1; na 8ª vai pro chefe; senão vai ao tipo mostrado na porta."""
    nome = f"porta_{lado}"
    return [se(igual("vivos", 0), [
        somar("profundidade"),
        se(op("gt", var("profundidade"), num(SALAS_ATE_CHEFE)), [ir_cena("sala_chefe")], [
            se(igual(nome, 2), [ir_cena("sala_tesouro")], [
                se(igual(nome, 3), [ir_cena("sala_fonte")], sortear_inimigos() + ir_combate_sorteado())])]),
    ])]


def gatilhos_portas():
    return [gatilho(f"entrar_{lado}", x, y, 2, 2, i, entrar_porta(lado))
            for i, (lado, (x, y)) in enumerate(zip(("esq", "dir"), A.PORTAS))]


def ajustar_velocidade():
    """Sempre define as duas: a velocidade do jogador persiste entre cenas e partidas."""
    return [se(igual("rapido", 1), [ev("EVENT_ACTOR_SET_MOVEMENT_SPEED", actorId="player", speed=2)],
               [ev("EVENT_ACTOR_SET_MOVEMENT_SPEED", actorId="player", speed=1)])]


def efeito_item():
    return [
        se(igual("item_sala", 1), [ev("EVENT_SET_VALUE", variable=VAR["dano"], value=op("add", var("dano"), num(1)))]),
        se(igual("item_sala", 2), [ev("EVENT_SET_VALUE", variable=VAR["cadencia"],
                                      value=op("max", num(1), op("sub", var("cadencia"), num(2))))]),
        se(igual("item_sala", 3), [
            ev("EVENT_SET_VALUE", variable=VAR["vida_max"], value=op("min", num(6), op("add", var("vida_max"), num(1)))),
            ev("EVENT_SET_VALUE", variable=VAR["vida"], value=op("min", var("vida_max"), op("add", var("vida"), num(1))))]),
        se(igual("item_sala", 4), [setar("rapido", 1)] + ajustar_velocidade()),
    ]


def pegar_item():
    return [se(op("ne", var("item_sala"), num(0)),
               efeito_item() + [setar("item_sala", 0), esconder("objeto"), som("tone", frequency=900, duration=0.3)]
               + atualizar_hud())]


def usar_fonte():
    return [se(igual("fonte_usada", 0), [
        setar("fonte_usada", 1),
        ev("EVENT_SET_VALUE", variable=VAR["vida"], value=op("min", var("vida_max"), op("add", var("vida"), num(2)))),
        som("tone", frequency=500, duration=0.4),
        ev("EVENT_ACTOR_SET_FRAME", actorId=a("objeto"), frame=num(0)),
    ] + atualizar_hud())]


def init_sala_comum(nome):
    """Partes comuns de toda sala jogável: número da cena, HUD, tiro, relógio, velocidade."""
    return [setar("cena", CENA_NUM[nome]), setar("recarga", 0), setar("invencivel", 0),
            ev("EVENT_ACTOR_SHOW", actorId="player")] + atualizar_hud() + \
        [sem_colisao(f"hud_{j}") for j in range(1, PARES_HUD + 1)] + ajustar_velocidade() + \
        [esconder(f"icone_{l}") for l in ("esq", "dir")] + [sem_colisao(f"icone_{l}") for l in ("esq", "dir")] + \
        [ev("EVENT_SET_INPUT_SCRIPT", children={"true": tiro_do_jogador()}, input=["a"], override=True)]


def init_tesouro():
    acoes = init_sala_comum("sala_tesouro") + [setar("vivos", 0), setar("item_sala", op("add", num(1), sorteio(4)))]
    for t, spr in ITENS.items():
        acoes.append(se(igual("item_sala", t), [trocar_sprite(a("objeto"), spr)]))
    return acoes + [sem_colisao("objeto")] + abrir_portas()


def init_fonte():
    return init_sala_comum("sala_fonte") + [setar("vivos", 0), setar("fonte_usada", 0), sem_colisao("objeto")] + \
        abrir_portas()


def init_chefe():
    return init_sala_comum("sala_chefe") + [setar("vivos", 1), setar("tipo_1", 9), setar("hp_chefe", 12)]


def ia_chefe():
    """Persegue (mergulha e recua como o morcego) por ~2 s, para e solta 4 tiros em cruz."""
    def persegue():  # ramo 'perseguir' do morcego (sem o END), com IDs de evento novos a cada uso
        return ia_inimigo(1)[1]["children"]["true"][:-1]
    rajada = [ev("EVENT_LAUNCH_PROJECTILE", spriteSheetId=ID("sprite-tiro_inimigo"), spriteStateId="",
                 actorId="$self$", x=0, y=0, directionType="direction", direction=d, otherActorId="$self$",
                 angle=0, speed=2, animSpeed=15, lifeTime=2, initialOffset=8, loopAnim=True, destroyOnHit=True,
                 collisionGroup="3", collisionMask=["player"]) for d in ("up", "down", "left", "right")]
    onde = ev("EVENT_ACTOR_GET_POSITION", actorId="$self$", vectorX=VAR["ex_1"], vectorY=VAR["ey_1"], units="pixels")
    return [onde] + persegue() + persegue() + persegue() + persegue() + renovar_ids([onde]) + [esperar(20)] + rajada + [somar("rajadas"), som("crash", pitch=6),
                                                                    esperar(40)]


def acerto_no_chefe():
    return [ev("EVENT_SET_VALUE", variable=VAR["hp_chefe"], value=op("sub", var("hp_chefe"), var("dano"))),
            som("crash", pitch=5, duration=0.05),
            se(op("lte", var("hp_chefe"), num(0)), [
                setar("tipo_1", 0), setar("vivos", 0), setar("venceu", 1),
                ev("EVENT_ACTOR_DEACTIVATE", actorId="$self$"),
                setar("recorde", op("max", var("recorde"), num(SALAS_ATE_CHEFE + 1))),
                salvar(), esperar(40), ir_cena("vitoria")])]


def salvar():
    return ev("EVENT_SAVE_DATA", children={"true": [], "load": []}, saveSlot=0)


def mostrar_digito(ator_nome, var_nome):
    return [se(igual(var_nome, d), [trocar_sprite(a(ator_nome), f"digito_{d}")]) for d in range(10)]


def init_fim():
    return [setar("cena", CENA_NUM["fim"]), ev("EVENT_ACTOR_HIDE", actorId="player"),
            setar("recorde", op("max", var("recorde"), var("profundidade"))), salvar()] + \
        mostrar_digito("dig_prof", "profundidade") + mostrar_digito("dig_rec", "recorde") + \
        [esperar(30), ev("EVENT_AWAIT_INPUT", input=["a", "start"]), ir_cena("titulo")]


def init_vitoria():
    return [setar("cena", CENA_NUM["vitoria"]), ev("EVENT_ACTOR_HIDE", actorId="player")] + \
        mostrar_digito("dig_rec", "recorde") + \
        [esperar(30), ev("EVENT_AWAIT_INPUT", input=["a", "start"]), ir_cena("titulo")]


def comecar_partida():
    return embaralhar() + iniciar_partida() + [
        se(op("gt", var("prof_inicial"), num(0)), [ev("EVENT_SET_VALUE", variable=VAR["profundidade"],
                                                      value=var("prof_inicial"))]),
        setar("prof_inicial", 0)] + sortear_inimigos() + ir_combate_sorteado()


def init_titulo():
    return [setar("cena", CENA_NUM["titulo"]), ev("EVENT_ACTOR_HIDE", actorId="player"),
            ev("EVENT_IF_SAVED_DATA", children={"true": [ev("EVENT_PEEK_DATA", variableDest=VAR["recorde"],
                                                            variableSource=VAR["recorde"], saveSlot=0)],
                                                "false": []}, saveSlot=0),
            esperar(20), ev("EVENT_AWAIT_INPUT", input=["a", "start"]), som("tone", frequency=800, duration=0.2)] + \
        comecar_partida()


def init_boot():
    cadeia = [ir_cena("titulo")]
    for n in sorted(IR_PARA, reverse=True):
        cadeia = [se(igual("ir_para", n), [ir_cena(IR_PARA[n])], cadeia)]
    return [setar("cena", 0), ev("EVENT_ACTOR_HIDE", actorId="player")] + iniciar_partida() + [esperar(20)] + cadeia


# ------------------------------------------------------------------ cenas

def cena(nome, fundo, script, atores=(), gats=(), colisao=None, tipo="TOPDOWN", dano=None):
    col = colisao if colisao is not None else [[0] * A.LARG for _ in range(A.ALT)]
    return {"_resourceType": "scene", "id": ID(f"cena-{nome}"), "_index": 0, "type": tipo, "name": nome,
            "symbol": f"scene_{nome}", "x": 0, "y": 0, "width": A.LARG, "height": A.ALT,
            "backgroundId": ID(f"bg-{fundo}"), "tilesetId": "", "colorModeOverride": "none",
            "paletteIds": [], "spritePaletteIds": [], "autoFadeSpeed": 1, "script": script,
            "playerHit1Script": dano or [], "playerHit2Script": [], "playerHit3Script": renovar_ids(dano or []),
            "collisions": colisoes_str(col)}, list(atores), list(gats)


def atores_hud(i0):
    out = []
    for j in range(1, PARES_HUD + 1):
        # o 1º par do HUD carrega o relógio de 4 frames (timer de cena do motor só roda a cada 16)
        relogio = relogio_recarga() + [esperar(4)] if j == 1 else None
        out.append(ator(f"hud_{j}", "hud_0", 7 + 2 * (j - 1), 0, i0, update=relogio)); i0 += 1
    return out, i0


def atores_portas(i0):
    out = []
    for lado, (x, y) in zip(("esq", "dir"), A.PORTAS):
        out.append(ator(f"grade_{lado}", "porta_fechada", x, y, i0)); i0 += 1
        out.append(ator(f"icone_{lado}", "porta_combate", x, y, i0)); i0 += 1
    return out, i0


def sala_combate(nome):
    CENA_ATUAL[0] = nome
    col = json.loads((A.ARTE / f"colisao_{nome}.json").read_text())
    atores, i = [], 0
    for k, (x, y) in zip(SLOTS, POS_SLOTS[nome]):
        atores.append(ator(f"inimigo_{k}", "morcego", x, y, i, grupo="1", update=ia_inimigo(k),
                           hit2=acerto_no_inimigo(k), animar=True)); i += 1
    portas, i = atores_portas(i)
    hud, i = atores_hud(i)
    return cena(nome, nome, init_sala_combate(nome), atores + portas + hud, gatilhos_portas(), col,
                dano=jogador_levou_dano())


def sala_especial(nome, sprite_objeto, init_fn, tocar_fn):
    CENA_ATUAL[0] = nome
    init, ao_tocar = init_fn(), tocar_fn()
    col = json.loads((A.ARTE / f"colisao_{nome}.json").read_text())
    portas, i = atores_portas(0)
    hud, i = atores_hud(i)
    objeto = ator("objeto", sprite_objeto, 9, 8, i)
    gats = gatilhos_portas() + [gatilho("tocar_objeto", 8, 7, 4, 4, 2, ao_tocar)]
    return cena(nome, nome, init, portas + hud + [objeto], gats, col, dano=jogador_levou_dano())


def todas_cenas():
    CENA_ATUAL[0] = "fim"
    fim = cena("fim", "fim", init_fim(), [ator("dig_prof", "digito_0", 9, 8, 0), ator("dig_rec", "digito_0", 9, 12, 1)])
    CENA_ATUAL[0] = "vitoria"
    vit = cena("vitoria", "vitoria", init_vitoria(), [ator("dig_rec", "digito_0", 9, 12, 0)])
    CENA_ATUAL[0] = "boot"
    return [cena("boot", "titulo", init_boot()), cena("titulo", "titulo", init_titulo()), fim, vit] + \
        [sala_combate(n) for n in COMBATE] + [
            sala_especial("sala_tesouro", "item_forte", init_tesouro, pegar_item),
            sala_especial("sala_fonte", "fonte", init_fonte, usar_fonte),
            sala_chefe()]


def sala_chefe():
    CENA_ATUAL[0] = "sala_chefe"
    col = json.loads((A.ARTE / "colisao_sala_chefe.json").read_text())
    portas, i = atores_portas(0)
    hud, i = atores_hud(i)
    rei = ator("rei", "rei", 9, 4, i, grupo="1", update=ia_chefe(), hit2=acerto_no_chefe(), animar=True)
    return cena("sala_chefe", "sala_chefe", init_chefe(), portas + hud + [rei], [], col, dano=jogador_levou_dano())


SPRITES = [("jogador", 8, "multi_movement"), ("tiro", 1, "fixed"), ("tiro_inimigo", 1, "fixed"),
           ("morcego", 2, "fixed"), ("slime", 2, "fixed"), ("esqueleto", 2, "fixed"), ("rei", 2, "fixed"),
           ("coracao", 2, "fixed"), ("digitos", 10, "fixed"), ("porta_combate", 1, "fixed"),
           ("porta_tesouro", 1, "fixed"), ("porta_fonte", 1, "fixed"), ("porta_fechada", 1, "fixed"),
           ("hud_0", 1, "fixed"), ("hud_1", 1, "fixed"), ("hud_2", 1, "fixed"), ("hud_3", 1, "fixed"),
           ("hud_4", 1, "fixed"), ("bau", 1, "fixed")] + [(f"digito_{d}", 1, "fixed") for d in range(10)] + [ ("fonte", 1, "fixed"), ("item_forte", 1, "fixed"), ("item_gatilho", 1, "fixed"),
           ("item_coracao", 1, "fixed"), ("item_botas", 1, "fixed")]
FUNDOS = list(A.OBSTACULOS) + ["titulo", "fim", "vitoria"]


# ------------------------------------------------------------------ escrita

def escrever(caminho, dado):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dado, indent=2, ensure_ascii=False))


def main():
    A.main()
    if PROJ.exists():
        shutil.rmtree(PROJ)
    shutil.copytree(TEMPLATE, PROJ)
    for d in ("sprites", "backgrounds"):
        for p in (PROJ / "assets" / d).glob("*"):
            p.unlink()
    dest = PROJ / "plugins/deslizar/engine/src/states/topdown.c"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(RAIZ / "motor/topdown.c", dest)

    escrever(PROJ / "project.gbsproj", {"_resourceType": "project", "name": "Cripta de Bolso", "author": "Tiago",
                                         "notes": "Gerado por ferramentas/gerar_projeto.py", "_version": "4.2.0",
                                         "_release": "10"})
    for nome, frames, tipo in SPRITES:
        shutil.copy(A.ARTE / f"{nome}.png", PROJ / "assets/sprites" / f"{nome}.png")
        escrever(PROJ / "assets/sprites" / f"{nome}.png.gbsres", sprite_res(nome, frames, tipo))
    for nome in FUNDOS:
        shutil.copy(A.ARTE / f"{nome}.png", PROJ / "assets/backgrounds" / f"{nome}.png")
        escrever(PROJ / "assets/backgrounds" / f"{nome}.png.gbsres", {
            "_resourceType": "background", "id": ID(f"bg-{nome}"), "name": nome, "symbol": f"bg_{nome}",
            "tileColors": "", "filename": f"{nome}.png", "width": A.LARG, "height": A.ALT,
            "imageWidth": 160, "imageHeight": 144, "autoColor": False})
    escrever(PROJ / "project/variables.gbsres", {
        "_resourceType": "variables",
        "variables": [{"id": VAR[n], "name": n, "symbol": f"var_{n}"} for n in VARIAVEIS], "constants": []})

    cfg = json.loads((PROJ / "project/settings.gbsres").read_text())
    cfg.update(startSceneId=ID("cena-boot"), startX=A.NASCIMENTO[0], startY=A.NASCIMENTO[1], startDirection="up",
               startMoveSpeed=1, colorMode="none", sgbEnabled=False)
    cfg["defaultPlayerSprites"] = {k: ID("sprite-jogador") for k in
                                   ["TOPDOWN", "PLATFORM", "ADVENTURE", "SHMUP", "POINTNCLICK", "LOGO"]}
    escrever(PROJ / "project/settings.gbsres", cfg)

    for i, (sc, atores, gats) in enumerate(todas_cenas()):
        sc["_index"], sc["x"] = i, 200 * i
        d = PROJ / "project/scenes" / sc["name"]
        escrever(d / "scene.gbsres", sc)
        for at in atores:
            escrever(d / "actors" / f"{at['name']}.gbsres", at)
        for g in gats:
            escrever(d / "triggers" / f"{g['name']}.gbsres", g)


if __name__ == "__main__":
    main()
