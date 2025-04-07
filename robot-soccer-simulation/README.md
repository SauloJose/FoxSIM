# Robot Soccer Simulation (FoxSIM)

## Objetivo do Projeto

O **Robot Soccer Simulation (FoxSIM)** é um simulador de futebol de robôs desenvolvido para explorar conceitos de inteligência artificial, física de colisões, e controle de agentes autônomos. O objetivo principal é criar um ambiente interativo e visualmente atraente para simular partidas de futebol entre robôs, permitindo o desenvolvimento e teste de algoritmos de IA para controle de equipes.

---

## Funcionalidades

- **Simulação Física**: Implementação de colisões entre robôs, bola e campo utilizando a biblioteca `numpy` para cálculos vetoriais.
- **Controle de Robôs**: Robôs controlados por IA com papéis definidos (atacante e defensor).
- **Interface Gráfica**: Interface visual desenvolvida com `pygame`, incluindo botões de controle (iniciar, resetar) e exibição de tempo restante.
- **Configuração Personalizável**: Parâmetros como velocidade dos robôs, dimensões do campo e tempo de partida podem ser ajustados.
- **Exibição de Objetos de Colisão**: Modo de depuração para visualizar os objetos de colisão no campo.

---

## Estrutura do Projeto

Abaixo está a estrutura de arquivos do projeto:

```
robot-soccer-simulation/
│
├── src/
│   ├── main.py                         # Arquivo principal da simulação
│   ├── assets/
│   │   └── field.png                   # Imagem do campo de jogo
│   │
│   ├── simulator/
│   │   ├── game_logic.py               # Lógica principal do jogo
│   │   ├── rules/
│   │   │   └── __init__.py             # Regras da simulação (placeholder)
│   │   ├── collision/
│   │   │   ├── collision.py            # Sistema de colisões (SAT, círculos, etc.)
│   │   │   └── COLLISION_README.md     # Documentação das colisões
│   │   │
│   │   ├── intelligence/
│   │   │   ├── data/                   # Dados para inteligência artificial
│   │   │   └── Intelligence.py         # Lógica da IA
│   │   │
│   │   ├── objects/
│   │   │   ├── ball.py                 # Classe Ball (representa a bola)
│   │   │   ├── team.py                 # Classe Team (representa os times)
│   │   │   ├── robot.py                # Classe Robot (representa os robôs)
│   │   │   ├── field.py                # Classe Field (representa o campo)
│   │   │   ├── timer.py                # Classe HighPrecisionTimer (controle de tempo)
│   │   │   └── OBJECTS_README.md       # Documentação dos objetos do jogo
│   │
│   ├── ui/
│   │   └── (em desenvolvimento)        # Módulos da interface gráfica
│
├── README.md                           # Documentação do projeto
└── requirements.txt                    # Dependências do projeto

```

---

## Principais Classes e Módulos

### `main.py`
- **Descrição**: Arquivo principal que inicializa o jogo, configura os times, bola e campo, e gerencia o loop principal.
- **Funções**:
  - `update_game_state`: Atualiza o estado do jogo (movimento dos robôs, colisões, etc.).
  - Controle de eventos do teclado e mouse.
- **Variáveis**:
  - `game_started`: Indica se o jogo está em andamento.
  - `draw_collision_objects`: Alterna a exibição dos objetos de colisão.

### `simulator/objects/ball.py`
- **Classe `Ball`**:
  - Representa a bola no jogo.
  - Métodos:
    - `update_position`: Atualiza a posição da bola com base na velocidade.
    - `set_velocity`: Define a velocidade da bola.
    - `reset_position`: Reseta a posição da bola para o centro do campo.

### `simulator/objects/team.py`
- **Classe `Team`**:
  - Representa um time de robôs.
  - Métodos:
    - `reset_positions`: Reseta as posições dos robôs.
    - `set_speed`: Define a velocidade dos robôs.

### `simulator/objects/collision.py`
- **Sistema de Colisões**:
  - Classes:
    - `CollisionObject`: Classe base para objetos de colisão.
    - `CollisionCircle`, `CollisionRectangle`, `CollisionLine`: Representam diferentes formas geométricas para detecção de colisão.
    - `Collision`: Gerencia as colisões entre objetos móveis (bola, robôs) e estruturas (campo, paredes).
  - Métodos:
    - `handle_collisions`: Gerencia todas as colisões no jogo.
    - `resolve_ball_robot_collision`: Resolve colisões entre a bola e os robôs.
    - `resolve_robot_robot_collision`: Resolve colisões entre robôs.

### `simulator/game_logic.py`
- **Função `update_game_state`**:
  - Atualiza o estado do jogo, incluindo movimentação dos robôs, atualização da bola e detecção de colisões.

### `ui/interface.py`
- **Classe `Interface`**:
  - Gerencia a interface gráfica do jogo.
  - Métodos:
    - `draw`: Desenha os elementos da interface, incluindo botões e tempo restante.

---

## Configurações Importantes

### Arquivo `ui/interface_config.py`
- **Parâmetros Configuráveis**:
  - `FIELD_WIDTH`, `FIELD_HEIGHT`: Dimensões do campo.
  - `SCOREBOARD_HEIGHT`: Altura do placar.
  - `SIDEBAR_WIDTH`: Largura da barra lateral.
  - `TIMER_PARTY`: Tempo total da partida.
  - `TEAM_BLUE_COLOR`, `TEAM_RED_COLOR`: Cores dos times.

---

## Objetivos e Implementações Futuras

1. **Inteligência Artificial Avançada**:
   - Implementar algoritmos de IA para controle dos robôs, como:
     - Estratégias de ataque e defesa.
     - Planejamento de trajetória.
     - Coordenação em equipe.

2. **Detecção de Gols**:
   - Adicionar lógica para verificar se a bola entrou na área do gol e identificar qual time marcou.

3. **Áreas de Goleiros**:
   - Implementar áreas de colisão específicas para os goleiros, restringindo seus movimentos.

4. **Simulação Física Melhorada**:
   - Adicionar efeitos como atrito e rotação da bola.

5. **Modo Multijogador**:
   - Permitir que jogadores humanos controlem os robôs.

6. **Gráficos Melhorados**:
   - Substituir os elementos gráficos básicos por sprites mais detalhados.

7. **Sistema de Replays**:
   - Implementar um sistema para salvar e reproduzir partidas.

---

## Dependências

- **Python 3.8+**
- **Bibliotecas**:
  - `pygame`: Para renderização gráfica e controle de eventos.
  - `numpy`: Para cálculos matemáticos e vetoriais.

### Instalação das Dependências
Execute o seguinte comando para instalar as dependências:
```bash
pip install -r requirements.txt
```

---

## Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/robot-soccer-simulation.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd robot-soccer-simulation
   ```
3. Execute o simulador:
   ```bash
   python src/main.py
   ```

---

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests para melhorias no projeto.

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
