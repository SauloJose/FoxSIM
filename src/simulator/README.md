# 🧠 Simulator - Módulo de Simulação do FoxSIM

O módulo `simulator` é o núcleo lógico do sistema **FoxSIM**, responsável por coordenar a física, os objetos e as regras da simulação de futebol de robôs (VSSS). Ele encapsula toda a lógica de tempo real que determina o comportamento dos elementos em campo, bem como a lógica de jogo.

## 🧩 Componentes principais

### `Simulator`
A classe `Simulator` (definida em `simulator.py`) é o componente central do módulo. Ela é responsável por:

- Inicializar e gerenciar todos os objetos da simulação (campo, bola, robôs, times).
- Integrar o motor físico, regras do jogo e lógica geral.
- Controlar o ciclo de atualização (update) e renderização (draw).
- Gerenciar o tempo de simulação e o estado da partida (início, pausa, reset).
- Fornecer interface para comandos externos (UI, scripts, etc).

#### Arquitetura e Fluxo de Dados

1. **Inicialização**  
   Ao ser instanciada, a `Simulator` cria os objetos principais do jogo (campo, bola, times, robôs), inicializa o motor de física (`Physics_Engine`), as regras (`Rules`), e conecta-se à interface visual (`GL2DWidget`).

2. **Ciclo de Atualização (`update()`)**  
   O método `update()` é chamado a cada frame (tipicamente por um timer ou loop principal). Ele executa:
   - Cálculo do delta de tempo (`dt`) usando `QElapsedTimer` para garantir precisão temporal.
   - Atualização do motor físico, que move os objetos conforme suas velocidades e aplica colisões.
   - Processamento das regras do jogo (gols, faltas, reinícios, etc).
   - Atualização dos estados internos (placar, tempo, eventos).
   - Comunicação de eventos relevantes para a interface ou outros módulos.

3. **Ciclo de Renderização (`draw(surface)`)**  
   O método `draw(surface)` é chamado pela interface gráfica para desenhar todos os elementos da simulação:
   - Campo, linhas e áreas.
   - Bola e robôs (aliados e adversários).
   - Elementos de depuração (colisores, vetores, grades, etc), se habilitados.
   - Informações de estado (placar, tempo, mensagens).

4. **Controle de Tempo e Estado**  
   - Usa uma instância de `Stopwatch` para controlar o tempo de partida.
   - Utiliza `QElapsedTimer` para precisão no cálculo de `dt`.
   - Flags como `running`, `is_simulation_paused` e `simulation_started` controlam o fluxo da simulação.
   - Métodos como `pause_simulation()`, `resume_simulation()`, `reset_simulation()` permitem manipulação do estado.

5. **Integração com Submódulos**
   - **objects/**: Define e instancia os objetos do campo, bola, robôs e times.
   - **collision/**: Gerencia detecção e resposta de colisões físicas.
   - **rules/**: Implementa as regras do jogo e lógica do árbitro.
   - **game_logic.py**: Orquestra a lógica geral da simulação.
   - **ui/**: Permite comunicação com a interface gráfica.

#### Principais Métodos

- `__init__()`: Inicializa todos os componentes da simulação.
- `update()`: Atualiza o estado da simulação a cada frame.
- `draw(surface)`: Renderiza todos os elementos na tela.
- `pause_simulation()`, `resume_simulation()`, `reset_simulation()`: Controlam o estado da simulação.
- Métodos auxiliares para manipulação de objetos, eventos e integração com a UI.

#### Fluxo Resumido

1. **Inicialização**: `Simulator` instancia todos os objetos e prepara o ambiente.
2. **Loop Principal**:
   - Chama `update()` para evoluir a simulação.
   - Chama `draw(surface)` para desenhar o estado atual.
3. **Controle**: Usuário pode pausar, reiniciar ou manipular a simulação via interface ou comandos.

---

## ⚙️ Funcionamento

### Ciclo de Atualização
O método `update()` da classe `Simulator` é chamado a cada frame. Ele realiza:

1. Cálculo de `dt` (delta time) usando `QElapsedTimer`, para garantir simulação consistente mesmo com variações de FPS.
2. Atualização do motor físico (`Physics_Engine`), movimentando bola e robôs, e resolvendo colisões.
3. Processamento das regras do jogo (gols, faltas, reinícios, etc) via submódulo `rules`.
4. Atualização do placar, tempo e eventos internos.
5. Comunicação de eventos para a interface gráfica, se necessário.

### Ciclo de Renderização
O método `draw(surface)` é chamado pela interface (`GL2DWidget`) para renderizar os objetos da simulação na tela.

- Campo (linhas, áreas, gols)
- Robôs (aliados e inimigos)
- Bola
- Elementos opcionais de debug (colisores, grade, vetores, etc.)
- Informações de estado (placar, tempo, mensagens)

## ⏱️ Controle de Tempo
O simulador usa uma classe `Stopwatch` para cronometrar a partida e o `QElapsedTimer` para garantir precisão no tempo de simulação. Isso permite simulação realista e sincronizada, independente do FPS da interface.

## ✅ Estado e Controle
A classe `Simulator` possui flags como:
- `running`: Define se a simulação está em execução.
- `is_simulation_paused`: Permite pausar e continuar.
- `simulation_started`: Indica se uma partida foi iniciada.

Também inclui métodos de controle como `pause_simulation()`, `resume_simulation()` e `reset_simulation()` para manipular o estado da simulação.

## 📁 Estrutura básica esperada
```
simulator/
├── collision/
│   └── collision.py
├── objects/
│   ├── ball.py
│   ├── robot.py
│   ├── team.py
│   └── field.py
├── rules/
│   └── rules.py
├── game_logic.py
├── simulator.py   ← Aqui está a classe Simulator
```

---

## 🚀 Futuras melhorias
- **Integração com IA e tomada de decisão**
- **Melhoria de performance com multithreading ou GPU**
- **Testes automáticos com diferentes cenários de jogo**

---

> Esse módulo torna o FoxSIM uma ferramenta poderosa para pesquisa, testes e ensino em ambientes simulados de futebol de robôs. Com o `Simulator`, é possível controlar cada aspecto do jogo de forma precisa e modular.

