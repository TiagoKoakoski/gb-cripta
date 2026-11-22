import shutil
from caminhos import boot, boot_sorteado, ate_titulo, limpar_sala, ir_porta

CENA_FIM, CENA_VITORIA, CENA_TITULO = 8, 9, 10


def esperar_cena(jogo, cena, frames=900):
    for _ in range(frames):
        jogo.tick(1)
        if jogo.var("cena") == cena:
            return True
    return False


def test_boot_vai_ao_titulo(jogo):
    ate_titulo(jogo)
    assert jogo.var("cena") == CENA_TITULO


def test_titulo_a_comeca(jogo):
    boot_sorteado(jogo)
    assert 1 <= jogo.var("cena") <= 4
    assert jogo.var("profundidade") == 1 and jogo.var("vida") == 3


def test_chefe_tem_12_e_rajada(jogo):
    boot(jogo, "chefe", vida=99)
    assert jogo.var("hp_chefe") == 12
    jogo.tick(400)
    assert jogo.var("rajadas") >= 1


def test_matar_chefe_vence(jogo):
    boot(jogo, "chefe", vida=99, dano=4, cadencia=1)
    assert limpar_sala(jogo, limite=1500)
    assert esperar_cena(jogo, CENA_VITORIA)


def test_recorde_salvo(rom_jogo, tmp_path):
    from emu import Emu
    rom = tmp_path / "cripta.gb"
    shutil.copy(rom_jogo[0], rom)
    shutil.copy(rom_jogo[1], tmp_path / "cripta.noi")
    shutil.copy(rom_jogo[0].with_suffix(".globals"), tmp_path / "cripta.globals")
    e = Emu(rom, tmp_path / "cripta.noi")
    boot(e, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=1, profundidade=3)
    assert esperar_cena(e, CENA_FIM)
    e.tick(30)
    assert e.var("recorde") == 3
    e.fechar(salvar=True)
    e2 = Emu(rom, tmp_path / "cripta.noi")
    ate_titulo(e2)
    assert e2.var("recorde") == 3
    e2.fechar()


def test_recomeco_zera_build(jogo):
    boot(jogo, tipo_1=1, tipo_2=0, tipo_3=0, tipo_4=0, vida=1, dano=3, cadencia=1, rapido=1, vida_max=5)
    assert esperar_cena(jogo, CENA_FIM)
    jogo.tick(60)
    jogo.pb.button_press("a"); jogo.tick(3); jogo.pb.button_release("a")
    assert esperar_cena(jogo, CENA_TITULO)
    jogo.tick(40)
    jogo.pb.button_press("a"); jogo.tick(3); jogo.pb.button_release("a")
    jogo.tick(90)
    assert (jogo.var("dano"), jogo.var("cadencia"), jogo.var("rapido"), jogo.var("vida"), jogo.var("vida_max"),
            jogo.var("profundidade")) == (1, 5, 0, 3, 3, 1)
