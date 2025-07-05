import tkinter as tk
import time
import datetime
from helpers.desktop_widget import DesktopWidget

#Aktiedata
aktier = {
    "Novo Nordisk":     {"antal": 7,  "udbytte": 6.0,   "frekvens": 2},   # 6 kr x 2 per år = 12 kr/aktie/år
    "Simon Property":   {"antal": 2,  "udbytte": 7.6,   "frekvens": 4},
    "Tesla":            {"antal": 66, "udbytte": 0.0,   "frekvens": 0},
    "thyssenkrupp AG":  {"antal": 29, "udbytte": 0.15,  "frekvens": 1},
    "Vestjysk Bank":    {"antal": 28, "udbytte": 0.20,  "frekvens": 1}
}

SEKUNDERPRÅR = 365 * 24 * 60 * 60

#Beregn årligt og pr. sekund
def beregn_årligt_udbytte():
    samlet = 0
    for aktie in aktier.values():
        samlet += aktie["antal"] * aktie["udbytte"] * aktie["frekvens"]
    return samlet

årligt_udbytte = beregn_årligt_udbytte()
udbytte_pr_sekund = årligt_udbytte / SEKUNDERPRÅR

#Find hvor mange sekunder vi er inde i året
nu = datetime.datetime.now()
startafåret = datetime.datetime(nu.year, 1, 1)
sekunder_gået = (nu - startafåret).total_seconds()

#Beregn startværdi
beløb = sekunder_gået * udbytte_pr_sekund

#GUI
root = tk.Tk()
root.title("Udbytte i år (live)")
root.geometry("300x100+100+100")
root.overrideredirect(True)

# Set up desktop widget functionality
desktop_widget = DesktopWidget(root)

# Schedule the window positioning after the window is created
root.after(100, desktop_widget.setup_desktop_level)

# Choose your preferred move method:
# Option 1: Hold Ctrl + drag to move
desktop_widget.make_draggable_with_key("ctrl")
desktop_widget.enable_edge_snap(margin=30)

# Optional: Set transparency (0.0 = fully transparent, 1.0 = fully opaque)
desktop_widget.set_transparency(0.8)  # 80% opacity

baggrundsfarve = "#000000"
tekstfarve = "#00FF00"

frame = tk.Frame(root, bg=baggrundsfarve)
frame.pack(expand=True, fill="both")

label = tk.Label(frame, text="", bg=baggrundsfarve, fg=tekstfarve, font=("Consolas", 12))
label.pack(padx=10, pady=20)

def opdater():
    global beløb
    beløb += udbytte_pr_sekund
    label.config(text=f"Udbytte i år: {beløb:.6f} kr")
    root.after(1000, opdater)

opdater()
root.mainloop()