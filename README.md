# Cripta de Bolso

Roguelike de masmorra para Game Boy, feito no **GB Studio 4.3.2**. Ação em tempo real sala por
sala (como The Binding of Isaac) com escolha de caminho (como Slay the Spire): ao limpar cada sala,
duas portas mostram o que vem a seguir. Morreu, recomeça do zero; o recorde fica salvo.

## Como jogar

- **No PC / TV:** `./jogar.sh` abre no navegador em tela cheia (controle USB/Bluetooth funciona).
- **Em emulador / celular:** `build/cripta.gb` (gerar com `./ferramentas/compilar.sh rom`).

Controles: **direcional** anda, **A** atira para onde o herói olha. No teclado do navegador:
setas (ou WASD) para andar, Z/J/Alt para o A, Enter para o Start.

- **Vida:** 3 corações (até 6). Encostar em inimigo ou levar tiro tira 1; depois ~1 s piscando, invencível.
- **Inimigos** (mais e mais fortes conforme você desce):
  - **Morcego**, 1 vida: mergulha em você e recua.
  - **Slime**, 2 vidas: anda à toa.
  - **Esqueleto**, 3 vidas: fica parado e atira em você.
- **Portas:** fechadas por grades até a sala ficar vazia. Aí cada porta mostra um ícone da próxima sala:
  **caveira** = combate, **baú** = tesouro, **coração** = fonte de cura.
- **Tesouro:** um destes itens, sorteado:
  - **Espada:** dano +1.
  - **Raio:** atira mais rápido.
  - **Coração:** +1 de vida máxima e cura 1.
  - **Botas:** anda mais rápido.
- **Fonte:** cura 2 corações (uma vez).
- **7 salas e depois o chefe:** o Rei Esqueleto tem 12 de vida, persegue você e solta tiros em cruz.
- **Recorde:** a maior profundidade alcançada, salva no cartucho. Aparece na tela de fim e de vitória.

## Gerar, compilar e testar

```bash
V=~/Projetos/jogos/_ferramentas/venv/bin
$V/python ferramentas/gerar_projeto.py    # arte/ + projeto/ (GB Studio), tudo gerado por código
./ferramentas/compilar.sh rom             # build/cripta.gb
./ferramentas/compilar.sh web             # build/web/
$V/pytest tests -q                        # 54 testes rodando a ROM no emulador PyBoy
$V/python ferramentas/jogar_sozinho.py    # bot joga do título até morrer e fotografa em build/fotos/
```

O projeto em `projeto/` abre no GB Studio (`projeto/project.gbsproj`), mas é **gerado**: mudanças
feitas só na interface somem na próxima geração. A lógica fica em `ferramentas/gerar_projeto.py`, com
uma função por regra: `ia_inimigo`, `ia_chefe`, `jogador_levou_dano`, `abrir_portas`, `entrar_porta`,
`sortear_inimigos`, `efeito_item`, `usar_fonte`, `init_titulo`...

Toolchain (CLI do GB Studio compilada do fonte, Node 21, PyBoy) em `~/Projetos/jogos/_ferramentas`.
`motor/topdown.c` é um ajuste do motor (deslizar ao segurar diagonal contra parede), aplicado como
plugin do projeto.

## Pegadinhas do GB Studio descobertas aqui

- **IDs e símbolos:** atores e gatilhos precisam de ID e símbolo únicos no projeto inteiro. Com nomes
  iguais em cenas diferentes, o GB Studio compila um só (o tesouro chegou a usar o gatilho da fonte).
- **Threads em colisão:** `EVENT_THREAD_START` disparado dentro do script de colisão do jogador
  corrompia o estado. A invencibilidade virou contagem no relógio.
- **Trocar quadro:** `EVENT_ACTOR_SET_FRAME` mostrou o quadro errado. Para HUD e dígitos foram usados
  sprites separados com `EVENT_ACTOR_SET_SPRITE`.
- **Limite de sprites:** 10 sprites por linha. Por isso os corações do HUD são pares pequenos.
- **Carregar jogo:** `EVENT_LOAD_DATA` restaura a cena salva. Para ler só o recorde, usamos `EVENT_PEEK_DATA`.

Arte e sons 100% próprios (sons são os efeitos sintetizados do motor).
