import pygame
import sys
import socket
import threading

# Configuração TCP
HOST = '127.0.0.1'
PORTA = 9999

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORTA))
cliente.setblocking(False)

# Variáveis de jogo
pygame.init()
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
AZUL = (0, 120, 215)

LARGURA, ALTURA = 400, 600
ALTURA_TABULEIRO = 400
TAMANHO_CELULA = ALTURA_TABULEIRO // 3
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Velha TCP")

fonte_jogo = pygame.font.SysFont(None, 130)
fonte_msg = pygame.font.SysFont(None, 50)
fonte_botao = pygame.font.SysFont(None, 35)

tabuleiro = [[None] * 3 for _ in range(3)]
meu_simbolo = None
vez_do_jogador = False
game_over = False
vencedor = None
mensagem_status = "Conectando..."
modo_menu = False

def desenhar_linhas():
    for i in range(1, 3):
        pygame.draw.line(tela, PRETO, (i * TAMANHO_CELULA, 0), (i * TAMANHO_CELULA, ALTURA_TABULEIRO), 15)
        pygame.draw.line(tela, PRETO, (0, i * TAMANHO_CELULA), (LARGURA, i * TAMANHO_CELULA), 15)

def desenhar_simbolos():
    for linha in range(3):
        for coluna in range(3):
            simbolo = tabuleiro[linha][coluna]
            if simbolo:
                texto = fonte_jogo.render(simbolo, True, PRETO)
                rect = texto.get_rect(center=(coluna * TAMANHO_CELULA + TAMANHO_CELULA // 2,
                                              linha * TAMANHO_CELULA + TAMANHO_CELULA // 2))
                tela.blit(texto, rect)

def desenhar_mensagem(texto):
    msg = fonte_msg.render(texto, True, AZUL)
    y = ALTURA_TABULEIRO + 20
    tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, y))


def desenhar_botao(texto, y):
    largura_botao = 140
    altura_botao = 45
    botao = pygame.Rect((LARGURA - largura_botao) // 2, y, largura_botao, altura_botao)
    pygame.draw.rect(tela, CINZA, botao)
    pygame.draw.rect(tela, PRETO, botao, 2)
    txt = fonte_botao.render(texto, True, PRETO)
    tela.blit(txt, (botao.x + (largura_botao - txt.get_width()) // 2, y + 8))
    return botao

def escutar_servidor():
    global meu_simbolo, vez_do_jogador, game_over, vencedor, mensagem_status
    buffer = ""
    while True:
        try:
            dados = cliente.recv(1024).decode()
            if not dados:
                continue
            buffer += dados
            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)
                if linha.startswith("SEU_SIMBOLO"):
                    meu_simbolo = linha.split()[1]
                    mensagem_status = f"Você é {meu_simbolo}"
                elif linha == "SUA_VEZ":
                    vez_do_jogador = True
                    mensagem_status = "Sua vez"
                elif linha == "AGUARDE":
                    vez_do_jogador = False
                    mensagem_status = "Aguardando oponente"
                elif linha.startswith("ATUALIZA"):
                    info = linha.split()[1]
                    simbolo, linha, coluna = info.split(",")
                    tabuleiro[int(linha)][int(coluna)] = simbolo
                elif linha.startswith("VITORIA"):
                    vencedor = linha.split()[1]
                    game_over = True
                    if vencedor == "EMPATE":
                        mensagem_status = "Velha!"
                    else:
                        mensagem_status = f"Vitória de {vencedor}!"
        except BlockingIOError:
            continue
        except Exception:
            break

threading.Thread(target=escutar_servidor, daemon=True).start()

# Loop principal
clock = pygame.time.Clock()
botao_reiniciar = None
botao_sair = None

while True:
    tela.fill(BRANCO)
    desenhar_linhas()
    desenhar_simbolos()

    if mensagem_status:
        desenhar_mensagem(mensagem_status)

    if game_over:
        botao_reiniciar = desenhar_botao("Reiniciar", 460)
        botao_sair = desenhar_botao("Fechar", 520)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            if not game_over and vez_do_jogador and y < ALTURA_TABULEIRO:
                linha = y // TAMANHO_CELULA
                coluna = x // TAMANHO_CELULA
                if tabuleiro[linha][coluna] is None:
                    cliente.sendall(f"JOGADA {linha},{coluna}\n".encode())
                    vez_do_jogador = False

            elif game_over:
                if botao_sair and botao_sair.collidepoint((x, y)):
                    pygame.quit()
                    sys.exit()
                elif botao_reiniciar and botao_reiniciar.collidepoint((x, y)):
                    cliente.sendall(b"REINICIAR\n")
                    tabuleiro = [[None]*3 for _ in range(3)]
                    vencedor = None
                    game_over = False
                    mensagem_status = "Aguardando oponente"

    pygame.display.update()
    clock.tick(30)
