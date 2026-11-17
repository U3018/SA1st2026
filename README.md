# Knife Log

A small knife-throwing game made with Python 3 and the standard-library Tkinter GUI. It does not need pip packages.

## Run

```sh
python3 main.py
```

You can also run `./run.sh`.

Controls: click or press Space to throw. Press R to restart and Esc to quit.

The lower panel shows the remaining knife count and a preview of the next knife. The `THROW HERE` label and `v v v` marker show the fixed impact point at the top of the log.

## Editing

Change the constants near the top of `main.py` to adjust the window, log size, number of knives, rotation speed, collision range, and score. Change `COLORS` to adjust the palette.

The `KnifeGame` drawing methods are split by screen area:

- `draw_background`: background decorations
- `draw_header`: title and subtitle
- `draw_log`: rotating log
- `draw_throw_marker`: fixed knife impact point
- `draw_playfield`: stuck knives and target marker
- `draw_hud`: score and stage
- `draw_knife_status`: remaining count and knife preview panel
- `draw_ready_knife`: preview knife drawing
- `draw_overlay`: controls and game-over screen
