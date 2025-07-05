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

# Afkast data with fake movement
afkast_kroner = 1250.75  # Starting amount
afkast_procent = 5.2     # Starting percentage

# Fake afkast movement parameters
afkast_change_per_second = 0.15  # Changes by 0.15 kr per second
afkast_procent_change_per_second = 0.001  # Changes by 0.001% per second

# Privacy/censoring functionality
censored = False

def toggle_censoring(event):
    """Toggle between showing and censoring the dividend amount."""
    global censored
    censored = not censored
    # Update display immediately
    update_display_text()

#GUI
root = tk.Tk()
root.title("Udbytte og Afkast i år (live)")
root.geometry("330x120+100+100")  # Increased height for two lines
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

# Create two labels - one for dividend, one for returns, both left-aligned
udbytte_label = tk.Label(frame, text="", bg=baggrundsfarve, fg=tekstfarve, font=("Consolas", 12), anchor="w", justify="left")
udbytte_label.pack(padx=20, pady=(15, 5), fill="x")

afkast_label = tk.Label(frame, text="", bg=baggrundsfarve, fg=tekstfarve, font=("Consolas", 12), anchor="w", justify="left")
afkast_label.pack(padx=20, pady=(5, 15), fill="x")

def update_display_text():
    """Update the display text, considering censoring state."""
    if censored:
        udbytte_text = "Udbytte i år: ******* kr"
        afkast_text = "Afkast i år:  ******* kr"
    else:
        udbytte_text = f"Udbytte i år: {beløb:.6f} kr"
        afkast_text = f"Afkast i år:  {afkast_kroner:.2f} kr ({afkast_procent:.1f}%)"
    
    udbytte_label.config(text=udbytte_text)
    afkast_label.config(text=afkast_text)

def opdater():
    global beløb, afkast_kroner, afkast_procent
    
    # Update dividend (existing logic)
    beløb += udbytte_pr_sekund
    
    # Update afkast with fake movement
    afkast_kroner += afkast_change_per_second
    afkast_procent += afkast_procent_change_per_second
    
    update_display_text()
    root.after(1000, opdater)

# Bind Ctrl+E to toggle censoring for both labels
root.bind('<Control-e>', toggle_censoring)
frame.bind('<Control-e>', toggle_censoring)
udbytte_label.bind('<Control-e>', toggle_censoring)
afkast_label.bind('<Control-e>', toggle_censoring)

opdater()
root.mainloop()