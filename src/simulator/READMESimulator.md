# 🧠 Simulator - Módulo de Simulação do FoxSIM

O módulo `simulator` é o núcleo lógico do sistema **FoxSIM**, responsável por coordenar a física, os objetos e as regras da simulação de futebol de robôs (VSSS). Ele encapsula toda a lógica de tempo real que determina o comportamento dos elementos em campo, bem como a lógica de jogo.

## 🧩 Componentes principais

### `Simulator`
Classe central que integra e orquestra a simulação. Ela conecta os objetos gráficos com a lógica física e as regras do jogo.

### Submódulos utilizados
- `objects/`: Define os elementos do campo (bola, robôs, times, etc).
- `rules/`: Lida com regras do jogo e a lógica do árbitro.
- `collision/`: Responsável pelas colisões e resposta física.
- `game_logic/`: Lógica geral da simulação.
- `ui/`: Integração com a interface visual (`GL2DWidget`).

## ⚙️ Funcionamento

### Ciclo de Atualização
O método `update()` da classe `Simulator` é chamado a cada frame. Ele realiza:

1. Cálculo de `dt` (delta time) usando `QElapsedTimer`, para garantir simulação consistente mesmo com variações de FPS.
2. Atualização do motor físico (`Physics_Engine`).
3. Decisões do árbitro são analisadas.

### Ciclo de Renderização
O método `draw(surface)` é chamado pela interface (`GL2DWidget`) para renderizar os objetos da simulação na tela.

- Campo
- Robôs (aliados e inimigos)
- Bola
- Elementos opcionais de debug (colisores, grade, etc.)

## ⏱️ Controle de Tempo
O simulador usa uma classe `Stopwatch` para cronometrar a partida e o `QElapsedTimer` para garantir precisão no tempo de simulação.

## ✅ Estado e Controle
A classe `Simulator` possui flags como:
- `running`: Define se a simulação está em execução.
- `is_simulation_paused`: Permite pausar e continuar.
- `simulation_started`: Indica se uma partida foi iniciada.

Também inclui métodos de controle como `pause_simulation()` e `reset_simulation()`.

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

