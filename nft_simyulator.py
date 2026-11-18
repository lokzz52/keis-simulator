import pygame
import random
import sys
import math
import array
import os

pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    AUDIO_OK = True
except:
    AUDIO_OK = False

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NFT Case Simulator v10 — Fixed")
clock = pygame.time.Clock()

# ============ ЦВЕТА ============
BG = (14, 14, 22)
PANEL = (28, 28, 42)
PANEL_LIGHT = (44, 44, 62)
ACCENT = (120, 80, 255)
GOLD = (255, 200, 50)
GREEN = (80, 220, 120)
RED = (240, 80, 80)
WHITE = (240, 240, 255)
GRAY = (120, 120, 140)

FONT_HUGE = pygame.font.SysFont("arial", 64, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 42, bold=True)
FONT_MED = pygame.font.SysFont("arial", 24, bold=True)
FONT = pygame.font.SysFont("arial", 19)
FONT_SMALL = pygame.font.SysFont("arial", 15)

# ============ ЗАГРУЗКА КАРТИНОК ============
if not os.path.exists("assets"):
    os.makedirs("assets")

def load_nft_image(name):
    exts = [".png", ".jpg", ".jpeg"]
    for ext in exts:
        path = os.path.join("assets", name + ext)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, (256, 256))
            except Exception as e:
                print(f"Ошибка загрузки {path}: {e}")
    return None

# ============ ГЕНЕРАЦИЯ ЗВУКОВ ============
def make_sound(freq, duration=0.2, volume=0.3, wave='sine', fade_out=True):
    if not AUDIO_OK: return None
    try:
        sample_rate = 44100
        n = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n):
            t = i / sample_rate
            if wave == 'sine':
                val = math.sin(2 * math.pi * freq * t)
            elif wave == 'triangle':
                val = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
            elif wave == 'noise':
                val = random.uniform(-1, 1) * 0.5
            else:
                val = math.sin(2 * math.pi * freq * t)
            env = (1.0 - (i / n)) ** 2 if fade_out else 1.0
            buf.append(int(val * env * volume * 32767))
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except:
        return None

SND_TICK = make_sound(800, 0.05, 0.1, 'sine')
SND_CLICK = make_sound(600, 0.08, 0.15, 'sine')
SND_UPGRADE_START = make_sound(300, 0.5, 0.25, 'sine')
SND_OPEN_CASE = make_sound(200, 0.6, 0.2, 'noise')
SND_WIN_COMMON = make_sound(440, 0.3, 0.25, 'sine')
SND_WIN_RARE = make_sound(523, 0.4, 0.3, 'sine')
SND_WIN_EPIC = make_sound(659, 0.5, 0.35, 'sine')
SND_WIN_LEGENDARY = make_sound(784, 0.6, 0.4, 'sine')
SND_FAIL = make_sound(150, 0.4, 0.3, 'triangle')

WIN_SOUNDS = {
    "Common": SND_WIN_COMMON, "Uncommon": SND_WIN_COMMON,
    "Rare": SND_WIN_RARE, "Epic": SND_WIN_EPIC,
    "Legendary": SND_WIN_LEGENDARY, "Mythic": SND_WIN_LEGENDARY,
    "Colossal": SND_WIN_LEGENDARY,
}

def play(snd):
    if snd:
        try: snd.play()
        except: pass

# ============ РЕДКОСТИ И ПУЛ ============
RARITY_COLORS = {
    "Common": (150, 150, 170), "Uncommon": (80, 220, 120),
    "Rare": (80, 150, 255), "Epic": (180, 80, 255),
    "Legendary": (255, 180, 50), "Mythic": (255, 60, 120),
    "Colossal": (255, 40, 40),
}

NFT_POOL = [
    ("Golden Ape #0427", "Legendary", 2500), ("Nebula Karambit", "Mythic", 5000),
    ("Cool Cat #1337", "Rare", 180), ("Dragon's Breath AK-47", "Colossal", 10000),
    ("Crystal King", "Mythic", 6000), ("Penguin Boss", "Rare", 220),
    ("Frostbite AWP", "Epic", 750), ("Alien #777", "Uncommon", 60),
    ("Royal Gloves", "Legendary", 3200), ("Street Girl #0089", "Epic", 600),
    ("Butterfly", "Rare", 200), ("Nike Airforce 1", "Uncommon", 70),
    ("Cyber Samurai", "Epic", 800), ("Floating Castle", "Rare", 250),
    ("Bitcoin", "Legendary", 4000), ("Lamborghini Huracan", "Colossal", 12000),
    ("Skeleton King", "Mythic", 5500), ("Spectrum Butterfly", "Epic", 700),
    ("Polar Bear #3141", "Rare", 210), ("Space Traveler", "Uncommon", 55),
]

NFT_IMAGES = {}
print("Загрузка картинок...")
for name, _, _ in NFT_POOL:
    img = load_nft_image(name)
    if img: NFT_IMAGES[name] = img

CASES = [
    {"name": "Common Case", "price": 100, "weights": {"Common": 50, "Uncommon": 30, "Rare": 15, "Epic": 4, "Legendary": 1}},
    {"name": "Rare Case", "price": 500, "weights": {"Common": 10, "Uncommon": 35, "Rare": 35, "Epic": 15, "Legendary": 4, "Mythic": 1}},
    {"name": "Legendary Case", "price": 2000, "weights": {"Uncommon": 5, "Rare": 25, "Epic": 40, "Legendary": 20, "Mythic": 8, "Colossal": 2}},
]

TAP_LEVELS = [(500, 1.5), (2000, 2.5), (8000, 5.0), (30000, 10.0), (100000, 25.0)]

def ease_out_quart(t): return 1 - pow(1 - t, 4)
def fmt_money(v):
    if abs(v - round(v)) < 0.01: return f"{int(round(v))}"
    return f"{v:.1f}"

# ============ КЛАССЫ ============
class NFT:
    def __init__(self, name, rarity, price):
        self.name = name; self.rarity = rarity; self.price = price
        self.color = RARITY_COLORS[rarity]
        self.image = NFT_IMAGES.get(name)

    def draw_icon(self, surface, x, y, size, glow=False):
        if glow:
            gs = pygame.Surface((size + 80, size + 80), pygame.SRCALPHA)
            for i in range(25, 0, -1):
                a = int(20 * (1 - i / 25) + 6)
                pygame.draw.rect(gs, (*self.color, a), (40 - i, 40 - i, size + i * 2, size + i * 2), border_radius=20)
            surface.blit(gs, (x - 40, y - 40))
            
        if self.image:
            img = pygame.transform.smoothscale(self.image, (size, size))
            surface.blit(img, (x, y))
            pygame.draw.rect(surface, self.color, (x, y, size, size), 3, border_radius=14)
        else:
            pygame.draw.rect(surface, self.color, (x, y, size, size), border_radius=14)
            inner = tuple(max(0, c - 70) for c in self.color)
            pygame.draw.rect(surface, inner, (x + 7, y + 7, size - 14, size - 14), border_radius=10)
            cx, cy = x + size // 2, y + size // 2
            letter = FONT_MED.render(self.name[0], True, WHITE)
            surface.blit(letter, (cx - letter.get_width() // 2, cy - letter.get_height() // 2))

class Player:
    def __init__(self):
        self.money = 1000.0; self.inventory = []
        self.tap_level = 0; self.coins_per_click = 1.0; self.total_taps = 0

    def add_nft(self, nft): self.inventory.append(nft)
    def sell_nft(self, index):
        nft = self.inventory.pop(index)
        self.money += nft.price
        return nft
    def tap(self):
        self.money += self.coins_per_click; self.total_taps += 1
    def can_upgrade_tap(self): return self.tap_level < len(TAP_LEVELS)
    def get_tap_upgrade_info(self): return TAP_LEVELS[self.tap_level] if self.can_upgrade_tap() else None
    def upgrade_tap(self):
        if not self.can_upgrade_tap(): return False
        price, new_rate = TAP_LEVELS[self.tap_level]
        if self.money < price: return False
        self.money -= price; self.tap_level += 1; self.coins_per_click = new_rate
        return True

class Button:
    def __init__(self, x, y, w, h, text, color=PANEL_LIGHT, hover=ACCENT, font=FONT):
        self.rect = pygame.Rect(x, y, w, h); self.text = text
        self.color = color; self.hover = hover; self.font = font; self.disabled = False

    def draw(self, surface, mouse_pos):
        color = self.hover if self.rect.collidepoint(mouse_pos) and not self.disabled else self.color
        if self.disabled: color = (60, 60, 70)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, ACCENT if not self.disabled else GRAY, self.rect, 2, border_radius=10)
        txt = self.font.render(self.text, True, WHITE if not self.disabled else GRAY)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def clicked(self, pos): return self.rect.collidepoint(pos) and not self.disabled

class Particle:
    def __init__(self, x, y, color, upward=False):
        self.x, self.y = x, y
        angle = random.uniform(0, math.tau); speed = random.uniform(2, 10)
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed - (4 if not upward else 6)
        self.life = random.randint(50, 110); self.max_life = self.life
        self.color = color; self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.3; self.vx *= 0.99; self.life -= 1
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

class FloatingText:
    def __init__(self, x, y, text, color=GOLD):
        self.x, self.y = x, y; self.text = text; self.color = color; self.life = 60; self.max_life = 60
    def update(self):
        self.y -= 1.5; self.life -= 1
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            txt = FONT_MED.render(self.text, True, self.color)
            surf = pygame.Surface((txt.get_width(), txt.get_height()), pygame.SRCALPHA)
            surf.blit(txt, (0, 0)); surf.set_alpha(alpha)
            surface.blit(surf, (self.x - txt.get_width() // 2, self.y))

class Roulette:
    ITEM_W = 170; ITEM_H = 210; SPACING = 195
    def __init__(self, items, winner, winner_index, duration=210):
        self.items = items; self.winner = winner; self.duration = duration
        self.timer = 0; self.scroll = 0.0; self.finished = False
        self.winner_idx = winner_index
        self.final_scroll = self.winner_idx * self.SPACING + random.uniform(-40, 40)
        self.center_x = WIDTH // 2; self.window_y = 260; self.window_h = self.ITEM_H + 60
        self.bg_surf = pygame.Surface((WIDTH, self.window_h), pygame.SRCALPHA)
        for i in range(self.window_h):
            t = i / self.window_h
            c = (int(20 + 10 * t), int(18 + 8 * t), int(32 + 18 * t))
            pygame.draw.line(self.bg_surf, c, (0, i), (WIDTH, i))
        self.last_tick_idx = -1; self.particles = []

    def update(self):
        if not self.finished:
            self.timer += 1
            if self.timer >= self.duration:
                self.scroll = self.final_scroll; self.finished = True; self._on_finish()
            else:
                t = self.timer / self.duration
                self.scroll = self.final_scroll * ease_out_quart(t)
            cur_idx = int(round(self.scroll / self.SPACING))
            if cur_idx != self.last_tick_idx:
                self.last_tick_idx = cur_idx
                if self.timer < self.duration * 0.85: play(SND_TICK)
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def _on_finish(self):
        play(WIN_SOUNDS.get(self.winner.rarity, SND_WIN_COMMON))
        cx = WIDTH // 2; cy = self.window_y + self.window_h // 2
        count = 100 if self.winner.rarity in ("Legendary", "Mythic", "Colossal") else 50
        for _ in range(count): self.particles.append(Particle(cx, cy, self.winner.color))

    def draw(self, surface):
        title = FONT_BIG.render("Открытие кейса...", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))
        pygame.draw.rect(surface, PANEL, (0, self.window_y - 5, WIDTH, self.window_h + 10))
        surface.blit(self.bg_surf, (0, self.window_y))
        pygame.draw.rect(surface, ACCENT, (0, self.window_y - 5, WIDTH, self.window_h + 10), 3)
        clip_rect = pygame.Rect(0, self.window_y, WIDTH, self.window_h)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        for i, nft in enumerate(self.items):
            ix = self.center_x + i * self.SPACING - self.scroll - self.ITEM_W // 2
            iy = self.window_y + (self.window_h - self.ITEM_H) // 2
            if -self.ITEM_W < ix < WIDTH + self.ITEM_W:
                card = pygame.Rect(int(ix) - 10, iy - 10, self.ITEM_W + 20, self.ITEM_H + 20)
                pygame.draw.rect(surface, PANEL, card, border_radius=14)
                pygame.draw.rect(surface, nft.color, card, 2, border_radius=14)
                nft.draw_icon(surface, int(ix + self.ITEM_W // 2 - 55), iy + 10, 110)
                nm = FONT_SMALL.render(nft.name[:16], True, WHITE)
                surface.blit(nm, (ix + self.ITEM_W // 2 - nm.get_width() // 2, iy + 135))
                rar = FONT_SMALL.render(nft.rarity, True, nft.color)
                surface.blit(rar, (ix + self.ITEM_W // 2 - rar.get_width() // 2, iy + 158))
                pr = FONT.render(f"${nft.price}", True, GOLD)
                surface.blit(pr, (ix + self.ITEM_W // 2 - pr.get_width() // 2, iy + 178))
        surface.set_clip(old_clip)
        for i in range(120):
            alpha = int(255 * (1 - i / 120))
            edge = pygame.Surface((1, self.window_h), pygame.SRCALPHA)
            edge.fill((*BG, alpha))
            surface.blit(edge, (i, self.window_y))
            surface.blit(edge, (WIDTH - 1 - i, self.window_y))
        cx = WIDTH // 2
        pygame.draw.polygon(surface, GOLD, [(cx - 15, self.window_y - 25), (cx + 15, self.window_y - 25), (cx, self.window_y + 5)])
        pygame.draw.polygon(surface, GOLD, [(cx - 15, self.window_y + self.window_h + 25), (cx + 15, self.window_y + self.window_h + 25), (cx, self.window_y + self.window_h - 5)])
        pygame.draw.line(surface, GOLD, (cx, self.window_y), (cx, self.window_y + self.window_h), 2)
        if self.finished:
            wy = self.window_y + self.window_h // 2
            glow = pygame.Surface((300, 300), pygame.SRCALPHA)
            for r in range(150, 0, -5):
                a = int(40 * (1 - r / 150))
                pygame.draw.circle(glow, (*self.winner.color, a), (150, 150), r)
            surface.blit(glow, (cx - 150, wy - 150), special_flags=pygame.BLEND_ADD)
        for p in self.particles: p.draw(surface)

class UpgradeWheel:
    def __init__(self, success, chance):
        self.success = success; self.chance = chance
        self.timer = 0; self.duration = 150; self.finished = False
        success_deg = self.chance * 360
        if success: target_deg = random.uniform(success_deg * 0.1, success_deg * 0.9)
        else: target_deg = random.uniform(success_deg + 10, 360 - 10)
        self.start_angle = -90.0
        self.final_angle = self.start_angle + 360 * 4 + target_deg
        self.angle = self.start_angle

    def update(self):
        if self.finished: return
        self.timer += 1
        if self.timer >= self.duration:
            self.angle = self.final_angle; self.finished = True
        else:
            t = self.timer / self.duration
            eased = 1 - pow(1 - t, 4)
            self.angle = self.start_angle + (self.final_angle - self.start_angle) * eased

    def _draw_sector(self, surface, cx, cy, radius, start_rad, end_rad, color):
        if end_rad <= start_rad: end_rad += math.tau
        points = [(cx, cy)]
        steps = max(8, int((end_rad - start_rad) * 30 / math.pi))
        for i in range(steps + 1):
            a = start_rad + (end_rad - start_rad) * (i / steps)
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
        pygame.draw.polygon(surface, color, points)

    def draw(self, surface, cx, cy, radius):
        pygame.draw.circle(surface, PANEL, (cx, cy), radius + 10)
        pygame.draw.circle(surface, ACCENT, (cx, cy), radius + 10, 3)
        success_deg = self.chance * 360
        start_rad = math.radians(-90); end_rad = math.radians(-90 + success_deg)
        self._draw_sector(surface, cx, cy, radius, start_rad, end_rad, GREEN)
        start_rad2 = math.radians(-90 + success_deg); end_rad2 = math.radians(270)
        self._draw_sector(surface, cx, cy, radius, start_rad2, end_rad2, RED)
        pygame.draw.circle(surface, WHITE, (cx, cy), radius, 2)
        rad = math.radians(self.angle)
        sx = cx + math.cos(rad) * (radius - 5); sy = cy + math.sin(rad) * (radius - 5)
        pygame.draw.line(surface, WHITE, (cx, cy), (sx, sy), 4)
        pygame.draw.circle(surface, GOLD, (int(sx), int(sy)), 9)
        pygame.draw.circle(surface, PANEL_LIGHT, (cx, cy), 30)
        pygame.draw.circle(surface, GOLD, (cx, cy), 30, 3)
        if self.finished:
            txt = FONT_BIG.render("УСПЕХ!" if self.success else "ПРОВАЛ", True, GREEN if self.success else RED)
            surface.blit(txt, (cx - txt.get_width() // 2, cy + radius + 15))

class Game:
    def __init__(self):
        self.player = Player()
        self.state = "cases"
        self.selected_case = None; self.roulette = None; self.roll_result = None
        self.rolled_sold = False 
        
        # Апгрейдер
        self.upgrade_selected = None; self.upgrade_target = None
        self.upgrade_extra_money = 0.0; self.upgrade_chance = 0.0
        self.upgrade_wheel = None; self.upgrade_message = ""; self.upgrade_msg_timer = 0
        self.upgrade_pending = False; self._pending_success = False
        
        self.tap_particles = []; self.tap_floats = []; self.tap_scale = 1.0
        self.notification = ""; self.notification_timer = 0
        self._inv_rects = []; self._inv_scroll = 0
        self._upg_src_rects = []; self._upg_dst_rects = []; self._upg_scroll_src = 0; self._upg_scroll_dst = 0
        
        self.upgrade_btn = Button(WIDTH // 2 - 130, HEIGHT - 90, 260, 55, "Апгрейд!")
        self.tap_upgrade_btn = Button(WIDTH - 380, HEIGHT - 90, 340, 55, "Улучшить тапалку")
        self.add_money_btn_10 = Button(0, 0, 50, 30, "+ $10")
        self.add_money_btn_100 = Button(0, 0, 50, 30, "+ $100")
        self.add_money_btn_max = Button(0, 0, 50, 30, "MAX")
        self.clear_money_btn = Button(0, 0, 80, 30, "Сброс", RED)
        
        self._build_ui()

    def _build_ui(self):
        self.nav_buttons = {
            "cases": Button(20, 20, 160, 50, "Кейсы"),
            "upgrader": Button(190, 20, 160, 50, "Апгрейдер"),
            "inventory": Button(360, 20, 160, 50, "Инвентарь"),
            "tapper": Button(530, 20, 160, 50, "Тапалка"),
        }
        self.case_buttons = []
        for i, case in enumerate(CASES):
            x = 80 + i * 370
            self.case_buttons.append({
                "case": case,
                "view": Button(x + 30, 560, 280, 45, "Осмотреть", ACCENT),
                "open": Button(x + 30, 620, 280, 55, f"Открыть — ${case['price']}")
            })
        self.sell_all_btn = Button(WIDTH - 220, HEIGHT - 70, 200, 50, "Продать всё", RED)

    def _get_safe_random_nft(self, rarity, weights):
        cands = [n for n in NFT_POOL if n[1] == rarity]
        if not cands:
            available = [r for r, w in weights.items() if w > 0]
            for r in available:
                cands = [n for n in NFT_POOL if n[1] == r]
                if cands: break
        if not cands: cands = NFT_POOL
        return random.choice(cands)

    def open_case(self, case):
        if self.player.money < case["price"]:
            self.show_notification("Недостаточно средств!"); play(SND_FAIL); return
        self.player.money -= case["price"]
        self.selected_case = case
        self.rolled_sold = False
        play(SND_OPEN_CASE)
        
        items = []
        for _ in range(20):
            rarity = self._roll_rarity(case["weights"])
            name, _, price = self._get_safe_random_nft(rarity, case["weights"])
            items.append(NFT(name, rarity, price))
            
        final_rarity = self._roll_rarity(case["weights"])
        name, _, price = self._get_safe_random_nft(final_rarity, case["weights"])
        self.roll_result = NFT(name, final_rarity, price)
        winner_index = len(items)
        items.append(self.roll_result)
        
        for _ in range(20):
            rarity = self._roll_rarity(case["weights"])
            name, _, price = self._get_safe_random_nft(rarity, case["weights"])
            items.append(NFT(name, rarity, price))
            
        self.roulette = Roulette(items, self.roll_result, winner_index, duration=210)
        self.state = "opening"

    def _roll_rarity(self, weights):
        valid = {k: v for k, v in weights.items() if v > 0}
        if not valid: return "Common"
        total = sum(valid.values()); r = random.uniform(0, total); upto = 0
        for rarity, w in valid.items():
            upto += w
            if r <= upto: return rarity
        return list(valid.keys())[-1]

    def _calc_upgrade(self):
        if not self.upgrade_selected or not self.upgrade_target:
            self.upgrade_chance = 0.0; return
        total_value = self.upgrade_selected.price + self.upgrade_extra_money
        dst = self.upgrade_target[2]
        if dst <= total_value: self.upgrade_chance = 0.95; return
        self.upgrade_chance = max(0.02, min(0.95, (total_value / dst) * 0.9))

    def start_upgrade(self):
        if not self.upgrade_selected or not self.upgrade_target:
            self.show_notification("Выбери NFT и цель!"); return
        if self.upgrade_chance <= 0:
            self.show_notification("Цель должна быть дороже!"); return
        if self.upgrade_pending or (self.upgrade_wheel and not self.upgrade_wheel.finished): return
        if self.player.money < self.upgrade_extra_money:
            self.show_notification("Недостаточно денег для доплаты!"); play(SND_FAIL); return

        try: idx = next(i for i, n in enumerate(self.player.inventory) if n is self.upgrade_selected)
        except StopIteration: self.upgrade_selected = None; return
            
        success = random.random() < self.upgrade_chance
        self.player.inventory.pop(idx)
        self.player.money -= self.upgrade_extra_money
        self._pending_success = success
        self.upgrade_wheel = UpgradeWheel(success, self.upgrade_chance)
        self.upgrade_pending = True
        play(SND_UPGRADE_START)

    def finalize_upgrade(self, success):
        if success:
            name, rarity, price = self.upgrade_target
            self.player.add_nft(NFT(name, rarity, price))
            self.upgrade_message = f"УСПЕХ! {name}"; play(SND_WIN_EPIC)
        else:
            self.upgrade_message = "ПРОВАЛ... NFT сгорел"; play(SND_FAIL)
        self.upgrade_msg_timer = 180
        self.upgrade_selected = None; self.upgrade_target = None
        self.upgrade_extra_money = 0.0; self.upgrade_chance = 0.0
        self.upgrade_wheel = None; self.upgrade_pending = False

    def show_notification(self, text):
        self.notification = text; self.notification_timer = 180

    def draw_topbar(self):
        pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 90))
        pygame.draw.line(screen, ACCENT, (0, 90), (WIDTH, 90), 2)
        mouse = pygame.mouse.get_pos()
        for key, btn in self.nav_buttons.items():
            btn.color = ACCENT if self.state.startswith(key) else PANEL_LIGHT
            btn.draw(screen, mouse)
        money_txt = FONT_MED.render(f"${fmt_money(self.player.money)}", True, GOLD)
        screen.blit(money_txt, (WIDTH - money_txt.get_width() - 30, 30))
        if self.notification_timer > 0:
            alpha = min(255, self.notification_timer * 3)
            notif = FONT.render(self.notification, True, WHITE)
            w = notif.get_width() + 40
            surf = pygame.Surface((w, 50), pygame.SRCALPHA)
            surf.fill((40, 40, 60, alpha))
            pygame.draw.rect(surf, (*ACCENT, alpha), (0, 0, w, 50), 2, border_radius=10)
            surf.blit(notif, (20, 15))
            screen.blit(surf, (WIDTH // 2 - w // 2, 100))
            self.notification_timer -= 1

    def draw_cases(self):
        title = FONT_BIG.render("Выбери кейс", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 130))
        mouse = pygame.mouse.get_pos()
        for i, (case, cbtn) in enumerate(zip(CASES, self.case_buttons)):
            x = 80 + i * 370
            rect = pygame.Rect(x, 200, 340, 380)
            pygame.draw.rect(screen, PANEL, rect, border_radius=20)
            pygame.draw.rect(screen, ACCENT, rect, 3, border_radius=20)
            name = FONT_MED.render(case["name"], True, WHITE)
            screen.blit(name, (rect.centerx - name.get_width() // 2, rect.y + 20))
            pulse = 1 + 0.05 * math.sin(pygame.time.get_ticks() / 200 + i)
            size = int(120 * pulse)
            cx, cy = rect.centerx, rect.y + 140
            pygame.draw.rect(screen, ACCENT, (cx - size // 2, cy - size // 2, size, size), border_radius=15)
            pygame.draw.rect(screen, PANEL_LIGHT, (cx - size // 2 + 10, cy - size // 2 + 10, size - 20, size - 20), border_radius=10)
            icon = FONT_BIG.render("?", True, GOLD)
            screen.blit(icon, (cx - icon.get_width() // 2, cy - icon.get_height() // 2))
            price = FONT_MED.render(f"${case['price']}", True, GOLD)
            screen.blit(price, (rect.centerx - price.get_width() // 2, rect.y + 230))
            
            cbtn["view"].draw(screen, mouse)
            cbtn["open"].disabled = self.player.money < case["price"]
            cbtn["open"].draw(screen, mouse)

    def draw_case_preview(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)); screen.blit(overlay, (0, 0))
        card = pygame.Rect(WIDTH // 2 - 350, 150, 700, 500)
        pygame.draw.rect(screen, PANEL, card, border_radius=20)
        pygame.draw.rect(screen, ACCENT, card, 3, border_radius=20)
        
        title = FONT_BIG.render(f"Осмотр: {self.selected_case['name']}", True, WHITE)
        screen.blit(title, (card.centerx - title.get_width() // 2, card.y + 20))
        
        info = FONT.render("Возможные выпадения:", True, GRAY)
        screen.blit(info, (card.x + 40, card.y + 80))
        
        possible = []
        for r, w in self.selected_case["weights"].items():
            if w > 0:
                cands = [n for n in NFT_POOL if n[1] == r]
                if cands: possible.extend(cands[:2])
        possible = list(set(possible))[:10]
        
        mouse = pygame.mouse.get_pos()
        for i, (name, rarity, price) in enumerate(possible):
            row = i // 5; col = i % 5
            x = card.x + 40 + col * 130
            y = card.y + 120 + row * 140
            rect = pygame.Rect(x, y, 110, 130)
            pygame.draw.rect(screen, PANEL_LIGHT, rect, border_radius=10)
            pygame.draw.rect(screen, RARITY_COLORS[rarity], rect, 2, border_radius=10)
            img = NFT_IMAGES.get(name)
            if img:
                icon = pygame.transform.smoothscale(img, (80, 80))
                screen.blit(icon, (x + 15, y + 10))
            else:
                pygame.draw.rect(screen, RARITY_COLORS[rarity], (x + 15, y + 10, 80, 80), border_radius=8)
            nm = FONT_SMALL.render(name[:12], True, WHITE)
            screen.blit(nm, (rect.centerx - nm.get_width() // 2, y + 95))
            rar = FONT_SMALL.render(rarity, True, RARITY_COLORS[rarity])
            screen.blit(rar, (rect.centerx - rar.get_width() // 2, y + 112))

        btn_back = pygame.Rect(card.centerx - 200, card.bottom - 60, 180, 45)
        btn_open = pygame.Rect(card.centerx + 20, card.bottom - 60, 180, 45)
        for btn, txt, col in [(btn_back, "Назад", PANEL_LIGHT), (btn_open, f"Открыть (${self.selected_case['price']})", ACCENT)]:
            c = col if btn.collidepoint(mouse) else (60, 60, 70)
            pygame.draw.rect(screen, c, btn, border_radius=10)
            pygame.draw.rect(screen, col, btn, 2, border_radius=10)
            t = FONT.render(txt, True, WHITE)
            screen.blit(t, (btn.centerx - t.get_width() // 2, btn.centery - t.get_height() // 2))

    def draw_opening_done(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)); screen.blit(overlay, (0, 0))
        card = pygame.Rect(WIDTH // 2 - 220, 180, 440, 440)
        pygame.draw.rect(screen, PANEL, card, border_radius=20)
        pygame.draw.rect(screen, self.roll_result.color, card, 4, border_radius=20)
        pulse = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2
        glow = pygame.Surface((card.w + 80, card.h + 80), pygame.SRCALPHA)
        for r in range(40, 0, -2):
            a = int(40 * pulse * (1 - r / 40))
            pygame.draw.rect(glow, (*self.roll_result.color, a), (40 - r, 40 - r, card.w + r * 2, card.h + r * 2), border_radius=30)
        screen.blit(glow, (card.x - 40, card.y - 40))
        title = FONT_MED.render("Вы получили!", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 205))
        self.roll_result.draw_icon(screen, WIDTH // 2 - 90, 240, 180, glow=True)
        name = FONT_MED.render(self.roll_result.name, True, WHITE)
        screen.blit(name, (WIDTH // 2 - name.get_width() // 2, 440))
        rarity = FONT.render(self.roll_result.rarity, True, self.roll_result.color)
        screen.blit(rarity, (WIDTH // 2 - rarity.get_width() // 2, 475))
        price = FONT_MED.render(f"${self.roll_result.price}", True, GOLD)
        screen.blit(price, (WIDTH // 2 - price.get_width() // 2, 510))
        
        mouse = pygame.mouse.get_pos()
        if self.rolled_sold:
            # Осталась только одна кнопка
            btn_ok = pygame.Rect(WIDTH // 2 - 90, 570, 180, 45)
            c = GREEN if btn_ok.collidepoint(mouse) else PANEL_LIGHT
            pygame.draw.rect(screen, c, btn_ok, border_radius=10)
            pygame.draw.rect(screen, GREEN, btn_ok, 2, border_radius=10)
            t = FONT.render("В инвентарь", True, WHITE)
            screen.blit(t, (btn_ok.centerx - t.get_width() // 2, btn_ok.centery - t.get_height() // 2))
            return btn_ok, None, None
        else:
            # Три кнопки
            btn1 = pygame.Rect(WIDTH // 2 - 270, 570, 170, 45)
            btn2 = pygame.Rect(WIDTH // 2 - 85, 570, 170, 45)
            btn3 = pygame.Rect(WIDTH // 2 + 100, 570, 170, 45)
            for btn, txt, col in [
                (btn1, "Забрать", GREEN),
                (btn2, f"Продать (${self.roll_result.price})", GOLD),
                (btn3, "Ещё кейс", ACCENT)
            ]:
                c = col if btn.collidepoint(mouse) else PANEL_LIGHT
                pygame.draw.rect(screen, c, btn, border_radius=10)
                pygame.draw.rect(screen, col, btn, 2, border_radius=10)
                t = FONT.render(txt, True, WHITE if col != GOLD else (30, 30, 30))
                screen.blit(t, (btn.centerx - t.get_width() // 2, btn.centery - t.get_height() // 2))
            return btn1, btn2, btn3

    def draw_inventory(self):
        title = FONT_BIG.render("Инвентарь", True, WHITE)
        screen.blit(title, (30, 110))
        total = sum(n.price for n in self.player.inventory)
        info = FONT.render(f"NFT: {len(self.player.inventory)} | Стоимость: ${total}", True, GOLD)
        screen.blit(info, (30, 165))
        self._inv_rects = []
        if not self.player.inventory:
            msg = FONT_MED.render("Пусто... Открой кейс!", True, GRAY)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        else:
            cols = 5; card_w, card_h = 210, 250; start_x, start_y = 30, 210; gap = 15
            mouse = pygame.mouse.get_pos()
            for i, nft in enumerate(self.player.inventory):
                col = i % cols; row = i // cols
                x = start_x + col * (card_w + gap)
                y = start_y + row * (card_h + gap) - self._inv_scroll
                if y + card_h < 180 or y > HEIGHT: continue
                rect = pygame.Rect(x, y, card_w, card_h)
                self._inv_rects.append((rect, i))
                hover = rect.collidepoint(mouse)
                pygame.draw.rect(screen, PANEL_LIGHT if hover else PANEL, rect, border_radius=12)
                pygame.draw.rect(screen, nft.color, rect, 2, border_radius=12)
                nft.draw_icon(screen, x + card_w // 2 - 40, y + 15, 80)
                nm = FONT_SMALL.render(nft.name[:16], True, WHITE)
                screen.blit(nm, (x + card_w // 2 - nm.get_width() // 2, y + 105))
                rar = FONT_SMALL.render(nft.rarity, True, nft.color)
                screen.blit(rar, (x + card_w // 2 - rar.get_width() // 2, y + 130))
                pr = FONT.render(f"${nft.price}", True, GOLD)
                screen.blit(pr, (x + card_w // 2 - pr.get_width() // 2, y + 155))
                sell_rect = pygame.Rect(x + 30, y + 195, card_w - 60, 38)
                pygame.draw.rect(screen, RED if sell_rect.collidepoint(mouse) else PANEL, sell_rect, border_radius=8)
                pygame.draw.rect(screen, RED, sell_rect, 2, border_radius=8)
                st = FONT_SMALL.render("Продать", True, WHITE)
                screen.blit(st, (sell_rect.centerx - st.get_width() // 2, sell_rect.centery - st.get_height() // 2))
        mouse = pygame.mouse.get_pos()
        self.sell_all_btn.disabled = not self.player.inventory
        self.sell_all_btn.draw(screen, mouse)

    def draw_upgrader(self):
        title = FONT_BIG.render("Апгрейдер", True, WHITE)
        screen.blit(title, (30, 110))
        info = FONT.render("Выбери NFT и цель. Можешь добавить баланс для повышения шанса!", True, GRAY)
        screen.blit(info, (30, 165))
        mouse = pygame.mouse.get_pos()

        left_rect = pygame.Rect(30, 210, 420, 460)
        pygame.draw.rect(screen, PANEL, left_rect, border_radius=15)
        pygame.draw.rect(screen, ACCENT, left_rect, 2, border_radius=15)
        t = FONT_MED.render("Твой NFT", True, WHITE)
        screen.blit(t, (left_rect.centerx - t.get_width() // 2, 225))
        self._upg_src_rects = []

        if not self.player.inventory:
            msg = FONT.render("Инвентарь пуст", True, GRAY)
            screen.blit(msg, (left_rect.centerx - msg.get_width() // 2, 400))
        else:
            cols = 3; cw, ch = 120, 140
            for i, nft in enumerate(self.player.inventory):
                col = i % cols; row = i // cols
                x = left_rect.x + 20 + col * (cw + 10)
                y = left_rect.y + 60 + row * (ch + 10) - self._upg_scroll_src
                if y + ch < left_rect.y + 50 or y > left_rect.bottom - 10: continue
                rect = pygame.Rect(x, y, cw, ch)
                self._upg_src_rects.append((rect, nft))
                selected = nft is self.upgrade_selected
                pygame.draw.rect(screen, ACCENT if selected else PANEL_LIGHT, rect, border_radius=10)
                pygame.draw.rect(screen, nft.color, rect, 3 if selected else 1, border_radius=10)
                nft.draw_icon(screen, x + cw // 2 - 30, y + 10, 60)
                nm = FONT_SMALL.render(nft.name[:12], True, WHITE)
                screen.blit(nm, (x + cw // 2 - nm.get_width() // 2, y + 75))
                pr = FONT_SMALL.render(f"${nft.price}", True, GOLD)
                screen.blit(pr, (x + cw // 2 - pr.get_width() // 2, y + 95))

        wheel_cx = 600; wheel_cy = 340; wheel_r = 100
        if self.upgrade_wheel:
            self.upgrade_wheel.draw(screen, wheel_cx, wheel_cy, wheel_r)
        else:
            pygame.draw.circle(screen, PANEL, (wheel_cx, wheel_cy), wheel_r + 10)
            pygame.draw.circle(screen, ACCENT, (wheel_cx, wheel_cy), wheel_r + 10, 3)
            if self.upgrade_selected and self.upgrade_target:
                success_angle = self.upgrade_chance * 360
                pygame.draw.arc(screen, RED, (wheel_cx - wheel_r, wheel_cy - wheel_r, wheel_r * 2, wheel_r * 2), math.radians(-90), math.radians(-90 + 360 - success_angle), 15)
                if success_angle > 0:
                    pygame.draw.arc(screen, GREEN, (wheel_cx - wheel_r, wheel_cy - wheel_r, wheel_r * 2, wheel_r * 2), math.radians(-90 + 360 - success_angle), math.radians(270), 15)
                chance_txt = FONT_HUGE.render(f"{int(self.upgrade_chance * 100)}%", True, GOLD)
                screen.blit(chance_txt, (wheel_cx - chance_txt.get_width() // 2, wheel_cy - chance_txt.get_height() // 2 - 10))
                lbl = FONT_SMALL.render("шанс успеха", True, GRAY)
                screen.blit(lbl, (wheel_cx - lbl.get_width() // 2, wheel_cy + 30))
            else:
                msg = FONT.render("Выбери NFT", True, GRAY)
                screen.blit(msg, (wheel_cx - msg.get_width() // 2, wheel_cy - 20))
                msg2 = FONT_SMALL.render("и цель", True, GRAY)
                screen.blit(msg2, (wheel_cx - msg2.get_width() // 2, wheel_cy + 10))

        # Панель добавления баланса (Строго под колесом)
        if self.upgrade_selected and self.upgrade_target:
            add_panel = pygame.Rect(510, 470, 180, 170)
            pygame.draw.rect(screen, PANEL_LIGHT, add_panel, border_radius=10)
            pygame.draw.rect(screen, ACCENT, add_panel, 2, border_radius=10)
            t_add = FONT.render("Добавить баланс:", True, WHITE)
            screen.blit(t_add, (add_panel.centerx - t_add.get_width() // 2, add_panel.y + 10))
            val_txt = FONT_MED.render(f"+ ${fmt_money(self.upgrade_extra_money)}", True, GOLD)
            screen.blit(val_txt, (add_panel.centerx - val_txt.get_width() // 2, add_panel.y + 40))

            self.add_money_btn_10.rect = pygame.Rect(add_panel.x + 10, add_panel.y + 75, 50, 30)
            self.add_money_btn_100.rect = pygame.Rect(add_panel.x + 65, add_panel.y + 75, 50, 30)
            self.add_money_btn_max.rect = pygame.Rect(add_panel.x + 120, add_panel.y + 75, 50, 30)
            self.clear_money_btn.rect = pygame.Rect(add_panel.x + 50, add_panel.y + 115, 80, 30)

            self.add_money_btn_10.disabled = self.player.money < 10
            self.add_money_btn_100.disabled = self.player.money < 100
            self.add_money_btn_max.disabled = self.player.money <= 0
            
            self.add_money_btn_10.draw(screen, mouse)
            self.add_money_btn_100.draw(screen, mouse)
            self.add_money_btn_max.draw(screen, mouse)
            self.clear_money_btn.draw(screen, mouse)

        right_rect = pygame.Rect(750, 210, 420, 460)
        pygame.draw.rect(screen, PANEL, right_rect, border_radius=15)
        pygame.draw.rect(screen, ACCENT, right_rect, 2, border_radius=15)
        t = FONT_MED.render("Цель апгрейда", True, WHITE)
        screen.blit(t, (right_rect.centerx - t.get_width() // 2, 225))
        self._upg_dst_rects = []
        targets = sorted(NFT_POOL, key=lambda n: n[2])
        for i, (name, rarity, price) in enumerate(targets):
            col = i % 2; row = i // 2
            x = right_rect.x + 20 + col * 190
            y = right_rect.y + 60 + row * 95 - self._upg_scroll_dst
            if y + 85 < right_rect.y + 50 or y > right_rect.bottom - 10: continue
            rect = pygame.Rect(x, y, 180, 85)
            self._upg_dst_rects.append((rect, (name, rarity, price)))
            selected = self.upgrade_target == (name, rarity, price)
            color = RARITY_COLORS[rarity]
            pygame.draw.rect(screen, ACCENT if selected else PANEL_LIGHT, rect, border_radius=8)
            pygame.draw.rect(screen, color, rect, 2, border_radius=8)
            
            img = NFT_IMAGES.get(name)
            if img:
                icon = pygame.transform.smoothscale(img, (60, 60))
                screen.blit(icon, (x + 5, y + 12))
            else:
                pygame.draw.rect(screen, color, (x + 5, y + 12, 60, 60), border_radius=8)

            nm = FONT_SMALL.render(name[:14], True, WHITE)
            screen.blit(nm, (x + 70, y + 10))
            rar = FONT_SMALL.render(rarity, True, color)
            screen.blit(rar, (x + 70, y + 32))
            pr = FONT_SMALL.render(f"${price}", True, GOLD)
            screen.blit(pr, (x + 70, y + 55))

        self.upgrade_btn.disabled = not (self.upgrade_selected and self.upgrade_target and self.upgrade_chance > 0 and not (self.upgrade_wheel and not self.upgrade_wheel.finished))
        self.upgrade_btn.draw(screen, mouse)

        if self.upgrade_msg_timer > 0:
            color = GREEN if "УСПЕХ" in self.upgrade_message else RED
            msg = FONT_MED.render(self.upgrade_message, True, color)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 180))
            self.upgrade_msg_timer -= 1

    def draw_tapper(self):
        title = FONT_BIG.render("Тапалка", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 110))
        rate_str = f"Монет за клик: {self.player.coins_per_click:g}"
        info = FONT.render(rate_str, True, GOLD)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 175))
        total = FONT_SMALL.render(f"Всего тапов: {self.player.total_taps}", True, GRAY)
        screen.blit(total, (WIDTH // 2 - total.get_width() // 2, 205))

        cx, cy = WIDTH // 2, 420
        base_r = 150; r = int(base_r * self.tap_scale)
        glow = pygame.Surface((r * 2 + 80, r * 2 + 80), pygame.SRCALPHA)
        for i in range(30, 0, -2):
            a = int(15 * (1 - i / 30))
            pygame.draw.circle(glow, (*ACCENT, a), (r + 40, r + 40), r + i)
        screen.blit(glow, (cx - r - 40, cy - r - 40))
        pygame.draw.circle(screen, ACCENT, (cx, cy), r)
        pygame.draw.circle(screen, PANEL_LIGHT, (cx, cy), r - 15)
        pygame.draw.circle(screen, ACCENT, (cx, cy), r - 15, 4)
        sym = FONT_HUGE.render("$", True, GOLD)
        screen.blit(sym, (cx - sym.get_width() // 2, cy - sym.get_height() // 2))

        for p in self.tap_particles: p.draw(screen)
        for ft in self.tap_floats: ft.draw(screen)

        panel = pygame.Rect(50, 620, WIDTH - 100, 140)
        pygame.draw.rect(screen, PANEL, panel, border_radius=15)
        pygame.draw.rect(screen, ACCENT, panel, 2, border_radius=15)
        t = FONT_MED.render("Магазин улучшений", True, WHITE)
        screen.blit(t, (panel.centerx - t.get_width() // 2, panel.y + 10))

        info_up = self.player.get_tap_upgrade_info()
        if info_up:
            price, new_rate = info_up
            cost = FONT.render(f"Следующий уровень: {new_rate:g} монет/клик", True, GOLD)
            screen.blit(cost, (panel.x + 30, panel.y + 55))
            price_txt = FONT.render(f"Цена: ${price}", True, WHITE)
            screen.blit(price_txt, (panel.x + 30, panel.y + 85))
            self.tap_upgrade_btn.rect.x = panel.right - 360
            self.tap_upgrade_btn.rect.y = panel.y + 50
            self.tap_upgrade_btn.text = f"Улучшить (${price})"
            self.tap_upgrade_btn.disabled = self.player.money < price
            self.tap_upgrade_btn.draw(screen, pygame.mouse.get_pos())
        else:
            maxed = FONT_MED.render("Максимальный уровень!", True, GREEN)
            screen.blit(maxed, (panel.centerx - maxed.get_width() // 2, panel.y + 65))

    def handle_event(self, e):
        mouse = pygame.mouse.get_pos()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if self.state != "cases": self.state = "cases"
            return

        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4:
                if self.state == "inventory": self._inv_scroll = max(0, self._inv_scroll - 40)
                elif self.state == "upgrader":
                    if mouse[0] < 480: self._upg_scroll_src = max(0, self._upg_scroll_src - 40)
                    elif mouse[0] > 750: self._upg_scroll_dst = max(0, self._upg_scroll_dst - 40)
                return
            if e.button == 5:
                if self.state == "inventory": self._inv_scroll += 40
                elif self.state == "upgrader":
                    if mouse[0] < 480: self._upg_scroll_src += 40
                    elif mouse[0] > 750: self._upg_scroll_dst += 40
                return

            if e.button == 1:
                for key, btn in self.nav_buttons.items():
                    if btn.clicked(mouse):
                        self.state = key; self.upgrade_selected = None; self.upgrade_target = None; self.upgrade_extra_money = 0.0; self.upgrade_chance = 0.0
                        return

                if self.state == "cases":
                    for cbtn in self.case_buttons:
                        if cbtn["view"].clicked(mouse):
                            self.selected_case = cbtn["case"]
                            self.state = "case_preview"
                            play(SND_CLICK)
                            return
                        if cbtn["open"].clicked(mouse):
                            self.open_case(cbtn["case"])
                            return
                            
                elif self.state == "case_preview":
                    btn_back = pygame.Rect(WIDTH // 2 - 200, 590, 180, 45)
                    btn_open = pygame.Rect(WIDTH // 2 + 20, 590, 180, 45)
                    if btn_back.collidepoint(mouse):
                        self.state = "cases"
                        play(SND_CLICK)
                    elif btn_open.collidepoint(mouse):
                        self.open_case(self.selected_case)
                        
                elif self.state == "opening_done":
                    if self.rolled_sold:
                        btn_ok = pygame.Rect(WIDTH // 2 - 90, 570, 180, 45)
                        if btn_ok.collidepoint(mouse):
                            self.state = "inventory"
                            play(SND_CLICK)
                    else:
                        btn1 = pygame.Rect(WIDTH // 2 - 270, 570, 170, 45)
                        btn2 = pygame.Rect(WIDTH // 2 - 85, 570, 170, 45)
                        btn3 = pygame.Rect(WIDTH // 2 + 100, 570, 170, 45)
                        if btn1.collidepoint(mouse):
                            self.state = "inventory"
                            play(SND_CLICK)
                        elif btn2.collidepoint(mouse):
                            self.player.money += self.roll_result.price
                            self.show_notification(f"Продан {self.roll_result.name} за ${self.roll_result.price}")
                            play(SND_WIN_COMMON)
                            self.rolled_sold = True 
                        elif btn3.collidepoint(mouse):
                            self.open_case(self.selected_case)
                            
                elif self.state == "inventory":
                    if self.sell_all_btn.clicked(mouse):
                        total = sum(n.price for n in self.player.inventory)
                        self.player.money += total; self.player.inventory.clear()
                        self.show_notification(f"Продано на ${total}"); play(SND_WIN_COMMON); return
                    for rect, idx in self._inv_rects:
                        sell_rect = pygame.Rect(rect.x + 30, rect.y + 195, rect.width - 60, 38)
                        if sell_rect.collidepoint(mouse):
                            if 0 <= idx < len(self.player.inventory):
                                nft = self.player.sell_nft(idx)
                                self.show_notification(f"Продан {nft.name} за ${nft.price}"); play(SND_CLICK)
                            return
                elif self.state == "upgrader":
                    if self.add_money_btn_10.clicked(mouse):
                        self.upgrade_extra_money += 10; self._calc_upgrade(); play(SND_CLICK); return
                    if self.add_money_btn_100.clicked(mouse):
                        self.upgrade_extra_money += 100; self._calc_upgrade(); play(SND_CLICK); return
                    if self.add_money_btn_max.clicked(mouse):
                        if self.upgrade_target:
                            dst_val = self.upgrade_target[2]
                            needed = dst_val - self.upgrade_selected.price
                            if needed > 0:
                                to_add = min(self.player.money, needed)
                                self.upgrade_extra_money += to_add; self._calc_upgrade(); play(SND_CLICK)
                        return
                    if self.clear_money_btn.clicked(mouse):
                        self.upgrade_extra_money = 0.0; self._calc_upgrade(); return

                    for rect, nft in self._upg_src_rects:
                        if rect.collidepoint(mouse):
                            self.upgrade_selected = nft; self.upgrade_extra_money = 0.0; self._calc_upgrade(); return
                    for rect, target in self._upg_dst_rects:
                        if rect.collidepoint(mouse):
                            self.upgrade_target = target; self.upgrade_extra_money = 0.0; self._calc_upgrade(); return
                    if self.upgrade_btn.clicked(mouse): self.start_upgrade(); return
                elif self.state == "tapper":
                    if self.tap_upgrade_btn.clicked(mouse):
                        if self.player.upgrade_tap():
                            self.show_notification(f"Улучшено! {self.player.coins_per_click:g} монет/клик")
                            play(SND_WIN_EPIC)
                        else:
                            self.show_notification("Не хватает денег!"); play(SND_FAIL)
                        return
                    cx, cy = WIDTH // 2, 420
                    if math.hypot(mouse[0] - cx, mouse[1] - cy) < 150:
                        self.player.tap(); play(SND_CLICK); self.tap_scale = 0.92
                        for _ in range(5):
                            angle = random.uniform(0, math.tau); dist = random.uniform(50, 140)
                            px = cx + math.cos(angle) * dist; py = cy + math.sin(angle) * dist
                            self.tap_particles.append(Particle(px, py, GOLD, upward=True))
                        gain = self.player.coins_per_click; gain_str = f"+{gain:g}"
                        self.tap_floats.append(FloatingText(mouse[0], mouse[1] - 30, gain_str, GOLD))

    def update(self):
        if self.state == "opening" and self.roulette:
            self.roulette.update()
            if self.roulette.finished:
                self.state = "opening_done"
                if not self.rolled_sold: 
                    self.player.add_nft(self.roll_result)
        if self.upgrade_wheel:
            self.upgrade_wheel.update()
            if self.upgrade_wheel.finished and self.upgrade_pending: self.finalize_upgrade(self._pending_success)
        self.tap_scale += (1.0 - self.tap_scale) * 0.2
        for p in self.tap_particles: p.update()
        self.tap_particles = [p for p in self.tap_particles if p.life > 0]
        for ft in self.tap_floats: ft.update()
        self.tap_floats = [ft for ft in self.tap_floats if ft.life > 0]

    def draw(self):
        screen.fill(BG)
        self.draw_topbar()
        if self.state == "cases": self.draw_cases()
        elif self.state == "case_preview": self.draw_cases(); self.draw_case_preview()
        elif self.state == "opening": self.roulette.draw(screen)
        elif self.state == "opening_done": self.roulette.draw(screen); self.draw_opening_done()
        elif self.state == "inventory": self.draw_inventory()
        elif self.state == "upgrader": self.draw_upgrader()
        elif self.state == "tapper": self.draw_tapper()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(e)
            self.update(); self.draw()
            pygame.display.flip(); clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()