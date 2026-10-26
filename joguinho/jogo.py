import pygame
import sys
import os
import random

# ==========================================
# 1. INICIALIZAÇÃO
# ==========================================
pygame.init()
pygame.mixer.init() # Inicializa o sistema de som do Pygame!

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Escape Room - O Susto de Flávio com Som")

# Cores e Fontes
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
CINZA_ESCURO = (50, 50, 50)
VERMELHO = (200, 50, 50)

fonte = pygame.font.SysFont("arial", 20)
fonte_grande = pygame.font.SysFont("arial", 35, bold=True)


# ==========================================
# 2. CLASSE PARA OBJETOS E SPRITES GRÁFICOS
# ==========================================
class ObjetoGrafico:
    def __init__(self, x, y, caminho_imagem=None, largura=None, altura=None, cor_fallback=VERMELHO, texto_fallback=""):
        self.visivel = True
        self.imagem = None
        self.texto_fallback = texto_fallback
        self.cor_fallback = cor_fallback

        if caminho_imagem:
            if os.path.exists(caminho_imagem):
                try:
                    img_original = pygame.image.load(caminho_imagem).convert_alpha()
                    if largura and altura:
                        self.imagem = pygame.transform.scale(img_original, (largura, altura))
                    else:
                        self.imagem = img_original
                except pygame.error:
                    self.imagem = None
            else:
                self.imagem = None

        if self.imagem:
            self.rect = self.imagem.get_rect()
            self.rect.x = x
            self.rect.y = y
        else:
            self.rect = pygame.Rect(x, y, largura or 100, altura or 50)

    def desenhar(self, surface):
        if not self.visivel:
            return
        
        if self.imagem:
            surface.blit(self.imagem, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, self.cor_fallback, self.rect, border_radius=8)
            pygame.draw.rect(surface, PRETO, self.rect, 2, border_radius=8)
            if self.texto_fallback:
                txt_surf = fonte.render(self.texto_fallback, True, BRANCO)
                txt_rect = txt_surf.get_rect(center=self.rect.center)
                surface.blit(txt_surf, txt_rect)

    def foi_clicado(self, pos_mouse):
        return self.visivel and self.rect.collidepoint(pos_mouse)


# ==========================================
# 3. ESTADOS, IMAGENS E SONS
# ==========================================
sala_atual = "sala_1"
inventario = []
mensagem_status = "Explore o casarão e decifre os enigmas para escapar."

susto_ativo = False
tempo_susto = 0

# --- CARREGA A IMAGEM DO FLÁVIO ---
img_flavio = None
if os.path.exists("flavio.png"):
    try:
        img_flavio = pygame.image.load("flavio.png").convert_alpha()
        img_flavio = pygame.transform.scale(img_flavio, (450, 450))
    except pygame.error:
        img_flavio = None
else:
    print("AVISO: Arquivo 'flavio.png' não encontrado.")

# --- CARREGA O EFEITO SONORO DO SUSTO ---
som_susto = None
if os.path.exists("susto.mp3"):
    try:
        som_susto = pygame.mixer.music.load("susto.mp3")
    except pygame.error:
        print("Erro ao carregar o arquivo de som.")
else:
    print("AVISO: Arquivo 'susto.wav' não encontrado. O susto será silencioso.")

# Fundos e Objetos das Salas
bg_sala1 = ObjetoGrafico(0, 0, "sala.png", 800, 600, CINZA_ESCURO, "Fundo Sala 1")
bg_quarto = ObjetoGrafico(0, 0, "quarto.png", 800, 600, CINZA_ESCURO, "Fundo Quarto")

btn_ir_quarto1 = ObjetoGrafico(50, 250, None, 160, 60, (50, 100, 200), "Quarto da Chave")
btn_ir_quarto2 = ObjetoGrafico(50, 340, None, 160, 60, (100, 50, 200), "Quarto do Cofre")
btn_porta = ObjetoGrafico(550, 200, None, 160, 250, (139, 69, 19), "Porta Principal")

btn_voltar_q1 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
img_mesa = ObjetoGrafico(200, 250, "mesa.png", 400, 250, CINZA, "Mesa")
btn_chave = ObjetoGrafico(350, 320, "chave.png", 60, 60, (220, 200, 50), "Chave")
btn_foto = ObjetoGrafico(450, 310, "foto.png", 80, 70, (150, 150, 150), "Foto")

btn_voltar_q2 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_quadro_mat = ObjetoGrafico(300, 150, None, 200, 100, (80, 80, 80), "Pista: 5 + 3 * 2 = ?")
btn_resposta_errada1 = ObjetoGrafico(250, 320, None, 80, 50, (150, 50, 50), "16")
btn_resposta_certa = ObjetoGrafico(360, 320, None, 80, 50, (50, 150, 50), "11")
btn_resposta_errada2 = ObjetoGrafico(470, 320, None, 80, 50, (150, 50, 50), "10")

btn_voltar_s3 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_tesouro = ObjetoGrafico(200, 250, None, 100, 80, (50, 200, 100), "Tesouro")
btn_porta_fuga = ObjetoGrafico(500, 200, None, 160, 250, (180, 50, 20), "Fuga!")

relogio = pygame.time.Clock()


# ==========================================
# 4. LOOP PRINCIPAL DO JOGO
# ==========================================
while True:
    tempo_atual = pygame.time.get_ticks()

    if susto_ativo and (tempo_atual - tempo_susto > 900):
        susto_ativo = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                pos = evento.pos

                # --- FUNÇÃO AUXILIAR PARA DISPARAR O SUSTO E O SOM ---
                def disparar_susto():
                    global susto_ativo, tempo_susto
                    susto_ativo = True
                    tempo_susto = pygame.time.get_ticks()
                    if som_susto:
                        som_susto.play() # Toca o som imediatamente!

                # --- CLIQUES NA SALA 1 ---
                if sala_atual == "sala_1":
                    if btn_ir_quarto1.foi_clicado(pos):
                        sala_atual = "quarto_1"
                        mensagem_status = "Você entrou no Quarto da Chave."
                        if random.random() < 0.3:
                            disparar_susto()

                    elif btn_ir_quarto2.foi_clicado(pos):
                        sala_atual = "quarto_2"
                        mensagem_status = "Você entrou no Quarto do Cofre."
                        if random.random() < 0.4:
                            disparar_susto()
                        
                    elif btn_porta.foi_clicado(pos):
                        if "Chave" in inventario and "Código do Cofre" in inventario:
                            sala_atual = "sala_3"
                            mensagem_status = "Porta aberta! Cuidado..."
                            disparar_susto()
                        else:
                            mensagem_status = "Trancada! Você precisa da Chave e do Cofre."

                # --- CLIQUES NO QUARTO 1 ---
                elif sala_atual == "quarto_1":
                    if btn_voltar_q1.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_chave.foi_clicado(pos):
                        if "Chave" not in inventario:
                            inventario.append("Chave")
                            btn_chave.visivel = False
                            mensagem_status = "Você pegou a Chave!"
                    elif btn_foto.foi_clicado(pos):
                        mensagem_status = "Foto antiga: 'Cuidado com as sombras'."

                # --- CLIQUES NO QUARTO 2 ---
                elif sala_atual == "quarto_2":
                    if btn_voltar_q2.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_quadro_mat.foi_clicado(pos):
                        mensagem_status = "Enigma: Quanto é 5 + 3 * 2?"
                    elif btn_resposta_certa.foi_clicado(pos):
                        if "Código do Cofre" not in inventario:
                            inventario.append("Código do Cofre")
                            mensagem_status = "Cofre aberto! Código obtido."
                    elif btn_resposta_errada1.foi_clicado(pos) or btn_resposta_errada2.foi_clicado(pos):
                        mensagem_status = "Senha incorreta!"
                        if random.random() < 0.5:
                            disparar_susto()

                # --- CLIQUES NA SALA 3 ---
                elif sala_atual == "sala_3":
                    if btn_voltar_s3.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao hall."
                    elif btn_tesouro.foi_clicado(pos):
                        if "Tesouro" not in inventario:
                            inventario.append("Tesouro")
                            btn_tesouro.visivel = False
                            mensagem_status = "Você pegou o Tesouro!"
                    elif btn_porta_fuga.foi_clicado(pos):
                        sala_atual = "vitoria"


    # ==========================================
    # 5. RENDERIZAÇÃO
    # ==========================================
    if sala_atual == "vitoria":
        tela.fill(PRETO)
        txt_vitoria = fonte_grande.render("PARABÉNS! VOCÊ ESCAPOU!", True, (50, 200, 100))
        tela.blit(txt_vitoria, (LARGURA // 2 - txt_vitoria.get_width() // 2, 250))
        pygame.display.flip()
        relogio.tick(60)
        continue

    if sala_atual == "sala_1":
        bg_sala1.desenhar(tela)
        titulo = fonte.render("--- SALA 1 (Hall Principal) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        if "Chave" in inventario and "Código do Cofre" in inventario:
            btn_porta.texto_fallback = "Porta (Aberta)"
            btn_porta.cor_fallback = (50, 200, 100)
        else:
            btn_porta.texto_fallback = "Porta (Trancada)"
            btn_porta.cor_fallback = (139, 69, 19)

        btn_ir_quarto1.desenhar(tela)
        btn_ir_quarto2.desenhar(tela)
        btn_porta.desenhar(tela)

    elif sala_atual == "quarto_1":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- QUARTO 1 ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_q1.desenhar(tela)
        img_mesa.desenhar(tela)
        btn_foto.desenhar(tela)
        btn_chave.desenhar(tela)

    elif sala_atual == "quarto_2":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- QUARTO 2 (Cofre) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_q2.desenhar(tela)
        btn_quadro_mat.desenhar(tela)
        btn_resposta_errada1.desenhar(tela)
        btn_resposta_certa.desenhar(tela)
        btn_resposta_errada2.desenhar(tela)

    elif sala_atual == "sala_3":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- SALA 3 (Final) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_s3.desenhar(tela)
        btn_tesouro.desenhar(tela)
        btn_porta_fuga.desenhar(tela)

    # --- EFEITO DE SUSTO (IMAGEM DO FLÁVIO + SOM) ---
    if susto_ativo:
        tela.fill((20, 0, 0))
        
        if img_flavio:
            pos_x = (LARGURA - img_flavio.get_width()) // 2
            pos_y = (ALTURA - img_flavio.get_height()) // 2
            tela.blit(img_flavio, (pos_x, pos_y))
        else:
            txt_susto = fonte_grande.render("BOO! FLÁVIO APARECEU!", True, BRANCO)
            tela.blit(txt_susto, (LARGURA // 2 - txt_susto.get_width() // 2, ALTURA // 2 - 20))

    # --- CAIXA DE MENSAGENS E INVENTÁRIO ---
    if not susto_ativo:
        pygame.draw.rect(tela, (30, 30, 30), (50, 420, 700, 50), border_radius=8)
        pygame.draw.rect(tela, BRANCO, (50, 420, 700, 50), 1, border_radius=8)
        txt_msg = fonte.render(mensagem_status, True, BRANCO)
        tela.blit(txt_msg, (70, 435))

        pygame.draw.rect(tela, PRETO, (0, 540, LARGURA, 60))
        txt_inv = fonte.render("Inventário:", True, BRANCO)
        tela.blit(txt_inv, (20, 555))

        for i, item in enumerate(inventario):
            x_slot = 130 + (i * 150)
            pygame.draw.rect(tela, CINZA, (x_slot, 545, 140, 50), border_radius=5)
            txt_item = fonte.render(item, True, PRETO)
            tela.blit(txt_item, (x_slot + 10, 558))

    pygame.display.flip()
    relogio.tick(60)      
    