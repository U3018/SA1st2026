import math
import time
import tkinter as tk


WIDTH = 900
HEIGHT = 700
CENTER_X = WIDTH // 2
CENTER_Y = 315
LOG_RADIUS = 82
START_TIP_Y = 548
THROW_SPEED = 820
TARGET_ANGLE = math.pi / 2


class KnifeOrbitGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Knife Orbit")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#171b22",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.configure(takefocus=True)
        self.canvas.bind("<Button-1>", self.throw_knife)
        self.root.bind("<space>", self.throw_knife)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)

        self.level = 1
        self.start_level()
        self.last_update = time.perf_counter()
        self.root.after(100, self.canvas.focus_set)
        self.update()

    def start_level(self):
        self.knives_left = self.level + 9
        self.rotation = 0.0
        self.rotation_direction = 1 if self.level % 2 == 1 else -1
        self.rotation_speed = min(0.7 + (self.level - 1) * 0.16, 2.8)
        # The first knife gives each round an obstacle to watch.
        self.knives = [{"angle": 0.0}]
        self.projectile_y = START_TIP_Y
        self.state = "playing"

    def throw_knife(self, event=None):
        if self.state != "playing" or self.knives_left <= 0:
            return
        self.state = "throwing"
        self.projectile_y = START_TIP_Y

    def restart(self, event=None):
        self.level = 1
        self.start_level()

    def update(self):
        now = time.perf_counter()
        elapsed = min(now - self.last_update, 0.05)
        self.last_update = now

        if self.state in ("playing", "throwing"):
            self.rotation = (
                self.rotation
                + self.rotation_direction * self.rotation_speed * elapsed
            ) % (2 * math.pi)

        if self.state == "throwing":
            self.projectile_y -= THROW_SPEED * elapsed
            target_y = CENTER_Y + LOG_RADIUS - 4
            if self.projectile_y <= target_y:
                self.projectile_y = target_y
                self.finish_throw()

        self.draw()
        self.root.after(16, self.update)

    def finish_throw(self):
        self.knives_left -= 1
        collided = False

        for knife in self.knives:
            knife_world_angle = knife["angle"] + self.rotation
            difference = (knife_world_angle - TARGET_ANGLE + math.pi) % (
                2 * math.pi
            ) - math.pi
            if abs(difference) < 0.22:
                collided = True
                break

        if collided:
            self.state = "gameover"
            return

        # Store the angle relative to the log so this knife rotates with it.
        self.knives.append({"angle": TARGET_ANGLE - self.rotation})
        if self.knives_left == 0:
            self.state = "levelup"
            self.root.after(1100, self.next_level)
        else:
            self.state = "playing"

    def next_level(self):
        if self.state == "levelup":
            self.level += 1
            self.start_level()

    def draw(self):
        self.canvas.delete("all")
        self.draw_header()
        self.draw_arena()
        self.draw_footer()

        if self.state in ("gameover", "levelup"):
            self.draw_overlay()

    def draw_header(self):
        self.canvas.create_text(
            46,
            37,
            text="ARCADE  /  TIMING GAME",
            anchor="w",
            fill="#8e9aaa",
            font=("Arial", 10, "bold"),
        )
        self.canvas.create_text(
            44,
            72,
            text="KNIFE ORBIT",
            anchor="w",
            fill="#f2f4f7",
            font=("Arial", 24, "bold"),
        )

        self.canvas.create_text(
            666,
            43,
            text=f"LEVEL  {self.level:02d}",
            anchor="w",
            fill="#f2bd68",
            font=("Arial", 13, "bold"),
        )
        self.canvas.create_text(
            666,
            70,
            text=f"SPIN SPEED  {self.rotation_speed:.2f}",
            anchor="w",
            fill="#aeb8c5",
            font=("Arial", 10),
        )
        self.canvas.create_line(44, 105, WIDTH - 44, 105, fill="#303843", width=1)

    def draw_arena(self):
        orbit_radius = 130
        self.canvas.create_oval(
            CENTER_X - orbit_radius,
            CENTER_Y - orbit_radius,
            CENTER_X + orbit_radius,
            CENTER_Y + orbit_radius,
            outline="#39424f",
            width=1,
            dash=(3, 8),
        )

        self.draw_log()

        for knife in self.knives:
            angle = knife["angle"] + self.rotation
            tip_x = CENTER_X + math.cos(angle) * (LOG_RADIUS - 3)
            tip_y = CENTER_Y + math.sin(angle) * (LOG_RADIUS - 3)
            self.draw_knife(tip_x, tip_y, angle + math.pi, small=True)

        if self.state in ("playing", "throwing", "gameover"):
            if self.state in ("throwing", "gameover"):
                tip_y = self.projectile_y
            else:
                tip_y = START_TIP_Y
            self.draw_knife(CENTER_X, tip_y, -math.pi / 2)

    def draw_log(self):
        x1 = CENTER_X - LOG_RADIUS
        y1 = CENTER_Y - LOG_RADIUS
        x2 = CENTER_X + LOG_RADIUS
        y2 = CENTER_Y + LOG_RADIUS

        self.canvas.create_oval(
            x1 + 5,
            y1 + 8,
            x2 + 5,
            y2 + 8,
            fill="#0e1116",
            outline="",
        )
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill="#9b6034",
            outline="#e0a765",
            width=3,
        )
        self.canvas.create_oval(
            x1 + 9,
            y1 + 9,
            x2 - 9,
            y2 - 9,
            fill="#b87940",
            outline="#754626",
            width=2,
        )

        # These moving grain marks make the log's rotation easy to see.
        for index in range(8):
            angle = self.rotation + index * (2 * math.pi / 8)
            inner = 27
            outer = 64
            self.canvas.create_line(
                CENTER_X + math.cos(angle) * inner,
                CENTER_Y + math.sin(angle) * inner,
                CENTER_X + math.cos(angle) * outer,
                CENTER_Y + math.sin(angle) * outer,
                fill="#87532f",
                width=3,
                capstyle=tk.ROUND,
            )

        for index in range(3):
            angle = self.rotation + index * (2 * math.pi / 3) + 0.35
            knot_x = CENTER_X + math.cos(angle) * 43
            knot_y = CENTER_Y + math.sin(angle) * 43
            self.canvas.create_oval(
                knot_x - 5,
                knot_y - 5,
                knot_x + 5,
                knot_y + 5,
                outline="#754626",
                width=2,
            )

        self.canvas.create_oval(
            CENTER_X - 9,
            CENTER_Y - 9,
            CENTER_X + 9,
            CENTER_Y + 9,
            fill="#754626",
            outline="#e0a765",
            width=2,
        )

    def draw_knife(self, tip_x, tip_y, direction, small=False):
        blade_length = 23 if small else 26
        handle_length = 26 if small else 30
        blade_half_width = 4 if small else 5
        handle_half_width = 3 if small else 4

        unit_x = math.cos(direction)
        unit_y = math.sin(direction)
        side_x = -unit_y
        side_y = unit_x
        blade_base_x = tip_x - unit_x * blade_length
        blade_base_y = tip_y - unit_y * blade_length
        handle_end_x = blade_base_x - unit_x * handle_length
        handle_end_y = blade_base_y - unit_y * handle_length

        self.canvas.create_polygon(
            tip_x,
            tip_y,
            blade_base_x + side_x * blade_half_width,
            blade_base_y + side_y * blade_half_width,
            blade_base_x - side_x * blade_half_width,
            blade_base_y - side_y * blade_half_width,
            fill="#dce5ec",
            outline="#f7f9fb",
            width=1,
        )
        self.canvas.create_line(
            tip_x,
            tip_y,
            blade_base_x,
            blade_base_y,
            fill="#8393a2",
            width=1,
        )
        self.canvas.create_polygon(
            blade_base_x + side_x * handle_half_width,
            blade_base_y + side_y * handle_half_width,
            blade_base_x - side_x * handle_half_width,
            blade_base_y - side_y * handle_half_width,
            handle_end_x - side_x * handle_half_width,
            handle_end_y - side_y * handle_half_width,
            handle_end_x + side_x * handle_half_width,
            handle_end_y + side_y * handle_half_width,
            fill="#53362a",
            outline="#8b6144",
            width=1,
        )
        self.canvas.create_line(
            blade_base_x + side_x * 7,
            blade_base_y + side_y * 7,
            blade_base_x - side_x * 7,
            blade_base_y - side_y * 7,
            fill="#f2bd68",
            width=2,
        )

    def draw_footer(self):
        self.canvas.create_line(44, 630, WIDTH - 44, 630, fill="#303843", width=1)
        self.canvas.create_text(
            48,
            657,
            text=f"KNIVES  {self.knives_left}",
            anchor="w",
            fill="#f2f4f7",
            font=("Arial", 15, "bold"),
        )
        self.canvas.create_text(
            WIDTH - 48,
            657,
            text="SPACE / CLICK  THROW     •     R  RESTART",
            anchor="e",
            fill="#aeb8c5",
            font=("Arial", 10, "bold"),
        )

    def draw_overlay(self):
        self.canvas.create_rectangle(
            0,
            0,
            WIDTH,
            HEIGHT,
            fill="#101319",
            stipple="gray50",
            outline="",
        )
        self.canvas.create_rectangle(
            250,
            260,
            650,
            420,
            fill="#202630",
            outline="#586372",
            width=2,
        )

        if self.state == "gameover":
            title = "GAME OVER"
            message = "Press R to try again"
            color = "#ff8c78"
        else:
            title = "LEVEL CLEAR"
            message = f"Get ready for level {self.level + 1}"
            color = "#f2bd68"

        self.canvas.create_text(
            CENTER_X,
            315,
            text=title,
            fill=color,
            font=("Arial", 26, "bold"),
        )
        self.canvas.create_text(
            CENTER_X,
            365,
            text=message,
            fill="#d5dbe3",
            font=("Arial", 12),
        )


def main():
    root = tk.Tk()
    KnifeOrbitGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
