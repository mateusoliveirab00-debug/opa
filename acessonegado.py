#!/usr/bin/env python3
"""
Acesso Negado — animação de perfil estilo cinema de cyber security.

Sequência:
  1) terminal tenta acessar o perfil -> "ACESSO NEGADO" (com glitch)
     "visitante não identificado. o que você faz aqui?"
  2) "invasão" simulada (só visual): logs + barra de progresso
  3) "ACESSO CONCEDIDO" -> cartão profissional com o seu perfil
Com LOOP = True (padrão) o GIF repete; com LOOP = False toca uma vez e para no cartão.

Requisitos: pip install pillow
Uso:        python acessonegado.py   ->  gera acessonegado.gif
Personalize na seção CONFIG logo abaixo.
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFont

# ======================= CONFIG =======================
USUARIO = "mt.vky_"
NOME = "MR. OLIVEIRA"
LINHAS = [  # (texto, cor RGB)
    ("Engenharia da Computação", (110, 220, 255)),
    ("Cyber Security", (255, 90, 120)),
    ("Futuro Engenheiro de Dados", (255, 205, 90)),
]
TAGS_VERDES = ["Python", "Segurança", "Dados"]
TAG_TIME = "Flamengo"  # use None para remover
SAIDA = "acessonegado.gif"
LOOP = True  # True = repete para sempre | False = toca uma vez e para no cartão
# ======================================================

W, H = 640, 400
MS = 50  # duração de cada quadro (ms)

BG = (3, 9, 7)
GREEN = (0, 255, 120)
DIM = (0, 150, 80)
RED = (255, 60, 80)
WHITE = (235, 245, 235)

S1, S2 = 66, 78
S3 = 100 if LOOP else 92  # quadros da última cena (com loop, termina em fade-out)


# ---------------------------- fontes ----------------------------
def _font(size, bold=False):
    regular = [
        "DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    heavy = [
        "DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/courbd.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for p in (heavy if bold else regular):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


F = _font(18)
F20 = _font(20)
FS = _font(14)
FXS = _font(12)
FB = _font(40, bold=True)
FT = _font(16)


# ---------------------------- utilidades ----------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def center(d, text, y, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)


def put(d, x, y, text, start, cps, t, font, fill):
    """Escreve `text` como máquina de escrever. Devolve posição do cursor."""
    if t < start:
        return None
    n = min(len(text), int((t - start + 1) * cps))
    s = text[:n]
    d.text((x, y), s, font=font, fill=fill)
    return (x + d.textlength(s, font=font), y, fill, font)


def draw_cursor(d, cur, t):
    if not cur or (t // 3) % 2:
        return
    x, y, fill, font = cur
    size = getattr(font, "size", 18)
    d.rectangle((x + 2, y + 2, x + 2 + size * 0.55, y + size * 1.15), fill=fill)


def make_base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 32):
        d.line((x, 30, x, H), fill=(5, 20, 14))
    for y in range(30, H, 32):
        d.line((0, y, W, y), fill=(5, 20, 14))
    d.rectangle((0, 0, W, 30), fill=(10, 28, 21))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((12 + i * 22, 9, 24 + i * 22, 21), fill=c)
    title = "visitante@perfil: ~"
    d.text(((W - d.textlength(title, font=FS)) / 2, 8), title, font=FS, fill=DIM)
    return img


BASE = make_base()

_scan = Image.new("RGB", (W, H), (255, 255, 255))
_sd = ImageDraw.Draw(_scan)
for _y in range(0, H, 3):
    _sd.line((0, _y, W, _y), fill=(205, 205, 205))
SCAN = _scan


def glitch(img, rng, level):
    """Fatias deslocadas + separação RGB."""
    if level <= 0:
        return img
    out = img.copy()
    for _ in range(max(1, int(7 * level))):
        y = rng.randrange(32, H - 24)
        hh = rng.randrange(4, 26)
        dx = rng.randrange(-46, 46)
        band = img.crop((0, y, W, min(H, y + hh)))
        out.paste(band, (dx, y))
    r, g, b = out.split()
    s = max(1, int(5 * level))
    r = ImageChops.offset(r, s, 0)
    b = ImageChops.offset(b, -s, 0)
    return Image.merge("RGB", (r, g, b))


# ---------------------------- cena 1: acesso negado ----------------------------
def scene1(d, t):
    cur = put(d, 24, 52, "$ acessar --perfil @" + USUARIO, 1, 1.7, t, F, GREEN)
    c = put(d, 24, 80, "> verificando credenciais...", 20, 2.4, t, F, DIM)
    cur = c or cur
    if t >= 34:
        on = t < 46 or (t // 3) % 2 == 0
        edge = RED if on else (110, 25, 40)
        d.rectangle((70, 108, W - 70, 190), fill=(36, 0, 8) if on else (18, 0, 4),
                    outline=edge, width=3)
        center(d, "ACESSO NEGADO", 114, FB, RED if on else (150, 35, 55))
        center(d, "ERRO 403 - área restrita", 168, FS, (255, 140, 150))
    c = put(d, 24, 212, "> visitante não identificado.", 42, 2.0, t, F, RED)
    cur = c or cur
    c = put(d, 24, 240, "> o que você faz aqui?", 52, 2.4, t, F, RED)
    cur = c or cur
    draw_cursor(d, cur, t)


def level1(t, rng):
    if 34 <= t <= 41:
        return 1.0
    if 20 <= t < 34:
        return 0.3 if rng.random() < 0.15 else 0
    if t >= 42:
        return 0.45 if rng.random() < 0.25 else 0
    return 0


# ---------------------------- cena 2: bypass simulado ----------------------------
LOGS = [
    "[*] escaneando portas...",
    "[*] contornando firewall...",
    "[*] ignorando autenticação...",
    "[*] elevando privilégios...",
]
LOG_START = [16, 28, 40, 52]


def scene2(d, t, rng):
    cur = put(d, 24, 52, "$ sudo ./bypass --alvo perfil", 1, 2.0, t, F, GREEN)
    for i, (txt, s0) in enumerate(zip(LOGS, LOG_START)):
        y = 80 + 28 * i
        c = put(d, 24, y, txt, s0, 3.0, t, F, WHITE)
        if c:
            cur = c
            if t >= s0 + len(txt) / 3.0 + 2:
                d.text((c[0] + 10, y), "[ OK ]", font=F, fill=GREEN)

    # colunas de "dump" hexadecimal
    if 14 <= t < 62:
        r2 = random.Random(500 + t // 2)
        for i in range(13):
            line = " ".join("%02x" % r2.randrange(256) for _ in range(5))
            d.text((440, 52 + i * 15), line, font=FXS, fill=(0, 100, 58))

    p = clamp((t - 14) / 46)
    p = p * p * (3 - 2 * p)  # ease
    d.text((24, 262), "progresso", font=FS, fill=DIM)
    pct = "%d%%" % int(p * 100)
    d.text((W - 24 - d.textlength(pct, font=FS), 262), pct, font=FS, fill=GREEN)
    d.rectangle((24, 284, W - 24, 306), outline=GREEN, width=2)
    blocks = int(p * 58)
    for i in range(blocks):
        d.rectangle((29 + i * 10, 289, 29 + i * 10 + 7, 301), fill=GREEN)

    c = put(d, 24, 196, "[+] acesso root obtido", 62, 3.0, t, F, GREEN)
    cur = c or cur
    c = put(d, 24, 224, "> carregando perfil...", 68, 3.0, t, F, DIM)
    cur = c or cur
    draw_cursor(d, cur, t)


def level2(t, rng):
    if 62 <= t <= 63:
        return 0.8
    return 0.4 if rng.random() < 0.10 else 0


# ---------------------------- cena 3: acesso concedido + cartão ----------------------------
def shield(d, cx, cy, s, width, fill):
    pts = [(cx, cy - s), (cx + 0.82 * s, cy - 0.6 * s), (cx + 0.82 * s, cy + 0.1 * s),
           (cx, cy + s), (cx - 0.82 * s, cy + 0.1 * s), (cx - 0.82 * s, cy - 0.6 * s)]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=GREEN, width=width, joint="curve")


def initials(nome):
    parts = [p for p in nome.replace(".", "").split() if p]
    letters = "".join(p[0] for p in parts[:2]).upper()
    return letters or "?"


def scene3(d, t):
    if t < 16:
        on = t < 8 or (t // 3) % 2 == 0
        d.rectangle((50, 146, W - 50, 254), fill=(0, 34, 18),
                    outline=GREEN if on else DIM, width=3)
        center(d, "ACESSO CONCEDIDO", 160, FB, GREEN if on else DIM)
        center(d, "bem-vindo ao perfil", 216, F, WHITE)
        return

    # anel pulsando em volta do escudo
    cx, cy = 104, 206
    ph = ((t - 16) % 22) / 22.0
    rad = 66 + ph * 26
    g = int(150 * (1 - ph))
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=(0, g, int(g * 0.5)), width=2)
    shield(d, cx, cy, 62, 3, (4, 32, 20))
    ini = initials(NOME)
    d.text((cx - d.textlength(ini, font=FB) / 2, cy - 24), ini, font=FB, fill=GREEN)

    x0 = 206
    cur = put(d, x0, 104, NOME, 18, 1.0, t, FB, WHITE)
    c = put(d, x0, 156, "@" + USUARIO, 30, 1.3, t, F20, DIM)
    cur = c or cur

    if t >= 34:
        prog = clamp((t - 34) / 10)
        d.line((x0, 194, x0 + (W - 28 - x0) * prog, 194), fill=GREEN, width=2)

    starts = [44, 56, 68]
    for i, ((txt, col), s0) in enumerate(zip(LINHAS, starts)):
        c = put(d, x0, 210 + 28 * i, "> " + txt, s0, 2.2, t, F20, col)
        cur = c or cur

    # tags
    tags = [(tx, GREEN) for tx in TAGS_VERDES]
    if TAG_TIME:
        tags.append((TAG_TIME, RED))
    x = x0
    for i, (tx, col) in enumerate(tags):
        w = d.textlength(tx, font=FT) + 20
        if t >= 78 + 3 * i:
            d.rounded_rectangle((x, 316, x + w, 340), radius=6, outline=col, width=2)
            d.text((x + 10, 320), tx, font=FT, fill=col)
        x += w + 10

    draw_cursor(d, cur if t < 80 else None, t)


def level3(t, rng):
    if t >= S3 - 4:  # últimos quadros limpos, sem glitch
        return 0
    if t < 8:
        return 1.0 - t * 0.08
    if t < 16:
        return 0.4 if rng.random() < 0.4 else 0
    if t in (16, 17):
        return 0.8
    return 0.3 if rng.random() < 0.04 else 0


# ---------------------------- render ----------------------------
def render_frame(f):
    rng = random.Random(1000 + f)
    if f < S1:
        sc, t = 1, f
    elif f < S1 + S2:
        sc, t = 2, f - S1
    else:
        sc, t = 3, f - S1 - S2

    img = BASE.copy()
    d = ImageDraw.Draw(img)
    if sc == 1:
        scene1(d, t)
        lvl = level1(t, rng)
    elif sc == 2:
        scene2(d, t, rng)
        lvl = level2(t, rng)
    else:
        scene3(d, t)
        lvl = level3(t, rng)

    img = glitch(img, rng, lvl)
    img = ImageChops.multiply(img, SCAN)

    # faixa de varredura (CRT)
    band_y = (f * 7) % (H + 60) - 30
    band = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, band_y, W, band_y + 34), fill=(0, 7, 4))
    img = ImageChops.add(img, band)

    if sc == 3 and t in (0, 1):  # flash
        flash = Image.new("RGB", (W, H), (170, 255, 205))
        img = Image.blend(img, flash, 0.32 if t == 0 else 0.14)
    if LOOP and sc == 3 and t >= 94:  # fade-out para fechar o loop suavemente
        img = Image.blend(img, Image.new("RGB", (W, H), BG), clamp((t - 93) / 7))
    return img


def build_palette(frames, colors=200):
    step = max(1, len(frames) // 16)
    samples = [fr.resize((320, 200)) for fr in frames[::step]]
    # amostra extra com as cores de texto (e seus tons de suavização) para
    # que ciano/amarelo/vermelho não percam o brilho na paleta do GIF
    cores = [c for _, c in LINHAS] + [RED, GREEN, DIM, WHITE, (255, 140, 150)]
    swatch = Image.new("RGB", (320, 200), BG)
    sd = ImageDraw.Draw(swatch)
    rh = 200 // len(cores)
    for i, col in enumerate(cores):
        for j in range(8):
            mix = tuple(int(BG[k] + (col[k] - BG[k]) * (j + 1) / 8) for k in range(3))
            sd.rectangle((j * 40, i * rh, j * 40 + 39, i * rh + rh - 1), fill=mix)
    samples.append(swatch)
    samples.append(swatch)
    sheet = Image.new("RGB", (320, 200 * len(samples)))
    for i, s in enumerate(samples):
        sheet.paste(s, (0, 200 * i))
    return sheet.quantize(colors=colors, method=0)  # 0 = median cut


def main():
    total = S1 + S2 + S3
    rgb = [render_frame(f) for f in range(total)]
    pal = build_palette(rgb)
    frames = [fr.quantize(palette=pal, dither=0) for fr in rgb]
    opcoes = {"duration": MS, "disposal": 1}
    if LOOP:
        opcoes["loop"] = 0  # 0 = infinito; sem o parâmetro, toca uma vez e para
    frames[0].save(SAIDA, save_all=True, append_images=frames[1:], **opcoes)
    print("Gerado:", SAIDA, "(%d quadros)" % total)


if __name__ == "__main__":
    main()
