import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

def show_genre_graph(df, canvas, fig, insight_label, widget):
    if not widget.winfo_ismapped():
        widget.pack()
    fig.clear()
    ax = fig.add_subplot(111)
    genre_totals = (
        df.groupby("genre", sort=False)["units_sold_millions"].sum().sort_values(ascending=False)
    )
    genre_totals.plot(kind="bar", color="skyblue", ax=ax)
    ax.set_title("Genre vs Units Sold (Millions)")
    ax.set_ylabel("Units Sold (Millions)")
    ax.set_xlabel("Genre")
    fig.tight_layout()
    canvas.draw()
    insight_label.config(
        text="Key insight: Popular genres drive the majority of unit sales, showing strong genre concentration in the market."
    )

def show_units_sold_histogram(df, canvas, fig, insight_label, widget):
    if not widget.winfo_ismapped():
        widget.pack()
    fig.clear()
    ax = fig.add_subplot(111)
    units_sold = df["units_sold_millions"].dropna()
    ax.hist(units_sold, bins=20, color="purple", edgecolor="black")
    ax.set_title("Units Sold Distribution")
    ax.set_xlabel("Units Sold (Millions)")
    ax.set_ylabel("Number of Games")
    fig.tight_layout()
    canvas.draw()
    insight_label.config(
        text="Key insight: Unit sales are skewed, with many games selling modestly and a smaller set of top titles accounting for the largest share."
    )

def show_publisher_graph(df, revenue_col, canvas, fig, insight_label, widget):
    if not widget.winfo_ismapped():
        widget.pack()
    fig.clear()
    ax = fig.add_subplot(111)
    publisher_revenue = (
        df.groupby("publisher", sort=False)[revenue_col].sum().sort_values(ascending=False)
    )
    if len(publisher_revenue) > 15:
        publisher_revenue = publisher_revenue.head(15)
    publisher_revenue.plot(kind="pie", ax=ax, autopct="%.1f%%", startangle=90, legend=False)
    ax.set_title(f"Publisher Share of {revenue_col.replace('_', ' ').title()}")
    ax.set_ylabel("")
    fig.tight_layout()
    canvas.draw()
    insight_label.config(
        text="Key insight: The top publishers contribute the majority of revenue, highlighting market concentration among major players."
    )


def reset_dashboard(canvas, fig, insight_label, widget):
    fig.clear()
    fig.tight_layout()
    canvas.draw()
    insight_label.config(text="")
    if widget.winfo_ismapped():
        widget.pack_forget()


def show_about_team():
    about_win = tk.Toplevel()
    about_win.title("About The Team")
    about_win.geometry("520x320")
    about_win.resizable(False, False)

    title = ttk.Label(about_win, text="Alp Ahmet Karahan", font=("Helvetica", 14, "bold"))
    title.pack(pady=(10, 5))

    description = ttk.Label(
        about_win,
        text="Coding.",
        wraplength=500,
        justify="center",
    )
    description.pack(padx=10)

    mission_title = ttk.Label(about_win, text="Fatih Mehmet Kayrak", font=("Helvetica", 12, "bold"))
    mission_title.pack(pady=(15, 5))
    mission_text = ttk.Label(
        about_win,
        text="Visual Design.",
        wraplength=500,
        justify="center",
    )
    mission_text.pack(padx=10)

    values_title = ttk.Label(about_win, text="Shawn Gray", font=("Helvetica", 12, "bold"))
    values_title.pack(pady=(15, 5))
    values_text = ttk.Label(
        about_win,
        text="Sound Design.",
        wraplength=500,
        justify="center",
    )
    values_text.pack(padx=10)


def show_instructions():
    instr_win = tk.Toplevel()
    instr_win.title("Instructions")
    instr_win.geometry("520x320")
    instr_win.resizable(False, False)

    title1 = ttk.Label(instr_win, text="The Objective", font=("Helvetica", 14, "bold"))
    title1.pack(pady=(10, 5))
    text1 = ttk.Label(
        instr_win,
        text="Kepron is a forgotten warrior and he wants to be remembered again. \nOne day he stumbles up on a kingdom ruled by a beast named Rotinus.\nThis is the chance to be remembered once again.\nKill the beast and claim the kingdom as your own. But do not underestimate the enemy.\nThe beastlings are after you.",
        wraplength=500,
        justify="center",
        font=("Helvetica", 10),
    )
    text1.pack(padx=10)

    title2 = ttk.Label(instr_win, text="Controls", font=("Helvetica", 14, "bold"))
    title2.pack(pady=(15, 5))
    text2 = ttk.Label(
        instr_win,
        text="Walk: A, D\nJump: Spacebar\nAttack: LMB",
        wraplength=500,
        justify="center",
        anchor="center",
        font=("Helvetica", 10),
    )
    text2.pack(padx=10)

def open_game(root=None):
    base_path = Path(__file__).resolve().parent
    game_path = base_path / "Kepron_Kafitza.py"
    if not game_path.exists():
        candidates = [
            path
            for path in base_path.iterdir()
            if path.is_file()
            and path.stem.lower().replace(" ", "_").replace("-", "_") in {
                "kepron_kafitza",
                "kepronkafitza",
            }
        ]
        if not candidates:
            candidates = [
                path
                for path in base_path.iterdir()
                if path.is_file()
                and "kepron" in path.stem.lower()
                and "kafitza" in path.stem.lower()
            ]
        if not candidates:
            raise FileNotFoundError(f"Could not find game script in {base_path}")
        game_path = candidates[0]
    if game_path.suffix.lower() in {".py", ".pyw"}:
        subprocess.Popen([sys.executable, str(game_path)], cwd=str(base_path))
    else:
        subprocess.Popen([str(game_path)], cwd=str(base_path))
    if root is not None:
        root.destroy()

def main():
    data_path = Path(__file__).with_name("sample_worldwide_video_games_cleaned.csv")
    df = pd.read_csv(data_path)

    required_columns = {"genre", "region", "publisher", "units_sold_millions"}
    if not required_columns.issubset(df.columns):
        raise SystemExit(
            "CSV must contain genre, region, publisher, and units_sold_millions columns"
        )

    # detect a revenue column (flexible name matching)
    revenue_cols = [c for c in df.columns if "revenue" in c.lower()]
    if not revenue_cols:
        raise SystemExit("CSV must contain a revenue column (name including 'revenue')")
    revenue_col = revenue_cols[0]

    # Create a simple GUI to choose which graph to display
    root = tk.Tk()
    root.title("Video Games Charts")
    root.geometry("1920x1080")

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="x")

    # buttons side by side
    btn_frame = ttk.Frame(frm)
    btn_frame.pack(fill="x")
    btn1 = ttk.Button(btn_frame, text="Genre vs Units Sold", command=lambda: show_genre_graph(df, canvas, fig, insight_label, widget))
    btn2 = ttk.Button(btn_frame, text="Units Sold Histogram", command=lambda: show_units_sold_histogram(df, canvas, fig, insight_label, widget))
    btn3 = ttk.Button(btn_frame, text=f"Publisher vs {revenue_col.replace('_', ' ').title()}", command=lambda: show_publisher_graph(df, revenue_col, canvas, fig, insight_label, widget))
    btn1.pack(side="left", expand=True, fill="x", padx=5, pady=5)
    btn2.pack(side="left", expand=True, fill="x", padx=5, pady=5)
    btn3.pack(side="left", expand=True, fill="x", padx=5, pady=5)

    # plotting area with fixed graph size (1200x600 pixels)
    plot_frame = ttk.Frame(root)
    plot_frame.pack()
    FIXED_WIDTH = 1200
    FIXED_HEIGHT = 600
    fig = Figure(figsize=(12, 6), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    widget = canvas.get_tk_widget()
    widget.config(width=FIXED_WIDTH, height=FIXED_HEIGHT)
    widget.pack()

    insight_label = ttk.Label(root, text="", wraplength=FIXED_WIDTH, anchor="w")
    insight_label.pack(fill="x", padx=10, pady=(5, 10))

    action_btn_frame = ttk.Frame(root)
    action_btn_frame.pack(fill="x", padx=10, pady=5)
    btn_play = ttk.Button(action_btn_frame, text="Play The Game", command=lambda: open_game(root))
    btn_instructions = ttk.Button(action_btn_frame, text="View Instructions", command=show_instructions)
    btn_reset = ttk.Button(action_btn_frame, text="Reset Dashboard", command=lambda: reset_dashboard(canvas, fig, insight_label, widget))
    btn_about = ttk.Button(action_btn_frame, text="About The Team", command=show_about_team)
    btn_exit = ttk.Button(action_btn_frame, text="Exit", command=root.destroy)
    btn_play.pack(side="left", padx=5)
    btn_instructions.pack(side="left", padx=5)
    btn_reset.pack(side="left", padx=5)
    btn_about.pack(side="left", padx=5)
    btn_exit.pack(side="left", padx=5)

    root.mainloop()


if __name__ == "__main__":
    main()