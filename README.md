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
│   ├── testInterface.py                # Arquivo com configurações para testar nova interface do sistema
│   ├── assets/                         # Arquivos png para o simulador
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
│   │   ├── mainWindow/                 # Janela principal da aplicação
│   │   ├── pages/                      # Páginas da aplicação
│   │   ├── interface_config.py         # Dados configuráveis do simulador
│   │   ├── interface.py                # Arquivo da organização da interface e desenho
│   │   └──  scoreboard.                 # Lógica do scoreboard do jogo
│   │   
│   │
│   └── utils/
│       └── helpers.py         # Dados configuráveis do simulador
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

### `simulator/objects/robot.py`
- ** Classe `Robot`**:
  - Robô com direção e movimento baseados em forças e torque.
  - Possui `velocity`, `angular_velocity`, `mass`, `inertia`.
  - Sincroniza com `CollisionRectangle` para colisões com quinas e frente do robô.

### `simulator/objects/ball.py`
- **Classe `Ball`**:
  - Movimento com atrito, rotação e colisões.
  - Resposta à colisão controlada por coeficientes de restituição específicos.


### `simulator/objects/team.py`
- **Classe `Team`**:
  - Representa um time de robôs.
  - Métodos:
    - `reset_positions`: Reseta as posições dos robôs.
    - `set_speed`: Define a velocidade dos robôs.

### `simulator/objects/collision.py`
#### `CollisionSystem`
- Sistema completo de detecção e resposta a colisões.
- Classes:
  - `CollisionCircle`, `CollisionRectangle`, `CollisionLine`, `CollisionGroup`.
  - `resolve_collision_with_field`: Aplica MTV, impulso e torque em MOVING vs STRUCTURE.
  - Detecção entre pares otimizada via spatial hashing e bounding box AABB.

#### ⚙️ Física de Colisão e Torque

- **MTV (Minimum Translation Vector)**:
  - Calculado para separar objetos colidindo.
  - Sempre empurra o objeto MOVING para fora de STRUCTURE.

- **Torque**:
  - Calculado a partir do vetor até o ponto de contato.
  - `τ = r × F` aplicado dinamicamente a `angular_velocity`.

- **Resolução com Impulsos**:
  - Normal + fricção.
  - Suporte para restituição elástica e inércia rotacional.

---


### `simulator/game_logic.py`
- **Função `update_game_state`**:
  - Atualiza o estado do jogo, incluindo movimentação dos robôs, atualização da bola e detecção de colisões.

### `ui/interface.py`
- **Classe `Interface`**:
  - Gerencia a interface gráfica do jogo.
  - Métodos:
    - `draw`: Desenha os elementos da interface, incluindo botões e tempo restante.

---
## 🔧 Parâmetros Configuráveis
### Arquivo `ui/interface_config.py`

Editáveis via `interface_config.py` ou constantes de colisão:
- **Parâmetros Configuráveis**:
  - `FIELD_WIDTH`, `FIELD_HEIGHT`: Dimensões do campo.
  - `SCOREBOARD_HEIGHT`: Altura do placar.
  - `SIDEBAR_WIDTH`: Largura da barra lateral.
  - `TIMER_PARTY`: Tempo total da partida.
  - `TEAM_BLUE_COLOR`, `TEAM_RED_COLOR`: Cores dos times.

Demais editáveis
- Tamanho do campo (`REAL_FIELD_INTERNAL_WIDTH_CM`, etc.)
- Massa e inércia de objetos
- Coeficientes de:
  - Atrito
  - Restituição
- Controle de visualização do debug

Numa versão futura as configuraçõe serão via interface.
---


## Objetivos e Implementações Futuras


## Objetivos e Implementações Futuras

Este projeto está em constante desenvolvimento e novas funcionalidades serão integradas em fases futuras. Abaixo, os principais objetivos planejados:

- [ ] Integrar o sistema completo com PyQt5 em uma interface gráfica única
- [ ] Migrar o sistema de renderização para OpenGL via PyQt para melhorar desempenho
- [ ] Realizar a integração entre os sistemas de visão computacional e comunicação com os robôs
- [ ] Implementar uma camada de inteligência artificial para tomada de decisão com bibliotecas como scikit-learn, TensorFlow ou similares
- [ ] Criar ambiente de simulação totalmente acoplado à interface (sem dependência de janelas externas)
- [ ] Adicionar controle PID realista aos robôs simulados
- [ ] Permitir testes de estratégias com múltiplas partidas simuladas em lote

---

## Dependências

- **Python 3.8+**
- **Bibliotecas**:
  - `pygame`: Para renderização gráfica e controle de eventos.
  - `numpy`: Para cálculos matemáticos e vetoriais.
  - `PyQt5`: Para a interface numérica 

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
