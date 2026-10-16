import pygame
import sys

WIDTH, HEIGHT = 500, 500
BG = (245, 235, 220)

def _font(size):
    return pygame.font.Font(None, size)

def _text(screen, text, font, color, center):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=center))

def _button(screen, rect, label, clickable, mp):
    hover = clickable and rect.collidepoint(mp) if mp else False
    color = (60, 130, 60) if hover else (80, 160, 80) if clickable else (180, 70, 70)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    if clickable:
        pygame.draw.rect(screen, (40, 40, 40), rect, width=2, border_radius=8)
    _text(screen, label, _font(26), (255, 255, 255), rect.center)

def _toggle(screen, rect, label, active, mp):
    color = (50, 150, 50) if active else (180, 70, 70)
    if rect.collidepoint(mp) if mp else False:
        color = tuple(min(255, c + 25) for c in color)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, (40, 40, 40), rect, width=2, border_radius=6)
    _text(screen, label, _font(24), (255, 255, 255), rect.center)

def _wait_for_launch():
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            return 'quit'
    return None

def _run_loop(screen, draw_fn, handle_fn):
    clock = pygame.time.Clock()
    result = None
    while result is None:
        mx, my = pygame.mouse.get_pos()
        mp = (mx, my) if pygame.mouse.get_focused() else None
        screen.fill(BG)
        draw_fn(screen, mp)
        pygame.display.flip()
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            r = handle_fn(ev)
            if r is not None:
                result = r
    return result


def main_menu():
    labels = ['Play against AI', 'Local multiplayer', 'Quit']

    def draw(screen, mp):
        _text(screen, "Man, don't be annoyed!", _font(42), (60, 60, 60), (WIDTH // 2, 45))
        for i, label in enumerate(labels):
            rect = pygame.Rect(WIDTH // 2 - 140, 130 + i * 90, 280, 60)
            _button(screen, rect, label, True, mp)

    def handle(ev):
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None
        for i, label in enumerate(labels):
            rect = pygame.Rect(WIDTH // 2 - 140, 130 + i * 90, 280, 60)
            if rect.collidepoint(ev.pos):
                return ['ai', 'local', 'quit'][i]
        return None

    return _run_loop(pygame.display.set_mode((WIDTH, HEIGHT)), draw, handle)


def ai_menu():
    human_first = True

    def draw(screen, mp):
        _text(screen, "Play against AI", _font(38), (60, 60, 60), (WIDTH // 2, 40))
        _text(screen, "Who goes first?", _font(26), (80, 80, 80), (WIDTH // 2, 105))
        r1 = pygame.Rect(WIDTH // 2 - 120, 140, 110, 50)
        r2 = pygame.Rect(WIDTH // 2 + 10, 140, 110, 50)
        _toggle(screen, r1, 'You', human_first, mp)
        _toggle(screen, r2, 'AI', not human_first, mp)
        rs = pygame.Rect(WIDTH // 2 - 100, 240, 200, 55)
        rb = pygame.Rect(WIDTH // 2 - 100, 330, 200, 50)
        _button(screen, rs, 'Start!', True, mp)
        _button(screen, rb, 'Back', True, mp)

    def handle(ev):
        nonlocal human_first
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None
        r1 = pygame.Rect(WIDTH // 2 - 120, 140, 110, 50)
        r2 = pygame.Rect(WIDTH // 2 + 10, 140, 110, 50)
        rs = pygame.Rect(WIDTH // 2 - 100, 240, 200, 55)
        rb = pygame.Rect(WIDTH // 2 - 100, 330, 200, 50)
        if r1.collidepoint(ev.pos):
            human_first = True
        elif r2.collidepoint(ev.pos):
            human_first = False
        elif rs.collidepoint(ev.pos):
            return ('launch_ai', human_first)
        elif rb.collidepoint(ev.pos):
            return 'back'
        return None

    return _run_loop(pygame.display.set_mode((WIDTH, HEIGHT + 60)), draw, handle)


def local_menu():
    nplayers = 4
    autoroll = False
    fast = False

    def draw(screen, mp):
        _text(screen, "Local Multiplayer", _font(38), (60, 60, 60), (WIDTH // 2, 30))
        _text(screen, "Number of players", _font(24), (80, 80, 80), (WIDTH // 2, 80))
        for i, n in enumerate([2, 3, 4]):
            r = pygame.Rect(110 + i * 140, 110, 110, 45)
            _toggle(screen, r, str(n), nplayers == n, mp)
        _text(screen, "Autoroll", _font(24), (80, 80, 80), (WIDTH // 2, 180))
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 205, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 205, 80, 40)
        _toggle(screen, r_ar_on, 'On', autoroll, mp)
        _toggle(screen, r_ar_off, 'Off', not autoroll, mp)
        _text(screen, "Fast mode", _font(24), (80, 80, 80), (WIDTH // 2, 270))
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 295, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 295, 80, 40)
        _toggle(screen, r_f_on, 'On', fast, mp)
        _toggle(screen, r_f_off, 'Off', not fast, mp)
        rs = pygame.Rect(WIDTH // 2 - 100, 365, 200, 50)
        rb = pygame.Rect(WIDTH // 2 - 100, 440, 200, 50)
        _button(screen, rs, 'Start!', True, mp)
        _button(screen, rb, 'Back', True, mp)

    def handle(ev):
        nonlocal nplayers, autoroll, fast
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None
        for i, n in enumerate([2, 3, 4]):
            r = pygame.Rect(110 + i * 140, 110, 110, 45)
            if r.collidepoint(ev.pos):
                nplayers = n
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 205, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 205, 80, 40)
        if r_ar_on.collidepoint(ev.pos):
            autoroll = True
        elif r_ar_off.collidepoint(ev.pos):
            autoroll = False
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 295, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 295, 80, 40)
        if r_f_on.collidepoint(ev.pos):
            fast = True
        elif r_f_off.collidepoint(ev.pos):
            fast = False
        rs = pygame.Rect(WIDTH // 2 - 100, 365, 200, 50)
        rb = pygame.Rect(WIDTH // 2 - 100, 440, 200, 50)
        if rs.collidepoint(ev.pos):
            return ('launch_local', nplayers, autoroll, fast)
        elif rb.collidepoint(ev.pos):
            return 'back'
        return None

    return _run_loop(pygame.display.set_mode((WIDTH, 520)), draw, handle)


if __name__ == '__main__':
    while True:
        choice = main_menu()
        if choice == 'quit':
            pygame.quit()
            sys.exit()
        elif choice == 'ai':
            result = ai_menu()
            if result == 'quit':
                pygame.quit()
                sys.exit()
            elif result == 'back':
                continue
            elif result[0] == 'launch_ai':
                _, human_first = result
                pygame.quit()
                from play_vs_ai import run_vs_ai
                run_vs_ai(ai_first=not human_first)
                sys.exit()
        elif choice == 'local':
            result = local_menu()
            if result == 'quit':
                pygame.quit()
                sys.exit()
            elif result == 'back':
                continue
            elif result[0] == 'launch_local':
                _, nplayers, autoroll, fast = result
                pygame.quit()
                from game import Game
                game = Game(nplayers, fast, autoroll)
                game.run_game()
                sys.exit()