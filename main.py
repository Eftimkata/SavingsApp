import flet as ft
import json
import os
from datetime import datetime

DATA_FILE = "savings_data.json"

EUR_TO_MKD = 61.5  # approximate fixed rate


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        # ── migrations ──
        changed = False
        for h in data.get("history", []):
            if "notes" not in h:
                h["notes"] = ""
                changed = True
        if changed:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        return data
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

    # ── Helpers ─────────────────────────────────────────────
    def progress_pct():
        if data["target"] <= 0:
            return 0.0
        return min(data["saved"] / data["target"], 1.0)

    def push_history(action, amount, currency, notes=""):
        data["history"].insert(0, {
            "action": action,
            "amount": amount,
            "currency": currency,
            "date": datetime.now().strftime("%d %b %Y, %H:%M"),
            "notes": notes,
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

        selected_currency = {"val": "MKD"}

        def on_currency_change(e):
            selected_currency["val"] = list(e.control.selected)[0]

        currency_btn = ft.SegmentedButton(
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
                    ft.Container(
                        content=ft.Column([
                            ft.Text("✦", size=36, color="#7C6FFF"),
                            ft.Text("SaveUp", size=42, weight=ft.FontWeight.W_700, color="#FFFFFF",
                                    font_family="Syne"),
                            ft.Text("Your personal savings tracker", size=14, color="#6060A0"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    ),
                    ft.Container(height=40),
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
                            ft.Row([ft.Container(content=amount_field, expand=True)]),
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

        notes_field = ft.TextField(
            hint_text="Add a note (optional)...",
            border_color="#3D3D5C",
            focused_border_color="#7C6FFF",
            color="#FFFFFF",
            bgcolor="#13131F",
            border_radius=14,
            text_size=14,
            multiline=True,
            min_lines=1,
            max_lines=3,
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

        progress_bar_ref = ft.Ref[ft.ProgressBar]()
        saved_text_ref = ft.Ref[ft.Text]()
        pct_text_ref = ft.Ref[ft.Text]()
        remaining_text_ref = ft.Ref[ft.Text]()
        history_col_ref = ft.Ref[ft.Column]()
        emoji_ref = ft.Ref[ft.Text]()

        # ── Delete entry ─────────────────────────────────
        def delete_entry(entry_index, reverse_amount):
            """Remove a history entry and reverse its effect on saved amount."""
            entry = data["history"][entry_index]
            amount_in_main_cur = entry["amount"]  # already stored in main currency

            # Reverse the transaction's effect
            if entry["action"] == "add":
                data["saved"] = max(data["saved"] - amount_in_main_cur, 0)
            else:
                data["saved"] += amount_in_main_cur

            data["history"].pop(entry_index)
            save_data(data)
            refresh_goal_ui()

        def confirm_delete_entry(entry_index):
            entry = data["history"][entry_index]
            is_add = entry["action"] == "add"

            def do_delete(ev):
                dlg.open = False
                page.update()
                delete_entry(entry_index, entry["amount"])

            def cancel(ev):
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete this entry?", color="#FFFFFF"),
                content=ft.Column([
                    ft.Text(
                        f"{'Added' if is_add else 'Removed'} {fmt(entry['amount'], entry['currency'])} on {entry['date']}",
                        color="#9090B0", size=13,
                    ),
                    ft.Container(height=6),
                    ft.Text(
                        "This will also reverse its effect on your saved amount.",
                        color="#FF6B6B", size=12,
                    ),
                ], tight=True, spacing=0),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel,
                                  style=ft.ButtonStyle(color={"": "#9090B0"})),
                    ft.TextButton("Delete", on_click=do_delete,
                                  style=ft.ButtonStyle(color={"": "#FF6B6B"})),
                ],
                bgcolor="#10101C",
                shape=ft.RoundedRectangleBorder(radius=18),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # ── Notes dialog ─────────────────────────────────
        def open_notes_dialog(entry_index):
            entry = data["history"][entry_index]
            is_add = entry["action"] == "add"
            note_edit = ft.TextField(
                value=entry.get("notes", ""),
                hint_text="Write a note...",
                border_color="#3D3D5C",
                focused_border_color="#7C6FFF",
                color="#FFFFFF",
                bgcolor="#13131F",
                border_radius=12,
                multiline=True,
                min_lines=2,
                max_lines=5,
                text_size=14,
            )

            def save_note(ev):
                data["history"][entry_index]["notes"] = note_edit.value.strip()
                save_data(data)
                dlg.open = False
                refresh_history_ui()
                page.update()

            def close_dlg(ev):
                dlg.open = False
                page.update()

            def on_delete(ev):
                dlg.open = False
                page.update()
                confirm_delete_entry(entry_index)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Column([
                    ft.Row([
                        ft.Container(
                            width=32, height=32, border_radius=8,
                            bgcolor="#1C1C30" if is_add else "#1C0E0E",
                            content=ft.Text(
                                "+" if is_add else "−",
                                size=18, color="#7C6FFF" if is_add else "#FF6B6B",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_700,
                            ),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text(
                                f"{'+' if is_add else '-'}{fmt(entry['amount'], entry['currency'])}",
                                size=15, weight=ft.FontWeight.W_600,
                                color="#7C6FFF" if is_add else "#FF6B6B",
                            ),
                            ft.Text(entry["date"], size=11, color="#505078"),
                        ], spacing=1),
                    ]),
                ], spacing=0),
                content=ft.Column([
                    ft.Text("Note", size=13, color="#9090B0"),
                    ft.Container(height=6),
                    note_edit,
                ], tight=True, spacing=0),
                actions=[
                    ft.TextButton("Delete Entry", on_click=on_delete,
                                  style=ft.ButtonStyle(color={"": "#FF6B6B"})),
                    ft.TextButton("Cancel", on_click=close_dlg,
                                  style=ft.ButtonStyle(color={"": "#9090B0"})),
                    ft.TextButton("Save Note", on_click=save_note,
                                  style=ft.ButtonStyle(color={"": "#7C6FFF"})),
                ],
                bgcolor="#10101C",
                shape=ft.RoundedRectangleBorder(radius=18),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # ── Build one history tile ────────────────────────
        def build_history_tile(h, idx):
            is_add = h["action"] == "add"
            has_notes = bool(h.get("notes", "").strip())

            # Swipe-reveal state
            tile_offset = {"x": 0.0}
            translate_ref = ft.Ref[ft.Container]()
            delete_btn_ref = ft.Ref[ft.Container]()

            def on_long_press(e, i=idx):
                open_notes_dialog(i)

            def on_pan_update(e: ft.DragUpdateEvent, i=idx):
                new_x = tile_offset["x"] + e.delta_x
                # Only allow swiping left (negative x), max -80
                new_x = max(min(new_x, 0), -80)
                tile_offset["x"] = new_x
                translate_ref.current.margin = ft.Margin(left=new_x, right=-new_x, top=0, bottom=0)
                # Show delete button opacity based on swipe
                delete_btn_ref.current.opacity = abs(new_x) / 80
                page.update()

            def on_pan_end(e, i=idx):
                if tile_offset["x"] < -40:
                    # Snap open
                    tile_offset["x"] = -80
                    translate_ref.current.margin = ft.Margin(left=-80, right=80, top=0, bottom=0)
                    delete_btn_ref.current.opacity = 1.0
                else:
                    # Snap closed
                    tile_offset["x"] = 0
                    translate_ref.current.margin = ft.Margin(left=0, right=0, top=0, bottom=0)
                    delete_btn_ref.current.opacity = 0.0
                page.update()

            def on_delete_tap(e, i=idx):
                # Reset swipe first
                tile_offset["x"] = 0
                translate_ref.current.margin = ft.Margin(left=0, right=0, top=0, bottom=0)
                delete_btn_ref.current.opacity = 0.0
                page.update()
                confirm_delete_entry(i)

            tile_content = ft.Container(
                ref=translate_ref,
                bgcolor="#0E0E1A",
                border_radius=12,
                border=ft.Border.all(1, "#1A1A30"),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                margin=ft.Margin(left=0, right=0, top=0, bottom=0),
                content=ft.Column([
                    ft.Row([
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
                        ft.Container(
                            content=ft.Text("📝", size=14) if has_notes else ft.Text(
                                "hold", size=9, color="#2A2A45", italic=True,
                            ),
                            padding=ft.Padding(left=4, right=0, top=0, bottom=0),
                        ),
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(
                        visible=has_notes,
                        padding=ft.Padding(left=48, right=0, top=4, bottom=0),
                        content=ft.Text(
                            h.get("notes", ""),
                            size=12, color="#7070A0", italic=True,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ], spacing=0),
            )

            delete_reveal = ft.Container(
                ref=delete_btn_ref,
                width=72,
                bgcolor="#FF6B6B",
                border_radius=ft.BorderRadius(top_left=0, top_right=12, bottom_left=0, bottom_right=12),
                opacity=0.0,
                alignment=ft.Alignment(0, 0),
                content=ft.Column([
                    ft.Icon(ft.Icons.DELETE_ROUNDED, color="#FFFFFF", size=20),
                    ft.Text("Delete", size=10, color="#FFFFFF", weight=ft.FontWeight.W_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                on_click=lambda e, i=idx: on_delete_tap(e, i),
            )

            return ft.GestureDetector(
                on_long_press_start=on_long_press,
                on_horizontal_drag_update=on_pan_update,
                on_horizontal_drag_end=on_pan_end,
                content=ft.Stack([
                    ft.Row([
                        ft.Container(expand=True),
                        delete_reveal,
                    ]),
                    tile_content,
                ]),
            )

        def refresh_history_ui():
            history_col_ref.current.controls.clear()
            if not data["history"]:
                history_col_ref.current.controls.append(
                    ft.Text("No transactions yet", size=13, color="#404060", italic=True)
                )
            else:
                for i, h in enumerate(data["history"][:20]):
                    history_col_ref.current.controls.append(build_history_tile(h, i))

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

            refresh_history_ui()
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

            converted = convert(amt, input_currency["val"], data["currency"])
            note = notes_field.value.strip()

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

            push_history(action, converted, data["currency"], notes=note)
            amount_field.value = ""
            notes_field.value = ""
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

        initial_history = []
        if not data["history"]:
            initial_history = [
                ft.Text("No transactions yet", size=13, color="#404060", italic=True)
            ]
        else:
            for i, h in enumerate(data["history"][:20]):
                initial_history.append(build_history_tile(h, i))

        return ft.Container(
            expand=True,
            bgcolor="#0A0A0F",
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                controls=[
                    # ── Header ──────────────────────────────
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
                                    ft.Container(
                                        margin=ft.Margin(left=6, right=0, top=0, bottom=0),
                                        bgcolor="#1E1E35",
                                        border_radius=6,
                                        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                        content=ft.Text("v1.6", size=10, color="#7C6FFF"),
                                    ),
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
                                    ft.Container(height=10),
                                    notes_field,
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
                            ft.Row([
                                ft.Text("Transaction History", size=15,
                                        weight=ft.FontWeight.W_600, color="#C0C0E0"),
                                ft.Container(
                                    bgcolor="#1A1A2E",
                                    border_radius=8,
                                    padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                                    content=ft.Text("← swipe to delete  •  hold to note", size=10,
                                                     color="#505078", italic=True),
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Container(height=10),

                            ft.Column(
                                ref=history_col_ref,
                                spacing=8,
                                controls=initial_history,
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

    if data["goal"]:
        show_main()
    else:
        show_setup()


ft.run(main)