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
    labels = ['Play against the machine', 'Local multiplayer', 'Quit']

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
    fast = False
    autoroll = False

    def draw(screen, mp):
        _text(screen, "Play against the machine", _font(38), (60, 60, 60), (WIDTH // 2, 25))
        _text(screen, "Who goes first?", _font(26), (80, 80, 80), (WIDTH // 2, 80))
        r1 = pygame.Rect(WIDTH // 2 - 120, 115, 110, 50)
        r2 = pygame.Rect(WIDTH // 2 + 10, 115, 110, 50)
        _toggle(screen, r1, 'You', human_first, mp)
        _toggle(screen, r2, 'AI', not human_first, mp)

        _text(screen, "Autoroll (auto-roll the die)", _font(22), (80, 80, 80), (WIDTH // 2, 195))
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 220, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 220, 80, 40)
        _toggle(screen, r_ar_on, 'On', autoroll, mp)
        _toggle(screen, r_ar_off, 'Off', not autoroll, mp)

        _text(screen, "Fast mode (auto-move when only 1 option)", _font(22), (80, 80, 80), (WIDTH // 2, 285))
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 310, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 310, 80, 40)
        _toggle(screen, r_f_on, 'On', fast, mp)
        _toggle(screen, r_f_off, 'Off', not fast, mp)

        rs = pygame.Rect(WIDTH // 2 - 100, 385, 200, 55)
        rb = pygame.Rect(WIDTH // 2 - 100, 460, 200, 50)
        _button(screen, rs, 'Start!', True, mp)
        _button(screen, rb, 'Back', True, mp)

    def handle(ev):
        nonlocal human_first, fast, autoroll
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None
        r1 = pygame.Rect(WIDTH // 2 - 120, 115, 110, 50)
        r2 = pygame.Rect(WIDTH // 2 + 10, 115, 110, 50)
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 220, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 220, 80, 40)
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 310, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 310, 80, 40)
        rs = pygame.Rect(WIDTH // 2 - 100, 385, 200, 55)
        rb = pygame.Rect(WIDTH // 2 - 100, 460, 200, 50)
        if r1.collidepoint(ev.pos):
            human_first = True
        elif r2.collidepoint(ev.pos):
            human_first = False
        elif r_ar_on.collidepoint(ev.pos):
            autoroll = True
        elif r_ar_off.collidepoint(ev.pos):
            autoroll = False
        elif r_f_on.collidepoint(ev.pos):
            fast = True
        elif r_f_off.collidepoint(ev.pos):
            fast = False
        elif rs.collidepoint(ev.pos):
            return ('launch_ai', human_first, fast, autoroll)
        elif rb.collidepoint(ev.pos):
            return 'back'
        return None

    return _run_loop(pygame.display.set_mode((WIDTH, 540)), draw, handle)


def local_menu():
    nplayers = 4
    autoroll = False
    fast = False

    def draw(screen, mp):
        _text(screen, "Local Multiplayer", _font(38), (60, 60, 60), (WIDTH // 2, 25))
        _text(screen, "Number of players", _font(24), (80, 80, 80), (WIDTH // 2, 70))
        for i, n in enumerate([2, 3]):
            r = pygame.Rect(WIDTH // 2 - 125 + i * 130, 100, 100, 45)
            _toggle(screen, r, str(n), nplayers == n, mp)
        r4 = pygame.Rect(WIDTH // 2 - 50, 160, 100, 45)
        _toggle(screen, r4, '4', nplayers == 4, mp)

        _text(screen, "Autoroll (auto-roll the die)", _font(22), (80, 80, 80), (WIDTH // 2, 225))
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 250, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 250, 80, 40)
        _toggle(screen, r_ar_on, 'On', autoroll, mp)
        _toggle(screen, r_ar_off, 'Off', not autoroll, mp)

        _text(screen, "Fast mode (auto-move when only 1 option)", _font(22), (80, 80, 80), (WIDTH // 2, 315))
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 340, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 340, 80, 40)
        _toggle(screen, r_f_on, 'On', fast, mp)
        _toggle(screen, r_f_off, 'Off', not fast, mp)

        rs = pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
        rb = pygame.Rect(WIDTH // 2 - 100, 480, 200, 50)
        _button(screen, rs, 'Start!', True, mp)
        _button(screen, rb, 'Back', True, mp)

    def handle(ev):
        nonlocal nplayers, autoroll, fast
        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None
        for i, n in enumerate([2, 3]):
            r = pygame.Rect(WIDTH // 2 - 125 + i * 130, 100, 100, 45)
            if r.collidepoint(ev.pos):
                nplayers = n
        r4 = pygame.Rect(WIDTH // 2 - 50, 160, 100, 45)
        if r4.collidepoint(ev.pos):
            nplayers = 4
        r_ar_on = pygame.Rect(WIDTH // 2 - 95, 250, 80, 40)
        r_ar_off = pygame.Rect(WIDTH // 2 + 15, 250, 80, 40)
        if r_ar_on.collidepoint(ev.pos):
            autoroll = True
        elif r_ar_off.collidepoint(ev.pos):
            autoroll = False
        r_f_on = pygame.Rect(WIDTH // 2 - 95, 340, 80, 40)
        r_f_off = pygame.Rect(WIDTH // 2 + 15, 340, 80, 40)
        if r_f_on.collidepoint(ev.pos):
            fast = True
        elif r_f_off.collidepoint(ev.pos):
            fast = False
        rs = pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
        rb = pygame.Rect(WIDTH // 2 - 100, 480, 200, 50)
        if rs.collidepoint(ev.pos):
            return ('launch_local', nplayers, autoroll, fast)
        elif rb.collidepoint(ev.pos):
            return 'back'
        return None

    return _run_loop(pygame.display.set_mode((WIDTH, 550)), draw, handle)


if __name__ == '__main__':
    pygame.init()
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
                _, human_first, fast, autoroll = result
                pygame.quit()
                from play_vs_ai import run_vs_ai
                run_vs_ai(ai_first=not human_first, fast=fast, autoroll=autoroll)
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