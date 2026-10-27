import math
import random
import pygame

pygame.init()
W, H = 480, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24, bold=True)
small = pygame.font.SysFont("arial", 18, bold=True)
big = pygame.font.SysFont("arial", 60, bold=True)

CX = W // 2            # screen centre (vanishing point x)
HORIZON = 230          # screen y of the horizon
PLAYER_Y = 590         # screen y of the runner's feet
LW = 125               # width of one lane in pixels at the runner
ZP = 2.0               # distance of the runner from the camera
ZFAR = 48.0            # how far ahead things appear
PH = 0.8               # runner height
EYE = (PLAYER_Y - HORIZON) / LW
GRAVITY = 0.006
JUMP_V = 0.11
SLEEPER_GAP = 1.2
BEST = 0

TRAIN_COLORS = [(60, 110, 190), (50, 150, 110), (150, 70, 160), (200, 80, 60)]
BUILD_COLORS = [(45, 50, 80), (60, 55, 90), (40, 65, 85), (70, 60, 70)]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def sx(x, z):
    return CX + x * LW * ZP / z


def sy(z, h=0.0):
    s = ZP / z
    return HORIZON + (PLAYER_Y - HORIZON) * s - h * LW * s


# ---------------------------------------------------------------- game state
def new_building(side, z):
    return {
        "side": side, "z": z,
        "w": random.uniform(1.2, 2.2), "h": random.uniform(2.0, 6.5),
        "len": random.uniform(2.0, 3.2), "col": random.choice(BUILD_COLORS),
    }


def new_game(state="menu"):
    g = {
        "state": state, "t": 0, "lane": 0, "px": 0.0, "pj": 0.0, "vy": 0.0,
        "slide": 0, "inv": 0, "shake": 0, "speed": 0.2, "dist": 0.0,
        "coins": 0, "gap": 1.0, "off": 0.0, "next": 14.0,
        "obs": [], "coin_list": [], "bld": [],
    }
    for side in (-1, 1):
        z = 3.0
        while z < ZFAR:
            g["bld"].append(new_building(side, z))
            z += random.uniform(3.0, 4.5)
    return g


def spawn(g):
    lanes = [-1, 0, 1]
    random.shuffle(lanes)
    blocked = lanes[:random.choice([1, 1, 2])]
    free = lanes[len(blocked):]
    for lane in blocked:
        r = random.random()
        if r < 0.40:
            kind, length = "barrier", 0.3
        elif r < 0.70:
            kind, length = "overhead", 0.25
        else:
            kind, length = "train", 4.0
        g["obs"].append({"lane": lane, "z": ZFAR, "kind": kind, "len": length,
                         "col": random.choice(TRAIN_COLORS)})
        if kind == "barrier" and random.random() < 0.6:
            for dz, h in ((-0.9, 0.7), (0.15, 1.0), (1.2, 0.7)):
                g["coin_list"].append({"lane": lane, "z": ZFAR + dz, "h": h})
    lane = random.choice(free)
    for i in range(5):
        g["coin_list"].append({"lane": lane, "z": ZFAR + i * 1.0, "h": 0.45})


def update_world(g, speed):
    g["off"] = (g["off"] - speed) % SLEEPER_GAP
    for b in g["bld"]:
        b["z"] -= speed
        if b["z"] + b["len"] < 0.8:
            b.update(new_building(b["side"], ZFAR + random.uniform(0, 3)))


def update(g):
    g["t"] += 1
    if g["state"] != "play":
        update_world(g, 0.12)
        g["px"] += (g["lane"] - g["px"]) * 0.22
        return

    g["speed"] = min(0.36, 0.20 + g["dist"] / 3000)
    speed = g["speed"]
    g["dist"] += speed
    update_world(g, speed)

    g["next"] -= speed
    if g["next"] <= 0:
        spawn(g)
        g["next"] = 11.0

    g["px"] += (g["lane"] - g["px"]) * 0.22
    if g["pj"] > 0 or g["vy"] != 0:
        g["pj"] += g["vy"]
        g["vy"] -= GRAVITY
        if g["pj"] <= 0:
            g["pj"] = 0.0
            g["vy"] = 0.0
    if g["slide"] > 0:
        g["slide"] -= 1
    if g["inv"] > 0:
        g["inv"] -= 1
    if g["shake"] > 0:
        g["shake"] -= 1

    ph = 0.35 if g["slide"] > 0 else PH
    spans = {"barrier": (0.0, 0.42), "overhead": (0.5, 0.85), "train": (0.0, 1.15)}

    for o in g["obs"][:]:
        o["z"] -= speed
        if o["z"] + o["len"] < 0.8:
            g["obs"].remove(o)
            continue
        if g["inv"] == 0 and o["z"] < ZP + 0.2 and o["z"] + o["len"] > ZP - 0.2:
            if abs(g["px"] - o["lane"]) < 0.6:
                y0, y1 = spans[o["kind"]]
                if g["pj"] < y1 and g["pj"] + ph > y0:
                    g["gap"] -= 0.45
                    g["inv"] = 70
                    g["shake"] = 14

    for c in g["coin_list"][:]:
        c["z"] -= speed
        if c["z"] < 1.0:
            g["coin_list"].remove(c)
        elif (abs(c["z"] - ZP) < 0.3 and abs(g["px"] - c["lane"]) < 0.6
              and g["pj"] < c["h"] + 0.15 and g["pj"] + ph > c["h"] - 0.15):
            g["coin_list"].remove(c)
            g["coins"] += 1

    g["gap"] = min(1.2, g["gap"] + 0.0012)
    if g["gap"] <= 0.12:
        g["state"] = "over"


def score(g):
    return int(g["dist"] * 1.5) + g["coins"] * 10


# ------------------------------------------------------------------ drawing
def box(xl, xr, z, length, h0, h1, col):
    zf = max(z, 0.55)
    zr = z + length
    if zr < 0.6:
        return None
    zr = max(zr, zf + 0.02)
    mid = (xl + xr) / 2
    if mid < -0.05:
        pts = [(sx(xr, zf), sy(zf, h1)), (sx(xr, zr), sy(zr, h1)),
               (sx(xr, zr), sy(zr, h0)), (sx(xr, zf), sy(zf, h0))]
        pygame.draw.polygon(screen, shade(col, 0.6), pts)
    elif mid > 0.05:
        pts = [(sx(xl, zf), sy(zf, h1)), (sx(xl, zr), sy(zr, h1)),
               (sx(xl, zr), sy(zr, h0)), (sx(xl, zf), sy(zf, h0))]
        pygame.draw.polygon(screen, shade(col, 0.6), pts)
    if h1 < EYE:
        top = [(sx(xl, zf), sy(zf, h1)), (sx(xr, zf), sy(zf, h1)),
               (sx(xr, zr), sy(zr, h1)), (sx(xl, zr), sy(zr, h1))]
        pygame.draw.polygon(screen, shade(col, 1.25), top)
    front = [(sx(xl, zf), sy(zf, h1)), (sx(xr, zf), sy(zf, h1)),
             (sx(xr, zf), sy(zf, h0)), (sx(xl, zf), sy(zf, h0))]
    pygame.draw.polygon(screen, col, front)
    return (sx(xl, zf), sy(zf, h1), sx(xr, zf), sy(zf, h0))


def draw_background(g):
    for i in range(0, HORIZON, 6):
        k = i / HORIZON
        col = (int(40 + 200 * k), int(70 + 90 * k), int(150 - 30 * k))
        pygame.draw.rect(screen, col, (0, i, W, 6))
    pygame.draw.circle(screen, (255, 225, 160), (CX + 110, HORIZON - 45), 38)
    pygame.draw.rect(screen, (38, 40, 52), (0, HORIZON, W, H - HORIZON))
    road = [(sx(-1.5, ZFAR), sy(ZFAR)), (sx(1.5, ZFAR), sy(ZFAR)),
            (sx(1.5, 0.9), sy(0.9)), (sx(-1.5, 0.9), sy(0.9))]
    pygame.draw.polygon(screen, (78, 78, 88), road)
    z = g["off"]
    while z < ZFAR:
        if z > 0.9:
            for lane in (-1, 0, 1):
                pts = [(sx(lane - 0.4, z), sy(z)), (sx(lane + 0.4, z), sy(z)),
                       (sx(lane + 0.4, z + 0.22), sy(z + 0.22)),
                       (sx(lane - 0.4, z + 0.22), sy(z + 0.22))]
                pygame.draw.polygon(screen, (95, 72, 52), pts)
        z += SLEEPER_GAP
    for lane in (-1, 0, 1):
        for rx in (-0.27, 0.27):
            xa = lane + rx
            pts = [(sx(xa - 0.025, ZFAR), sy(ZFAR)), (sx(xa + 0.025, ZFAR), sy(ZFAR)),
                   (sx(xa + 0.025, 0.9), sy(0.9)), (sx(xa - 0.025, 0.9), sy(0.9))]
            pygame.draw.polygon(screen, (175, 175, 185), pts)


def draw_building(b):
    if b["side"] < 0:
        xl, xr = -2.1 - b["w"], -2.1
    else:
        xl, xr = 2.1, 2.1 + b["w"]
    r = box(xl, xr, b["z"], b["len"], 0, b["h"], b["col"])
    if r:
        x0, y0, x1, y1 = r
        w, h = x1 - x0, y1 - y0
        if w > 14:
            for i in range(1, 4):
                for j in range(1, 6):
                    lit = (int(b["z"] * 3) + i * j) % 3 != 0
                    col = (250, 220, 120) if lit else (30, 35, 55)
                    pygame.draw.rect(screen, col, (x0 + w * i / 4.6, y0 + h * j / 6.6,
                                                   max(2, w / 9), max(2, h / 16)))


def draw_obstacle(o):
    lane, z = o["lane"], o["z"]
    if o["kind"] == "barrier":
        r = box(lane - 0.43, lane + 0.43, z, 0.3, 0, 0.42, (210, 50, 50))
        if r:
            x0, y0, x1, y1 = r
            pygame.draw.rect(screen, (250, 250, 250), (x0, y0 + (y1 - y0) * 0.32, x1 - x0, (y1 - y0) * 0.3))
    elif o["kind"] == "overhead":
        box(lane - 0.48, lane - 0.38, z, 0.25, 0, 0.6, (120, 120, 130))
        box(lane + 0.38, lane + 0.48, z, 0.25, 0, 0.6, (120, 120, 130))
        box(lane - 0.48, lane + 0.48, z, 0.25, 0.5, 0.85, (240, 160, 30))
    else:
        r = box(lane - 0.45, lane + 0.45, z, 4.0, 0, 1.15, o["col"])
        if r:
            x0, y0, x1, y1 = r
            w, h = x1 - x0, y1 - y0
            if w > 12:
                pygame.draw.rect(screen, (255, 235, 140), (x0 + w * 0.12, y0 + h * 0.2, w * 0.3, h * 0.22))
                pygame.draw.rect(screen, (255, 235, 140), (x0 + w * 0.58, y0 + h * 0.2, w * 0.3, h * 0.22))
                pygame.draw.rect(screen, (30, 30, 40), (x0 + w * 0.1, y0 + h * 0.75, w * 0.8, h * 0.08))


def draw_coin(c, t):
    z = c["z"]
    s = ZP / z
    r = max(2, int(0.13 * LW * s))
    x, y = sx(c["lane"], z), sy(z, c["h"])
    wid = max(2, int(r * abs(math.cos(t * 0.1 + z))) + 2)
    pygame.draw.ellipse(screen, (255, 200, 0), (x - wid, y - r, wid * 2, r * 2))
    pygame.draw.ellipse(screen, (200, 140, 0), (x - wid, y - r, wid * 2, r * 2), 2)


def person(cx, feet, f, t, shirt, pants, skin, hair, squash=1.0, zombie=False):
    legh = 40 * f * squash
    th = 46 * f * squash
    sw = math.sin(t * 0.5) * 7 * f
    pygame.draw.rect(screen, pants, (cx - 15 * f + sw, feet - legh, 14 * f, legh))
    pygame.draw.rect(screen, pants, (cx + 1 * f - sw, feet - legh, 14 * f, legh))
    top = feet - legh - th
    pygame.draw.rect(screen, shirt, (cx - 19 * f, top, 38 * f, th), border_radius=int(7 * f))
    if zombie:
        for side in (-1, 1):
            pygame.draw.line(screen, skin, (cx + side * 18 * f, top + 8 * f),
                             (cx + side * 34 * f, top - 26 * f), max(2, int(8 * f)))
    else:
        for side in (-1, 1):
            pygame.draw.rect(screen, shirt, (cx + side * 24 * f - 4 * f, top + 3 * f + side * sw * 0.6,
                                             8 * f, 30 * f * squash), border_radius=int(3 * f))
    hr = 15 * f
    hy = top - hr + 3 * f
    pygame.draw.circle(screen, skin, (int(cx), int(hy)), int(hr))
    pygame.draw.circle(screen, hair, (int(cx), int(hy - 2 * f)), int(hr), draw_top_left=True, draw_top_right=True)
    if not zombie:
        pygame.draw.circle(screen, hair, (int(cx), int(hy)), int(hr))
        pygame.draw.rect(screen, (240, 60, 60), (cx - hr, hy - 4 * f, hr * 2, 6 * f))


def draw_player(g):
    x = CX + g["px"] * LW
    feet = PLAYER_Y - g["pj"] * LW
    shadow_w = 44 - g["pj"] * 18
    pygame.draw.ellipse(screen, (20, 20, 25), (x - shadow_w / 2, PLAYER_Y - 5, shadow_w, 12))
    if g["inv"] > 0 and (g["t"] // 4) % 2 == 0:
        return
    squash = 0.5 if g["slide"] > 0 else 1.0
    moving = g["state"] == "play" and g["pj"] == 0
    person(x, feet, 1.0, g["t"] if moving else 0, (230, 90, 30), (35, 60, 150),
           (240, 200, 160), (30, 30, 40), squash)


def draw_zombies(g):
    x = CX + g["px"] * LW
    feet = PLAYER_Y + 40 + max(g["gap"], 0) * 130
    for dx, dt, f in ((-52, 3, 1.35), (52, 7, 1.35), (0, 0, 1.55)):
        person(x + dx, feet + 6, f, g["t"] + dt, (100, 60, 60), (55, 65, 85),
               (105, 160, 95), (60, 80, 50), 1.0, True)


def draw_game(g, best):
    draw_background(g)
    items = [(b["z"], 0, b) for b in g["bld"]]
    items += [(o["z"], 1, o) for o in g["obs"]]
    items += [(c["z"], 2, c) for c in g["coin_list"]]
    items.append((ZP, 3, None))
    items.sort(key=lambda it: -it[0])
    for z, kind, obj in items:
        if z > ZFAR + 6:
            continue
        if kind == 0:
            draw_building(obj)
        elif kind == 1:
            draw_obstacle(obj)
        elif kind == 2:
            draw_coin(obj, g["t"])
        else:
            draw_player(g)
    draw_zombies(g)

    if g["state"] == "play":
        screen.blit(font.render(f"Score {score(g)}", True, (255, 255, 255)), (16, 14))
        screen.blit(font.render(f"Coins {g['coins']}", True, (255, 215, 0)), (16, 44))
        screen.blit(small.render(f"Best {best}", True, (255, 255, 255)), (W - 100, 16))
        ratio = max(0.0, min(1.0, (g["gap"] - 0.12) / 1.08))
        pygame.draw.rect(screen, (120, 25, 25), (W - 140, 44, 120, 14), border_radius=6)
        pygame.draw.rect(screen, (70, 200, 90), (W - 140, 44, int(120 * ratio), 14), border_radius=6)
        screen.blit(small.render("zombies", True, (255, 255, 255)), (W - 140, 62))
        if g["inv"] > 40:
            flash = pygame.Surface((W, H))
            flash.fill((255, 0, 0))
            flash.set_alpha(70)
            screen.blit(flash, (0, 0))

    if g["state"] in ("menu", "over"):
        shade_s = pygame.Surface((W, H))
        shade_s.set_alpha(150)
        shade_s.fill((0, 0, 0))
        screen.blit(shade_s, (0, 0))
        if g["state"] == "menu":
            t1 = big.render("RUNNER", True, (255, 200, 40))
            screen.blit(t1, t1.get_rect(center=(CX, 200)))
            lines = ["Zombies are chasing you!", "", "LEFT / RIGHT   change lane",
                     "UP / SPACE   jump", "DOWN   slide", "", "Press SPACE to start"]
        else:
            t1 = big.render("CAUGHT!", True, (230, 50, 50))
            screen.blit(t1, t1.get_rect(center=(CX, 200)))
            lines = [f"Score {score(g)}", f"Coins {g['coins']}", f"Best {best}", "", "Press R to run again"]
        for i, line in enumerate(lines):
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(CX, 290 + i * 36)))


# --------------------------------------------------------------------- main
def handle_key(g, key):
    if g["state"] == "menu":
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            return new_game("play")
    elif g["state"] == "over":
        if key == pygame.K_r:
            return new_game("play")
    else:
        if key in (pygame.K_LEFT, pygame.K_a):
            g["lane"] = max(-1, g["lane"] - 1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            g["lane"] = min(1, g["lane"] + 1)
        elif key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
            if g["pj"] == 0:
                g["vy"] = JUMP_V
                g["pj"] = 0.001
                g["slide"] = 0
        elif key in (pygame.K_DOWN, pygame.K_s):
            g["slide"] = 36
            if g["pj"] > 0:
                g["vy"] = -0.14
    return g


def main():
    global BEST
    game = new_game("menu")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game = handle_key(game, event.key)
        update(game)
        if game["state"] != "menu":
            BEST = max(BEST, score(game))
        draw_game(game, BEST)
        if game["shake"] > 0:
            frame = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(frame, (random.randint(-5, 5), random.randint(-5, 5)))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()