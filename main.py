# -*- coding: utf-8 -*-
"""Python標準ライブラリのTkinterで作ったナイフゲーム。"""

import math
import tkinter as tk
from dataclasses import dataclass, field

# --- 画面サイズとゲーム難易度の設定 ---
WIDTH, HEIGHT = 1040, 760  # ゲーム画面の幅と高さ（ピクセル）。
CENTER = (WIDTH // 2, HEIGHT // 2 - 70)  # 丸太の中心。下側にナイフ表示欄を確保する。
LOG_RADIUS = 122  # 丸太の半径。
KNIFE_RADIUS = 154  # 丸太の中心からナイフを描画する距離。
KNIVES_PER_ROUND = 8  # 1ステージで投げられるナイフの本数。
START_ROTATION_SPEED = 1.35  # 最初の回転速度（ラジアン/秒）。
SPEED_UP_PER_ROUND = 0.32  # ステージクリアごとに加算する回転速度。
MAX_ROTATION_SPEED = 3.8  # 難しくなりすぎないようにする回転速度の上限。
COLLISION_ANGLE = 0.20  # ナイフ同士が衝突する角度の範囲（ラジアン）。
POINTS_PER_KNIFE = 10  # ナイフを1本刺すごとに加算する得点。
FRAME_MS = 16  # 描画更新の間隔。約60フレーム/秒。

# 色を変えると、画面の対応する部分の色が変わる。
COLORS = {
    "background": "#111a26",  # 画面全体の背景。
    "cream": "#f4ead7",  # 主な文字や明るい部分。
    "muted": "#9aabba",  # 補足ラベル。
    "knife": "#e0e9ef",  # ナイフの刃。
    "handle": "#b47042",  # ナイフの持ち手。
    "log_outer": "#3b241a",  # 丸太の外側の影。
    "log": "#9b6038",  # 丸太の表面。
    "log_edge": "#d09a61",  # 丸太の縁。
    "gold": "#f4c95d",  # 投げる位置の目印や強調部分。
}


@dataclass
class GameState:
    """ゲーム中に変化する状態をまとめる。"""

    angle: float = 0.0  # 丸太が今どれだけ回転したか。
    speed: float = START_ROTATION_SPEED  # 現在の回転速度。
    stuck: list[float] = field(default_factory=list)  # 丸太に刺さったナイフの角度。
    remaining: int = KNIVES_PER_ROUND  # このステージで残っているナイフ。
    score: int = 0  # これまでに獲得した合計得点。
    level: int = 1  # 現在のステージ番号。
    game_over: bool = False  # Trueの間は回転を止め、リトライ画面を表示する。

    def reset(self):
        """ゲームの状態をすべて初期値に戻す。"""
        self.angle = 0.0
        self.speed = START_ROTATION_SPEED
        self.stuck.clear()
        self.remaining = KNIVES_PER_ROUND
        self.score = 0
        self.level = 1
        self.game_over = False


class KnifeGame:
    """ゲーム状態、入力処理、画面描画をまとめるTkinterアプリ。"""

    def __init__(self, root):
        self.root = root
        self.root.title("Knife Log")  # ウィンドウ枠に表示するタイトル。
        self.root.resizable(False, False)  # 固定レイアウトに合わせ、ウィンドウの拡大縮小を無効にする。
        # 丸太、ナイフ、文字、カードを描くキャンバス。
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=COLORS["background"], highlightthickness=0)
        self.canvas.pack()
        self.state = GameState()
        # キーとマウスの操作を、それぞれ投げる・リセットする処理につなぐ。
        self.root.bind("<space>", self.on_throw)
        self.root.bind("<r>", self.on_reset)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()
        self.tick()

    def text_font(self, size, bold=False):
        """画面内の文字に使う標準フォントの設定を返す。"""
        if bold:
            return ("TkDefaultFont", size, "bold")
        return ("TkDefaultFont", size)

    def draw_background(self):
        """背景色と小さな星の飾りを描く。"""
        self.canvas.configure(bg=COLORS["background"])
        # 星の座標。スコアやステージ表示に重ならない位置に置く。
        for x, y in ((80, 100), (230, 160), (960, 108), (850, 170),
                     (90, 450), (955, 490), (300, 520), (750, 455)):
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#415263", outline="")

    def draw_header(self):
        """ゲームタイトルと短い説明を描く。"""
        self.canvas.create_text(WIDTH // 2, 42, text="KNIFE LOG",
                                fill=COLORS["cream"], font=self.text_font(20, bold=True))
        self.canvas.create_text(WIDTH // 2, 76, text="Throw knives at the spinning log",
                                fill=COLORS["muted"], font=self.text_font(11))

    def draw_log(self):
        """丸太の本体、縁、年輪、中心を描く。"""
        x, y = CENTER
        r = LOG_RADIUS
        # 一回り大きい暗い円で丸太の影を作る。
        self.canvas.create_oval(x-r-9, y-r-9, x+r+9, y+r+9, fill=COLORS["log_outer"], outline="")
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=COLORS["log"], outline=COLORS["log_edge"], width=3)
        # 同心円を重ねて、切り株の年輪を表現する。
        for radius, color, width in ((89, "#754327", 3), (62, "#b57b4b", 2), (34, "#754327", 3)):
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                    outline=color, width=width)
        self.canvas.create_oval(x-7, y-7, x+7, y+7, fill="#593722", outline="")

    def draw_knife(self, angle, radius, scale=1.0):
        """丸太の中心から指定距離・角度の位置にナイフを描く。"""
        x = CENTER[0] + math.cos(angle) * radius
        y = CENTER[1] + math.sin(angle) * radius
        # 1本目の線が刃、2本目の線が持ち手。
        blade_x, blade_y = x - math.cos(angle) * 25 * scale, y - math.sin(angle) * 25 * scale
        handle_x, handle_y = x - math.cos(angle) * 37 * scale, y - math.sin(angle) * 37 * scale
        self.canvas.create_line(x, y, blade_x, blade_y, fill=COLORS["knife"],
                                width=max(2, 5 * scale), capstyle=tk.ROUND)
        self.canvas.create_line(blade_x, blade_y, handle_x, handle_y, fill=COLORS["handle"],
                                width=max(3, 9 * scale), capstyle=tk.ROUND)
        self.canvas.create_oval(x-3*scale, y-3*scale, x+3*scale, y+3*scale,
                                fill="#f7f9fa", outline="")

    def draw_throw_marker(self):
        """ナイフが当たる丸太の真上の位置を示す。"""
        target_x = CENTER[0]
        target_y = CENTER[1] - LOG_RADIUS
        # ラベルで狙う場所を示し、v印で丸太の縁を指す。
        self.canvas.create_text(
            target_x, target_y - 48,
            text="THROW HERE", fill=COLORS["gold"],
            font=self.text_font(11, bold=True)
        )
        self.canvas.create_text(
            target_x, target_y - 23,
            text="v v v", fill=COLORS["gold"],
            font=self.text_font(17, bold=True)
        )
        # 金色のリングが丸太表面の着弾位置。
        self.canvas.create_oval(
            target_x - 10, target_y - 10,
            target_x + 10, target_y + 10,
            fill=COLORS["background"], outline=COLORS["gold"], width=3
        )

    def draw_playfield(self):
        """固定された狙い位置と、丸太と一緒に回るナイフを描く。"""
        self.draw_throw_marker()
        for angle in self.state.stuck:
            self.draw_knife(angle + self.state.angle, KNIFE_RADIUS, 0.9)

    def draw_hud(self):
        """左にスコア、右にステージ番号を表示する。"""
        state = self.state
        self.canvas.create_text(100, 132, anchor="w", text=f"SCORE  {state.score:04d}",
                                fill=COLORS["cream"], font=self.text_font(13, bold=True))
        self.canvas.create_text(WIDTH - 100, 132, anchor="e", text=f"STAGE  {state.level}",
                                fill=COLORS["cream"], font=self.text_font(13, bold=True))

    def draw_ready_knife(self, center_x, center_y):
        """次に投げるナイフを横向きに描く。刃先は左向き。"""
        # 銀色の多角形が刃。左端を細くして鋭い先端にする。
        blade_points = (
            center_x - 72, center_y,
            center_x - 15, center_y - 12,
            center_x - 5, center_y - 8,
            center_x - 5, center_y + 8,
            center_x - 15, center_y + 12,
        )
        self.canvas.create_polygon(
            blade_points, fill=COLORS["knife"], outline="#ffffff", width=2
        )
        # 細い白線で刃の縁にハイライトを入れる。
        self.canvas.create_line(
            center_x - 70, center_y,
            center_x - 18, center_y - 8,
            fill="#ffffff", width=2
        )
        # 金色の鍔で刃と持ち手を分ける。
        self.canvas.create_polygon(
            center_x - 5, center_y - 15,
            center_x + 2, center_y - 12,
            center_x + 2, center_y + 12,
            center_x - 5, center_y + 15,
            fill=COLORS["gold"], outline="#d9b45a", width=1
        )
        # 茶色の多角形が持ち手。短い線で表面の模様を付ける。
        self.canvas.create_polygon(
            center_x + 2, center_y - 8,
            center_x + 53, center_y - 8,
            center_x + 64, center_y,
            center_x + 53, center_y + 8,
            center_x + 2, center_y + 8,
            fill=COLORS["handle"], outline="#e0a16c", width=2
        )
        for offset in (18, 30, 42):
            self.canvas.create_line(
                center_x + offset, center_y - 6,
                center_x + offset + 6, center_y + 6,
                fill="#d69a70", width=2
            )

    def draw_knife_status(self):
        """残り本数カウンターと次のナイフのプレビューを描く。"""
        # 画面幅を変えても2つのカードが中央に並ぶように配置する。
        card_top, card_bottom = HEIGHT - 212, HEIGHT - 86
        card_width, card_gap = 245, 110
        group_left = (WIDTH - (card_width * 2 + card_gap)) // 2
        counter_left, counter_right = group_left, group_left + card_width
        knife_left, knife_right = counter_right + card_gap, counter_right + card_gap + card_width
        for left, right in ((counter_left, counter_right), (knife_left, knife_right)):
            # 同じ見た目のカードにして、カウンターとプレビューをひとまとまりにする。
            self.canvas.create_rectangle(
                left, card_top, right, card_bottom,
                fill="#1a2735", outline="#344656", width=2
            )

        # カウンターカードの見出し。下の大きな数字が残り本数。
        self.canvas.create_text(
            counter_left + 22, card_top + 25,
            anchor="w", text="KNIVES LEFT",
            fill=COLORS["muted"], font=self.text_font(12, bold=True)
        )
        self.canvas.create_text(
            counter_left + 24, card_top + 77,
            anchor="w", text=f"{self.state.remaining:02d}",
            fill=COLORS["cream"], font=self.text_font(32, bold=True)
        )
        # スラッシュの後ろはステージ開始時の本数。
        self.canvas.create_text(
            counter_left + 86, card_top + 82,
            anchor="w", text=f"/ {KNIVES_PER_ROUND}",
            fill=COLORS["muted"], font=self.text_font(13)
        )

        # クリックまたはSpaceキーで次に投げるナイフのプレビュー。
        self.canvas.create_text(
            knife_left + 20, card_top + 25,
            anchor="w", text="NEXT KNIFE",
            fill=COLORS["muted"], font=self.text_font(12, bold=True)
        )
        self.draw_ready_knife((knife_left + knife_right) // 2, card_top + 82)

    def draw_overlay(self):
        """ゲーム中は操作方法、衝突後はリトライ案内を表示する。"""
        state = self.state
        if state.game_over:
            # 画面全体を暗くして、その上に最終スコアを表示する。
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#05090f", stipple="gray50", outline="")
            self.canvas.create_text(WIDTH//2, HEIGHT//2 - 80, text="GAME OVER", fill="#ff8070",
                                    font=self.text_font(22, bold=True))
            self.canvas.create_text(WIDTH//2, HEIGHT//2 - 34, text=f"Score: {state.score}",
                                    fill=COLORS["cream"], font=self.text_font(14, bold=True))
            self.canvas.create_text(WIDTH//2, HEIGHT//2 + 10, text="Click or press Space to retry",
                                    fill="#c1ced8", font=self.text_font(11))
        else:
            # 投げる操作とリセット・終了キーを画面下部に表示する。
            self.canvas.create_text(WIDTH//2, HEIGHT - 50, text="Click or press Space to throw",
                                    fill=COLORS["cream"], font=self.text_font(13, bold=True))
            self.canvas.create_text(WIDTH//2, HEIGHT - 20,
                                    text="Hit another knife to lose  |  R: restart  |  Esc: quit",
                                    fill="#8293a2", font=self.text_font(10))

    def draw(self):
        """画面を消去し、奥にあるものから順に描き直す。"""
        self.canvas.delete("all")
        self.draw_background()
        self.draw_header()
        self.draw_log()
        self.draw_playfield()
        self.draw_hud()
        self.draw_knife_status()
        self.draw_overlay()

    def throw_knife(self):
        """着弾位置の衝突を調べ、ナイフ・得点・ゲーム状態を更新する。"""
        state = self.state
        if state.game_over:
            return
        # 固定された画面上部の着弾位置を、回転中の丸太の角度に変換する。
        impact = -math.pi / 2 - state.angle
        # 角度差を-piからpiの範囲に折り返し、近くのナイフと比較する。
        collision = any(abs((impact - old + math.pi) % (2 * math.pi) - math.pi) < COLLISION_ANGLE
                        for old in state.stuck)
        if collision:
            state.game_over = True
        else:
            # 衝突しなければナイフを追加し、得点と残り本数を更新する。
            state.stuck.append(impact)
            state.score += POINTS_PER_KNIFE
            state.remaining -= 1
            if state.remaining == 0:
                # ステージをクリアしたら次を加速し、丸太上のナイフを消す。
                state.level += 1
                state.remaining = KNIVES_PER_ROUND
                state.speed = min(state.speed + SPEED_UP_PER_ROUND, MAX_ROTATION_SPEED)
                state.stuck.clear()

    def on_throw(self, _event=None):
        """投げる操作。ゲームオーバー中は同じ操作でリトライする。"""
        if self.state.game_over:
            self.state.reset()
        else:
            self.throw_knife()
        self.draw()

    def on_reset(self, _event=None):
        """どの状態からでもゲームを最初からやり直す。"""
        self.state.reset()
        self.draw()

    def on_click(self, _event=None):
        """キャンバスのクリックを投げる操作として扱う。"""
        self.on_throw()

    def tick(self):
        """丸太を回転させ、次のアニメーション更新を予約する。"""
        if not self.state.game_over:
            self.state.angle += self.state.speed * FRAME_MS / 1000
        self.draw()
        self.root.after(FRAME_MS, self.tick)


def main():
    """ウィンドウを作成してTkinterのイベントループを開始する。"""
    root = tk.Tk()
    KnifeGame(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
