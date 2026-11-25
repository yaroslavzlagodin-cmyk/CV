"""Pulse / PC Diagnostic Tool — desktop entry point."""
import json
import os
import sys
import time
import tkinter as tk
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".deps"))
import customtkinter as ct
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from metrics import power_events, snapshot
from strings import LANGUAGES, TEXT

DARK = ("#14131d", "#1c1a28", "#252232", "#352f46", "#f5f2fc", "#b0a8c2", "#5edbe9", "#d79aff", "#f7b582")
LIGHT = ("#f3f1f7", "#ffffff", "#faf8fe", "#ddd7e7", "#231c32", "#645a72", "#077885", "#8444a2", "#99531d")


def gib(value):
    return f"{value / 2**30:,.1f} GiB"


class Monitor(ct.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pulse · PC Diagnostic Tool")
        self.geometry("1160x820")
        self.minsize(850, 680)
        self.dark = True
        self.lang = 0
        self.page = "overview"
        self.data = None
        self.events = None
        self.errors = {}
        self.query = tk.StringVar()
        self.query.trace_add("write", lambda *_: self.render_table())
        self.history = deque()
        # Один послідовний потік для CPU: psutil обчислює відсоток між двома
        # викликами того самого потоку. Перший виклик лише створює базову точку.
        self.sampler = ThreadPoolExecutor(1)
        self.journal = ThreadPoolExecutor(1)
        from psutil import cpu_percent
        self.sampler.submit(cpu_percent, 0.15, True)
        self.pending = {}
        self.due = {"data": 0, "events": 0}
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.rebuild()
        self.after(20, self.poll)

    def t(self, key):
        return TEXT[key][self.lang]

    def label(self, parent, text, size=14, color=None, bold=False, **pack):
        widget = ct.CTkLabel(parent, text=text, text_color=color or self.ink,
                             font=("Segoe UI", size, "bold" if bold else "normal"), anchor="w")
        widget.pack(**(pack or {"anchor": "w"}))
        return widget

    def frame(self, parent, color, radius=12):
        return ct.CTkFrame(parent, fg_color=color, corner_radius=radius, border_width=0)

    def button(self, parent, text, command, active=False):
        b = ct.CTkButton(parent, text=text, command=command, anchor="w", height=39,
                         fg_color=self.edge if active else "transparent", hover_color=self.edge,
                         text_color=self.ink, font=("Segoe UI", 14))
        b.pack(fill="x", padx=12, pady=2)
        return b

    def rebuild(self):
        for child in self.winfo_children():
            child.destroy()
        self.bg, self.side, self.card, self.edge, self.ink, self.muted, self.cyan, self.pink, self.amber = DARK if self.dark else LIGHT
        ct.set_appearance_mode("dark" if self.dark else "light")
        self.configure(fg_color=self.bg)
        nav = self.frame(self, self.side, 0)
        nav.pack(side="left", fill="y")
        self.label(nav, "◈  PULSE", 26, self.cyan, True, padx=18, pady=(22, 25), anchor="w")
        for key, icon in (("overview", "◉"), ("processes", "≡"), ("history", "◷")):
            self.button(nav, f"{icon}    {self.t(key)}", lambda k=key: self.switch(k), key == self.page)
        self.frame(nav, self.side).pack(fill="both", expand=True)
        self.label(nav, self.t("language"), 12, self.muted, padx=16, anchor="w")
        language = ct.CTkOptionMenu(nav, values=LANGUAGES, command=self.set_language,
                                   fg_color=self.edge, button_color=self.edge, text_color=self.ink)
        language.set(LANGUAGES[self.lang])
        language.pack(fill="x", padx=12, pady=7)
        self.button(nav, self.t("light" if self.dark else "dark"), self.toggle_theme)
        self.button(nav, self.t("report"), self.save, True)
        self.label(nav, "PC Diagnostic Tool", 11, self.muted, padx=15, pady=12, anchor="w")
        self.main = self.frame(self, self.bg, 0)
        self.main.pack(side="left", expand=True, fill="both", padx=20, pady=15)
        self.label(self.main, self.t(self.page), 29, bold=True)
        self.sub = self.label(self.main, "", 13, self.muted, anchor="w", pady=(0, 12))
        if self.page == "overview":
            self.build_overview()
        else:
            self.build_table()
        self.refresh()

    def switch(self, page):
        self.page = page
        self.rebuild()

    def set_language(self, language):
        self.lang = LANGUAGES.index(language)
        self.rebuild()

    def toggle_theme(self):
        self.dark = not self.dark
        self.rebuild()

    def build_overview(self):
        body = ct.CTkScrollableFrame(self.main, fg_color=self.bg, corner_radius=0)
        body.pack(fill="both", expand=True)
        cards = self.frame(body, self.bg)
        cards.pack(fill="x")
        self.gauges = []
        for idx, (key, color) in enumerate(zip(("cpu", "ram", "disks"), (self.cyan, self.pink, self.amber))):
            cards.columnconfigure(idx, weight=1, uniform="metric")
            box = self.frame(cards, self.card)
            box.grid(row=0, column=idx, sticky="nsew", padx=(0, 7))
            self.label(box, self.t(key), 15, bold=True, padx=14, pady=(9, 1), anchor="w")
            ring = tk.Canvas(box, width=96, height=83, bg=self.card, highlightthickness=0)
            ring.pack()
            detail = self.label(box, "—", 12, self.muted, anchor="center", pady=(1, 8))
            self.gauges.append((ring, detail, color))
        graph = self.frame(body, self.card)
        graph.pack(fill="x", pady=10, padx=(0, 7))
        head = self.frame(graph, self.card)
        head.pack(fill="x", padx=14, pady=(8, 0))
        self.label(head, self.t("activity"), 16, bold=True, side="left")
        self.label(head, "● RAM", 12, self.pink, side="right")
        self.label(head, "● CPU", 12, self.cyan, side="right", padx=10)
        self.figure = Figure(figsize=(6, 1.65), dpi=100, facecolor=self.card)
        self.axes = self.figure.add_axes([0.075, 0.23, 0.90, 0.70], facecolor=self.card)
        self.axes.set(xlim=(-60, 0), ylim=(0, 100), yticks=[0, 50, 100],
                      yticklabels=["0%", "50%", "100%"], xticks=[-60, -45, -30, -15, 0])
        self.axes.tick_params(colors=self.muted, labelsize=8, length=0, pad=5)
        self.axes.grid(axis="y", color=self.edge)
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        self.lines = [self.axes.plot([], [], color=c, linewidth=2)[0] for c in (self.cyan, self.pink)]
        self.chart = FigureCanvasTkAgg(self.figure, master=graph)
        self.chart.get_tk_widget().pack(fill="x", padx=8, pady=(0, 4))
        self.sections = []
        for key in ("disks", "network"):
            box = self.frame(body, self.card)
            box.pack(fill="x", padx=(0, 7), pady=(0, 8))
            self.label(box, self.t(key), 15, bold=True, padx=14, pady=(8, 0), anchor="w")
            self.sections.append(self.label(box, "—", 13, self.muted, padx=14, pady=(1, 8), anchor="w"))

    def build_table(self):
        if self.page == "processes":
            entry = ct.CTkEntry(self.main, textvariable=self.query, width=260)
            self.label(self.main, self.t("search"), 12, self.muted)
            entry.pack(anchor="w", pady=(0, 8))
            headers = ["PID", self.t("name"), "MiB ↓", self.t("started")]
        else:
            headers = [self.t("at"), self.t("event"), "ID", self.t("source")]
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=self.card, fieldbackground=self.card, foreground=self.ink,
                        borderwidth=0, rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=self.edge, foreground=self.ink, relief="flat")
        style.map("Treeview", background=[("selected", "#484369")], foreground=[("selected", "white")])
        holder = self.frame(self.main, self.card)
        holder.pack(fill="both", expand=True)
        self.table = ttk.Treeview(holder, columns=list(range(4)), show="headings")
        for i, header in enumerate(headers):
            self.table.heading(i, text=header, anchor="w")
            widths = (55, 180, 80, 160) if self.page == "processes" else (135, 220, 45, 170)
            self.table.column(i, width=widths[i], minwidth=30)
        scroll = ttk.Scrollbar(holder, command=self.table.yview)
        scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)

    def render_table(self):
        if self.page == "overview" or not hasattr(self, "table") or not self.table.winfo_exists():
            return
        position = self.table.yview()
        self.table.delete(*self.table.get_children())
        if self.page == "processes" and self.data:
            q = self.query.get().strip().casefold()
            for p in self.data["processes"]:
                if q in p["name"].casefold() or q == str(p["pid"]):
                    mem = "—" if p["memory"] is None else f"{p['memory']/2**20:,.1f}"
                    self.table.insert("", "end", values=(p["pid"], p["name"], mem, (p["started"] or "—")[:19].replace("T", " ")))
        elif self.page == "history":
            for e in self.events or []:
                self.table.insert("", "end", values=(e["time"], self.t(str(e["id"])), e["id"], e["source"]))
        if position:
            self.table.yview_moveto(position[0])

    def refresh(self):
        d = self.data
        if self.page == "history":
            note = self.t("pending") if self.events is None else self.t("journal") if self.events else self.t("empty")
            self.sub.configure(text=self.t("failed") if "events" in self.errors else note)
            self.render_table()
            return
        if not d:
            self.sub.configure(text=self.t("failed" if "data" in self.errors else "pending"))
            return
        status = self.t("failed") if "data" in self.errors else self.t("updated")
        self.sub.configure(text=f"{d['host']}   ·   {status} {d['time'][11:19]}   ·   {self.t('boot')} {d['boot'][:16].replace('T',' ')}")
        if self.page != "overview":
            self.render_table()
            return
        total = sum(p["total"] for p in d["disks"])
        used = sum(p["total"]-p["free"] for p in d["disks"])
        metrics = [(d["cpu"], f"{self.t('cores')} · {len(d['cores'])}"),
                   (d["ram"], f"{gib(d['ram_used'])} / {gib(d['ram_total'])}"),
                   (100*used/total if total else None, f"{self.t('diskusage')} · {gib(used)}")]
        for (canvas, label, color), (value, detail) in zip(self.gauges, metrics):
            canvas.delete("all")
            canvas.create_arc(10, 5, 86, 81, start=230, extent=-280, outline=self.edge, width=5, style="arc")
            if value is not None:
                canvas.create_arc(10, 5, 86, 81, start=230, extent=-2.8*value, outline=color, width=5, style="arc")
            canvas.create_text(48, 45, text=f"{value:.0f}%" if value is not None else "—",
                               fill=self.ink, font=("Segoe UI", 15, "bold"))
            label.configure(text=detail)
        now = time.monotonic()
        for index, line in enumerate(self.lines, 1):
            line.set_data([p[0]-now for p in self.history], [p[index] for p in self.history])
        self.chart.draw_idle()
        volumes = [f"{p['path']}   {p['fs']}     {p['percent']}%   ·   {gib(p['free'])} {self.t('free')} / {gib(p['total'])}" for p in d["disks"]]
        ips = [f"{name}     {ip}" for name, ip in d["addresses"]]
        for widget, rows in zip(self.sections, (volumes, ips)):
            widget.configure(text="\n".join(rows) or self.t("unavailable"), justify="left")

    def poll(self):
        now = time.monotonic()
        changed = False
        for key, future in list(self.pending.items()):
            if not future.done():
                continue
            del self.pending[key]
            try:
                result = future.result()
                self.errors.pop(key, None)
                if key == "data":
                    self.data = result
                    self.history.append((now, result["cpu"], result["ram"]))
                    while self.history and now-self.history[0][0] > 60:
                        self.history.popleft()
                else:
                    self.events = result
            except Exception as error:
                self.errors[key] = str(error)
            changed = True
        if changed:
            self.refresh()
        for key, pool, fn, interval in (("data", self.sampler, snapshot, 2), ("events", self.journal, power_events, 60)):
            if key not in self.pending and now >= self.due[key]:
                self.pending[key] = pool.submit(fn)
                self.due[key] = now + interval
        self.after(250, self.poll)

    def save(self):
        if not self.data:
            messagebox.showinfo("Pulse", self.t("failed" if "data" in self.errors else "pending"), parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title=self.t("report"), defaultextension=".json",
                initialfile=datetime.now().strftime("Pulse-%Y%m%d-%H%M%S.json"), filetypes=[("JSON", "*.json")])
        if path:
            payload = dict(self.data, power_events=self.events, collection_errors=self.errors)
            try:
                Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
                messagebox.showinfo(self.t("saved"), path, parent=self)
            except OSError as error:
                messagebox.showerror(self.t("saveerr"), str(error), parent=self)

    def close(self):
        self.sampler.shutdown(wait=False, cancel_futures=True)
        self.journal.shutdown(wait=False, cancel_futures=True)
        self.destroy()


if __name__ == "__main__":
    Monitor().mainloop()

