import flet as ft
import json
import os
from datetime import datetime

DATA_FILE = "savings_data.json"

EUR_TO_MKD = 61.5  # approximate fixed rate


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"goal": None, "target": 0.0, "saved": 0.0, "currency": "MKD", "history": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fmt(amount, currency):
    if currency == "MKD":
        return f"{amount:,.0f} ден"
    else:
        return f"€{amount:,.2f}"


def convert(amount, from_cur, to_cur):
    if from_cur == to_cur:
        return amount
    if from_cur == "EUR" and to_cur == "MKD":
        return amount * EUR_TO_MKD
    if from_cur == "MKD" and to_cur == "EUR":
        return amount / EUR_TO_MKD
    return amount


def main(page: ft.Page):
    page.title = "SaveUp"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0A0A0F"
    page.padding = 0
    page.fonts = {
        "Syne": "https://fonts.gstatic.com/s/syne/v22/8vIS7w4qzmVxsWxjEKc.woff2",
        "JetBrains": "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOV.woff2",
    }
    page.theme = ft.Theme(font_family="Syne")

    data = load_data()

    # ── State refs ──────────────────────────────────────────
    view_stack = []  # "setup" | "main"

    # ── Helpers ─────────────────────────────────────────────
    def progress_pct():
        if data["target"] <= 0:
            return 0.0
        return min(data["saved"] / data["target"], 1.0)

    def push_history(action, amount, currency):
        data["history"].insert(0, {
            "action": action,
            "amount": amount,
            "currency": currency,
            "date": datetime.now().strftime("%d %b %Y, %H:%M"),
        })
        if len(data["history"]) > 100:
            data["history"] = data["history"][:100]
        save_data(data)

    # ═══════════════════════════════════════════════════════
    #  SETUP SCREEN
    # ═══════════════════════════════════════════════════════
    def build_setup_screen():
        goal_field = ft.TextField(
            label="What are you saving for?",
            hint_text="e.g. New iPhone, Vacation, Car...",
            border_color="#3D3D5C",
            focused_border_color="#7C6FFF",
            label_style=ft.TextStyle(color="#9090B0"),
            color="#FFFFFF",
            bgcolor="#13131F",
            border_radius=14,
            text_size=16,
        )

        amount_field = ft.TextField(
            label="Target amount",
            hint_text="0",
            border_color="#3D3D5C",
            focused_border_color="#7C6FFF",
            label_style=ft.TextStyle(color="#9090B0"),
            color="#FFFFFF",
            bgcolor="#13131F",
            border_radius=14,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_size=16,
        )

        currency_ref = ft.Ref[ft.SegmentedButton]()
        selected_currency = {"val": "MKD"}

        def on_currency_change(e):
            selected_currency["val"] = list(e.control.selected)[0]

        currency_btn = ft.SegmentedButton(
            ref=currency_ref,
            selected=["MKD"],
            allow_empty_selection=False,
            allow_multiple_selection=False,
            on_change=on_currency_change,
            segments=[
                ft.Segment(value="MKD", label=ft.Text("MKD ден", color="#FFFFFF")),
                ft.Segment(value="EUR", label=ft.Text("EUR €", color="#FFFFFF")),
            ],
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.SELECTED: "#7C6FFF", ft.ControlState.DEFAULT: "#13131F"},
                side={ft.ControlState.DEFAULT: ft.BorderSide(1, "#3D3D5C")},
            ),
        )

        error_text = ft.Text("", color="#FF6B6B", size=13)

        def on_start(e):
            goal = goal_field.value.strip()
            raw = amount_field.value.strip().replace(",", ".")
            if not goal:
                error_text.value = "Please name your goal ✦"
                page.update()
                return
            try:
                target = float(raw)
                if target <= 0:
                    raise ValueError
            except ValueError:
                error_text.value = "Enter a valid target amount ✦"
                page.update()
                return

            data["goal"] = goal
            data["target"] = target
            data["saved"] = 0.0
            data["currency"] = selected_currency["val"]
            data["history"] = []
            save_data(data)
            show_main()

        start_btn = ft.FilledButton(
            content=ft.Row([
                ft.Text("Start Saving", size=16, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=14, color="#FFFFFF"),
            ], tight=True, spacing=8),
            on_click=on_start,
            style=ft.ButtonStyle(
                bgcolor={"": "#7C6FFF"},
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.Padding(left=32, right=32, top=18, bottom=18),
                elevation={"": 0},
                overlay_color={"": "#6A5EE0"},
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor="#0A0A0F",
            padding=ft.Padding(left=28, right=28, top=48, bottom=48),
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=20),
                    # Logo / title
                    ft.Container(
                        content=ft.Column([
                            ft.Text("✦", size=36, color="#7C6FFF"),
                            ft.Text("SaveUp", size=42, weight=ft.FontWeight.W_700, color="#FFFFFF",
                                    font_family="Syne"),
                            ft.Text("Your personal savings tracker", size=14, color="#6060A0"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    ),
                    ft.Container(height=40),
                    # Card
                    ft.Container(
                        bgcolor="#10101C",
                        border_radius=22,
                        border=ft.Border.all(1, "#1E1E35"),
                        padding=ft.Padding(left=28, right=28, top=28, bottom=28),
                        content=ft.Column([
                            ft.Text("Create your goal", size=18, weight=ft.FontWeight.W_600,
                                    color="#C0C0E0"),
                            ft.Container(height=6),
                            goal_field,
                            ft.Container(height=12),
                            ft.Row([
                                ft.Container(content=amount_field, expand=True),
                            ]),
                            ft.Container(height=12),
                            ft.Text("Currency", size=13, color="#6060A0"),
                            ft.Container(height=6),
                            currency_btn,
                            ft.Container(height=8),
                            error_text,
                            ft.Container(height=12),
                            ft.Row([start_btn], alignment=ft.MainAxisAlignment.END),
                        ], spacing=0),
                    ),
                ],
            ),
        )

    # ═══════════════════════════════════════════════════════
    #  MAIN SCREEN
    # ═══════════════════════════════════════════════════════

    def build_main_screen():
        cur = data["currency"]

        # ── Amount input section ─────────────────────────
        amount_field = ft.TextField(
            hint_text="Enter amount...",
            border_color="#3D3D5C",
            focused_border_color="#7C6FFF",
            color="#FFFFFF",
            bgcolor="#13131F",
            border_radius=14,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_size=18,
            text_align=ft.TextAlign.CENTER,
            expand=True,
        )

        input_currency = {"val": cur}

        def on_input_currency(e):
            input_currency["val"] = list(e.control.selected)[0]

        input_cur_btn = ft.SegmentedButton(
            selected=[cur],
            allow_empty_selection=False,
            allow_multiple_selection=False,
            on_change=on_input_currency,
            segments=[
                ft.Segment(value="MKD", label=ft.Text("ден", color="#FFFFFF", size=12)),
                ft.Segment(value="EUR", label=ft.Text("€", color="#FFFFFF", size=12)),
            ],
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.SELECTED: "#7C6FFF", ft.ControlState.DEFAULT: "#13131F"},
                side={ft.ControlState.DEFAULT: ft.BorderSide(1, "#3D3D5C")},
            ),
        )

        feedback_text = ft.Text("", size=13, color="#7C6FFF")

        # ── Dynamic controls refs ─────────────────────────
        progress_bar_ref = ft.Ref[ft.ProgressBar]()
        saved_text_ref = ft.Ref[ft.Text]()
        pct_text_ref = ft.Ref[ft.Text]()
        remaining_text_ref = ft.Ref[ft.Text]()
        history_col_ref = ft.Ref[ft.Column]()
        emoji_ref = ft.Ref[ft.Text]()

        def refresh_goal_ui():
            cur2 = data["currency"]
            pct = progress_pct()
            remaining = max(data["target"] - data["saved"], 0)

            progress_bar_ref.current.value = pct
            saved_text_ref.current.value = fmt(data["saved"], cur2)
            pct_text_ref.current.value = f"{pct * 100:.1f}%"
            remaining_text_ref.current.value = f"{fmt(remaining, cur2)} to go"

            if pct >= 1.0:
                emoji_ref.current.value = "🎉"
            elif pct >= 0.75:
                emoji_ref.current.value = "🔥"
            elif pct >= 0.5:
                emoji_ref.current.value = "⚡"
            elif pct >= 0.25:
                emoji_ref.current.value = "🌱"
            else:
                emoji_ref.current.value = "✦"

            # Rebuild history
            history_col_ref.current.controls.clear()
            if not data["history"]:
                history_col_ref.current.controls.append(
                    ft.Text("No transactions yet", size=13, color="#404060", italic=True)
                )
            else:
                for h in data["history"][:20]:
                    is_add = h["action"] == "add"
                    history_col_ref.current.controls.append(
                        ft.Container(
                            bgcolor="#0E0E1A",
                            border_radius=12,
                            border=ft.Border.all(1, "#1A1A30"),
                            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                            content=ft.Row([
                                ft.Container(
                                    width=36, height=36,
                                    border_radius=10,
                                    bgcolor="#1C1C30" if is_add else "#1C0E0E",
                                    content=ft.Text(
                                        "+" if is_add else "−",
                                        size=20, color="#7C6FFF" if is_add else "#FF6B6B",
                                        text_align=ft.TextAlign.CENTER,
                                        weight=ft.FontWeight.W_700,
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Container(width=12),
                                ft.Column([
                                    ft.Text(
                                        f"{'+' if is_add else '-'}{fmt(h['amount'], h['currency'])}",
                                        size=15,
                                        weight=ft.FontWeight.W_600,
                                        color="#7C6FFF" if is_add else "#FF6B6B",
                                    ),
                                    ft.Text(h["date"], size=11, color="#505078"),
                                ], spacing=2, expand=True),
                            ], alignment=ft.MainAxisAlignment.START),
                        )
                    )
            page.update()

        def do_action(action):
            raw = amount_field.value.strip().replace(",", ".")
            try:
                amt = float(raw)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                feedback_text.value = "Enter a valid amount ✦"
                page.update()
                return

            # Convert to goal currency
            converted = convert(amt, input_currency["val"], data["currency"])

            if action == "add":
                data["saved"] += converted
                feedback_text.value = f"Added {fmt(converted, data['currency'])} ✓"
            else:
                if converted > data["saved"]:
                    feedback_text.value = "Not enough saved to subtract ✦"
                    page.update()
                    return
                data["saved"] -= converted
                feedback_text.value = f"Removed {fmt(converted, data['currency'])} ✓"

            push_history(action, converted, data["currency"])
            amount_field.value = ""
            refresh_goal_ui()

        def on_add(e):
            feedback_text.value = ""
            do_action("add")

        def on_subtract(e):
            feedback_text.value = ""
            do_action("subtract")

        def on_reset(e):
            def confirm_reset(ev):
                dlg.open = False
                data["goal"] = None
                data["target"] = 0.0
                data["saved"] = 0.0
                data["history"] = []
                save_data(data)
                show_setup()

            def cancel_reset(ev):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Reset goal?", color="#FFFFFF"),
                content=ft.Text("This will clear all progress and history.", color="#9090B0"),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_reset,
                                  style=ft.ButtonStyle(color={"": "#9090B0"})),
                    ft.TextButton("Reset", on_click=confirm_reset,
                                  style=ft.ButtonStyle(color={"": "#FF6B6B"})),
                ],
                bgcolor="#10101C",
                shape=ft.RoundedRectangleBorder(radius=18),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        pct = progress_pct()
        remaining = max(data["target"] - data["saved"], 0)

        return ft.Container(
            expand=True,
            bgcolor="#0A0A0F",
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                controls=[
                    # ── Header ────────────────────────────────
                    ft.Container(
                        bgcolor="#0D0D1A",
                        padding=ft.Padding(left=24, right=24, top=52, bottom=24),
                        border=ft.Border.only(bottom=ft.BorderSide(1, "#1A1A30")),
                        content=ft.Row([
                            ft.Column([
                                ft.Row([
                                    ft.Text("✦", size=16, color="#7C6FFF"),
                                    ft.Text("SaveUp", size=16, weight=ft.FontWeight.W_700,
                                            color="#FFFFFF"),
                                ], spacing=6),
                                ft.Text(data["goal"], size=22, weight=ft.FontWeight.W_700,
                                        color="#FFFFFF"),
                            ], spacing=2, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH_ROUNDED,
                                icon_color="#404060",
                                tooltip="New goal",
                                on_click=on_reset,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ),

                    ft.Container(
                        padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                        content=ft.Column([

                            # ── Goal card ─────────────────────
                            ft.Container(
                                bgcolor="#10101C",
                                border_radius=22,
                                border=ft.Border.all(1, "#1E1E35"),
                                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                                content=ft.Column([
                                    ft.Row([
                                        ft.Column([
                                            ft.Text("Saved so far", size=12, color="#6060A0"),
                                            ft.Text(
                                                ref=saved_text_ref,
                                                value=fmt(data["saved"], cur),
                                                size=32, weight=ft.FontWeight.W_700,
                                                color="#FFFFFF",
                                            ),
                                        ], expand=True, spacing=2),
                                        ft.Column([
                                            ft.Text(ref=emoji_ref, value=(
                                                "🎉" if pct >= 1 else
                                                "🔥" if pct >= 0.75 else
                                                "⚡" if pct >= 0.5 else
                                                "🌱" if pct >= 0.25 else "✦"
                                            ), size=36),
                                        ]),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                                    ft.Container(height=16),

                                    ft.ProgressBar(
                                        ref=progress_bar_ref,
                                        value=pct,
                                        bgcolor="#1E1E35",
                                        color="#7C6FFF",
                                        border_radius=8,
                                        height=10,
                                    ),

                                    ft.Container(height=12),

                                    ft.Row([
                                        ft.Text(
                                            ref=pct_text_ref,
                                            value=f"{pct * 100:.1f}%",
                                            size=13, color="#7C6FFF",
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        ft.Text(
                                            ref=remaining_text_ref,
                                            value=f"{fmt(remaining, cur)} to go",
                                            size=13, color="#6060A0",
                                        ),
                                        ft.Text(
                                            f"Goal: {fmt(data['target'], cur)}",
                                            size=13, color="#404060",
                                        ),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ], spacing=0),
                            ),

                            ft.Container(height=20),

                            # ── Add / Subtract card ───────────
                            ft.Container(
                                bgcolor="#10101C",
                                border_radius=22,
                                border=ft.Border.all(1, "#1E1E35"),
                                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                                content=ft.Column([
                                    ft.Text("Add or Remove Money", size=15,
                                            weight=ft.FontWeight.W_600, color="#C0C0E0"),
                                    ft.Container(height=14),
                                    ft.Row([amount_field, ft.Container(width=8), input_cur_btn],
                                           alignment=ft.MainAxisAlignment.START),
                                    ft.Container(height=12),
                                    ft.Row([
                                        ft.FilledButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.ADD_ROUNDED, color="#FFFFFF", size=18),
                                                ft.Text("Add", color="#FFFFFF",
                                                        weight=ft.FontWeight.W_600),
                                            ], tight=True, spacing=6),
                                            on_click=on_add,
                                            expand=True,
                                            style=ft.ButtonStyle(
                                                bgcolor={"": "#7C6FFF"},
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                                                elevation={"": 0},
                                                overlay_color={"": "#6A5EE0"},
                                            ),
                                        ),
                                        ft.Container(width=10),
                                        ft.FilledButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.REMOVE_ROUNDED, color="#FF6B6B",
                                                        size=18),
                                                ft.Text("Remove", color="#FF6B6B",
                                                        weight=ft.FontWeight.W_600),
                                            ], tight=True, spacing=6),
                                            on_click=on_subtract,
                                            expand=True,
                                            style=ft.ButtonStyle(
                                                bgcolor={"": "#1C0E0E"},
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                                                elevation={"": 0},
                                                overlay_color={"": "#2C1414"},
                                                side={ft.ControlState.DEFAULT:
                                                      ft.BorderSide(1, "#3D1A1A")},
                                            ),
                                        ),
                                    ]),
                                    ft.Container(height=4),
                                    feedback_text,
                                ], spacing=0),
                            ),

                            ft.Container(height=20),

                            # ── History ───────────────────────
                            ft.Text("Transaction History", size=15,
                                    weight=ft.FontWeight.W_600, color="#C0C0E0"),
                            ft.Container(height=10),

                            ft.Column(
                                ref=history_col_ref,
                                spacing=8,
                                controls=[
                                    ft.Text("No transactions yet", size=13, color="#404060",
                                            italic=True)
                                ] if not data["history"] else [
                                    ft.Container(
                                        bgcolor="#0E0E1A",
                                        border_radius=12,
                                        border=ft.Border.all(1, "#1A1A30"),
                                        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                                        content=ft.Row([
                                            ft.Container(
                                                width=36, height=36, border_radius=10,
                                                bgcolor="#1C1C30" if h["action"] == "add" else "#1C0E0E",
                                                content=ft.Text(
                                                    "+" if h["action"] == "add" else "−",
                                                    size=20,
                                                    color="#7C6FFF" if h["action"] == "add" else "#FF6B6B",
                                                    text_align=ft.TextAlign.CENTER,
                                                    weight=ft.FontWeight.W_700,
                                                ),
                                                alignment=ft.Alignment(0, 0),
                                            ),
                                            ft.Container(width=12),
                                            ft.Column([
                                                ft.Text(
                                                    f"{'+' if h['action'] == 'add' else '-'}{fmt(h['amount'], h['currency'])}",
                                                    size=15,
                                                    weight=ft.FontWeight.W_600,
                                                    color="#7C6FFF" if h["action"] == "add" else "#FF6B6B",
                                                ),
                                                ft.Text(h["date"], size=11, color="#505078"),
                                            ], spacing=2, expand=True),
                                        ]),
                                    ) for h in data["history"][:20]
                                ],
                            ),

                            ft.Container(height=32),
                        ], spacing=0),
                    ),
                ],
            ),
        )

    # ═══════════════════════════════════════════════════════
    #  ROUTING
    # ═══════════════════════════════════════════════════════

    def show_setup():
        page.controls.clear()
        page.controls.append(build_setup_screen())
        page.update()

    def show_main():
        page.controls.clear()
        page.controls.append(build_main_screen())
        page.update()

    # Initial route
    if data["goal"]:
        show_main()
    else:
        show_setup()


ft.run(main)