# Contribuindo com o FoxSIM

Obrigado por contribuir com o FoxSIM. O simulador é organizado para que a interface e as regras possam evoluir sem concentrar lógica no ponto de entrada.

## Estrutura para desenvolvimento

- `src/main.py` inicia `Simulation` e não deve conter o loop do jogo.
- `src/simulator/simulation.py` controla ciclo de vida, eventos, atualização, renderização e encerramento.
- `src/ui/interface.py` desenha a interface. Novas telas, painéis e controles devem ficar na camada de UI.
- `src/simulator/intelligence/BT/` contém as estratégias. Use `robot.go_to_point(...)` quando um nó definir um alvo para que ele apareça em `target_position`.
- `src/simulator/rules/rules.py` contém `Arbitrator` e `Decisions`. Regras novas devem retornar uma decisão e não ser colocadas em `Simulation.update()`.

## Debug de estratégias

Pressione `D` para mostrar a orientação, a velocidade real, a velocidade desejada e o target dos robôs selecionados. A seta vermelha representa a orientação, o vetor ciano a velocidade real e a reta laranja a velocidade desejada. Pressione `C` para mostrar os objetos geométricos de colisão. Os modos são independentes. Pressione `Ctrl+0`, `Ctrl+1` ou `Ctrl+2` para alternar o target do goleiro, atacante 1 ou atacante 2 em cada equipe. O target é azul para o Time A e vermelho para o Time B.

O robô armazena somente o ponto atual. O valor é substituído quando a estratégia calcula um novo alvo, sem criar histórico ou custo crescente durante a partida.

## Como estender o árbitro

`Arbitrator.evaluate()` é chamado a cada frame em que a partida está ativa. O método retorna um valor de `Decisions` ou `None`. Para adicionar uma regra:

1. Adicione a decisão correspondente ao enum `Decisions`.
2. Crie um método privado de avaliação ou atendimento em `Arbitrator`.
3. Faça `analyzer()`/`evaluate()` retornar a decisão quando a condição ocorrer.
4. Adicione a reação da simulação em `Simulation.handle_arbitrator_decision()` somente quando houver uma mudança de estado necessária.

A classe já possui pontos para gols e fim de partida. Faltas, pênaltis, laterais, escanteios e reinícios podem ser implementados gradualmente sem alterar o launcher.

## Executando

Na raiz do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
python src/main.py
```

Antes de abrir um pull request, valide a sintaxe:

```powershell
python -m compileall -q src
```

Descreva no pull request a regra, estratégia ou componente de interface alterado e informe como o comportamento foi validado.
