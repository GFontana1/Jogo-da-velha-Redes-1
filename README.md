# Jogo-da-velha-Redes-1

#### Feito por: Guilherme Fontana, Henrique Fadigas e Douglas Rocha

## 1\. Propósito do Software

O software implementa um Jogo da Velha para dois jogadores através de uma rede. Ele segue um modelo cliente-servidor:

  * **Servidor (`Jogo_TCP.py`):** É a autoridade central do jogo. Ele gerencia o estado do tabuleiro, controla as rodadas dos jogadores, valida as jogadas e determina o vencedor. O servidor não possui interface gráfica e é executado em um terminal.
  * **Cliente (`Jogo_Cliente.py`):** É a interface com a qual os jogadores interagem. Ele fornece uma representação gráfica do tabuleiro, captura as jogadas do usuário através do mouse, as envia para o servidor e atualiza a tela com base nas mensagens recebidas do servidor.

O sistema foi projetado para que os dois primeiros clientes a se conectarem assumam os papéis de jogador 'X' e jogador 'O'. Conexões subsequentes são colocadas como Espectador.

## 2\. Motivação da Escolha do Protocolo de Transporte (TCP)

O protocolo de transporte escolhido para esta aplicação foi o **TCP (Transmission Control Protocol)**. A escolha é justificada pelos seguintes motivos:

  * **Confiabilidade:** Em um jogo de turnos como o Jogo da Velha, é crucial que nenhuma jogada ou mensagem de estado seja perdida. O TCP garante a entrega ordenada e sem erros de todos os pacotes. Perder uma mensagem de `JOGADA` ou `ATUALIZA` corromperia o estado do jogo para um dos clientes, tornando a partida inconsistente.
  * **Orientado à Conexão:** O TCP estabelece uma conexão persistente entre o cliente e o servidor durante toda a partida, o que se encaixa perfeitamente no modelo do jogo, onde os jogadores precisam de um canal de comunicação contínuo desde o início até o fim da partida.
  * **Controle de Fluxo:** O TCP gerencia o fluxo de dados, garantindo que o servidor ou o cliente não seja sobrecarregado com mais informações do que pode processar, embora para esta aplicação de baixa intensidade de dados, seja um benefício secundário.

Em suma, a confiabilidade e a natureza orientada à conexão do TCP eliminam a necessidade de implementar lógicas complexas de retransmissão e ordenação na camada de aplicação, simplificando o desenvolvimento e garantindo a integridade do jogo.

## 3\. Protocolo da Camada de Aplicação

O protocolo de aplicação define o conjunto de regras e mensagens que o cliente e o servidor trocam para garantir o funcionamento do jogo.

### Formato Geral

Todas as mensagens são strings de texto plano e são terminadas com um caractere de nova linha (`\n`). Isso permite que o receptor processe os dados recebidos linha por linha.

### Estados do Cliente

Um cliente pode estar em um dos seguintes estados principais:

1.  **Conectando:** Estado inicial ao tentar estabelecer a comunicação com o servidor.
2.  **Aguardando Oponente:** O cliente está conectado, recebeu seu símbolo ('X' ou 'O'), mas não é sua vez de jogar.
3.  **Sua Vez:** O cliente está conectado e o servidor indicou que ele deve realizar a próxima jogada.
4.  **Fim de Jogo:** A partida terminou por vitória, derrota ou empate. O cliente pode escolher reiniciar a partida ou encerrar o programa.

### Mensagens Trocadas

#### **A. Mensagens do Servidor para o Cliente**

| Mensagem | Formato | Descrição |
| :--- | :--- | :--- |
| **Atribuição de Símbolo**| `SEU_SIMBOLO <SÍMBOLO>\n` | Enviada logo após a conexão. Informa ao cliente se ele será 'X' ou 'O'. Ex: `SEU_SIMBOLO X\n` |
| **Início de Turno** | `SUA_VEZ\n` | Indica que é a vez deste cliente fazer uma jogada. |
| **Aguardar Turno** | `AGUARDE\n` | Indica que o cliente deve esperar pela jogada do oponente. |
| **Atualização do Tabuleiro**| `ATUALIZA <S>,<L>,<C>\n` | Transmitida a todos os clientes após uma jogada válida. Informa qual símbolo (`S`) foi colocado em qual linha (`L`) e coluna (`C`). Ex: `ATUALIZA X,0,1\n` |
| **Fim de Jogo** | `VITORIA <SÍMBOLO>\n` | Anuncia o fim do jogo e quem foi o vencedor (`X` ou `O`). Ex: `VITORIA O\n` |
| **Empate** | `VITORIA EMPATE\n` | Anuncia que o jogo terminou em empate (Velha). |
| **Modo Espectador** | `AGUARDANDO OPONENTE\n` | Enviada a um cliente que tenta se conectar quando o jogo já tem dois jogadores. O servidor mantém a conexão mas o cliente não pode fazer nenhuma jogada, apenas assistir. |

#### **B. Mensagens do Cliente para o Servidor**

| Mensagem | Formato | Descrição |
| :--- | :--- | :--- |
| **Realizar Jogada** | `JOGADA <L>,<C>\n` | Enviada quando o jogador clica em uma célula vazia do tabuleiro. Informa ao servidor a linha (`L`) e a coluna (`C`) da jogada. Ex: `JOGADA 1,2\n` |
| **Reiniciar Jogo** | `REINICIAR\n` | Enviada quando o jogador clica no botão "Reiniciar" após o fim de uma partida. |

### Diagrama de Sequência Simplificado

```
    participant Cliente_A
    participant Servidor
    participant Cliente_B

    Cliente_A->>+Servidor: Tenta Conexão TCP
    Servidor-->>-Cliente_A: SEU_SIMBOLO X
    Servidor-->>Cliente_A: SUA_VEZ

    Cliente_B->>+Servidor: Tenta Conexão TCP
    Servidor-->>-Cliente_B: SEU_SIMBOLO O
    Servidor-->>Cliente_B: AGUARDE

    Cliente_A->>+Servidor: JOGADA 0,0
    Servidor-->>-Cliente_A: ATUALIZA X,0,0
    Servidor-->>Cliente_B: ATUALIZA X,0,0
    Servidor-->>Cliente_A: AGUARDE
    Servidor-->>Cliente_B: SUA_VEZ

    Cliente_B->>+Servidor: JOGADA 1,1
    Servidor-->>-Cliente_A: ATUALIZA O,1,1
    Servidor-->>Cliente_B: ATUALIZA O,1,1
    Servidor-->>Cliente_B: AGUARDE
    Servidor-->>Cliente_A: SUA_VEZ

    loop Jogo continua...

    Cliente_A->>+Servidor: JOGADA 2,0 (Jogada da vitória)
    Servidor-->>-Cliente_A: ATUALIZA X,2,0
    Servidor-->>Cliente_B: ATUALIZA X,2,0
    Servidor-->>Cliente_A: VITORIA X
    Servidor-->>Cliente_B: VITORIA X

    Note over Cliente_A, Cliente_B: Interface mostra "Vitória de X!" e botões de Reiniciar/Sair

    Cliente_B->>+Servidor: REINICIAR
    Servidor-->>-Cliente_A: AGUARDE
    Servidor-->>Cliente_B: AGUARDE
    Note over Servidor: Servidor reinicia o tabuleiro
    Servidor-->>Cliente_A: SUA_VEZ
```

## 4\. Requisitos Mínimos de Funcionamento

  * **Software:**

      * Python 3
      * Biblioteca Pygame (apenas para o cliente). Para instalar, abra o terminal e execute: `pip install pygame`

  * **Rede:**

      * Uma conexão de rede funcional entre a máquina do servidor e as máquinas dos clientes.
      * O servidor deve estar acessível pelos clientes. Se o servidor e os clientes estiverem em redes diferentes, pode ser necessário configurar o encaminhamento de portas (port forwarding) no roteador do servidor para a porta `9999`.

## 5\. Instruções de Uso

1.  **Iniciar o Servidor:**

      * Abra um terminal ou prompt de comando.
      * Navegue até o diretório onde o arquivo `Jogo_TCP.py` está localizado.
      * Execute o seguinte comando: `python Jogo_TCP.py`

      * O servidor exibirá a mensagem `Servidor TCP ouvindo em 0.0.0.0:9999...` e aguardará as conexões dos clientes.

2.  **Iniciar os Clientes:**

      * **Se o cliente estiver na mesma máquina que o servidor:**
          * Abra dois novos terminais.
          * Em cada um, navegue até o diretório do arquivo `Jogo_Cliente.py` e execute: `python Jogo_Cliente.py`
          * As duas janelas do jogo irão aparecer e se conectar ao servidor.

      * **Se o cliente estiver em uma máquina diferente:**
          * Abra o arquivo `Jogo_Cliente.py` em um editor de texto.
          * Localize a linha: `HOST = '127.0.0.1'`
          * Altere o valor de `HOST` do endereço de loopback (`'127.0.0.1'`) para o endereço IP da máquina onde o servidor está sendo executado. Por exemplo: `HOST = '192.168.1.10'`
          * Salve o arquivo e execute-o com `python Jogo_Cliente.py`.

3.  **Jogar:**

      * O jogador 'X' começa. A janela do jogo indicará "Sua vez".
      * Clique em uma célula vazia para fazer sua jogada.
      * O turno passará para o jogador 'O'.
      * O jogo continua até que haja um vencedor ou um empate.
      * Após o fim da partida, os jogadores podem clicar em "Reiniciar" para começar um novo jogo ou "Fechar" para encerrar o programa.
