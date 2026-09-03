# ⚽ **FoxSIM - Simulador de Futebol de Robôs**

Bem-vindo ao **FoxSIM**, um simulador de futebol de robôs 2D projetado para experimentação com física realista, controle autônomo e algoritmos de inteligência artificial. Este projeto é ideal para fins educacionais, pesquisa e desenvolvimento de estratégias para times de robôs em partidas simuladas.


## 🎯 **Objetivo do Projeto**

O **FoxSIM** foi criado para:
- Simular partidas de futebol de robôs com física realista.
- Permitir o desenvolvimento e teste de estratégias de controle autônomo.
- Servir como uma ferramenta educacional para aprendizado de física, programação e inteligência artificial.

---

## 🚀 **Funcionalidades Principais**

- **Física Realista**: Sistema completo de colisões e torque usando vetores e matrizes com `NumPy`.
- **Robôs Autônomos**: Cada robô pode ser programado com papéis táticos (como atacante, defensor, goleiro).
- **Interface com `Pygame`**: Permite interações via mouse e teclado, exibição do placar e debug visual.
- **Configuração Personalizável**: Parâmetros como velocidade dos robôs, dimensões do campo e tempo podem ser modificados.
- **Debug Visual**: Exibição das direções de velocidade e do target atual de cada robô.
- **Controle de Partida**: Temporizador, pausa, reinício e controle de estados do jogo.
- **Interação via Mouse**: Permite selecionar robôs, mover a bola e rotacionar robôs manualmente.
- **Sistema de Regras**: Um árbitro virtual avalia gols, tempo, faltas e reinícios por meio de decisões extensíveis.
- **Arquitetura Modular**: A classe `Simulation` concentra o ciclo do jogo, enquanto `main.py` apenas inicia a aplicação.

---
## 📸 **Galeria de Imagens**

Aqui você pode adicionar imagens e prints do simulador para torná-lo mais visual e interativo. 

### **Exemplo de Simulação**
![Exemplo de Simulação](src/assets/CampoEInterface.png)



### **Debug de Estratégias**
O debug de estratégia é acionado pressionando **D**. Ele exibe, para os robôs selecionados, a seta vermelha de orientação, o vetor ciano da velocidade real, a reta laranja da velocidade desejada e o target atual.

Os objetos geométricos de colisão são uma opção independente, alternada pela tecla **C**.

Os targets podem ser alternados com **Ctrl+1**, **Ctrl+2** ou **Ctrl+3**. A ordem é `1 = goleiro`, `2 = atacante 1` e `3 = atacante 2`; **Ctrl+4** alterna todos. Cada atalho seleciona o robô correspondente nos dois times. O target e a linha azuis pertencem ao Time A e os vermelhos ao Time B.

![Debug de targets e velocidades do FoxSIM](src/assets/FoxSIM_Debug_Targets.png)

Na captura, o painel confirma quais jogadores estão em debug. A linha azul ou vermelha aponta para o target atual; a reta laranja representa a velocidade desejada do controlador e a seta vermelha representa a orientação do robô.

### **Debug de Colisão**

O atalho **C** exibe os limites geométricos usados pelo Pymunk. Ele pode ser ativado independentemente do debug de estratégias, permitindo analisar colisões sem desenhar os targets dos robôs.

![Debug dos objetos de colisão do FoxSIM](src/assets/FoxSIM_Debug_Collision.png)

### **Selecionando robôs com o mouse**


![Debug Visual](src/assets/robotSelecionado.png)

### 🕹️ **Interações no Modo Pausado**

Quando o jogo está pausado (pressionando a tecla **"P"**), você pode interagir diretamente com os elementos do campo de forma intuitiva e divertida! Confira as funcionalidades disponíveis:

- **Seleção de Robôs**:
  - Clique em um robô para selecioná-lo. O robô selecionado será destacado com um brilho especial, indicando que está pronto para ser manipulado.

- **Mover Robôs**:
  - Segure o botão esquerdo do mouse e arraste o robô para reposicioná-lo no campo. Ideal para ajustar estratégias ou corrigir posições.

- **Rotacionar Robôs**:
  - Clique com o botão direito do mouse em um robô para rotacioná-lo. Isso permite ajustar a direção do robô para jogadas específicas.

- **Reposicionar a Bola**:
  - Clique em qualquer lugar do campo (fora dos robôs) para reposicionar a bola naquele local. Perfeito para simular cobranças de falta, escanteios ou reinícios de jogo.

> **Dica**: Use essas funcionalidades para criar cenários personalizados, testar estratégias ou simplesmente se divertir ajustando os elementos do simulador!

---

Essa descrição pode ser adicionada ao README na seção de funcionalidades ou interações, tornando o projeto mais atrativo e fácil de entender. 🎉
---


## 📁 **Estrutura do Projeto**

```plaintext
FoxSIM/
│
├── src/
│   ├── main.py                         # Entrada principal do simulador
│   ├── test.py                         # Testes gerais
│   ├── testInterface.py                # Testes com a interface PyQt5
│   ├── assets/                         # Imagens e sprites do jogo
│   │   ├── ball.png                    # Imagem da bola
│   │   ├── robot.png                   # Imagem dos robôs
│   │   ├── field.png                   # Imagem do campo
│   │   └── ...                         # Outros ícones e imagens
│   ├── simulator/                      # Núcleo da simulação
│   │   ├── objects/                    # Elementos físicos do jogo
│   │   │   ├── ball.py                 # Classe da bola
│   │   │   ├── robot.py                # Classe dos robôs
│   │   │   ├── team.py                 # Classe das equipes
│   │   │   ├── field.py                # Classe do campo
│   │   │   ├── timer.py                # Temporizador do jogo
│   │   │   └── OBJECTS_README.md       # Documentação dos objetos
│   │   ├── collision/                  # Sistema de colisão
│   │   │   ├── collision.py            # Colisão via SAT, AABB, etc.
│   │   │   └── COLISION_README.md      # Documentação do sistema de colisão
│   │   ├── rules/                      # Regras do jogo
│   │   │   └── rules.py                # Classe de regras e lógica do árbitro
│   │   ├── game_logic.py               # Regras e atualização do jogo
│   │   └── simulator.py                # Classe geral da simulação
│   ├── ui/                             # Interface gráfica
│   │   ├── interface.py                # Classe principal da interface
│   │   ├── interface_config.py         # Configurações da interface
│   │   ├── scoreboard.py               # Placar visual
│   │   └── README.md                   # Documentação da interface
│   ├── utils/                          # Funções auxiliares
│   │   └── helpers.py                  # Funções utilitárias
│   └── data/                           # Dados e testes
│       ├── redes/                      # Dados de redes neurais (em construção)
│       └── testes/                     # Testes de PID e trajetórias
├── README.md                           # Documentação principal
└── requirements.txt                    # Dependências do projeto
```

---

## 🛠️ **Tecnologias Utilizadas**

- **Python 3.8+**
- **Bibliotecas**:
  - `pygame`: Para renderização gráfica e controle de eventos.
  - `pygame_gui`: Para elementos de interface gráfica.
  - `numpy`: Para cálculos matemáticos e vetoriais.
  - `shapely`: Para cálculos geométricos e manipulação de polígonos.
  - `matplotlib`: Para visualização de gráficos (opcional).
  - `PyQt5`: Para interfaces gráficas avançadas.
  - `scipy`: Para cálculos científicos e interpolação.
  - `logging`: Para registro de logs e depuração.
  - `os` e `sys`: Para manipulação de arquivos e caminhos.
  - `time`: Para controle de tempo e medições de desempenho.
  - `random`: Para geração de valores aleatórios.
  - `json`: Para manipulação de configurações e dados.
  - `pickle`: Para serialização de objetos.
- **Arquitetura Modular**:
  - Sistema de colisão baseado no **Separating Axis Theorem (SAT)**.
  - Estrutura de objetos para robôs, bola, campo e equipes.
  - Implementação de códigos para controle PID e inteligência artificial.

## 🧩 Arquitetura da Simulação

`src/main.py` é somente o ponto de entrada:

```python
from simulator.simulation import Simulation

if __name__ == "__main__":
    Simulation().run()
```

A classe `Simulation` oferece os métodos `handle_events()`, `update(dt)`, `render()`, `reset()`, `run()` e `shutdown()`. Para criar uma interface alternativa, herde de `Simulation` e sobrescreva os métodos necessários. Os componentes principais ficam disponíveis como atributos, incluindo `screen`, `space`, `interface`, `ball`, `blue_team`, `red_team`, `arbitrator` e as árvores de comportamento.

As árvores são criadas por `StrategyManager`. O perfil (`aggressive`, `balanced` ou `defensive`) controla a agressividade, e uma `TeamStrategy` pode ser injetada no construtor para configurar os gols e outros parâmetros do time. A árvore do atacante é organizada em recuperação, ataque principal, escape da parede e suporte. A condição de atacante considera somente `ATACKER1` e `ATACKER2`; o goleiro possui uma árvore independente.

Cada robô mantém `target_position`, um único ponto atualizado, além de `target_velocity` e `target_angular_velocity`, que representam o comando desejado. A velocidade real vem de `robot.velocity`. Os nós de estratégia devem usar `robot.go_to_point(...)` para que seu target seja atualizado no debug.

O árbitro está em `src/simulator/rules/rules.py`. `Arbitrator.evaluate()` é chamado a cada atualização e retorna um membro de `Decisions`. A lógica específica de gols, faltas, pênaltis, laterais, escanteios e reinícios deve ser implementada nessa classe. O método `Simulation.handle_arbitrator_decision()` é o ponto de extensão para reagir às decisões sem alterar o loop principal.

---

## 🔧 **Configurações e Parâmetros Editáveis**

Os parâmetros do simulador podem ser ajustados no arquivo `interface_config.py`. Alguns exemplos incluem:

- **Dimensões do campo**: `FIELD_WIDTH`, `FIELD_HEIGHT`
- **Tempo de partida**: `TIMER_PARTY`
- **Cores dos times**: `TEAM_BLUE_COLOR`, `TEAM_RED_COLOR`
- **Massa, inércia e coeficientes físicos dos objetos**
- **Opções de visualização (debug)**

---

## 🌟 **Como Executar**

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/FoxSIM.git
   ```

2. Navegue até o diretório do projeto:
   ```bash
   cd FoxSIM
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o simulador:
   ```bash
   python src/main.py
   ```

---

## 🏗️ **Futuras Implementações**

- **Integração com IA**:
  - Implementar algoritmos de tomada de decisão para os robôs.
- **Renderização com OpenGL**:
  - Migrar o sistema de renderização para `PyQt5` com suporte a OpenGL.
- **Controle PID Realista**:
  - Adicionar controle PID para os robôs simulados.
- **Simulação em Lote**:
  - Permitir testes de estratégias com múltiplas partidas simuladas.
- **Melhoria de Performance**:
  - Otimizar o sistema com multithreading ou GPU.
- **Interface Completa em PyQt5**:
  - Substituir a interface atual por uma interface mais avançada e interativa usando PyQt5.
- **Integração com o Sistema VSSS Vysion**:
  - Conectar o simulador ao sistema [VSSS Vysion](https://github.com/vsss/vsss-vysion) para controle e visão computacional.

---

## 🤝 **Contribuindo com o Projeto**

Contribuições são bem-vindas! Siga os passos abaixo para colaborar:

1. **Faça um Fork** do repositório.
2. Crie uma nova branch para sua funcionalidade ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça suas alterações e commit:
   ```bash
   git commit -m "Adiciona minha nova funcionalidade"
   ```
4. Envie suas alterações:
   ```bash
   git push origin minha-feature
   ```
5. Abra um **Pull Request** no repositório principal.

---

## 📄 **Licença**

Este projeto está licenciado sob a MIT License.

---

## 💬 **Contato**

Se tiver dúvidas ou sugestões, entre em contato:
- **Email**: saulo-jose12@hotmail.com
- **GitHub**: [GN0MI0](https://github.com/SauloJose)
- **Instagram**: [sauloj.almeida](https://www.instagram.com/sauloj.almeida/)
---

**Divirta-se simulando e desenvolvendo estratégias no FoxSIM!** 🎉