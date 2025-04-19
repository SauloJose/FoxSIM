# ⚽ Robot Soccer Simulation (FoxSIM)

## 🎯 Objetivo do Projeto

O **FoxSIM** é um simulador de futebol de robôs voltado para experimentação com física realista, controle autônomo e algoritmos de inteligência artificial. Criado com foco educacional e de pesquisa, o projeto permite desenvolver, testar e visualizar estratégias de times de robôs em partidas simuladas.

---

## 🚀 Funcionalidades Principais

- **Física Realista**: Sistema completo de colisões e torque usando vetores e matrizes com `NumPy`.
- **Robôs Autônomos**: Cada robô pode ser programado com papéis táticos (como atacante, defensor, goleiro).
- **Interface com `Pygame`**: Permite interações via mouse e teclado, exibição do placar e debug visual.
- **Nova Interface `PyQt5 + OpenGL` (em desenvolvimento)**: Substitui o Pygame por renderização acelerada por GPU.
- **Configuração Personalizável**: Parâmetros como velocidade dos robôs, dimensões do campo e tempo podem ser modificados.
- **Debug Visual**: Possibilidade de exibir objetos de colisão para fins de depuração.

---

## 📁 Estrutura do Projeto

```
FoxSIM/
|
├── src/
│   ├── main.py                         # Entrada principal
│   ├── testInterface.py                # Testes com a nova interface PyQt5
│   ├── assets/                         # Imagens e sprites do jogo
│   ├── simulator/
│   │   ├── game_logic.py               # Regras e atualização do jogo
│   │   ├── simulator.py                # Classe geral da simulação
│   │   ├── collision/                  # Sistema de colisão
│   │   │   ├── collision.py            # Colisão via SAT, AABB, etc.
│   │   │   └── COLLISION_README.md     # Documentação do sistema
│   │   ├── intelligence/               # Lógica e dados da IA
│   │   │   ├── data/
│   │   │   └── Intelligence.py
│   │   ├── objects/                    # Elementos físicos do jogo
│   │   │   ├── ball.py, robot.py, team.py, field.py, timer.py
│   │   │   └── OBJECTS_README.md
│   ├── ui/                             # Interface gráfica
│   │   ├── mainWindow/, pages/         # Componentes da janela
│   │   ├── interface.py, interface_config.py
│   │   └── scoreboard.py
│   └── utils/
│       └── helpers.py
├── README.md
└── requirements.txt
```

---

## 🔧 Componentes e Classes Importantes

### `simulator/objects/robot.py`
- **Classe `Robot`**: Robô com movimento físico e rotação, interage com colisão via `CollisionRectangle`.

### `simulator/objects/ball.py`
- **Classe `Ball`**: Simula atrito, impulso e colisões com resposta física realista.

### `simulator/objects/team.py`
- **Classe `Team`**: Gerencia grupo de robôs, velocidades e posições.

### `simulator/collision/collision.py`
- **Sistema de Colisão**: Detecção baseada em bounding boxes, SAT, e resolução com impulso e torque.

### `simulator/game_logic.py`
- **Função `update_game_state`**: Atualiza todo o estado do jogo, detectando colisões e movimentações.

### `ui/interface.py`
- **Classe `Interface`**: Responsável por desenhar e gerenciar a interface com botões, tempo e interação visual.

---

## 🔧 Configurações e Parâmetros Editáveis

Local: `ui/interface_config.py`

- Dimensões do campo: `FIELD_WIDTH`, `FIELD_HEIGHT`
- Tempo de partida: `TIMER_PARTY`
- Cores dos times: `TEAM_BLUE_COLOR`, `TEAM_RED_COLOR`
- Massa, inércia e coeficientes físicos dos objetos
- Opções de visualização (debug)

---

## 🌐 OpenGL Rendering Interface com PyQt5

Este projeto possui uma renderização 2D com `QOpenGLWidget`, inspirada no estilo `pygame`, mas acelerada por GPU.

### Componentes:

- **Image**: Classe que carrega imagens via `PIL` e cria texturas OpenGL.
- **GLWidget**: Superfície de renderização com métodos para:
  - Imagens com rotação e escala;
  - Retângulos, linhas, círculos, setas;
  - Polígonos personalizados e textos.

### Como funciona:
- `GLWidget` atua como a "tela" (semelhante ao `pygame.display.set_mode`)
- Um `QTimer` atualiza a tela a ~60 FPS.
- A lógica do jogo pode usar `GLWidget` para desenhar cada frame diretamente com OpenGL.

```python
widget = GLWidget(parent=self, width=1024, height=768)
widget.image = Image(image_path="field.png")

# Integração com o simulador:
simulator = Simulator(widget)
widget.simulator = simulator
```

---


## Objetivos e Implementações Futuras

Este projeto está em constante desenvolvimento e novas funcionalidades serão integradas em fases futuras. Abaixo, os principais objetivos planejados:

- [ ] Integrar o sistema completo com PyQt5 em uma interface gráfica única
- [ ] Migrar o sistema de renderização para OpenGL via PyQt para melhorar desempenho
- [ ] Realizar a integração entre os sistemas de visão computacional e comunicação com os robôs
- [ ] Implementar uma camada de inteligência artificial para tomada de decisão com bibliotecas como scikit-learn, TensorFlow ou similares
- [ ] Criar ambiente de simulação totalmente acoplado à interface (sem dependência de janelas externas)
- [ ] Adicionar controle PID realista aos robôs simulados
- [ ] Permitir testes de estratégias com múltiplas partidas simuladas em lote
- [ ] Performance otimizada com renderizações offscreen

---

## Dependências

- **Python 3.8+**
- **Bibliotecas**:
  - `pygame`: Para renderização gráfica e controle de eventos.
  - `numpy`: Para cálculos matemáticos e vetoriais.
  - `PyQt5`: Para a interface numérica 
  - `OpenGL`: Para renderizações 

### Instalação das Dependências
Execute o seguinte comando para instalar as dependências:
```bash
pip install -r requirements.txt
```

---

## Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/FoxSIM.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd FoxSIM
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
