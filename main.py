"""Rotating log knife game. Install with `python3 -m pip install pygame` then run."""

import math
import random
import sys

import pygame

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, 260)
LOG_R = 112
KNIFE_R = 137
KNIVES_PER_ROUND = 8
BG = (17, 26, 38)


def draw_knife(surface, angle, radius, scale=1.0, color=(224, 233, 239)):
    x = CENTER[0] + math.cos(angle) * radius
    y = CENTER[1] + math.sin(angle) * radius
    tip = (round(x), round(y))
    blade_end = (round(x - math.cos(angle) * 25 * scale), round(y - math.sin(angle) * 25 * scale))
    handle_end = (round(x - math.cos(angle) * 37 * scale), round(y - math.sin(angle) * 37 * scale))
    pygame.draw.line(surface, color, tip, blade_end, max(2, round(5 * scale)))
    pygame.draw.line(surface, (180, 112, 66), blade_end, handle_end, max(3, round(9 * scale)))
    pygame.draw.circle(surface, (247, 249, 250), tip, max(2, round(3 * scale)))


def main():
    pygame.init()
    pygame.display.set_caption("丸太にナイフ！")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    # Try Japanese-capable fonts, with a system default fallback.
    font_name = next((name for name in ("Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "Meiryo")
                      if pygame.font.match_font(name)), None)
    title_font = pygame.font.SysFont(font_name, 27, bold=True)
    ui_font = pygame.font.SysFont(font_name, 18, bold=True)
    small_font = pygame.font.SysFont(font_name, 14)

    angle, speed, stuck = 0.0, 1.35, []
    remaining, score, level = KNIVES_PER_ROUND, 0, 1
    game_over = False
    running = True

    def reset():
        return 0.0, 1.35, [], KNIVES_PER_ROUND, 0, 1, False

    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r or (game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN)):
                    angle, speed, stuck, remaining, score, level, game_over = reset()
                elif event.key == pygame.K_SPACE and not game_over:
                    local_impact = -math.pi / 2 - angle
                    if any(abs((local_impact - old + math.pi) % (2 * math.pi) - math.pi) < 0.20 for old in stuck):
                        game_over = True
                    else:
                        stuck.append(local_impact)
                        score += 10
                        remaining -= 1
                        if remaining == 0:
                            level += 1
                            remaining = KNIVES_PER_ROUND
                            speed = min(speed + 0.32, 3.8)
                            stuck.clear()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    angle, speed, stuck, remaining, score, level, game_over = reset()
                else:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

        if not game_over:
            angle += speed * dt
        screen.fill(BG)
        for x, y in ((65, 72), (178, 130), (711, 90), (638, 174), (91, 370), (724, 420), (220, 480)):
            pygame.draw.circle(screen, (65, 82, 99), (x, y), 2)
        screen.blit(title_font.render("丸太にナイフ！", True, (244, 234, 215)), (WIDTH // 2 - 90, 26))
        screen.blit(small_font.render("回転する丸太に、ナイフをすき間なく刺そう", True, (154, 171, 186)), (WIDTH // 2 - 130, 63))
        pygame.draw.circle(screen, (59, 36, 26), CENTER, LOG_R + 9)
        pygame.draw.circle(screen, (155, 96, 56), CENTER, LOG_R)
        pygame.draw.circle(screen, (208, 154, 97), CENTER, LOG_R, 3)
        for radius, color, width in ((89, (117, 67, 39), 3), (62, (181, 123, 75), 2), (34, (117, 67, 39), 3)):
            pygame.draw.circle(screen, color, CENTER, radius, width)
        pygame.draw.circle(screen, (89, 55, 34), CENTER, 7)
        for old in stuck:
            draw_knife(screen, old + angle, KNIFE_R, 0.9)
        marker_angle = angle - math.pi / 2
        marker = (round(CENTER[0] + math.cos(marker_angle) * 78), round(CENTER[1] + math.sin(marker_angle) * 78))
        pygame.draw.circle(screen, (244, 201, 93), marker, 8)
        pygame.draw.circle(screen, (255, 240, 174), marker, 8, 2)
        screen.blit(ui_font.render(f"SCORE  {score:04d}", True, (244, 234, 215)), (48, 121))
        stage = ui_font.render(f"STAGE  {level}", True, (244, 234, 215))
        screen.blit(stage, (WIDTH - 48 - stage.get_width(), 121))
        for i in range(remaining):
            draw_knife(screen, math.pi / 2, 194 + i * 24, 0.58)
        if game_over:
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((5, 9, 15, 190))
            screen.blit(shade, (0, 0))
            for label, y, font, color in (("GAME OVER", 236, title_font, (255, 128, 111)),
                                           (f"スコア  {score}", 283, ui_font, (244, 234, 215)),
                                           ("クリック / Space でリトライ", 326, small_font, (193, 206, 216))):
                image = font.render(label, True, color)
                screen.blit(image, (WIDTH // 2 - image.get_width() // 2, y))
        else:
            hint = ui_font.render("クリック または Space で投げる", True, (244, 234, 215))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 520))
            foot = small_font.render("刺さったナイフに当たると終了  ·  R で最初から  ·  Esc で終了", True, (130, 147, 162))
            screen.blit(foot, (WIDTH // 2 - foot.get_width() // 2, 552))
        pygame.display.flip()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
