"""Bot simples: começa no título, limpa cada sala mirando no inimigo mais próximo, entra na porta
da esquerda e fotografa cada sala em build/fotos/. Não precisa vencer; prova que a partida flui.

Uso: venv/bin/python ferramentas/jogar_sozinho.py   (compile antes com ferramentas/compilar.sh rom)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "ferramentas"), str(RAIZ / "tests")]
from emu import Emu  # noqa: E402
from caminhos import ate_titulo, limpar_sala, ir_porta, ir_eixo  # noqa: E402

NOMES = {1: "combate", 2: "combate", 3: "combate", 4: "combate", 5: "tesouro", 6: "fonte", 7: "chefe",
         8: "fim", 9: "vitoria"}


def main():
    fotos = RAIZ / "build/fotos"
    fotos.mkdir(parents=True, exist_ok=True)
    e = Emu(RAIZ / "build/cripta.gb", RAIZ / "build/cripta.noi")
    ate_titulo(e)
    e.foto(fotos / "00_titulo.png")
    e.pb.button_press("a"); e.tick(3); e.pb.button_release("a"); e.tick(90)
    n = 1
    while e.var("cena") not in (8, 9) and n < 12:
        cena = e.var("cena")
        e.foto(fotos / f"{n:02d}_{NOMES.get(cena, cena)}_p{e.var('profundidade')}.png")
        print(f"sala {n}: {NOMES.get(cena)} prof={e.var('profundidade')} vida={e.var('vida')}")
        if cena in (5, 6):                      # pega o item / usa a fonte no centro
            ir_eixo(e, 1, 11.0); e.tick(30)
        limpar_sala(e, limite=1200)
        if e.var("cena") in (8, 9):
            break
        e.tick(20)
        try:
            ir_porta(e, "esq")
        except AssertionError:
            if e.var("cena") not in (8, 9):
                raise
        n += 1
    e.tick(60)
    e.foto(fotos / f"{n:02d}_{NOMES.get(e.var('cena'))}.png")
    print("terminou em", NOMES.get(e.var("cena")), "profundidade", e.var("profundidade"), "recorde", e.var("recorde"))
    e.fechar()


if __name__ == "__main__":
    main()
