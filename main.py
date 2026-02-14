import pygame
import sys
import os
import random
import math
import json
import asyncio

pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 1920, 900
TELA = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
pygame.display.set_caption("Aventura Matemática Medieval - Estrada dos Reis")

MARROM = (139, 69, 19)
BEGE = (245, 222, 179)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
OURO = (218, 165, 32)
BEGE_ESCURO = (210, 180, 140)
MARROM_CLARO = (139, 90, 43)
VERDE = (34, 139, 34)
VERDE_ESCURO = (0, 100, 0)
VERDE_FLORESTA = (46, 125, 50)
VERMELHO = (178, 34, 34)
VERMELHO_ESCURO = (139, 0, 0)
AMARELO = (255, 215, 0)
AZUL = (65, 105, 225)
AZUL_ESCURO = (25, 25, 112)
AZUL_CEU = (135, 206, 235)
DOURADO = (218, 165, 32)
ROXO = (138, 43, 226)
LARANJA = (255, 140, 0)
CINZA_PEDRA = (105, 105, 105)
CINZA_CLARO = (169, 169, 169)
CINZA_ESCURO = (60, 60, 60)
TERRA = (139, 69, 19)
GRAMA = (85, 107, 47)

fonte_titulo = pygame.font.Font(None, 72)
fonte_grande = pygame.font.Font(None, 52)
fonte_media = pygame.font.Font(None, 40)
fonte_pequena = pygame.font.Font(None, 32)
fonte_mini = pygame.font.Font(None, 24)
fonte_titulo_menu = pygame.font.Font(None, 64)
fonte_texto_menu = pygame.font.Font(None, 32)

MUSICA_MENU = "som/tema.ogg"
NARRACAO_LORE = "som/narrador_da_lore.ogg"

class SistemaRanking:
    def __init__(self, arquivo="ranking.json"):
        self.arquivo = arquivo
        self.ranking = self.carregar_ranking()

    def carregar_ranking(self):
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def salvar_ranking(self):
        try:
            with open(self.arquivo, "w") as f:
                json.dump(self.ranking, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar ranking: {e}")

    def adicionar_vitoria(self, nome, cor, desafios, tempo):
        cor_rgb = f"({cor[0]}, {cor[1]}, {cor[2]})" if isinstance(cor, tuple) else str(cor)
        nova_vitoria = {"nome": nome, "cor": cor_rgb, "desafios": desafios, "tempo": tempo, "data": pygame.time.get_ticks() // 1000}
        self.ranking.append(nova_vitoria)
        self.ranking.sort(key=lambda x: (x["tempo"], -x["desafios"]))
        self.salvar_ranking()

class Particula:
    def __init__(self, x, y, cor, tipo="normal"):
        self.x = x
        self.y = y
        self.tipo = tipo
        if tipo == "fogo":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-6, -3)
            self.vida = 90
        elif tipo == "magico":
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-4, -1)
            self.vida = 120
        else:
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-5, -1)
            self.vida = 60
        self.cor = cor
        self.tamanho = random.randint(3, 8)
        self.rotacao = random.uniform(0, 360)

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        if self.tipo == "fogo":
            self.vy += 0.15
            self.vx *= 0.98
        elif self.tipo == "magico":
            self.rotacao += 5
            self.vy += 0.1
        else:
            self.vy += 0.2
        self.vida -= 1
        self.tamanho = max(1, self.tamanho - 0.1)

    def desenhar(self, tela):
        if self.vida > 0:
            try:
                alpha = int(255 * (self.vida / 90))
                s = pygame.Surface((int(self.tamanho * 2) + 2, int(self.tamanho * 2) + 2), pygame.SRCALPHA)
                if self.tipo == "magico":
                    pontos = []
                    for i in range(5):
                        angulo = math.radians(self.rotacao + i * 72)
                        px = self.tamanho + math.cos(angulo) * self.tamanho
                        py = self.tamanho + math.sin(angulo) * self.tamanho
                        pontos.append((int(px), int(py)))
                    if len(pontos) >= 3:
                        pygame.draw.polygon(s, (*self.cor, alpha), pontos)
                else:
                    pygame.draw.circle(s, (*self.cor, alpha), (int(self.tamanho), int(self.tamanho)), int(self.tamanho))
                tela.blit(s, (int(self.x - self.tamanho), int(self.y - self.tamanho)))
            except:
                pass

particulas = []

def criar_explosao_particulas(x, y, cor, quantidade=20, tipo="normal"):
    for _ in range(quantidade):
        particulas.append(Particula(x, y, cor, tipo))

def atualizar_particulas():
    global particulas
    for p in particulas:
        p.atualizar()
    particulas = [p for p in particulas if p.vida > 0]

def desenhar_particulas():
    for p in particulas:
        p.desenhar(TELA)

class Nuvem:
    def __init__(self):
        self.x = random.randint(-100, LARGURA)
        self.y = random.randint(50, 250)
        self.velocidade = random.uniform(0.2, 0.8)
        self.escala = random.uniform(0.5, 1.5)
        self.opacidade = random.randint(150, 220)

    def atualizar(self):
        self.x += self.velocidade
        if self.x > LARGURA + 100:
            self.x = -100
            self.y = random.randint(50, 250)

    def desenhar(self, tela):
        try:
            s = pygame.Surface((int(150 * self.escala), int(60 * self.escala)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, self.opacidade), (int(40 * self.escala), int(30 * self.escala)), int(25 * self.escala))
            pygame.draw.circle(s, (255, 255, 255, self.opacidade), (int(70 * self.escala), int(25 * self.escala)), int(30 * self.escala))
            pygame.draw.circle(s, (255, 255, 255, self.opacidade), (int(100 * self.escala), int(30 * self.escala)), int(25 * self.escala))
            tela.blit(s, (int(self.x), int(self.y)))
        except:
            pass

class Arvore:
    def __init__(self, x, y, tipo="pinheiro"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.balanco = random.uniform(0, 360)
        self.velocidade_balanco = random.uniform(0.05, 0.3)

    def atualizar(self):
        self.balanco += self.velocidade_balanco

    def desenhar(self, tela):
        try:
            offset = math.sin(math.radians(self.balanco)) * 1.5
            if self.tipo == "pinheiro":
                pygame.draw.rect(tela, MARROM, (int(self.x - 8), int(self.y), 16, 50))
                for i in range(3):
                    y_copa = self.y - 20 - i * 25
                    largura = 60 - i * 10
                    pontos = [
                        (int(self.x + offset), int(y_copa)),
                        (int(self.x - largura / 2), int(y_copa + 30)),
                        (int(self.x + largura / 2), int(y_copa + 30)),
                    ]
                    pygame.draw.polygon(tela, VERDE_FLORESTA, pontos)
                    pygame.draw.polygon(tela, VERDE_ESCURO, pontos, 2)
            else:
                pygame.draw.rect(tela, MARROM, (int(self.x - 10), int(self.y), 20, 60))
                pygame.draw.circle(tela, VERDE_FLORESTA, (int(self.x + offset), int(self.y - 20)), 35)
                pygame.draw.circle(tela, VERDE, (int(self.x + offset), int(self.y - 20)), 35, 2)
        except:
            pass

class Tocha:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.intensidade = 0
        self.offset_fogo = 0

    def atualizar(self):
        self.intensidade = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() / 300)
        self.offset_fogo = math.sin(pygame.time.get_ticks() / 200) * 2

    def desenhar(self, tela):
        try:
            pygame.draw.rect(tela, CINZA_PEDRA, (int(self.x - 8), int(self.y - 10), 16, 60), border_radius=3)
            pygame.draw.rect(tela, CINZA_ESCURO, (int(self.x - 8), int(self.y - 10), 16, 60), 2, border_radius=3)
            pygame.draw.ellipse(tela, (100, 80, 50), (int(self.x - 12), int(self.y - 15), 24, 12))
            pygame.draw.rect(tela, MARROM_CLARO, (int(self.x - 4), int(self.y - 5), 8, 35))
            tamanho = 18 * self.intensidade
            pontos_ext = [
                (int(self.x + self.offset_fogo), int(self.y - 5 - tamanho * 1.4)),
                (int(self.x - tamanho * 0.6), int(self.y)),
                (int(self.x + tamanho * 0.6), int(self.y)),
            ]
            pygame.draw.polygon(tela, (255, 100, 0), pontos_ext)
            pontos_med = [
                (int(self.x + self.offset_fogo * 0.7), int(self.y - 5 - tamanho * 1.1)),
                (int(self.x - tamanho * 0.45), int(self.y)),
                (int(self.x + tamanho * 0.45), int(self.y)),
            ]
            pygame.draw.polygon(tela, LARANJA, pontos_med)
            pontos_int = [
                (int(self.x + self.offset_fogo * 0.5), int(self.y - 5 - tamanho * 0.8)),
                (int(self.x - tamanho * 0.3), int(self.y)),
                (int(self.x + tamanho * 0.3), int(self.y)),
            ]
            pygame.draw.polygon(tela, AMARELO, pontos_int)
            pontos_centro = [
                (int(self.x), int(self.y - 5 - tamanho * 0.5)),
                (int(self.x - tamanho * 0.15), int(self.y)),
                (int(self.x + tamanho * 0.15), int(self.y)),
            ]
            pygame.draw.polygon(tela, (255, 255, 200), pontos_centro)
            if random.random() < 0.1:
                particulas.append(Particula(self.x + self.offset_fogo, self.y - 15, LARANJA, "fogo"))
            if random.random() < 0.05:
                particulas.append(Particula(self.x + self.offset_fogo, self.y - 20, AMARELO, "fogo"))
        except:
            pass

class Riacho:
    def __init__(self):
        self.offset_onda = 0
        self.pedras = []
        for _ in range(15):
            x = random.randint(0, LARGURA)
            y = random.randint(ALTURA - 200, ALTURA - 100)
            tamanho = random.randint(8, 20)
            self.pedras.append((x, y, tamanho))

    def atualizar(self):
        self.offset_onda += 0.05

    def desenhar(self, tela):
        try:
            tempo = pygame.time.get_ticks() / 1000
            for i in range(LARGURA):
                onda1 = math.sin(tempo * 2 + i * 0.01) * 8
                onda2 = math.sin(tempo * 1.5 + i * 0.015) * 5
                y_base = ALTURA - 150 + onda1 + onda2
                pygame.draw.line(tela, (70, 130, 180), (i, int(y_base)), (i, ALTURA - 100), 1)
            for i in range(0, LARGURA, 40):
                x = i + math.sin(tempo + i * 0.05) * 20
                y = ALTURA - 140 + math.sin(tempo * 2 + i * 0.02) * 5
                tamanho = 15 + math.sin(tempo + i) * 5
                s = pygame.Surface((int(tamanho * 2), int(tamanho)), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (150, 200, 255, 100), (0, 0, int(tamanho * 2), int(tamanho)))
                tela.blit(s, (int(x), int(y)))
            for px, py, tam in self.pedras:
                pygame.draw.ellipse(tela, (50, 80, 100), (px - tam // 2 + 2, py + tam // 2, tam, tam // 2))
                pygame.draw.circle(tela, CINZA_PEDRA, (px, py), tam)
                pygame.draw.circle(tela, CINZA_CLARO, (px - tam // 4, py - tam // 4), tam // 3)
                pygame.draw.circle(tela, CINZA_ESCURO, (px, py), tam, 2)
            for i in range(0, LARGURA, 60):
                x = i + math.sin(tempo * 3 + i * 0.1) * 10
                y = ALTURA - 145 + math.sin(tempo * 2.5 + i * 0.03) * 8
                s = pygame.Surface((30, 5), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (200, 230, 255, 150), (0, 0, 30, 5))
                tela.blit(s, (int(x), int(y)))
        except:
            pass

class Castelo:
    def __init__(self, x, y, escala=1.0):
        self.x = x
        self.y = y
        self.escala = escala
        self.bandeira_angulo = 0

    def atualizar(self):
        self.bandeira_angulo = math.sin(pygame.time.get_ticks() / 500) * 15

    def desenhar(self, tela):
        try:
            s = self.escala
            pygame.draw.rect(tela, CINZA_PEDRA, (int(self.x), int(self.y), int(60 * s), int(180 * s)))
            pygame.draw.rect(tela, CINZA_ESCURO, (int(self.x), int(self.y), int(60 * s), int(180 * s)), 3)
            for i in range(4):
                pygame.draw.rect(tela, CINZA_PEDRA, (int(self.x + i * 15 * s), int(self.y - 15 * s), int(12 * s), int(15 * s)))
            pygame.draw.rect(tela, CINZA_PEDRA, (int(self.x + 120 * s), int(self.y), int(60 * s), int(180 * s)))
            pygame.draw.rect(tela, CINZA_ESCURO, (int(self.x + 120 * s), int(self.y), int(60 * s), int(180 * s)), 3)
            for i in range(4):
                pygame.draw.rect(tela, CINZA_PEDRA, (int(self.x + 120 * s + i * 15 * s), int(self.y - 15 * s), int(12 * s), int(15 * s)))
            pygame.draw.rect(tela, CINZA_CLARO, (int(self.x + 40 * s), int(self.y - 40 * s), int(100 * s), int(220 * s)))
            pygame.draw.rect(tela, CINZA_ESCURO, (int(self.x + 40 * s), int(self.y - 40 * s), int(100 * s), int(220 * s)), 3)
            pontos_telhado = [
                (int(self.x + 90 * s), int(self.y - 80 * s)),
                (int(self.x + 30 * s), int(self.y - 40 * s)),
                (int(self.x + 150 * s), int(self.y - 40 * s)),
            ]
            pygame.draw.polygon(tela, VERMELHO_ESCURO, pontos_telhado)
            pygame.draw.polygon(tela, MARROM, pontos_telhado, 2)
            for i in range(4):
                y_janela = self.y - 20 * s + i * 45 * s
                pygame.draw.rect(tela, (50, 50, 80), (int(self.x + 70 * s), int(y_janela), int(40 * s), int(35 * s)))
                pygame.draw.polygon(
                    tela,
                    (50, 50, 80),
                    [
                        (int(self.x + 90 * s), int(y_janela)),
                        (int(self.x + 70 * s), int(y_janela + 10 * s)),
                        (int(self.x + 110 * s), int(y_janela + 10 * s)),
                    ],
                )
                if i < 2:
                    s_luz = pygame.Surface((int(40 * s), int(35 * s)), pygame.SRCALPHA)
                    pygame.draw.rect(s_luz, (255, 220, 100, 80), (0, 0, int(40 * s), int(35 * s)))
                    tela.blit(s_luz, (int(self.x + 70 * s), int(y_janela)))
            pygame.draw.rect(tela, MARROM_CLARO, (int(self.x + 65 * s), int(self.y + 140 * s), int(50 * s), int(40 * s)))
            pygame.draw.rect(tela, MARROM, (int(self.x + 65 * s), int(self.y + 140 * s), int(50 * s), int(40 * s)), 3)
            pygame.draw.arc(tela, MARROM, (int(self.x + 65 * s), int(self.y + 120 * s), int(50 * s), int(40 * s)), 0, math.pi, 3)
            for i in range(3):
                for j in range(6):
                    if random.random() < 0.3:
                        cor_pedra = CINZA_ESCURO if random.random() < 0.5 else CINZA_CLARO
                        pygame.draw.rect(
                            tela,
                            cor_pedra,
                            (int(self.x + 45 * s + j * 15 * s), int(self.y - 30 * s + i * 70 * s), int(12 * s), int(8 * s)),
                        )
            mastro_x = self.x + 90 * s
            mastro_y = self.y - 80 * s
            pygame.draw.line(tela, MARROM_CLARO, (int(mastro_x), int(mastro_y)), (int(mastro_x), int(mastro_y - 50 * s)), 3)
            bandeira_pontos = [
                (int(mastro_x), int(mastro_y - 50 * s)),
                (int(mastro_x + 30 * s + math.sin(self.bandeira_angulo * 0.1) * 5), int(mastro_y - 45 * s)),
                (int(mastro_x + 30 * s + math.sin(self.bandeira_angulo * 0.1) * 3), int(mastro_y - 30 * s)),
                (int(mastro_x), int(mastro_y - 25 * s)),
            ]
            pygame.draw.polygon(tela, VERMELHO, bandeira_pontos)
            pygame.draw.circle(tela, OURO, (int(mastro_x + 15 * s), int(mastro_y - 37 * s)), int(5 * s))
        except:
            pass

nuvens = [Nuvem() for _ in range(8)]
arvores = []
tochas = []
riacho = None
castelos = []
tamanho_casa = 20

def inicializar_cenario():
    global arvores, tochas, riacho, castelos
    arvores = []
    tochas = []
    castelos = []
    for i in range(20):
        x = random.randint(50, max(100, LARGURA - 400))
        y = random.randint(max(100, ALTURA - 280), ALTURA - 180)
        tipo = random.choice(["pinheiro", "normal"])
        arvores.append(Arvore(x, y, tipo))
    num_tochas = min(8, LARGURA // 200)
    for i in range(num_tochas):
        x = 80 + i * (LARGURA - 400) // max(1, num_tochas - 1)
        y = ALTURA - 130
        tochas.append(Tocha(x, y))
    riacho = Riacho()
    castelos.append(Castelo(50, ALTURA - 350, 0.6))
    castelos.append(Castelo(LARGURA - 300, ALTURA - 320, 0.55))

inicializar_cenario()

def tocar_som_sucesso():
    try:
        pygame.mixer.Sound(
            buffer=bytearray([int(128 + 127 * math.sin(2 * math.pi * 880 * x / 22050)) for x in range(1000)])
        ).play()
    except:
        pass

def tocar_som_erro():
    try:
        pygame.mixer.Sound(
            buffer=bytearray([int(128 + 70 * math.sin(2 * math.pi * 150 * x / 22050)) for x in range(5000)])
        ).play()
    except:
        pass

def tocar_som_movimento():
    try:
        pygame.mixer.Sound(
            buffer=bytearray([int(128 + 70 * math.sin(2 * math.pi * 400 * x / 22050)) for x in range(800)])
        ).play()
    except:
        pass

def tocar_som_vitoria():
    try:
        for freq in [523, 659, 784, 988]:
            som = pygame.mixer.Sound(
                buffer=bytearray([int(128 + 127 * math.sin(2 * math.pi * freq * x / 22050)) for x in range(2500)])
            )
            som.set_volume(0.3)
            som.play()
            pygame.time.wait(150)
    except:
        pass

class Pergaminho:
    def __init__(self, largura, altura, titulo, texto_lore, regras):
        self.largura = min(largura, LARGURA - 100)
        self.altura = min(altura, ALTURA - 100)
        self.titulo = titulo
        self.texto_lore = texto_lore
        self.regras = regras
        self.anim_progress = 0
        self.velocidade_abertura = 8
        self.narracao_iniciada = False

    def desenhar(self, surface, jogo_ref=None):
        if self.anim_progress < self.largura - 200:
            self.anim_progress += self.velocidade_abertura
        perg_rect = pygame.Rect(
            (LARGURA - self.anim_progress) // 2, max(50, (ALTURA - self.altura) // 2), self.anim_progress, self.altura
        )
        pygame.draw.rect(surface, BEGE, perg_rect, border_radius=12)
        pygame.draw.rect(surface, MARROM, perg_rect, 8, border_radius=12)
        if self.anim_progress >= self.largura - 200:
            if jogo_ref and not self.narracao_iniciada:
                jogo_ref.iniciar_narracao()
                self.narracao_iniciada = True
            titulo_surf = fonte_titulo_menu.render(self.titulo, True, OURO)
            surface.blit(titulo_surf, (LARGURA // 2 - titulo_surf.get_width() // 2, perg_rect.y + 30))
            y = perg_rect.y + 100
            for linha in self.texto_lore:
                txt = fonte_texto_menu.render(linha, True, PRETO)
                if txt.get_width() > self.largura - 100:
                    txt = fonte_pequena.render(linha, True, PRETO)
                surface.blit(txt, (LARGURA // 2 - txt.get_width() // 2, y))
                y += 35
            y += 20
            regras_titulo = fonte_texto_menu.render("Regras do Jogo", True, OURO)
            surface.blit(regras_titulo, (LARGURA // 2 - regras_titulo.get_width() // 2, y))
            y += 50
            for regra in self.regras:
                txt = fonte_pequena.render(regra, True, PRETO)
                if txt.get_width() > self.largura - 100:
                    txt = fonte_mini.render(regra, True, PRETO)
                surface.blit(txt, (LARGURA // 2 - txt.get_width() // 2, y))
                y += 30

def remover_fundo_branco(surface, threshold=240):
    try:
        img_sem_fundo = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                pixel = surface.get_at((x, y))
                r, g, b, a = pixel
                if r >= threshold and g >= threshold and b >= threshold:
                    img_sem_fundo.set_at((x, y), (r, g, b, 0))
                else:
                    img_sem_fundo.set_at((x, y), pixel)
        return img_sem_fundo
    except Exception as e:
        return surface

def carregar_imagens_personagens():
    imagens = {}
    cores_caminhos = {
        VERMELHO: ["cavaleiro_vermelho.png", "./img/cavaleiro_vermelho.png"],
        AZUL: ["cavaleiro_azul.png", "./img/cavaleiro_azul.png"],
    }
    for cor, caminhos in cores_caminhos.items():
        img_carregada = None
        for caminho in caminhos:
            try:
                img_carregada = pygame.image.load(caminho)
                img_sem_fundo = remover_fundo_branco(img_carregada, threshold=240)
                imagens[cor] = img_sem_fundo.convert_alpha()
                break
            except Exception:
                continue
    return imagens   


IMAGENS_PERSONAGENS = carregar_imagens_personagens()

def atualizar_imagens_personagens(jogadores):
    global IMAGENS_PERSONAGENS
    for jogador in jogadores:
        if jogador.cor in IMAGENS_PERSONAGENS:
            jogador.imagem_original = IMAGENS_PERSONAGENS[jogador.cor]

class Personagem:
    def __init__(self, cor, nome):
        self.cor = cor
        self.nome = nome
        self.posicao = 0
        self.posicao_visual = 0.0
        self.pontos = 0
        self.desafios_completados = 0
        self.animacao_offset = 0
        self.animacao_direcao = 1
        self.velocidade_movimento = 0.05
        self.danca_frame = 0
        self.danca_ativa = False
        self.imagem_original = IMAGENS_PERSONAGENS.get(cor)

    def atualizar_animacao(self):
        if self.danca_ativa:
            self.danca_frame += 1
            return
        self.animacao_offset += 0.15 * self.animacao_direcao
        if abs(self.animacao_offset) > 3:
            self.animacao_direcao *= -1
        if self.posicao_visual < self.posicao:
            self.posicao_visual += self.velocidade_movimento
            if self.posicao_visual > self.posicao:
                self.posicao_visual = self.posicao
        elif self.posicao_visual > self.posicao:
            self.posicao_visual -= self.velocidade_movimento
            if self.posicao_visual < self.posicao:
                self.posicao_visual = self.posicao

    def iniciar_danca(self):
        self.danca_ativa = True
        self.danca_frame = 0

    def desenhar(self, x, y, escala=1.0):
        try:
            self.atualizar_animacao()
            if self.imagem_original is None:
                y_anim = y + self.animacao_offset
                pygame.draw.ellipse(
                    TELA, (50, 50, 50), (int(x - 20 * escala), int(y + 35 * escala), int(40 * escala), int(10 * escala))
                )
                pygame.draw.rect(
                    TELA,
                    self.cor,
                    (int(x - 12 * escala), int(y_anim - 5 * escala), int(24 * escala), int(28 * escala)),
                    border_radius=int(5 * escala),
                )
                pygame.draw.circle(TELA, self.cor, (int(x), int(y_anim - 18 * escala)), int(14 * escala))
                texto_nome = fonte_mini.render(self.nome[:15], True, BRANCO)
                TELA.blit(texto_nome, (int(x - texto_nome.get_width() // 2), int(y + 45)))
                return
            tamanho_base = max(60, min(140, max(LARGURA // 25, ALTURA // 15))) * 1.8 * escala
            largura_img = int(tamanho_base)
            altura_img = int(tamanho_base)
            if self.danca_ativa:
                tempo = self.danca_frame / 10
                pulo = abs(math.sin(tempo * 2)) * 25 * escala
                y_anim = y - pulo
                angulo = math.sin(tempo * 3) * 15
                if self.danca_frame % 10 == 0:
                    for _ in range(5):
                        criar_explosao_particulas(
                            x + random.randint(-30, 30),
                            y - 40,
                            random.choice([DOURADO, AMARELO, LARANJA, ROXO, VERDE]),
                            3,
                            "magico",
                        )
                sombra_largura = int((largura_img * 0.7) + pulo * 0.3)
                sombra_altura = int((largura_img * 0.15) * escala)
                s_sombra = pygame.Surface((sombra_largura, sombra_altura), pygame.SRCALPHA)
                pygame.draw.ellipse(s_sombra, (50, 50, 50, 180), (0, 0, sombra_largura, sombra_altura))
                TELA.blit(s_sombra, (int(x - sombra_largura // 2), int(y + 50 * escala - sombra_altura // 2)))
                imagem_rotacionada = pygame.transform.rotate(self.imagem_original, angulo)
                imagem_final = pygame.transform.scale(imagem_rotacionada, (largura_img, altura_img))
                TELA.blit(
                    imagem_final,
                    (
                        int(x - imagem_final.get_width() // 2),
                        int(y_anim - imagem_final.get_height() + 50 * escala),
                    ),
                )
            else:
                y_anim = y + self.animacao_offset
                sombra_largura = int(largura_img * 0.7)
                sombra_altura = int(largura_img * 0.15 * escala)
                s_sombra = pygame.Surface((sombra_largura, sombra_altura), pygame.SRCALPHA)
                pygame.draw.ellipse(s_sombra, (50, 50, 50, 180), (0, 0, sombra_largura, sombra_altura))
                TELA.blit(s_sombra, (int(x - sombra_largura // 2), int(y + 50 * escala - sombra_altura // 2)))
                imagem_final = pygame.transform.scale(self.imagem_original, (largura_img, altura_img))
                TELA.blit(
                    imagem_final, (int(x - imagem_final.get_width() // 2), int(y_anim - imagem_final.get_height() + 50 * escala))
                )
                texto_nome = fonte_mini.render(self.nome[:15], True, BRANCO)
                TELA.blit(texto_nome, (int(x - texto_nome.get_width() // 2), int(y + 55 * escala)))
        except Exception as e:
            pass

class Dado:
    def __init__(self):
        self.valor = 1
        self.animacao_frame = 0

    def rolar(self):
        self.valor = random.randint(1, 6)
        self.animacao_frame = 30

    def desenhar_dado(self, valor, x, y, tamanho=50):
        try:
            rect = pygame.Rect(x - tamanho // 2, y - tamanho // 2, tamanho, tamanho)
            pygame.draw.rect(TELA, BRANCO, rect, border_radius=tamanho // 8)
            pygame.draw.rect(TELA, PRETO, rect, 2, border_radius=tamanho // 8)
            tamanho_ponto = tamanho // 8
            pontos = {
                1: [(0, 0)],
                2: [(-1, -1), (1, 1)],
                3: [(-1, -1), (0, 0), (1, 1)],
                4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
                5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
                6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)],
            }
            if valor in pontos:
                for px, py in pontos[valor]:
                    pos_x = x + px * (tamanho // 3)
                    pos_y = y + py * (tamanho // 3)
                    pygame.draw.circle(TELA, PRETO, (pos_x, pos_y), tamanho_ponto)
        except:
            pass

class Painel:
    def desenhar_painel(self, jogadores, jogador_atual_idx, dado_valor, estado, tempo_inicio):
        largura_painel = min(400, LARGURA // 4)
        x_painel = LARGURA - largura_painel
        y_painel = 0
        altura_painel = ALTURA
        s_painel = pygame.Surface((largura_painel, altura_painel), pygame.SRCALPHA)
        pygame.draw.rect(s_painel, (0, 0, 0, 200), (0, 0, largura_painel, altura_painel))
        TELA.blit(s_painel, (x_painel, y_painel))
        pygame.draw.line(TELA, DOURADO, (x_painel, 0), (x_painel, ALTURA), 5)
        jogador = jogadores[jogador_atual_idx]
        nome_curto = jogador.nome if len(jogador.nome) <= 10 else jogador.nome
        texto_jogador = fonte_grande.render(nome_curto, True, jogador.cor)
        TELA.blit(texto_jogador, (LARGURA - largura_painel + 20, 60))
        dado_obj = Dado()
        dado_obj.desenhar_dado(dado_valor if estado in ["rolando_dado", "aguardando_movimento"] else 0, LARGURA - largura_painel + largura_painel // 2, 150)
        y_status = 250
        for i, p in enumerate(jogadores):
            cor = DOURADO if i == jogador_atual_idx else BRANCO
            texto_status = fonte_pequena.render(f"{p.nome[:8]}: {p.posicao}", True, cor)
            TELA.blit(texto_status, (LARGURA - largura_painel + 20, y_status + i * 50))
            progresso = p.posicao / 40
            barra_largura = largura_painel - 40
            pygame.draw.rect(
                TELA, CINZA_CLARO, (LARGURA - largura_painel + 20, y_status + i * 50 + 25, barra_largura, 8), border_radius=5
            )
            if progresso > 0:
                pygame.draw.rect(
                    TELA,
                    p.cor,
                    (LARGURA - largura_painel + 20, y_status + i * 50 + 25, int(barra_largura * progresso), 8),
                    border_radius=5,
                )
        if tempo_inicio > 0:
            tempo_decorrido = pygame.time.get_ticks() // 1000 - tempo_inicio
            minutos = tempo_decorrido // 60
            segundos = tempo_decorrido % 60
            txt_tempo = fonte_pequena.render(f"Tempo: {minutos}:{segundos:02d}", True, BRANCO)
            TELA.blit(txt_tempo, (LARGURA - largura_painel + 20, 400))
        y_botao = ALTURA - 80
        if estado == "aguardando_dado":
            self.desenhar_botao("Rolar Dado", LARGURA - largura_painel + 20, y_botao, largura_painel - 40, 50, DOURADO)
        elif estado == "aguardando_movimento":
            self.desenhar_botao(f"Mover ({dado_valor})", LARGURA - largura_painel + 20, y_botao, largura_painel - 40, 50, MARROM_CLARO)

    def desenhar_botao(self, texto, x, y, largura, altura, cor):
        rect = pygame.Rect(x, y, largura, altura)
        pygame.draw.rect(TELA, cor, rect, border_radius=10)
        pygame.draw.rect(TELA, DOURADO, rect, 3, border_radius=10)
        txt = fonte_media.render(texto, True, PRETO)
        TELA.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

class Desafio:
    def __init__(self, tipo, posicao_casa):
        self.tipo = tipo
        self.posicao_casa = posicao_casa
        self.titulo = ""
        self.pergunta = ""
        self.resposta = 0
        self.icone_cor = BRANCO
        self.gerar_desafio()

    def gerar_desafio(self):
        if self.tipo == "soma":
            a = random.randint(10, 50)
            b = random.randint(10, 50)
            self.pergunta = f"{a} + {b}"
            self.resposta = a + b
            self.titulo = "Desafio da Adicao"
            self.icone_cor = VERDE
        elif self.tipo == "subtracao":
            b = random.randint(10, 40)
            a = random.randint(b + 5, 80)
            self.pergunta = f"{a} - {b}"
            self.resposta = a - b
            self.titulo = "Desafio da Subtracao"
            self.icone_cor = AZUL
        elif self.tipo == "multiplicacao":
            a = random.randint(6, 18)
            b = random.randint(3, 15)
            self.pergunta = f"{a} x {b}"
            self.resposta = a * b
            self.titulo = "Desafio da Multiplicacao"
            self.icone_cor = ROXO
        elif self.tipo == "divisao":
            b = random.randint(3, 12)
            resposta = random.randint(6, 20)
            a = b * resposta
            self.pergunta = f"{a} / {b}"
            self.resposta = resposta
            self.titulo = "Desafio da Divisao"
            self.icone_cor = LARANJA
        elif self.tipo == "raiz":
            resposta = random.randint(6, 18)
            a = resposta**2
            self.pergunta = f"Raiz de {a}"
            self.resposta = resposta
            self.titulo = "Desafio da Raiz Quadrada"
            self.icone_cor = ROXO
        elif self.tipo == "completo":
            a = random.randint(3, 7)
            b = random.randint(3, 7)
            c = random.randint(2, 6)
            d = random.randint(2, 5)
            self.pergunta = f"({a} + {b}) x {c} - {d}"
            self.resposta = (a + b) * c - d
            self.titulo = "DESAFIO FINAL DO REI"
            self.icone_cor = DOURADO

class Tabuleiro:
    def __init__(self):
        self.casas = []
        self.desafios = {}
        self.criar_tabuleiro()

    def criar_tabuleiro(self):
        self.casas = []
        centro_x, centro_y = LARGURA // 2, min(ALTURA // 2 + 50, ALTURA - 200)
        raio = min(300, min(LARGURA, ALTURA) // 3)
        for i in range(41):
            angulo = -90 + (i * 360 / 40) * 2.0 
            rad = math.radians(angulo)
            espiral = 1 - (i / 70) 
            x = centro_x + int(raio * math.cos(rad) * espiral)
            y = centro_y + int(raio * math.sin(rad) * espiral)
            x = max(50, min(x, LARGURA - 350))
            y = max(100, min(y, ALTURA - 150))
            if i < 40:
                angulo_prox = -90 + ((i + 1) * 360 / 40) * 2.0
                rad_prox = math.radians(angulo_prox)
                espiral_prox = 1 - ((i + 1) / 70)
                x_prox = centro_x + int(raio * math.cos(rad_prox) * espiral_prox)
                y_prox = centro_y + int(raio * math.sin(rad_prox) * espiral_prox)
                dx = x_prox - x
                dy = y_prox - y
                orientacao = math.atan2(dy, dx)
            else:
                orientacao = 0
            self.casas.append({"centro": (x, y), "orientacao": orientacao})
        self.desafios = {
            7: Desafio("soma", 7),
            14: Desafio("subtracao", 14),
            21: Desafio("multiplicacao", 21),
            28: Desafio("divisao", 28),
            35: Desafio("raiz", 35),
            40: Desafio("completo", 40),
        }

    def desenhar(self):
        pontos_estrada = [casa["centro"] for casa in self.casas]
        if len(pontos_estrada) >= 2:
            for i in range(len(pontos_estrada) - 1):
                p1 = pontos_estrada[i]
                p2 = pontos_estrada[i+1]
                pygame.draw.line(TELA, TERRA, p1, p2, 80)
                pygame.draw.line(TELA, MARROM_CLARO, p1, p2, 70)
                pygame.draw.line(TELA, CINZA_PEDRA, p1, p2, 8)
        for i, casa in enumerate(self.casas):
            x, y = casa["centro"]
            tamanho_bloco = 40
            cor = (180, 140, 80)
            cor_borda = (120, 90, 50)
            if i == 0:
                cor = (100, 200, 100)
                cor_borda = (50, 150, 50)
            elif i == 40:
                cor = (255, 215, 0)
                cor_borda = (200, 160, 0)
            elif i in self.desafios:
                cor = (200, 100, 100)
                cor_borda = (150, 50, 50)
            pontos_iso = [
                (x, y - tamanho_bloco // 2),
                (x + tamanho_bloco // 2, y),
                (x, y + tamanho_bloco // 2),
                (x - tamanho_bloco // 2, y),
            ]
            pygame.draw.polygon(TELA, cor, pontos_iso)
            pygame.draw.polygon(TELA, cor_borda, pontos_iso, 4)
            cor_sombra = tuple(c // 2 for c in cor)
            pontos_lateral = [
                (x, y + tamanho_bloco // 2),
                (x + tamanho_bloco // 2, y),
                (x + tamanho_bloco // 2, y + tamanho_bloco // 2),
                (x, y + tamanho_bloco),
            ]
            pygame.draw.polygon(TELA, cor_sombra, pontos_lateral)
            pygame.draw.polygon(TELA, (60, 50, 40), pontos_lateral, 1)
            for j in range(3):
                offset = random.randint(-2, 2)
                cor_textura = tuple(max(0, min(255, c + offset)) for c in cor)
                px = int(x + random.uniform(-tamanho_bloco // 4, tamanho_bloco // 4))
                py = int(y + random.uniform(-tamanho_bloco // 8, tamanho_bloco // 8))
                pygame.draw.circle(TELA, cor_textura, (px, py), 2)
            if i > 0:
                cor_texto = (30, 30, 30)
                if i in self.desafios or i == 40:
                    cor_texto = BRANCO
                texto_num = fonte_media.render(str(i), True, cor_texto)
                TELA.blit(texto_num, (x - texto_num.get_width() // 2, y - texto_num.get_height() // 2))

class TecladoMobile:
    def __init__(self):
        self.teclas = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫'],
        ]
        self.tamanho_tecla = 35
        self.espacamento = 5

    def desenhar(self, x_inicio, y_inicio, input_ativo):
        if not input_ativo:
            return None
        
        rects_teclas = []
        y = y_inicio
        
        for linha_idx, linha in enumerate(self.teclas):
            x = x_inicio
            for tecla in linha:
                rect = pygame.Rect(x, y, self.tamanho_tecla, self.tamanho_tecla)
                rects_teclas.append((rect, tecla))
                
                cor = OURO if tecla == '⌫' else DOURADO
                pygame.draw.rect(TELA, cor, rect, border_radius=5)
                pygame.draw.rect(TELA, BRANCO, rect, 2, border_radius=5)
                
                texto = fonte_mini.render(tecla, True, PRETO)
                TELA.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))
                
                x += self.tamanho_tecla + self.espacamento
            
            y += self.tamanho_tecla + self.espacamento
        
        return rects_teclas

class PopupSair:
    def __init__(self):
        self.ativo = False
        self.confirmacao_rect = None
        self.cancelamento_rect = None
        self.animacao_frame = 0

    def mostrar(self):
        self.ativo = True
        self.animacao_frame = 0

    def fechar(self):
        self.ativo = False

    def desenhar(self, tela):
        if not self.ativo:
            return
        
        self.animacao_frame += 1
        alpha = min(255, self.animacao_frame * 10)
        
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        tela.blit(overlay, (0, 0))
        
        largura_popup = 600
        altura_popup = 350
        x_popup = LARGURA // 2 - largura_popup // 2
        y_popup = ALTURA // 2 - altura_popup // 2
        
        popup_rect = pygame.Rect(x_popup, y_popup, largura_popup, altura_popup)
        pygame.draw.rect(tela, CINZA_ESCURO, popup_rect, border_radius=20)
        pygame.draw.rect(tela, OURO, popup_rect, 5, border_radius=20)
        
        titulo = fonte_grande.render("SAIR DO JOGO?", True, VERMELHO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, y_popup + 40))
        
        mensagem = fonte_media.render("Tem certeza que deseja sair?", True, BRANCO)
        tela.blit(mensagem, (LARGURA // 2 - mensagem.get_width() // 2, y_popup + 120))
        
        self.confirmacao_rect = pygame.Rect(x_popup + 50, y_popup + 220, 200, 80)
        pygame.draw.rect(tela, VERMELHO, self.confirmacao_rect, border_radius=10)
        pygame.draw.rect(tela, BRANCO, self.confirmacao_rect, 3, border_radius=10)
        txt_sim = fonte_media.render("SIM", True, BRANCO)
        tela.blit(txt_sim, (self.confirmacao_rect.centerx - txt_sim.get_width() // 2, self.confirmacao_rect.centery - txt_sim.get_height() // 2))
        
        self.cancelamento_rect = pygame.Rect(x_popup + 350, y_popup + 220, 200, 80)
        pygame.draw.rect(tela, VERDE, self.cancelamento_rect, border_radius=10)
        pygame.draw.rect(tela, BRANCO, self.cancelamento_rect, 3, border_radius=10)
        txt_nao = fonte_media.render("NÃO", True, BRANCO)
        tela.blit(txt_nao, (self.cancelamento_rect.centerx - txt_nao.get_width() // 2, self.cancelamento_rect.centery - txt_nao.get_height() // 2))

class Jogo:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.sistema_ranking = SistemaRanking()
        self.tabuleiro = Tabuleiro()
        self.painel = Painel()
        self.teclado_mobile = TecladoMobile()
        self.popup_sair = PopupSair()
        self.estado = "fade_in"
        self.transicao_ativa = False
        self.transicao_opacidade = 255
        self.transicao_destino = None
        self.narracao_ativa = False
        self.volume_musica_original = 0.5
        self.pergaminho = Pergaminho(
            largura=min(1400, LARGURA - 200),
            altura=min(800, ALTURA - 100),
            titulo="A Estrada dos Reis",
            texto_lore=[ 
                "No reino de Aetheria, a paz foi desfeita.", 
                "O Rei Theron sumiu, e a coroa jaz em perigo.", 
                "Cavaleiros de toda parte sao convocados para a Estrada dos Reis.", 
                "Voce deve enfrentar desafios matematicos para provar seu valor."
            ],
            regras=[
                "1. Escolha seu cavaleiro e nome.",
                "2. Role o dado e avance. A cada rodada, o proximo jogador joga.",
                "3. Casas especiais (7, 14, 21, 28, 35, 40) ativam desafios matematicos.",
                "4. Resposta correta: avanca 3 casas. Resposta errada: recua 2 casas.",
                "5. O primeiro a chegar na Casa 40 e resolver o Desafio Final vence!",
            ]
        )
        self.personagens = [Personagem(AZUL, "Cavaleiro Azul"), Personagem(VERMELHO, "Cavaleiro Vermelho")]
        atualizar_imagens_personagens(self.personagens)
        self.jogador_atual = 0
        self.dado_valor = 1
        self.dado_frame = 0
        self.tempo_inicio = 0
        self.vencedor = None
        self.desafio_atual = None
        self.resposta_usuario = ""
        self.input_ativo = [False, False]
        self.nomes_personagens = ["", ""]
        self.mensagem = ""
        self.tempo_mensagem = 0
        inicializar_cenario()
        self.iniciar_musica_menu()

    def iniciar_musica_menu(self):
        if os.path.exists(MUSICA_MENU):
            try:
                pygame.mixer.music.load(MUSICA_MENU)
                pygame.mixer.music.set_volume(self.volume_musica_original)
                pygame.mixer.music.play(-1)
            except:
                pass

    def iniciar_narracao(self):
        if os.path.exists(NARRACAO_LORE):
            try:
                pygame.mixer.music.set_volume(0.15)
                self.narracao_ativa = True
                pygame.mixer.Sound(NARRACAO_LORE).play()
            except:
                pass

    def verificar_narracao_terminou(self):
        if self.narracao_ativa and not pygame.mixer.get_busy():
            self.narracao_ativa = False
            pygame.mixer.music.set_volume(self.volume_musica_original)

    def iniciar_transicao(self, destino):
        self.transicao_ativa = True
        self.transicao_destino = destino
        self.transicao_opacidade = 0

    def desenhar_transicao(self):
        if not self.transicao_ativa:
            return
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))
        if self.estado == self.transicao_destino:
            self.transicao_opacidade -= 6
            if self.transicao_opacidade <= 0:
                self.transicao_ativa = False
        else:
            self.transicao_opacidade += 6
            if self.transicao_opacidade >= 255:
                self.transicao_opacidade = 255
                self.estado = self.transicao_destino
            if self.estado == "aguardando_dado":
                self.tempo_inicio = pygame.time.get_ticks() // 1000
        overlay.set_alpha(self.transicao_opacidade)
        TELA.blit(overlay, (0, 0))

    def desenhar_fade_in(self):
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))
        self.transicao_opacidade -= 4
        if self.transicao_opacidade <= 0:
            self.transicao_opacidade = 0
            self.estado = "menu_inicial"
            self.iniciar_musica_menu()
        overlay.set_alpha(self.transicao_opacidade)
        TELA.blit(overlay, (0, 0))

    def desenhar_fundo_medieval(self):
        TELA.fill(AZUL_CEU)
        self.desenhar_paisagem_isometrica()
        for arvore in arvores:
            arvore.atualizar()
            arvore.desenhar(TELA)
        for tocha in tochas:
            tocha.atualizar()
            tocha.desenhar(TELA)
        for castelo in castelos:
            castelo.atualizar()
            castelo.desenhar(TELA)

    fundo_cache = None
    
    def desenhar_paisagem_isometrica(self):
        if Jogo.fundo_cache is None:
            Jogo.fundo_cache = pygame.Surface((LARGURA, ALTURA))
            
            Jogo.fundo_cache.fill((255, 220, 180))
            
            pygame.draw.ellipse(Jogo.fundo_cache, (255, 200, 100), (-200, -100, 800, 600))
            
            nuvem_cor = (255, 250, 240)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (200, 150), 80)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (280, 140), 90)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (150, 180), 70)
            
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (LARGURA - 300, 120), 85)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (LARGURA - 200, 130), 95)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (LARGURA - 380, 150), 75)
            
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (LARGURA // 2 + 100, 200), 80)
            pygame.draw.circle(Jogo.fundo_cache, nuvem_cor, (LARGURA // 2 + 200, 190), 85)
            
            colinas_cores = [
                (100, 200, 80),
                (120, 180, 100),
                (90, 190, 70),
            ]
            
            pontos_colina1 = [
                (0, ALTURA - 150),
                (400, ALTURA - 300),
                (600, ALTURA - 250),
                (800, ALTURA - 350),
                (LARGURA, ALTURA - 200),
                (LARGURA, ALTURA),
                (0, ALTURA),
            ]
            pygame.draw.polygon(Jogo.fundo_cache, colinas_cores[0], pontos_colina1)
            
            pontos_colina2 = [
                (100, ALTURA - 200),
                (500, ALTURA - 280),
                (900, ALTURA - 220),
                (1200, ALTURA - 320),
                (LARGURA, ALTURA - 250),
                (LARGURA, ALTURA),
                (0, ALTURA),
            ]
            pygame.draw.polygon(Jogo.fundo_cache, colinas_cores[1], pontos_colina2)
            
            pontos_colina3 = [
                (200, ALTURA - 180),
                (600, ALTURA - 250),
                (1000, ALTURA - 180),
                (1400, ALTURA - 280),
                (LARGURA, ALTURA - 220),
                (LARGURA, ALTURA),
                (0, ALTURA),
            ]
            pygame.draw.polygon(Jogo.fundo_cache, colinas_cores[2], pontos_colina3)
            
            for i in range(5):
                x_arvore = random.randint(100, LARGURA - 100)
                y_arvore = ALTURA - 200 + random.randint(0, 50)
                tamanho = random.randint(30, 60)
                pygame.draw.polygon(Jogo.fundo_cache, (100, 150, 50), [
                    (x_arvore, y_arvore - tamanho),
                    (x_arvore - tamanho // 2, y_arvore),
                    (x_arvore + tamanho // 2, y_arvore)
                ])
                pygame.draw.rect(Jogo.fundo_cache, (80, 50, 20), (x_arvore - 5, y_arvore, 10, tamanho // 2))
            
            flores_cores = [(255, 100, 150), (255, 200, 100), (100, 200, 255), (255, 255, 100)]
            for _ in range(20):
                x_flor = random.randint(50, LARGURA - 50)
                y_flor = ALTURA - 150 + random.randint(0, 50)
                cor_flor = random.choice(flores_cores)
                pygame.draw.circle(Jogo.fundo_cache, cor_flor, (int(x_flor), int(y_flor)), random.randint(3, 8))
            
            castelo_x = LARGURA - 200
            castelo_y = ALTURA - 250
            pygame.draw.rect(Jogo.fundo_cache, (150, 120, 100), (castelo_x - 60, castelo_y, 120, 100))
            pygame.draw.polygon(Jogo.fundo_cache, (180, 80, 80), [
                (castelo_x - 60, castelo_y),
                (castelo_x, castelo_y - 60),
                (castelo_x + 60, castelo_y),
            ])
            pygame.draw.rect(Jogo.fundo_cache, (100, 100, 120), (castelo_x - 50, castelo_y + 20, 20, 40))
            pygame.draw.rect(Jogo.fundo_cache, (100, 100, 120), (castelo_x + 30, castelo_y + 20, 20, 40))
            
            for i in range(3):
                pygame.draw.circle(Jogo.fundo_cache, (150, 150, 150), 
                                 (int(castelo_x - 50 + i * 60), int(castelo_y + 30)), 5)
        
        TELA.blit(Jogo.fundo_cache, (0, 0))

    def desenhar_menu_inicial(self):
        self.desenhar_fundo_medieval()
        self.pergaminho.desenhar(TELA, self)
        self.verificar_narracao_terminou()
        self.botao_rect = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 180, 620), 240, 50)
        if self.narracao_ativa:
            cor_botao = VERMELHO_ESCURO
            texto_botao_str = "Pular Narracao"
        else:
            cor_botao = OURO
            texto_botao_str = "Iniciar Jornada"
        pygame.draw.rect(TELA, cor_botao, self.botao_rect, border_radius=10)
        texto_botao = fonte_media.render(texto_botao_str, True, PRETO)
        TELA.blit(
            texto_botao,
            (self.botao_rect.centerx - texto_botao.get_width() // 2, self.botao_rect.centery - texto_botao.get_height() // 2),
        )
        botao_ranking = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 120, 690), 240, 50)
        pygame.draw.rect(TELA, MARROM_CLARO, botao_ranking, border_radius=10)
        texto_rank = fonte_media.render("Ver Ranking", True, BRANCO)
        TELA.blit(
            texto_rank,
            (botao_ranking.centerx - texto_rank.get_width() // 2, botao_ranking.centery - texto_rank.get_height() // 2)
        )
        botao_sair = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 60, 760), 240, 50)
        pygame.draw.rect(TELA, VERMELHO, botao_sair, border_radius=10)
        texto_sair = fonte_media.render("Sair", True, BRANCO)
        TELA.blit(
            texto_sair,
            (botao_sair.centerx - texto_sair.get_width() // 2, botao_sair.centery - texto_sair.get_height() // 2)
        )

    def desenhar_selecao_personagem(self):
        self.desenhar_fundo_medieval()
        titulo = fonte_titulo.render("ESCOLHA SEU CAVALEIRO", True, DOURADO)
        for dx, dy in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            txt_sombra = fonte_titulo.render("ESCOLHA SEU CAVALEIRO", True, PRETO)
            TELA.blit(txt_sombra, (LARGURA // 2 - titulo.get_width() // 2 + dx, 40 + dy))
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 40))
        largura_painel = min(400, (LARGURA - 200) // 2)
        altura_painel = min(600, ALTURA - 250)
        espacamento = 50
        x_esquerda = LARGURA // 2 - largura_painel - espacamento // 2
        x_direita = LARGURA // 2 + espacamento // 2
        y_painel = 150
        self._desenhar_painel_selecao(x_esquerda, y_painel, largura_painel, altura_painel, 0)
        self._desenhar_painel_selecao(x_direita, y_painel, largura_painel, altura_painel, 1)
        todos_nomes_validos = all(len(nome.strip()) > 0 for nome in self.nomes_personagens)
        cor_botao = DOURADO if todos_nomes_validos else CINZA_ESCURO
        botao_iniciar = pygame.Rect(LARGURA // 2 - 150, ALTURA - 100, 300, 60)
        pygame.draw.rect(TELA, cor_botao, botao_iniciar, border_radius=15)
        pygame.draw.rect(TELA, DOURADO, botao_iniciar, 4, border_radius=15)
        texto_iniciar = fonte_grande.render("INICIAR BATALHA", True, BRANCO if todos_nomes_validos else CINZA_CLARO)
        TELA.blit(
            texto_iniciar,
            (botao_iniciar.centerx - texto_iniciar.get_width() // 2, botao_iniciar.centery - texto_iniciar.get_height() // 2),
        )
        if not todos_nomes_validos:
            aviso = fonte_pequena.render("Digite os nomes dos cavaleiros", True, VERMELHO)
            TELA.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, ALTURA - 130))

    def _desenhar_painel_selecao(self, x, y, largura, altura, idx):
        cor_padrao = self.personagens[idx].cor
        s_painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(s_painel, (40, 40, 50, 200), (0, 0, largura, altura), border_radius=20)
        TELA.blit(s_painel, (x, y))
        cor_borda = DOURADO if self.input_ativo[idx] else cor_padrao
        pygame.draw.rect(TELA, cor_borda, (x, y, largura, altura), 5, border_radius=20)
        texto_jogador = fonte_grande.render(f"JOGADOR {idx + 1}", True, cor_padrao)
        TELA.blit(texto_jogador, (x + largura // 2 - texto_jogador.get_width() // 2, y + 20))
        pos_cavaleiro_x = x + largura // 2
        pos_cavaleiro_y = y + 180
        personagem_temp = Personagem(cor_padrao, self.nomes_personagens[idx] if self.nomes_personagens[idx] else "...")
        personagem_temp.imagem_original = IMAGENS_PERSONAGENS.get(cor_padrao)
        personagem_temp.desenhar(pos_cavaleiro_x, pos_cavaleiro_y, 1.0)
        largura_input = largura - 40
        y_input = y + altura - 180
        input_rect = pygame.Rect(x + 20, y_input, largura_input, 50)
        pygame.draw.rect(TELA, BRANCO, input_rect, border_radius=5)
        pygame.draw.rect(TELA, cor_borda, input_rect, 3, border_radius=5)
        texto_input = fonte_media.render(self.nomes_personagens[idx] or "Nome do Cavaleiro", True, PRETO)
        TELA.blit(
            texto_input,
            (input_rect.x + 10, input_rect.centery - texto_input.get_height() // 2)
        )
        if self.input_ativo[idx] and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.x + 10 + (fonte_media.size(self.nomes_personagens[idx])[0] if self.nomes_personagens[idx] else 0)
            pygame.draw.line(TELA, PRETO, (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)
        
        # Desenhar teclado mobile se input estiver ativo
        if self.input_ativo[idx]:
            rects_teclas = self.teclado_mobile.desenhar(x + 20, y_input + 70, True)

    def desenhar_tabuleiro(self):
        self.desenhar_fundo_medieval()
        self.tabuleiro.desenhar()
        for i, p in enumerate(self.personagens):
            casa_pos = self.tabuleiro.casas[int(p.posicao_visual)]["centro"]
            x_offset = (-1) ** i * 15
            y_base = casa_pos[1] - 30
            p.desenhar(casa_pos[0] + x_offset, y_base, 0.7)

    def desenhar_painel(self):
        self.painel.desenhar_painel(self.personagens, self.jogador_atual, self.dado_valor, self.estado, self.tempo_inicio)

    def desenhar_desafio(self):
        D = self.desafio_atual
        if not D:
            return
        largura_painel = min(500, LARGURA - 100)
        altura_painel = min(400, ALTURA - 100)
        rect_fundo = pygame.Rect(
            LARGURA // 2 - largura_painel // 2,
            ALTURA // 2 - altura_painel // 2,
            largura_painel,
            altura_painel,
        )
        pygame.draw.rect(TELA, CINZA_ESCURO, rect_fundo, border_radius=20)
        pygame.draw.rect(TELA, DOURADO, rect_fundo, 5, border_radius=20)
        texto_titulo = fonte_grande.render(D.titulo, True, D.icone_cor)
        TELA.blit(texto_titulo, (rect_fundo.centerx - texto_titulo.get_width() // 2, rect_fundo.y + 20))
        texto_pergunta = fonte_titulo.render(D.pergunta, True, BRANCO)
        if texto_pergunta.get_width() > largura_painel - 40:
            texto_pergunta = fonte_grande.render(D.pergunta, True, BRANCO)
        TELA.blit(texto_pergunta, (rect_fundo.centerx - texto_pergunta.get_width() // 2, rect_fundo.y + 100))
        largura_input = min(200, largura_painel - 100)
        input_rect = pygame.Rect(rect_fundo.centerx - largura_input // 2, rect_fundo.y + 200, largura_input, 50)
        pygame.draw.rect(TELA, BRANCO, input_rect, border_radius=5)
        pygame.draw.rect(TELA, PRETO, input_rect, 2, border_radius=5)
        texto_resposta = fonte_media.render(self.resposta_usuario, True, PRETO)
        TELA.blit(
            texto_resposta,
            (input_rect.x + 10, input_rect.centery - texto_resposta.get_height() // 2)
        )
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.x + 10 + fonte_media.size(self.resposta_usuario)[0]
            pygame.draw.line(TELA, PRETO, (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)
        botao_responder = pygame.Rect(rect_fundo.centerx - 100, rect_fundo.y + 280, 200, 50)
        self.painel.desenhar_botao("Responder", botao_responder.x, botao_responder.y, 200, 50, VERDE)

    def desenhar_fim_jogo(self):
        self.desenhar_fundo_medieval()
        texto_vitoria = fonte_titulo.render("VITORIA", True, DOURADO)
        pos_x = LARGURA // 2
        pos_y = ALTURA // 2 - 50
        self.vencedor.desenhar(pos_x, pos_y, 1.5)
        painel_y = ALTURA // 2 + 120
        texto_vencedor = fonte_grande.render(f"Vencedor: {self.vencedor.nome}", True, self.vencedor.cor)
        TELA.blit(texto_vencedor, (LARGURA // 2 - texto_vencedor.get_width() // 2, painel_y))
        botao_menu = pygame.Rect(LARGURA // 2 - 120, ALTURA - 100, 240, 50)
        self.painel.desenhar_botao("Menu Inicial", botao_menu.x, botao_menu.y, 240, 50, MARROM_CLARO)

    def desenhar_ranking(self):
        self.desenhar_fundo_medieval()
        titulo = fonte_titulo.render("RANKING", True, DOURADO)
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 40))
        y = 150
        if not self.sistema_ranking.ranking:
            texto_vazio = fonte_media.render("Nenhuma vitoria registrada", True, BRANCO)
            TELA.blit(texto_vazio, (LARGURA // 2 - texto_vazio.get_width() // 2, y))
        else:
            for idx, vitoria in enumerate(self.sistema_ranking.ranking[:10]):
                texto = fonte_pequena.render(
                    f"{idx + 1}. {vitoria['nome']} - Tempo: {vitoria['tempo']}s - Desafios: {vitoria['desafios']}",
                    True,
                    BRANCO
                )
                TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, y))
                y += 40
        botao_voltar = pygame.Rect(LARGURA // 2 - 120, ALTURA - 100, 240, 50)
        self.painel.desenhar_botao("Voltar", botao_voltar.x, botao_voltar.y, 240, 50, MARROM_CLARO)

    def rolar_dado(self):
        if self.estado == "aguardando_dado":
            self.estado = "rolando_dado"
            self.dado_frame = 0
            self.dado_valor = 0
            tocar_som_movimento()

    def processar_rolagem_dado(self):
        if self.estado != "rolando_dado":
            return
        self.dado_frame += 1
        if self.dado_frame < 30:
            self.dado_valor = random.randint(1, 6)
        else:
            self.dado_valor = random.randint(1, 6)
            self.estado = "aguardando_movimento"

    def mover_jogador(self):
        jogador = self.personagens[self.jogador_atual]
        if self.estado == "aguardando_movimento":
            if abs(jogador.posicao_visual - jogador.posicao) < 0.1:
                if self.dado_valor > 0:
                    jogador.posicao = min(40, jogador.posicao + 1)
                    self.dado_valor -= 1
                    tocar_som_movimento()
                if self.dado_valor == 0 and abs(jogador.posicao_visual - jogador.posicao) < 0.1:
                    if jogador.posicao in self.tabuleiro.desafios:
                        self.desafio_atual = self.tabuleiro.desafios[jogador.posicao]
                        self.estado = "desafio"
                        self.resposta_usuario = ""
                    else:
                        self.proximo_jogador()
            if self.estado in ["aguardando_movimento", "rolando_dado"]:
                if self.dado_valor == 0 and jogador.posicao_visual < jogador.posicao:
                    jogador.posicao_visual += jogador.velocidade_movimento * 1.5

    def proximo_jogador(self):
        self.jogador_atual = (self.jogador_atual + 1) % len(self.personagens)
        self.estado = "aguardando_dado"

    def verificar_resposta(self):
        if not self.desafio_atual:
            return False
        try:
            resposta_int = int(self.resposta_usuario)
            if resposta_int == self.desafio_atual.resposta:
                self.mensagem = "Correto! +3 casas!"
                self.tempo_mensagem = 100
                criar_explosao_particulas(LARGURA // 2, ALTURA // 2, DOURADO, 50, "magico")
                tocar_som_sucesso()
                jogador = self.personagens[self.jogador_atual]
                jogador.desafios_completados += 1
                if self.desafio_atual.posicao_casa == 40:
                    self.vencedor = jogador
                    jogador.iniciar_danca()
                    self.sistema_ranking.adicionar_vitoria(jogador.nome, jogador.cor, jogador.desafios_completados, pygame.time.get_ticks() // 1000 - self.tempo_inicio)
                    tocar_som_vitoria()
                    self.estado = "fim_jogo"
                else:
                    jogador.posicao = min(40, jogador.posicao + 3)
                    self.proximo_jogador()
            else:
                self.mensagem = "Errado! -2 casas!"
                self.tempo_mensagem = 100
                tocar_som_erro()
                jogador = self.personagens[self.jogador_atual]
                jogador.posicao = max(0, jogador.posicao - 2)
                self.proximo_jogador()
            self.desafio_atual = None
        except ValueError:
            self.mensagem = "Resposta invalida."
            self.tempo_mensagem = 50

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.popup_sair.mostrar()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                x, y = evento.pos
                # Processar cliques no popup de sair
                if self.popup_sair.ativo:
                    if self.popup_sair.confirmacao_rect and self.popup_sair.confirmacao_rect.collidepoint(evento.pos):
                        pygame.quit()
                        sys.exit()
                    elif self.popup_sair.cancelamento_rect and self.popup_sair.cancelamento_rect.collidepoint(evento.pos):
                        self.popup_sair.fechar()
                    continue
                
                if self.estado == "menu_inicial":
                    botao_rect = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 180, 620), 240, 50)
                    if botao_rect.collidepoint(evento.pos):
                        if self.narracao_ativa:
                            pygame.mixer.music.set_volume(self.volume_musica_original)
                            self.narracao_ativa = False
                            pygame.mixer.stop()
                        self.iniciar_transicao("selecao_personagem")
                    botao_ranking = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 120, 690), 240, 50)
                    if botao_ranking.collidepoint(evento.pos):
                        self.iniciar_transicao("ranking")
                    botao_sair = pygame.Rect(LARGURA // 2 - 120, min(ALTURA - 60, 760), 240, 50)
                    if botao_sair.collidepoint(evento.pos):
                        self.popup_sair.mostrar()
                elif self.estado == "selecao_personagem":
                    largura_painel = min(400, (LARGURA - 200) // 2)
                    altura_painel = min(600, ALTURA - 250)
                    espacamento = 50
                    x_esquerda = LARGURA // 2 - largura_painel - espacamento // 2
                    x_direita = LARGURA // 2 + espacamento // 2
                    y_painel = 150
                    largura_input = largura_painel - 40
                    y_input = y_painel + altura_painel - 180
                    input_rect_1 = pygame.Rect(x_esquerda + 20, y_input, largura_input, 50)
                    input_rect_2 = pygame.Rect(x_direita + 20, y_input, largura_input, 50)
                    
                    # Verificar cliques no teclado mobile
                    rects_teclas_1 = None
                    rects_teclas_2 = None
                    if self.input_ativo[0]:
                        rects_teclas_1 = self.teclado_mobile.desenhar(x_esquerda + 20, y_input + 70, True)
                    if self.input_ativo[1]:
                        rects_teclas_2 = self.teclado_mobile.desenhar(x_direita + 20, y_input + 70, True)
                    
                    # Processar cliques nas teclas
                    if rects_teclas_1:
                        for rect, tecla in rects_teclas_1:
                            if rect.collidepoint(evento.pos):
                                if tecla == '⌫':
                                    self.nomes_personagens[0] = self.nomes_personagens[0][:-1]
                                else:
                                    if len(self.nomes_personagens[0]) < 15:
                                        self.nomes_personagens[0] += tecla.lower()
                                break
                    
                    if rects_teclas_2:
                        for rect, tecla in rects_teclas_2:
                            if rect.collidepoint(evento.pos):
                                if tecla == '⌫':
                                    self.nomes_personagens[1] = self.nomes_personagens[1][:-1]
                                else:
                                    if len(self.nomes_personagens[1]) < 15:
                                        self.nomes_personagens[1] += tecla.lower()
                                break
                    
                    # Cliques nos inputs
                    self.input_ativo[0] = input_rect_1.collidepoint(evento.pos)
                    self.input_ativo[1] = input_rect_2.collidepoint(evento.pos)
                    if self.input_ativo[0] and self.input_ativo[1]:
                        if input_rect_1.collidepoint(evento.pos):
                            self.input_ativo[1] = False
                        else:
                            self.input_ativo[0] = False
                    todos_nomes_validos = all(len(nome.strip()) > 0 for nome in self.nomes_personagens)
                    botao_iniciar = pygame.Rect(LARGURA // 2 - 150, ALTURA - 100, 300, 60)
                    if botao_iniciar.collidepoint(evento.pos) and todos_nomes_validos:
                        self.personagens[0].nome = self.nomes_personagens[0].strip()
                        self.personagens[1].nome = self.nomes_personagens[1].strip()
                        self.iniciar_transicao("aguardando_dado")
                elif self.estado == "aguardando_dado":
                    largura_painel = min(400, LARGURA // 4)
                    y_botao = ALTURA - 80
                    x_botao = LARGURA - largura_painel + 20
                    rect_dado = pygame.Rect(x_botao, y_botao, largura_painel - 40, 50)
                    if rect_dado.collidepoint(evento.pos):
                        self.rolar_dado()
                elif self.estado == "aguardando_movimento":
                    largura_painel = min(400, LARGURA // 4)
                    y_botao = ALTURA - 80
                    x_botao = LARGURA - largura_painel + 20
                    rect_mover = pygame.Rect(x_botao, y_botao, largura_painel - 40, 50)
                    if rect_mover.collidepoint(evento.pos):
                        self.mover_jogador()
                elif self.estado == "desafio":
                    largura_painel = min(500, LARGURA - 100)
                    altura_painel = min(400, ALTURA - 100)
                    rect_fundo = pygame.Rect(
                        LARGURA // 2 - largura_painel // 2, ALTURA // 2 - altura_painel // 2, largura_painel, altura_painel
                    )
                    botao_responder = pygame.Rect(rect_fundo.centerx - 100, rect_fundo.y + 280, 200, 50)
                    if botao_responder.collidepoint(evento.pos):
                        self.verificar_resposta()
                elif self.estado == "fim_jogo":
                    botao_menu = pygame.Rect(LARGURA // 2 - 120, ALTURA - 100, 240, 50)
                    if botao_menu.collidepoint(evento.pos):
                        self.__init__()
                        self.estado = "menu_inicial"
                elif self.estado == "ranking":
                    botao_voltar = pygame.Rect(LARGURA // 2 - 120, ALTURA - 100, 240, 50)
                    if botao_voltar.collidepoint(evento.pos):
                        self.iniciar_transicao("menu_inicial")
            if evento.type == pygame.KEYDOWN:
                if self.estado == "selecao_personagem":
                    idx_ativo = -1
                    if self.input_ativo[0]:
                        idx_ativo = 0
                    elif self.input_ativo[1]:
                        idx_ativo = 1
                    if idx_ativo != -1:
                        if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                            if idx_ativo == 0:
                                self.input_ativo[0] = False
                                self.input_ativo[1] = True
                            elif idx_ativo == 1 and all(len(n.strip()) > 0 for n in self.nomes_personagens):
                                self.personagens[0].nome = self.nomes_personagens[0].strip()
                                self.personagens[1].nome = self.nomes_personagens[1].strip()
                                self.iniciar_transicao("aguardando_dado")
                        elif evento.key == pygame.K_BACKSPACE:
                            self.nomes_personagens[idx_ativo] = self.nomes_personagens[idx_ativo][:-1]
                        elif evento.unicode.isalnum() or evento.unicode.isspace():
                            if len(self.nomes_personagens[idx_ativo]) < 15:
                                self.nomes_personagens[idx_ativo] += evento.unicode
                elif self.estado == "desafio":
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                        self.verificar_resposta()
                    elif evento.key == pygame.K_BACKSPACE:
                        self.resposta_usuario = self.resposta_usuario[:-1]
                    elif evento.unicode.isdigit() or (evento.unicode == "-" and len(self.resposta_usuario) == 0):
                        if len(self.resposta_usuario) < 10:
                            self.resposta_usuario += evento.unicode

    async def executar(self):
        while True:
            self.processar_eventos()
            if self.estado == "fade_in":
                TELA.fill((0, 0, 0))
                self.desenhar_fade_in()
            elif self.estado == "menu_inicial":
                self.desenhar_menu_inicial()
            elif self.estado == "selecao_personagem":
                self.desenhar_selecao_personagem()
            elif self.estado == "ranking":
                self.desenhar_ranking()
            elif self.estado == "fim_jogo":
                self.desenhar_fim_jogo()
            elif self.estado == "desafio":
                self.desenhar_tabuleiro()
                self.desenhar_painel()
                self.desenhar_desafio()
                atualizar_particulas()
                desenhar_particulas()
            else:
                self.desenhar_tabuleiro()
                self.processar_rolagem_dado()
                self.mover_jogador()
                self.desenhar_painel()
                atualizar_particulas()
                desenhar_particulas()
            self.desenhar_transicao()
            self.popup_sair.desenhar(TELA)
            pygame.display.flip()
            await asyncio.sleep(0)

if __name__ == "__main__":
    if not os.path.exists("som"):
        os.makedirs("som")
    try:
        jogo = Jogo()
        asyncio.run(jogo.executar())
    except Exception as e:
        print(f"Erro na execucao do jogo: {e}")
    finally:
        pygame.quit()
