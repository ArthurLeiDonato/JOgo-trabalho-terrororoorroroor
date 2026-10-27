import pygame
import sys
import os
import random

# ==========================================
# 1. INICIALIZAÇÃO
# ==========================================
pygame.init()
pygame.mixer.init()

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
fonte_enorme = pygame.font.SysFont("arial", 50, bold=True)


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
mensagem_status = "Explore o casarão e decifre os enigmas."

susto_ativo = False
tempo_susto = 0
duracao_susto_ms = 1000  # Fallback padrão

# Variáveis do Puzzle de Zoom do Relógio (Manual)
relogio_hora = 1
relogio_min = 0

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

# --- CARREGA O EFEITO SONORO DO SUSTO E CALCULA SUA DURAÇÃO EXATA ---
som_susto = None
if os.path.exists("susto.mp3"):
    try:
        som_susto = pygame.mixer.Sound("susto.mp3")
        # Descobre exatamente quantos milissegundos o áudio tem!
        duracao_susto_ms = int(som_susto.get_length() * 1000)
    except pygame.error:
        print("Erro ao carregar o arquivo de som.")
else:
    print("AVISO: Arquivo 'susto.mp3' não encontrado. O susto será silencioso.")

# Fundos e Objetos das Salas
bg_sala1 = ObjetoGrafico(0, 0, "sala.png", 800, 600, CINZA_ESCURO, "Fundo Sala 1")
bg_quarto = ObjetoGrafico(0, 0, "quarto.png", 800, 600, CINZA_ESCURO, "Fundo Quarto")

# Botões de Navegação na Sala 1 (Hall)
btn_ir_quarto1 = ObjetoGrafico(50, 220, None, 160, 50, (50, 100, 200), "Quarto do Relógio")
btn_ir_quarto2 = ObjetoGrafico(50, 280, None, 160, 50, (100, 50, 200), "Quarto do Cofre")
btn_ir_quarto3 = ObjetoGrafico(50, 340, None, 160, 50, (150, 100, 50), "Quarto da Vela")
btn_ir_quarto4 = ObjetoGrafico(50, 400, None, 160, 50, (100, 100, 150), "Porão")
btn_porta = ObjetoGrafico(550, 200, None, 160, 250, (139, 69, 19), "Porta Principal")

# Quarto 1 (Relógio e Pista)
btn_voltar_q1 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
img_mesa = ObjetoGrafico(200, 250, "mesa.png", 400, 250, CINZA, "Mesa")
btn_foto = ObjetoGrafico(450, 310, "foto.png", 80, 70, (150, 150, 150), "Foto")
btn_relogio = ObjetoGrafico(230, 280, None, 90, 120, (120, 80, 40), "Relógio de Pêndulo")

# --- BOTÕES DA TELA DE ZOOM DO RELÓGIO ---
btn_voltar_zoom = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_hora_mais = ObjetoGrafico(280, 250, None, 60, 50, (70, 70, 70), "+ H")
btn_hora_menos = ObjetoGrafico(280, 330, None, 60, 50, (70, 70, 70), "- H")
btn_min_mais = ObjetoGrafico(460, 250, None, 60, 50, (70, 70, 70), "+ M")
btn_min_menos = ObjetoGrafico(460, 330, None, 60, 50, (70, 70, 70), "- M")
btn_confirmar_relogio = ObjetoGrafico(330, 430, None, 140, 50, (50, 150, 50), "Abrir Relógio")

# Quarto 2 (Cofre - Arrombado com Pé de Cabra)
btn_voltar_q2 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_cofre = ObjetoGrafico(300, 200, None, 200, 180, (90, 90, 90), "Cofre Aço")

# Quarto 3 (Quarto da Vela)
btn_voltar_q3 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_vela = ObjetoGrafico(380, 320, None, 50, 80, (240, 200, 50), "Vela")

# Quarto 4 (Porão Escuro)
btn_voltar_q4 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_pedecabra = ObjetoGrafico(350, 340, None, 100, 40, (130, 130, 130), "Pé de Cabra")

# Sala Final / Fuga
btn_voltar_s3 = ObjetoGrafico(50, 500, None, 120, 40, VERMELHO, "<- Voltar")
btn_tesouro = ObjetoGrafico(200, 250, None, 100, 80, (50, 200, 100), "Tesouro")
btn_porta_fuga = ObjetoGrafico(500, 200, None, 160, 250, (180, 50, 20), "Fuga!")

relogio = pygame.time.Clock()


# ==========================================
# 4. LOOP PRINCIPAL DO JOGO
# ==========================================
while True:
    tempo_atual = pygame.time.get_ticks()

    # O susto acaba exatamente quando o áudio termina!
    if susto_ativo and (tempo_atual - tempo_susto > duracao_susto_ms):
        susto_ativo = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                pos = evento.pos

                def disparar_susto():
                    global susto_ativo, tempo_susto
                    susto_ativo = True
                    tempo_susto = pygame.time.get_ticks()
                    if som_susto:
                        som_susto.play()

                # --- CLIQUES NA SALA 1 (HALL) ---
                if sala_atual == "sala_1":
                    if btn_ir_quarto1.foi_clicado(pos):
                        sala_atual = "quarto_1"
                        mensagem_status = "Você entrou no Quarto do Relógio."
                        if random.random() < 0.3:
                            disparar_susto()

                    elif btn_ir_quarto2.foi_clicado(pos):
                        # Exige o Pé de Cabra para arrombar o cofre
                        if "Pé de Cabra" in inventario:
                            sala_atual = "quarto_2"
                            mensagem_status = "Você usou o Pé de Cabra para forçar a porta do Cofre."
                        else:
                            mensagem_status = "A porta do cofre está lacrada. Precisa de algo pesado para forçá-la."
                            if random.random() < 0.4:
                                disparar_susto()

                    elif btn_ir_quarto3.foi_clicado(pos):
                        # Exige a Chave obtida no relógio para entrar
                        if "Chave" in inventario:
                            sala_atual = "quarto_3"
                            mensagem_status = "Você destrancou o Quarto da Vela com a Chave."
                        else:
                            mensagem_status = "A porta está trancada! Precisa de uma chave."
                            if random.random() < 0.4:
                                disparar_susto()

                    elif btn_ir_quarto4.foi_clicado(pos):
                        sala_atual = "quarto_4"
                        mensagem_status = "Você entrou no Porão."
                        if random.random() < 0.5:
                            disparar_susto()
                        
                    elif btn_porta.foi_clicado(pos):
                        # Fuga final exige todos os itens da cadeia de puzzles
                        if "Chave" in inventario and "Vela" in inventario and "Pé de Cabra" in inventario and "Código do Cofre" in inventario:
                            sala_atual = "sala_3"
                            mensagem_status = "Porta principal aberta! Fuja!"
                            disparar_susto()
                        else:
                            mensagem_status = "Trancada! Complete todos os enigmas e colete os itens."

                # --- CLIQUES NO QUARTO 1 ---
                elif sala_atual == "quarto_1":
                    if btn_voltar_q1.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_foto.foi_clicado(pos):
                        mensagem_status = "Foto antiga manchada: 'A tragédia ocorreu às 03:45'."
                    elif btn_relogio.foi_clicado(pos):
                        # Abre a tela de zoom manual do relógio
                        sala_atual = "zoom_relogio"
                        mensagem_status = "Ajuste os ponteiros do relógio manualmente."

                # --- CLIQUES NA TELA DE ZOOM DO RELÓGIO ---
                elif sala_atual == "zoom_relogio":
                    if btn_voltar_zoom.foi_clicado(pos):
                        sala_atual = "quarto_1"
                        mensagem_status = "Você se afastou do relógio."
                    elif btn_hora_mais.foi_clicado(pos):
                        relogio_hora = (relogio_hora % 12) + 1
                    elif btn_hora_menos.foi_clicado(pos):
                        relogio_hora = 12 if relogio_hora <= 1 else relogio_hora - 1
                    elif btn_min_mais.foi_clicado(pos):
                        relogio_min = (relogio_min + 15) % 60
                    elif btn_min_menos.foi_clicado(pos):
                        relogio_min = (relogio_min - 15) % 60
                    elif btn_confirmar_relogio.foi_clicado(pos):
                        # Verifica se acertou a hora da pista (03:45)
                        if relogio_hora == 3 and relogio_min == 45:
                            if "Chave" not in inventario:
                                inventario.append("Chave")
                                mensagem_status = "O relógio abriu! Uma Chave caiu de dentro."
                            else:
                                mensagem_status = "O relógio já está vazio."
                        else:
                            mensagem_status = "Nada aconteceu. Horário incorreto."
                            if random.random() < 0.4:
                                disparar_susto()

                # --- CLIQUES NO QUARTO 2 (COFRE) ---
                elif sala_atual == "quarto_2":
                    if btn_voltar_q2.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_cofre.foi_clicado(pos):
                        if "Código do Cofre" not in inventario:
                            inventario.append("Código do Cofre")
                            mensagem_status = "Cofre forçado com sucesso! Documentos obtidos."

                # --- CLIQUES NO QUARTO 3 (VELA) ---
                elif sala_atual == "quarto_3":
                    if btn_voltar_q3.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_vela.foi_clicado(pos):
                        if "Vela" not in inventario:
                            inventario.append("Vela")
                            btn_vela.visivel = False
                            mensagem_status = "Você pegou a Vela acesa!"

                # --- CLIQUES NO QUARTO 4 (PORÃO) ---
                elif sala_atual == "quarto_4":
                    if btn_voltar_q4.foi_clicado(pos):
                        sala_atual = "sala_1"
                        mensagem_status = "Você voltou ao Hall."
                    elif btn_pedecabra.foi_clicado(pos):
                        # Só consegue pegar o pé de cabra se estiver com a vela acesa para iluminar
                        if "Vela" in inventario:
                            if "Pé de Cabra" not in inventario:
                                inventario.append("Pé de Cabra")
                                btn_pedecabra.visivel = False
                                mensagem_status = "A luz da vela revelou e permitiu pegar o Pé de Cabra!"
                        else:
                            mensagem_status = "Está muito escuro para ver qualquer coisa aqui embaixo..."

                # --- CLIQUES NA SALA 3 (FINAL) ---
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
        txt_vitoria = fonte_grande.render("PARABÉNS! VOCÊ ESCAPOU DO CASARÃO!", True, (50, 200, 100))
        tela.blit(txt_vitoria, (LARGURA // 2 - txt_vitoria.get_width() // 2, 250))
        pygame.display.flip()
        relogio.tick(60)
        continue

    if sala_atual == "sala_1":
        bg_sala1.desenhar(tela)
        titulo = fonte.render("--- SALA 1 (Hall Principal) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        if "Chave" in inventario and "Vela" in inventario and "Pé de Cabra" in inventario and "Código do Cofre" in inventario:
            btn_porta.texto_fallback = "Porta (Aberta)"
            btn_porta.cor_fallback = (50, 200, 100)
        else:
            btn_porta.texto_fallback = "Porta (Trancada)"
            btn_porta.cor_fallback = (139, 69, 19)

        btn_ir_quarto1.desenhar(tela)
        btn_ir_quarto2.desenhar(tela)
        btn_ir_quarto3.desenhar(tela)
        btn_ir_quarto4.desenhar(tela)
        btn_porta.desenhar(tela)

    elif sala_atual == "quarto_1":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- QUARTO DO RELÓGIO ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_q1.desenhar(tela)
        img_mesa.desenhar(tela)
        btn_foto.desenhar(tela)
        btn_relogio.desenhar(tela)

    elif sala_atual == "zoom_relogio":
        # Tela de Zoom dedicada para configurar o relógio manualmente
        tela.fill((30, 20, 10))
        titulo_zoom = fonte_grande.render("AJUSTE O RELÓGIO", True, BRANCO)
        tela.blit(titulo_zoom, (LARGURA // 2 - titulo_zoom.get_width() // 2, 80))

        # Mostra o horário atual selecionado
        str_horario = f"{relogio_hora:02d}:{relogio_min:02d}"
        txt_horario = fonte_enorme.render(str_horario, True, (255, 215, 0))
        tela.blit(txt_horario, (LARGURA // 2 - txt_horario.get_width() // 2, 160))

        # Desenha os botões de ajuste manual
        btn_voltar_zoom.desenhar(tela)
        btn_hora_mais.desenhar(tela)
        btn_hora_menos.desenhar(tela)
        btn_min_mais.desenhar(tela)
        btn_min_menos.desenhar(tela)
        btn_confirmar_relogio.desenhar(tela)

        # Rótulos de H e M
        lbl_h = fonte.render("HORAS", True, BRANCO)
        tela.blit(lbl_h, (285, 215))
        lbl_m = fonte.render("MINUTOS", True, BRANCO)
        tela.blit(lbl_m, (455, 215))

    elif sala_atual == "quarto_2":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- QUARTO DO COFRE (Arrombado) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_q2.desenhar(tela)
        btn_cofre.desenhar(tela)

    elif sala_atual == "quarto_3":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- QUARTO DA VELA ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_q3.desenhar(tela)
        btn_vela.desenhar(tela)

    elif sala_atual == "quarto_4":
        # Se não tiver a vela, o porão fica totalmente escuro (preto)
        if "Vela" not in inventario:
            tela.fill((10, 10, 10))
            titulo = fonte.render("--- PORÃO (TOTALMENTE ESCURO) ---", True, VERMELHO)
            tela.blit(titulo, (50, 30))
            txt_escuro = fonte.render("Está muito escuro... Você precisa de uma fonte de luz.", True, BRANCO)
            tela.blit(txt_escuro, (200, 250))
            btn_voltar_q4.desenhar(tela)
        else:
            bg_quarto.desenhar(tela)
            titulo = fonte.render("--- PORÃO (Iluminado pela Vela) ---", True, BRANCO)
            tela.blit(titulo, (50, 30))
            btn_voltar_q4.desenhar(tela)
            btn_pedecabra.desenhar(tela)

    elif sala_atual == "sala_3":
        bg_quarto.desenhar(tela)
        titulo = fonte.render("--- SALA 3 (Final) ---", True, BRANCO)
        tela.blit(titulo, (50, 30))
        
        btn_voltar_s3.desenhar(tela)
        btn_tesouro.desenhar(tela)
        btn_porta_fuga.desenhar(tela)

    # --- EFEITO DE SUSTO (IMAGEM DO FLÁVIO + SOM COM DURAÇÃO SINCRONIZADA) ---
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
        pygame.draw.rect(tela, (30, 30, 30), (50, 450, 700, 50), border_radius=8)
        pygame.draw.rect(tela, BRANCO, (50, 450, 700, 50), 1, border_radius=8)
        txt_msg = fonte.render(mensagem_status, True, BRANCO)
        tela.blit(txt_msg, (70, 465))

        pygame.draw.rect(tela, PRETO, (0, 540, LARGURA, 60))
        txt_inv = fonte.render("Inventário:", True, BRANCO)
        tela.blit(txt_inv, (20, 555))

        for i, item in enumerate(inventario):
            x_slot = 130 + (i * 115)
            pygame.draw.rect(tela, CINZA, (x_slot, 545, 110, 50), border_radius=5)
            txt_item = fonte.render(item, True, PRETO)
            tela.blit(txt_item, (x_slot + 5, 558))

    pygame.display.flip()
    relogio.tick(60)
