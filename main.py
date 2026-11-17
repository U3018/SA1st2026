"""標準ライブラリだけで動く、丸太にナイフを投げるゲーム。"""

import math
import tkinter as tk
from dataclasses import dataclass, field

# 編集ポイント: 画面サイズ、丸太の位置、ゲームの難易度はここで調整できます。
WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, 260)
LOG_RADIUS = 112
KNIFE_RADIUS = 137
KNIVES_PER_ROUND = 8
START_ROTATION_SPEED = 1.35
SPEED_UP_PER_ROUND = 0.32
MAX_ROTATION_SPEED = 3.8
COLLISION_ANGLE = 0.20
POINTS_PER_KNIFE = 10
FRAME_MS = 16

COLORS = {
    "background": "#111a26",
    "cream": "#f4ead7",
    "muted": "#9aabba",
    "knife": "#e0e9ef",
    "handle": "#b47042",
    "log_outer": "#3b241a",
    "log": "#9b6038",
    "log_edge": "#d09a61",
    "gold": "#f4c95d",
}


@dataclass
class GameState:
    angle: float = 0.0
    speed: float = START_ROTATION_SPEED
    stuck: list[float] = field(default_factory=list)
    remaining: int = KNIVES_PER_ROUND
    score: int = 0
    level: int = 1
    game_over: bool = False

    def reset(self):
        self.angle = 0.0
        self.speed = START_ROTATION_SPEED
        self.stuck.clear()
        self.remaining = KNIVES_PER_ROUND
        self.score = 0
        self.level = 1
        self.game_over = False


class KnifeGame:
    """ゲーム状態、入力、描画をまとめる Tkinter アプリ。"""

    def __init__(self, root):
        self.root = root
        self.root.title("丸太にナイフ！")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=COLORS["background"], highlightthickness=0)
        self.canvas.pack()
        self.state = GameState()
        self.root.bind("<space>", self.on_throw)
        self.root.bind("<r>", self.on_reset)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()
        self.tick()

    # 個別の描画関数を編集すると、各画面要素の見た目を変更できます。
    def draw_background(self):
        self.canvas.configure(bg=COLORS["background"])
        for x, y in ((65, 72), (178, 130), (711, 90), (638, 174),
                     (91, 370), (724, 420), (220, 480)):
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#415263", outline="")

    def draw_header(self):
        self.canvas.create_text(WIDTH // 2, 39, text="丸太にナイフ！",
                                fill=COLORS["cream"], font=("TkDefaultFont", 20, "bold"))
        self.canvas.create_text(WIDTH // 2, 70, text="回転する丸太に、ナイフをすき間なく刺そう",
                                fill=COLORS["muted"], font=("TkDefaultFont", 11))

    def draw_log(self):
        x, y = CENTER
        r = LOG_RADIUS
        self.canvas.create_oval(x-r-9, y-r-9, x+r+9, y+r+9, fill=COLORS["log_outer"], outline="")
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=COLORS["log"], outline=COLORS["log_edge"], width=3)
        for radius, color, width in ((89, "#754327", 3), (62, "#b57b4b", 2), (34, "#754327", 3)):
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                    outline=color, width=width)
        self.canvas.create_oval(x-7, y-7, x+7, y+7, fill="#593722", outline="")

    def draw_knife(self, angle, radius, scale=1.0):
        x = CENTER[0] + math.cos(angle) * radius
        y = CENTER[1] + math.sin(angle) * radius
        blade_x, blade_y = x - math.cos(angle) * 25 * scale, y - math.sin(angle) * 25 * scale
        handle_x, handle_y = x - math.cos(angle) * 37 * scale, y - math.sin(angle) * 37 * scale
        self.canvas.create_line(x, y, blade_x, blade_y, fill=COLORS["knife"],
                                width=max(2, 5 * scale), capstyle=tk.ROUND)
        self.canvas.create_line(blade_x, blade_y, handle_x, handle_y, fill=COLORS["handle"],
                                width=max(3, 9 * scale), capstyle=tk.ROUND)
        self.canvas.create_oval(x-3*scale, y-3*scale, x+3*scale, y+3*scale,
                                fill="#f7f9fa", outline="")

    def draw_playfield(self):
        state = self.state
        for angle in state.stuck:
            self.draw_knife(angle + state.angle, KNIFE_RADIUS, 0.9)
        marker_angle = state.angle - math.pi / 2
        mx = CENTER[0] + math.cos(marker_angle) * 78
        my = CENTER[1] + math.sin(marker_angle) * 78
        self.canvas.create_oval(mx-8, my-8, mx+8, my+8, fill=COLORS["gold"], outline="#fff0ae", width=2)
        for i in range(state.remaining):
            self.draw_knife(math.pi / 2, 194 + i * 24, 0.58)

    def draw_hud(self):
        state = self.state
        self.canvas.create_text(48, 130, anchor="w", text=f"SCORE  {state.score:04d}",
                                fill=COLORS["cream"], font=("TkDefaultFont", 13, "bold"))
        self.canvas.create_text(WIDTH - 48, 130, anchor="e", text=f"STAGE  {state.level}",
                                fill=COLORS["cream"], font=("TkDefaultFont", 13, "bold"))

    def draw_overlay(self):
        state = self.state
        if state.game_over:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#05090f", stipple="gray50", outline="")
            self.canvas.create_text(WIDTH//2, 250, text="GAME OVER", fill="#ff8070",
                                    font=("TkDefaultFont", 22, "bold"))
            self.canvas.create_text(WIDTH//2, 292, text=f"スコア  {state.score}",
                                    fill=COLORS["cream"], font=("TkDefaultFont", 14, "bold"))
            self.canvas.create_text(WIDTH//2, 334, text="クリック / Space でリトライ",
                                    fill="#c1ced8", font=("TkDefaultFont", 11))
        else:
            self.canvas.create_text(WIDTH//2, 520, text="クリック または Space で投げる",
                                    fill=COLORS["cream"], font=("TkDefaultFont", 13, "bold"))
            self.canvas.create_text(WIDTH//2, 552,
                                    text="刺さったナイフに当たると終了  ·  R で最初から  ·  Esc で終了",
                                    fill="#8293a2", font=("TkDefaultFont", 10))

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_header()
        self.draw_log()
        self.draw_playfield()
        self.draw_hud()
        self.draw_overlay()

    def throw_knife(self):
        state = self.state
        if state.game_over:
            return
        impact = -math.pi / 2 - state.angle
        collision = any(abs((impact - old + math.pi) % (2 * math.pi) - math.pi) < COLLISION_ANGLE
                        for old in state.stuck)
        if collision:
            state.game_over = True
        else:
            state.stuck.append(impact)
            state.score += POINTS_PER_KNIFE
            state.remaining -= 1
            if state.remaining == 0:
                state.level += 1
                state.remaining = KNIVES_PER_ROUND
                state.speed = min(state.speed + SPEED_UP_PER_ROUND, MAX_ROTATION_SPEED)
                state.stuck.clear()

    def on_throw(self, _event=None):
        if self.state.game_over:
            self.state.reset()
        else:
            self.throw_knife()
        self.draw()

    def on_reset(self, _event=None):
        self.state.reset()
        self.draw()

    def on_click(self, _event=None):
        self.on_throw()

    def tick(self):
        if not self.state.game_over:
            self.state.angle += self.state.speed * FRAME_MS / 1000
        self.draw()
        self.root.after(FRAME_MS, self.tick)


def main():
    root = tk.Tk()
    KnifeGame(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
