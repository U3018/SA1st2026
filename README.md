# SA1st2026

丸太にナイフを投げるゲームです。Python 3 と標準ライブラリの Tkinter で動作し、pip による追加パッケージのインストールは不要です。

## 起動

```sh
./run.sh
```

または `python3 main.py` で直接起動できます。Ubuntu/Debian の最小構成などで Tkinter がない場合は `sudo apt install python3-tk` が必要です。

操作: クリックまたは Space でナイフを投げます。R で最初から、Esc で終了します。

## コード構成

画面の各要素は `main.py` の `KnifeGame` クラス内の描画メソッドに分けています。見た目を調整するときは対応するメソッドを編集してください。

難易度や得点を変えるときは、`main.py` の先頭にある定数を編集します。たとえば `KNIVES_PER_ROUND` は1ステージのナイフ数、`START_ROTATION_SPEED` は最初の回転速度、`SPEED_UP_PER_ROUND` はステージごとの加速量、`COLLISION_ANGLE` はナイフ同士が当たる範囲、`POINTS_PER_KNIFE` は1本あたりの得点です。色は `COLORS` で変更できます。

- `draw_background`: 背景色と装飾
- `draw_header`: タイトルと説明
- `draw_log`: 丸太
- `draw_playfield`: 刺さったナイフ、照準、残りナイフ
- `draw_hud`: スコアとステージ表示
- `draw_overlay`: 操作案内とゲームオーバー表示
- `GameState`: ゲームの状態
- `throw_knife`: 投げる処理と当たり判定
