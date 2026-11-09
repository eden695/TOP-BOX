# -*- coding: utf-8 -*-
"""
================================================================================
TOP-BOX — Solution de Caisse Enregistreuse Professionnelle (Windows 10 & 11)
Version : 3.5.0 Pro
Architecture : Standalone Offline POS / Tkinter UI Moderne / SQLite Persistent
================================================================================
"""

import os, sys, sqlite3, shutil, datetime, math, json, hashlib, tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Gestion multi-plateforme des chemins et persistance sécurisée
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, '_MEIPASS', str(Path(__file__).resolve().parent)))
LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local')))

# Emplacement officiel de la base TOP-BOX
USER_DATA_DIR = LOCAL_APPDATA / 'TOP_BOX'
USER_ASSET_DIR = USER_DATA_DIR / 'assets'
USER_PRODUCT_DIR = USER_ASSET_DIR / 'products'
BACKUP_DIR = USER_DATA_DIR / 'backups'

DATA_DIR = APP_DIR / 'data'
ASSET_DIR = DATA_DIR / 'assets'
PROD_DIR = ASSET_DIR / 'products'
BUNDLED_DATA_DIR = RESOURCE_DIR / 'data'
BUNDLED_ASSET_DIR = BUNDLED_DATA_DIR / 'assets'

for d in (USER_DATA_DIR, USER_ASSET_DIR, USER_PRODUCT_DIR, BACKUP_DIR, DATA_DIR, ASSET_DIR, PROD_DIR):
    try: d.mkdir(parents=True, exist_ok=True)
    except Exception: pass

DB_PATH = USER_DATA_DIR / 'caisse.db'

# Préservation intégrale et migration automatique des anciennes bases (MINI_SUPERMARCHE & local)
if not DB_PATH.exists():
    legacy_candidates = [
        LOCAL_APPDATA / 'MINI_SUPERMARCHE' / 'caisse.db',
        DATA_DIR / 'caisse.db',
        BUNDLED_DATA_DIR / 'caisse.db'
    ]
    for candidate in legacy_candidates:
        if candidate.exists():
            try:
                shutil.copy2(candidate, DB_PATH)
                break
            except Exception:
                pass

THEMES = {
    'Bleu TOP-BOX': {'bg': '#0f172a', 'sidebar': '#0a0f1d', 'card': '#1e293b', 'card_inner': '#162032', 'accent': '#3b82f6', 'accent_hover': '#2563eb', 'accent2': '#60a5fa', 'soft': '#1e3a8a', 'text': '#f8fafc', 'muted': '#94a3b8', 'line': '#334155', 'warn': '#f59e0b', 'danger': '#ef4444', 'ok': '#10b981', 'highlight': '#1e293b'},
    'Bleu': {'bg': '#f8fafc', 'sidebar': '#0b1f3a', 'card': '#ffffff', 'card_inner': '#f1f5f9', 'accent': '#2563eb', 'accent_hover': '#1d4ed8', 'accent2': '#60a5fa', 'soft': '#eff6ff', 'text': '#0f172a', 'muted': '#64748b', 'line': '#e2e8f0', 'warn': '#f59e0b', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#f1f5f9'},
    'Bleu Royal': {'bg': '#f5f8ff', 'sidebar': '#122b5c', 'card': '#ffffff', 'card_inner': '#ebf2ff', 'accent': '#315ee7', 'accent_hover': '#2146c7', 'accent2': '#7aa2ff', 'soft': '#eaf0ff', 'text': '#102044', 'muted': '#66779b', 'line': '#dbe4f7', 'warn': '#f59e0b', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#f0f5ff'},
    'Bleu Nuit': {'bg': '#0b132b', 'sidebar': '#070c1e', 'card': '#1c2541', 'card_inner': '#131b31', 'accent': '#48cae4', 'accent_hover': '#0096c7', 'accent2': '#90e0ef', 'soft': '#1b3b5a', 'text': '#f8fafc', 'muted': '#8d99ae', 'line': '#2d3748', 'warn': '#f59e0b', 'danger': '#ef4444', 'ok': '#10b981', 'highlight': '#232f52'},
    'Turquoise': {'bg': '#f0fdfa', 'sidebar': '#042f2e', 'card': '#ffffff', 'card_inner': '#ccfbf1', 'accent': '#0d9488', 'accent_hover': '#0f766e', 'accent2': '#2dd4bf', 'soft': '#e6fffa', 'text': '#134e4a', 'muted': '#5eead4', 'line': '#99f6e4', 'warn': '#d97706', 'danger': '#dc2626', 'ok': '#059669', 'highlight': '#e6fffa'},
    'Émeraude': {'bg': '#f0fdf4', 'sidebar': '#064e3b', 'card': '#ffffff', 'card_inner': '#dcfce7', 'accent': '#059669', 'accent_hover': '#047857', 'accent2': '#34d399', 'soft': '#e8f5e9', 'text': '#064e3b', 'muted': '#6ee7b7', 'line': '#a7f3d0', 'warn': '#d97706', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#e8f5e9'},
    'Violet': {'bg': '#faf5ff', 'sidebar': '#3b0764', 'card': '#ffffff', 'card_inner': '#f3e8ff', 'accent': '#7e22ce', 'accent_hover': '#6b21a8', 'accent2': '#c084fc', 'soft': '#f3e8ff', 'text': '#3b0764', 'muted': '#a855f7', 'line': '#e9d5ff', 'warn': '#d97706', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#f3e8ff'},
    'Orange': {'bg': '#fff7ed', 'sidebar': '#431407', 'card': '#ffffff', 'card_inner': '#ffedd5', 'accent': '#ea580c', 'accent_hover': '#c2410c', 'accent2': '#fb923c', 'soft': '#ffedd5', 'text': '#431407', 'muted': '#fb923c', 'line': '#fed7aa', 'warn': '#d97706', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#ffedd5'},
    'Graphite': {'bg': '#f8fafc', 'sidebar': '#1e293b', 'card': '#ffffff', 'card_inner': '#f1f5f9', 'accent': '#475569', 'accent_hover': '#334155', 'accent2': '#94a3b8', 'soft': '#e2e8f0', 'text': '#0f172a', 'muted': '#64748b', 'line': '#cbd5e1', 'warn': '#d97706', 'danger': '#dc2626', 'ok': '#16a34a', 'highlight': '#f1f5f9'},
    'Sombre': {'bg': '#090d16', 'sidebar': '#05070c', 'card': '#121826', 'card_inner': '#0c101a', 'accent': '#38bdf8', 'accent_hover': '#0284c7', 'accent2': '#7dd3fc', 'soft': '#0c2340', 'text': '#f8fafc', 'muted': '#94a3b8', 'line': '#1e293b', 'warn': '#fbbf24', 'danger': '#f87171', 'ok': '#34d399', 'highlight': '#1e293b'}
}

def now(): return datetime.datetime.now()

def safe_float(s):
    try: return float(str(s).replace(' ', '').replace(',', '.'))
    except Exception: return 0.0

def money(v, cur='FCFA'):
    try: val = float(v)
    except Exception: val = 0.0
    return f"{val:,.0f}".replace(',', ' ') + (f" {cur}" if cur else "")

def fit_image(path, max_w, max_h, master=None):
    try:
        raw = Path(path)
        candidates = [raw] if raw.is_absolute() else [APP_DIR / raw, RESOURCE_DIR / raw]
        candidates += [USER_ASSET_DIR / raw.name, BUNDLED_ASSET_DIR / raw.name, ASSET_DIR / raw.name]
        found = next((x for x in candidates if x.is_file()), None)
        if not found: return None
        im = Image.open(found).convert('RGBA')
        im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        bg = Image.new('RGBA', (max_w, max_h), (255, 255, 255, 0))
        x = (max_w - im.width) // 2
        y = (max_h - im.height) // 2
        bg.paste(im, (x, y), im)
        return ImageTk.PhotoImage(bg, master=master)
    except Exception:
        return None

# ==============================================================================
# GESTION BASE DE DONNÉES SQLite (100% RÉTRO-COMPATIBLE)
# ==============================================================================
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.init()

    def init(self):
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            price REAL DEFAULT 0,
            qty REAL DEFAULT 0,
            image TEXT DEFAULT '',
            expiry_date TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice TEXT UNIQUE,
            date TEXT,
            subtotal REAL,
            discount REAL,
            tax_rate REAL,
            tax REAL,
            total REAL,
            received REAL,
            change_amt REAL,
            cashier TEXT,
            register TEXT,
            printed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS sale_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            name TEXT,
            qty REAL,
            unit_price REAL,
            total REAL
        );
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            note TEXT
        );
        CREATE TABLE IF NOT EXISTS settings(
            k TEXT PRIMARY KEY,
            v TEXT
        );
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Caissier',
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS cash_closings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            closed_at TEXT,
            total_sales REAL,
            cash_received REAL,
            change_given REAL,
            discount_total REAL,
            sales_count INTEGER,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT '',
            loyalty_points INTEGER DEFAULT 0,
            debt REAL DEFAULT 0,
            notes TEXT DEFAULT ''
        );
        ''')
        # Vérification colonnes optionnelles
        scols = [r['name'] for r in self.conn.execute('PRAGMA table_info(sales)').fetchall()]
        if 'printed' not in scols:
            self.conn.execute("ALTER TABLE sales ADD COLUMN printed INTEGER DEFAULT 0")

        pcols = [r['name'] for r in self.conn.execute('PRAGMA table_info(products)').fetchall()]
        if 'expiry_date' not in pcols:
            self.conn.execute("ALTER TABLE products ADD COLUMN expiry_date TEXT DEFAULT ''")

        self.conn.commit()
        self.seed()

    def setting(self, k, default=''):
        r = self.conn.execute('SELECT v FROM settings WHERE k=?', (k,)).fetchone()
        return r['v'] if r else default

    def set_setting(self, k, v):
        self.conn.execute('INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v', (k, str(v)))

    def products(self, q=''):
        if q:
            return self.conn.execute(
                'SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name COLLATE NOCASE',
                (f'%{q}%', f'%{q}%')
            ).fetchall()
        return self.conn.execute('SELECT * FROM products ORDER BY name COLLATE NOCASE').fetchall()

    def seed(self):
        defaults = {
            'company': 'TOP-BOX',
            'register': 'CAISSE CENTRALE 01',
            'cashier': 'Caissier Principal',
            'currency': 'FCFA',
            'header': 'TOP-BOX — COMMERCE MODERNE',
            'address': 'Centre Commercial, Avenue Principale',
            'phone': '+225 07 00 00 00 00',
            'email': 'contact@topbox-caisse.com',
            'footer': 'Merci pour votre confiance ! À très bientôt.',
            'logo': '',
            'icon': '',
            'tax_enabled': '0',
            'tax_rate': '0',
            'discount_enabled': '1',
            'default_discount': '0',
            'ticket_format': '80MM',
            'stock_threshold': '5',
            'allow_negative_stock': '0',
            'auto_ticket': '1',
            'theme': 'Bleu TOP-BOX',
            'require_login': '1'
        }
        for k, v in defaults.items():
            if self.conn.execute('SELECT 1 FROM settings WHERE k=?', (k,)).fetchone() is None:
                self.set_setting(k, v)
        self.conn.commit()

# ==============================================================================
# INTERFACE GRAPHIQUE MODERNE TOP-BOX
# ==============================================================================
class TopBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = DB()
        theme_name = self.db.setting('theme', 'Bleu TOP-BOX')
        self.theme = THEMES.get(theme_name, THEMES['Bleu TOP-BOX'])
        self.title(f"TOP-BOX — {self.db.setting('company', 'Système de Caisse')}")
        self.geometry('1340x820')
        self.minsize(1180, 720)
        self.cart = self.load_saved_cart()
        self._after_id = None
        self._blink = False
        self.current_user = None
        self.current_page = 'dashboard'

        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.apply_window_icon()

        if self.db.setting('require_login', '1') != '1':
            self.current_user = {'id': 0, 'username': 'Accès Direct', 'role': 'Administrateur'}
            authenticated = True
        else:
            authenticated = self.authenticate()

        if not authenticated:
            self.db.conn.close()
            self.destroy()
            return

        self.deiconify()
        self.build_ui()
        self.show_dashboard()
        self.start_live_daemon()

    def apply_window_icon(self):
        try:
            candidates = [
                USER_ASSET_DIR / 'app.ico',
                ASSET_DIR / 'app.ico',
                BUNDLED_ASSET_DIR / 'app.ico'
            ]
            for c in candidates:
                if c.is_file():
                    self.iconbitmap(str(c))
                    return
        except Exception:
            pass

    def authenticate(self):
        count = self.db.conn.execute('SELECT COUNT(*) n FROM users').fetchone()['n']
        t = self.theme
        win = tk.Toplevel(self)
        win.title('Connexion — TOP-BOX POS')
        win.configure(bg=t['bg'])
        win.resizable(False, False)
        self.center_window(win, 480, 480 if count else 510)
        win.transient('')
        win.grab_set()

        shell = tk.Frame(win, bg=t['bg'])
        shell.pack(fill='both', expand=True, padx=24, pady=24)

        # Header élégant
        hero = tk.Frame(shell, bg=t['sidebar'], height=120)
        hero.pack(fill='x', pady=(0, 16))
        hero.pack_propagate(False)

        tk.Label(hero, text='TOP-BOX', bg=t['sidebar'], fg=t['accent2'], font=('Segoe UI', 24, 'bold')).pack(pady=(20, 2))
        tk.Label(hero, text='SOLUTION DE CAISSE ENREGISTREUSE HAUT DE GAMME', bg=t['sidebar'], fg='#94a3b8', font=('Segoe UI', 8, 'bold')).pack()

        tk.Label(shell, text='Créer le compte administrateur initial' if not count else 'Connectez-vous pour ouvrir la caisse',
                 bg=t['bg'], fg=t['muted'], font=('Segoe UI', 10)).pack(pady=(0, 14))

        card = tk.Frame(shell, bg=t['card'], highlightbackground=t['line'], highlightthickness=1)
        card.pack(fill='x', padx=6)
        form = tk.Frame(card, bg=t['card'])
        form.pack(fill='x', padx=20, pady=18)

        tk.Label(form, text='IDENTIFIANT', bg=t['card'], fg=t['muted'], font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        user_var = tk.StringVar(value='admin' if not count else '')
        user_ent = ttk.Entry(form, textvariable=user_var, font=('Segoe UI', 10))
        user_ent.pack(fill='x', pady=(4, 12), ipady=5)

        tk.Label(form, text='MOT DE PASSE', bg=t['card'], fg=t['muted'], font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        pw_var = tk.StringVar()
        pw_ent = ttk.Entry(form, textvariable=pw_var, show='•', font=('Segoe UI', 10))
        pw_ent.pack(fill='x', pady=(4, 4), ipady=5)

        result = {'ok': False}

        def submit(event=None):
            name = user_var.get().strip()
            password = pw_var.get()
            if not name or not password:
                messagebox.showwarning('Connexion', 'Veuillez saisir votre identifiant et mot de passe.', parent=win)
                return
            digest = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if count == 0:
                if len(password) < 6:
                    messagebox.showwarning('Sécurité', 'Le mot de passe doit comporter au moins 6 caractères.', parent=win)
                    return
                try:
                    self.db.conn.execute('INSERT INTO users(username,password_hash,role,active) VALUES(?,?,?,1)',
                                         (name, digest, 'Administrateur'))
                    self.db.conn.commit()
                except sqlite3.IntegrityError:
                    messagebox.showerror('Erreur', 'Cet identifiant existe déjà.', parent=win)
                    return
                row = self.db.conn.execute('SELECT id,username,role FROM users WHERE username=?', (name,)).fetchone()
            else:
                row = self.db.conn.execute('SELECT id,username,role,password_hash,active FROM users WHERE lower(trim(username))=lower(trim(?))',
                                           (name,)).fetchone()
                if not row or row['password_hash'] != digest:
                    messagebox.showerror('Connexion', 'Identifiant ou mot de passe incorrect.', parent=win)
                    pw_var.set('')
                    pw_ent.focus_set()
                    return
                if not row['active']:
                    messagebox.showerror('Accès refusé', 'Ce compte est actuellement désactivé.', parent=win)
                    return

            self.current_user = {'id': row['id'], 'username': row['username'], 'role': row['role']}
            result['ok'] = True
            win.destroy()

        btn_box = tk.Frame(shell, bg=t['bg'])
        btn_box.pack(fill='x', padx=6, pady=(16, 0))
        ttk.Button(btn_box, text='Créer le compte et démarrer' if not count else 'Connexion Sécurisée', command=submit).pack(fill='x', ipady=6)

        win.bind('<Return>', submit)
        if count: user_ent.focus_set()
        else: pw_ent.focus_set()
        self.wait_window(win)
        return result['ok']

    def center_window(self, win, w, h):
        try:
            win.update_idletasks()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            win.geometry(f"{w}x{h}+100+80")

    def load_saved_cart(self):
        raw = self.db.setting('cart_state', '[]')
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def save_cart(self):
        self.db.set_setting('cart_state', json.dumps(self.cart, ensure_ascii=False))
        self.db.conn.commit()

    def build_ui(self):
        t = self.theme
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('.', font=('Segoe UI', 10), background=t['bg'], foreground=t['text'])
        s.configure('TButton', font=('Segoe UI', 9, 'bold'), padding=(10, 6))
        s.configure('Treeview', font=('Segoe UI', 10), rowheight=36, background=t['card'], fieldbackground=t['card'], foreground=t['text'])
        s.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background=t['line'], foreground=t['text'])

        for w in self.winfo_children():
            w.destroy()

        # BARRE LATÉRALE MODERNE
        sidebar = tk.Frame(self, bg=t['sidebar'], width=240)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        brand_frame = tk.Frame(sidebar, bg=t['sidebar'])
        brand_frame.pack(fill='x', padx=18, pady=(24, 20))

        tk.Label(brand_frame, text='TOP-BOX', bg=t['sidebar'], fg=t['accent2'], font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        company_name = self.db.setting('company', 'Caisse Pro').strip()
        tk.Label(brand_frame, text=company_name, bg=t['sidebar'], fg=t['muted'], font=('Segoe UI', 9)).pack(anchor='w')

        nav_items = [
            ('Tableau de bord', self.show_dashboard, 'dashboard'),
            ('Nouvelle vente', self.show_sale, 'sale'),
            ('Produits & stock', self.show_products, 'products'),
            ('Historique des ventes', self.show_history, 'history'),
            ('Clients & Crédits', self.show_clients, 'clients'),
            ('Carnet de caisse', self.show_notes, 'notes'),
            ('Paramètres', self.show_settings, 'settings'),
        ]

        self.nav_buttons = {}
        for label, cmd, key in nav_items:
            btn = tk.Button(sidebar, text=f"  {label}", command=cmd,
                            bg=t['sidebar'], fg='#cbd5e1', activebackground=t['accent'], activeforeground='white',
                            relief='flat', anchor='w', font=('Segoe UI', 10, 'bold'), padx=14, pady=11, cursor='hand2')
            btn.pack(fill='x', padx=10, pady=2)
            self.nav_buttons[key] = btn

        # Badge utilisateur
        if self.current_user:
            user_box = tk.Frame(sidebar, bg=t['card_inner'], highlightbackground=t['line'], highlightthickness=1)
            user_box.pack(side='bottom', fill='x', padx=12, pady=16)
            tk.Label(user_box, text=self.current_user['username'], bg=t['card_inner'], fg=t['text'], font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=10, pady=(8, 1))
            tk.Label(user_box, text=f"Rôle : {self.current_user['role']}", bg=t['card_inner'], fg=t['accent2'], font=('Segoe UI', 8)).pack(anchor='w', padx=10, pady=(0, 8))

        # CONTENEUR PRINCIPAL
        self.main_container = tk.Frame(self, bg=t['bg'])
        self.main_container.pack(side='left', fill='both', expand=True)

    def set_nav_active(self, key):
        self.current_page = key
        t = self.theme
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg=t['accent'], fg='white')
            else:
                btn.configure(bg=t['sidebar'], fg='#cbd5e1')

    def page_header(self, title, subtitle=''):
        for w in self.main_container.winfo_children():
            w.destroy()
        t = self.theme
        header = tk.Frame(self.main_container, bg=t['bg'])
        header.pack(fill='x', padx=28, pady=(20, 10))
        tk.Label(header, text=title, bg=t['bg'], fg=t['text'], font=('Segoe UI', 22, 'bold')).pack(anchor='w')
        if subtitle:
            tk.Label(header, text=subtitle, bg=t['bg'], fg=t['muted'], font=('Segoe UI', 10)).pack(anchor='w', pady=(2, 0))

    def create_card(self, parent):
        t = self.theme
        return tk.Frame(parent, bg=t['card'], highlightbackground=t['line'], highlightthickness=1)

    # ==========================================================================
    # TABLEAU DE BORD (DASHBOARD)
    # ==========================================================================
    def show_dashboard(self):
        self.set_nav_active('dashboard')
        self.page_header('Tableau de bord', 'Statistiques en direct, indicateurs de rentabilité et état des stocks')
        t = self.theme

        wrap = tk.Frame(self.main_container, bg=t['bg'])
        wrap.pack(fill='both', expand=True, padx=28, pady=4)

        # Ligne des 4 KPI
        kpi_row = tk.Frame(wrap, bg=t['bg'])
        kpi_row.pack(fill='x', pady=(0, 12))

        self.kpi_labels = []
        kpi_defs = [
            ('Chiffre d’affaires du jour', '0', t['accent']),
            ('Nombre de ventes', '0', t['accent2']),
            ('Articles en catalogue', '0', t['ok']),
            ('Alertes rupture / stock bas', '0', t['warn']),
        ]

        for title, default_val, accent_color in kpi_defs:
            c = self.create_card(kpi_row)
            c.pack(side='left', fill='x', expand=True, padx=(0, 10))
            tk.Frame(c, bg=accent_color, height=4).pack(fill='x')
            tk.Label(c, text=title, bg=t['card'], fg=t['muted'], font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=14, pady=(10, 2))
            val_lbl = tk.Label(c, text=default_val, bg=t['card'], fg=t['text'], font=('Segoe UI', 20, 'bold'))
            val_lbl.pack(anchor='w', padx=14, pady=(0, 12))
            self.kpi_labels.append(val_lbl)

        # Barre d'actions intelligentes & alertes
        smart_bar = self.create_card(wrap)
        smart_bar.pack(fill='x', pady=(0, 12))
        tk.Frame(smart_bar, bg=t['accent'], height=3).pack(fill='x')

        actions_inner = tk.Frame(smart_bar, bg=t['card'])
        actions_inner.pack(fill='x', padx=14, pady=10)

        tk.Label(actions_inner, text='Analyses & Outils :', bg=t['card'], fg=t['text'], font=('Segoe UI', 11, 'bold')).pack(side='left', padx=(0, 10))
        for label, fn in [('Top Produits', lambda: self.smart_modal('top')),
                          ('Produits Inactifs', lambda: self.smart_modal('dead')),
                          ('Meilleur Jour', lambda: self.smart_modal('day')),
                          ('Heures Fortes', lambda: self.smart_modal('hour'))]:
            tk.Button(actions_inner, text=label, command=fn, bg=t['soft'], fg=t['accent'],
                      relief='flat', font=('Segoe UI', 9, 'bold'), padx=10, pady=5, cursor='hand2').pack(side='left', padx=3)

        tk.Button(actions_inner, text='Calculatrice', command=self.open_calculator, bg=t['card_inner'], fg=t['text'],
                  relief='flat', font=('Segoe UI', 9, 'bold'), padx=10, pady=5, cursor='hand2').pack(side='right', padx=4)
        tk.Button(actions_inner, text='Alertes Péremption', command=self.open_expiry_alerts, bg=t['warn'], fg='white',
                  relief='flat', font=('Segoe UI', 9, 'bold'), padx=10, pady=5, cursor='hand2').pack(side='right', padx=4)
        tk.Button(actions_inner, text='Alertes Rupture', command=self.open_stock_alerts, bg=t['danger'], fg='white',
                  relief='flat', font=('Segoe UI', 9, 'bold'), padx=10, pady=5, cursor='hand2').pack(side='right', padx=4)

        # Tableau d'état des stocks
        table_card = self.create_card(wrap)
        table_card.pack(fill='both', expand=True, pady=(0, 8))
        tk.Frame(table_card, bg=t['accent2'], height=3).pack(fill='x')

        top_tbl = tk.Frame(table_card, bg=t['card'])
        top_tbl.pack(fill='x', padx=16, pady=10)
        tk.Label(top_tbl, text='Surveillance du stock en direct', bg=t['card'], fg=t['text'], font=('Segoe UI', 12, 'bold')).pack(side='left')

        cols = ('num', 'name', 'qty', 'price', 'status', 'expiry')
        self.dash_tree = ttk.Treeview(table_card, columns=cols, show='headings')
        headers = [('num', '#', 45), ('name', 'Article', 320), ('qty', 'Quantité', 100),
                   ('price', 'Prix Unitaire', 140), ('status', 'État du Stock', 140), ('expiry', 'Péremption', 120)]
        for col, hname, w in headers:
            self.dash_tree.heading(col, text=hname)
            self.dash_tree.column(col, width=w, anchor='center' if col != 'name' else 'w')

        sb = ttk.Scrollbar(table_card, orient='vertical', command=self.dash_tree.yview)
        self.dash_tree.configure(yscrollcommand=sb.set)
        self.dash_tree.pack(side='left', fill='both', expand=True, padx=(12, 0), pady=(0, 12))
        sb.pack(side='right', fill='y', padx=(0, 12), pady=(0, 12))

        self.refresh_dashboard_data()

    def refresh_dashboard_data(self):
        if not hasattr(self, 'kpi_labels') or not self.kpi_labels: return
        try:
            cur = self.db.setting('currency', 'FCFA')
            today = now().strftime('%Y-%m-%d')
            row = self.db.conn.execute('SELECT COALESCE(SUM(total),0) t, COUNT(*) n FROM sales WHERE date LIKE ?', (today + '%',)).fetchone()
            nprod = self.db.conn.execute('SELECT COUNT(*) n FROM products').fetchone()['n']
            th = safe_float(self.db.setting('stock_threshold', '5'))
            low = self.db.conn.execute('SELECT COUNT(*) n FROM products WHERE qty <= ?', (th,)).fetchone()['n']

            values = [money(row['t'], cur), str(row['n']), str(nprod), str(low)]
            for lbl, val in zip(self.kpi_labels, values):
                lbl.configure(text=val)

            if hasattr(self, 'dash_tree') and self.dash_tree.winfo_exists():
                for item in self.dash_tree.get_children():
                    self.dash_tree.delete(item)
                for idx, p in enumerate(self.db.products(), 1):
                    q = float(p['qty'])
                    status = 'RUPTURE' if q <= 0 else ('STOCK BAS' if q <= th else 'NORMAL')
                    tag = 'zero' if q <= 0 else ('low' if q <= th else 'ok')
                    self.dash_tree.insert('', 'end', values=(idx, p['name'], f"{q:g}", money(p['price'], cur), status, p['expiry_date'] or '—'), tags=(tag,))

                blink = getattr(self, '_blink', False)
                self.dash_tree.tag_configure('zero', background='#fef2f2' if not blink else '#fee2e2', foreground='#dc2626')
                self.dash_tree.tag_configure('low', background='#fffbeb' if not blink else '#fef3c7', foreground='#b45309')
                self.dash_tree.tag_configure('ok', background=self.theme['card'], foreground=self.theme['text'])
        except Exception:
            pass

    def start_live_daemon(self):
        self._blink = not getattr(self, '_blink', False)
        if self.current_page == 'dashboard':
            self.refresh_dashboard_data()
        self._after_id = self.after(1000, self.start_live_daemon)

    # ==========================================================================
    # NOUVELLE VENTE / ENCAISSEMENT RAPIDE
    # ==========================================================================
    def show_sale(self):
        self.set_nav_active('sale')
        self.page_header('Nouvelle Vente', 'Sélectionnez les articles, ajustez le panier et encaissez')
        t = self.theme

        grid_frame = tk.Frame(self.main_container, bg=t['bg'])
        grid_frame.pack(fill='both', expand=True, padx=28, pady=2)
        grid_frame.columnconfigure(0, weight=5)
        grid_frame.columnconfigure(1, weight=3)
        grid_frame.columnconfigure(2, weight=4)
        grid_frame.rowconfigure(1, weight=1)

        # Barre supérieure de recherche
        search_bar = tk.Frame(grid_frame, bg=t['bg'])
        search_bar.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 10))

        self.sale_search_var = tk.StringVar()
        s_ent = ttk.Entry(search_bar, textvariable=self.sale_search_var, font=('Segoe UI', 11))
        s_ent.pack(side='left', fill='x', expand=True, ipady=4)
        s_ent.focus_set()
        tk.Label(search_bar, text=' 🔍 Recherche par nom ou référence', bg=t['bg'], fg=t['muted'], font=('Segoe UI', 9)).pack(side='left', padx=8)
        self.sale_search_var.trace_add('write', lambda *_: self.refresh_sale_items())

        ttk.Button(search_bar, text='Calculatrice', command=self.open_calculator).pack(side='right')

        # COLONNE GAUCHE : Catalogue Articles
        left_card = self.create_card(grid_frame)
        left_card.grid(row=1, column=0, sticky='nsew', padx=(0, 8))
        left_card.rowconfigure(1, weight=1)
        left_card.columnconfigure(0, weight=1)

        tk.Label(left_card, text='Catalogue Produits', bg=t['card'], fg=t['text'], font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=14, pady=10)

        cols = ('id', 'name', 'price', 'stock')
        self.sale_tree = ttk.Treeview(left_card, columns=cols, show='headings')
        self.sale_tree.heading('id', text='#')
        self.sale_tree.heading('name', text='Article')
        self.sale_tree.heading('price', text='Prix')
        self.sale_tree.heading('stock', text='Stock')
        self.sale_tree.column('id', width=45, anchor='center')
        self.sale_tree.column('name', width=220, anchor='w')
        self.sale_tree.column('price', width=110, anchor='e')
        self.sale_tree.column('stock', width=80, anchor='center')

        sb = ttk.Scrollbar(left_card, orient='vertical', command=self.sale_tree.yview)
        self.sale_tree.configure(yscrollcommand=sb.set)
        self.sale_tree.grid(row=1, column=0, sticky='nsew', padx=(10, 0), pady=(0, 10))
        sb.grid(row=1, column=1, sticky='ns', pady=(0, 10), padx=(0, 10))

        self.sale_tree.bind('<<TreeviewSelect>>', self.on_sale_select)
        self.sale_tree.bind('<Double-1>', self.on_sale_double_click)

        # COLONNE DU MILIEU : Aperçu Visuel
        mid_card = self.create_card(grid_frame)
        mid_card.grid(row=1, column=1, sticky='nsew', padx=4)
        tk.Label(mid_card, text='Visuel Produit', bg=t['card'], fg=t['text'], font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=14, pady=10)
        self.preview_lbl = tk.Label(mid_card, text='Sélectionnez un article\npour voir l’aperçu', bg=t['card_inner'], fg=t['muted'])
        self.preview_lbl.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        # COLONNE DROITE : Panier & Total
        right_card = self.create_card(grid_frame)
        right_card.grid(row=1, column=2, sticky='nsew', padx=(8, 0))
        right_card.rowconfigure(1, weight=1)

        tk.Label(right_card, text='Panier Courant', bg=t['card'], fg=t['text'], font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=14, pady=10)

        cart_cols = ('name', 'qty', 'total')
        self.cart_tree = ttk.Treeview(right_card, columns=cart_cols, show='headings', height=7)
        self.cart_tree.heading('name', text='Article')
        self.cart_tree.heading('qty', text='Qté')
        self.cart_tree.heading('total', text='Total')
        self.cart_tree.column('name', width=160, anchor='w')
        self.cart_tree.column('qty', width=60, anchor='center')
        self.cart_tree.column('total', width=100, anchor='e')
        self.cart_tree.pack(fill='both', expand=True, padx=12)

        self.total_lbl = tk.Label(right_card, text='Total : 0 FCFA', bg=t['card'], fg=t['accent2'], font=('Segoe UI', 18, 'bold'))
        self.total_lbl.pack(anchor='e', padx=14, pady=10)

        actions_box = tk.Frame(right_card, bg=t['card'])
        actions_box.pack(fill='x', padx=10, pady=(0, 12))

        ttk.Button(actions_box, text='Vider', command=self.clear_cart).pack(side='left', padx=2)
        ttk.Button(actions_box, text='Supprimer', command=self.remove_cart_item).pack(side='left', padx=2)
        tk.Button(actions_box, text='ENCAISSER  ➔', command=self.start_checkout,
                  bg=t['ok'], fg='white', relief='flat', font=('Segoe UI', 11, 'bold'), padx=14, pady=6, cursor='hand2').pack(side='right', padx=2)

        self.refresh_sale_items()
        self.render_cart()

    def refresh_sale_items(self):
        if not hasattr(self, 'sale_tree') or not self.sale_tree.winfo_exists(): return
        try:
            for item in self.sale_tree.get_children():
                self.sale_tree.delete(item)
            q = self.sale_search_var.get()
            cur = self.db.setting('currency', 'FCFA')
            for idx, p in enumerate(self.db.products(q), 1):
                self.sale_tree.insert('', 'end', iid=str(p['id']),
                                      values=(idx, p['name'], money(p['price'], cur), f"{float(p['qty']):g}"))
        except Exception:
            pass

    def on_sale_select(self, e=None):
        sel = self.sale_tree.selection()
        if not sel: return
        p = self.db.conn.execute('SELECT * FROM products WHERE id=?', (int(sel[0]),)).fetchone()
        if p and p['image']:
            img = fit_image(p['image'], 280, 280, master=self.preview_lbl)
            if img:
                self.preview_lbl.configure(image=img, text='')
                self.preview_lbl.image = img
                return
        self.preview_lbl.configure(image='', text=p['name'] if p else 'Aucun visuel')

    def on_sale_double_click(self, e=None):
        sel = self.sale_tree.selection()
        if not sel: return
        pid = int(sel[0])
        p = self.db.conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        if not p: return

        # Boîte de dialogue pour la quantité
        win = tk.Toplevel(self)
        win.title('Ajouter au panier')
        win.configure(bg=self.theme['bg'])
        win.resizable(False, False)
        self.center_window(win, 380, 220)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=p['name'], bg=self.theme['bg'], fg=self.theme['text'], font=('Segoe UI', 12, 'bold')).pack(pady=(20, 4))
        tk.Label(win, text=f"En stock : {p['qty']}", bg=self.theme['bg'], fg=self.theme['muted']).pack()

        qty_var = tk.StringVar(value='1')
        q_ent = ttk.Entry(win, textvariable=qty_var, justify='center', font=('Segoe UI', 16))
        q_ent.pack(pady=14, ipady=4)
        q_ent.focus_set()

        def add():
            q = safe_float(qty_var.get())
            if q <= 0: return
            exist = next((x for x in self.cart if x['id'] == p['id']), None)
            if exist:
                exist['qty'] += q
            else:
                self.cart.append({'id': p['id'], 'name': p['name'], 'qty': q, 'price': float(p['price'])})
            self.save_cart()
            win.destroy()
            self.render_cart()

        bar = tk.Frame(win, bg=self.theme['bg'])
        bar.pack()
        ttk.Button(bar, text='Annuler', command=win.destroy).pack(side='left', padx=4)
        ttk.Button(bar, text='Valider', command=add).pack(side='left', padx=4)
        win.bind('<Return>', lambda _: add())

    def render_cart(self):
        if not hasattr(self, 'cart_tree') or not self.cart_tree.winfo_exists(): return
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        cur = self.db.setting('currency', 'FCFA')
        total = 0.0
        for x in self.cart:
            sub = x['qty'] * x['price']
            total += sub
            self.cart_tree.insert('', 'end', values=(x['name'], f"{x['qty']:g}", money(sub, cur)))
        self.total_lbl.configure(text=f"Total : {money(total, cur)}")

    def clear_cart(self):
        self.cart = []
        self.save_cart()
        self.render_cart()

    def remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel: return
        idx = self.cart_tree.index(sel[0])
        self.cart.pop(idx)
        self.save_cart()
        self.render_cart()

    def start_checkout(self):
        if not self.cart:
            messagebox.showwarning('Panier vide', 'Veuillez ajouter au moins un produit dans le panier.', parent=self)
            return

        cur = self.db.setting('currency', 'FCFA')
        subtotal = sum(x['qty'] * x['price'] for x in self.cart)

        # Étape 1 : Saisie montant reçu
        win = tk.Toplevel(self)
        win.title('Paiement et Encaissement')
        win.configure(bg=self.theme['bg'])
        win.resizable(False, False)
        self.center_window(win, 460, 420)
        win.transient(self)
        win.grab_set()

        t = self.theme
        card = self.create_card(win)
        card.pack(fill='both', expand=True, padx=18, pady=18)

        tk.Label(card, text='ENCAISSEMENT', bg=t['card'], fg=t['text'], font=('Segoe UI', 16, 'bold')).pack(pady=(16, 4))
        tk.Label(card, text=f"Total articles : {money(subtotal, cur)}", bg=t['card'], fg=t['muted'], font=('Segoe UI', 11)).pack(pady=(0, 14))

        # Remise optionnelle
        disc_frame = tk.Frame(card, bg=t['card'])
        disc_frame.pack(fill='x', padx=20, pady=4)
        tk.Label(disc_frame, text='Remise accordée (%) :', bg=t['card'], fg=t['text']).pack(side='left')
        disc_var = tk.StringVar(value=self.db.setting('default_discount', '0'))
        disc_ent = ttk.Entry(disc_frame, textvariable=disc_var, width=8, justify='center')
        disc_ent.pack(side='right')

        # TVA optionnelle
        tax_frame = tk.Frame(card, bg=t['card'])
        tax_frame.pack(fill='x', padx=20, pady=4)
        tk.Label(tax_frame, text='Taux TVA (%) :', bg=t['card'], fg=t['text']).pack(side='left')
        tax_var = tk.StringVar(value=self.db.setting('tax_rate', '0'))
        tax_ent = ttk.Entry(tax_frame, textvariable=tax_var, width=8, justify='center')
        tax_ent.pack(side='right')

        # Montant Reçu
        rec_frame = tk.Frame(card, bg=t['card'])
        rec_frame.pack(fill='x', padx=20, pady=12)
        tk.Label(rec_frame, text='Montant Encaissé :', bg=t['card'], fg=t['accent2'], font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        rec_var = tk.StringVar(value=str(int(subtotal)))
        rec_ent = ttk.Entry(rec_frame, textvariable=rec_var, font=('Segoe UI', 16), justify='center')
        rec_ent.pack(fill='x', pady=4, ipady=6)
        rec_ent.focus_set()

        change_lbl = tk.Label(card, text='Monnaie à rendre : 0 FCFA', bg=t['card'], fg=t['ok'], font=('Segoe UI', 12, 'bold'))
        change_lbl.pack(pady=6)

        def update_change(*_):
            try:
                d = max(0, min(100, safe_float(disc_var.get())))
                tx = max(0, min(100, safe_float(tax_var.get())))
                base = subtotal * (1 - d / 100)
                tot = base * (1 + tx / 100)
                rc = safe_float(rec_var.get())
                chg = rc - tot
                change_lbl.configure(text=f"Monnaie à rendre : {money(chg, cur)}", fg=t['ok'] if chg >= 0 else t['danger'])
            except Exception:
                pass

        disc_var.trace_add('write', update_change)
        tax_var.trace_add('write', update_change)
        rec_var.trace_add('write', update_change)
        update_change()

        def confirm_checkout():
            d = max(0, min(100, safe_float(disc_var.get())))
            tx = max(0, min(100, safe_float(tax_var.get())))
            base = subtotal * (1 - d / 100)
            tax_amt = base * (tx / 100)
            total = base + tax_amt
            received = safe_float(rec_var.get())

            if received + 1e-9 < total:
                messagebox.showerror('Montant insuffisant', f"Le montant reçu est inférieur au total ({money(total, cur)}).", parent=win)
                return

            # Vérification des stocks
            allow_neg = self.db.setting('allow_negative_stock', '0') == '1'
            for item in self.cart:
                cur_qty = self.db.conn.execute('SELECT qty FROM products WHERE id=?', (item['id'],)).fetchone()['qty']
                if not allow_neg and cur_qty < item['qty']:
                    messagebox.showerror('Stock insuffisant', f"Stock insuffisant pour {item['name']}.\nRestant : {cur_qty}", parent=win)
                    return

            # Enregistrement dans la base
            inv = f"FAC-{self.db.conn.execute('SELECT COALESCE(MAX(id),0)+1 FROM sales').fetchone()[0]:06d}"
            ts = now().strftime('%Y-%m-%d %H:%M:%S')
            chg = received - total

            cursor = self.db.conn.cursor()
            try:
                cursor.execute('''INSERT INTO sales(invoice,date,subtotal,discount,tax_rate,tax,total,received,change_amt,cashier,register,printed)
                                  VALUES(?,?,?,?,?,?,?,?,?,?,?,0)''',
                               (inv, ts, subtotal, subtotal * (d / 100), tx, tax_amt, total, received, chg,
                                self.current_user['username'] if self.current_user else '',
                                self.db.setting('register', 'CAISSE 01')))
                sale_id = cursor.lastrowid
                for item in self.cart:
                    cursor.execute('''INSERT INTO sale_items(sale_id,product_id,name,qty,unit_price,total)
                                      VALUES(?,?,?,?,?,?)''',
                                   (sale_id, item['id'], item['name'], item['qty'], item['price'], item['qty'] * item['price']))
                    cursor.execute('UPDATE products SET qty=qty-? WHERE id=?', (item['qty'], item['id']))
                self.db.conn.commit()
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror('Erreur vente', f"Échec de l'enregistrement : {e}", parent=win)
                return

            win.destroy()
            self.cart = []
            self.save_cart()
            self.render_cart()
            self.refresh_sale_items()
            self.refresh_dashboard_data()

            # Proposition impression ticket
            if messagebox.askyesno('Impression ticket', 'Vente validée avec succès !\nVoulez-vous imprimer le ticket de caisse ?', parent=self):
                self.print_ticket(inv)

        btn_bar = tk.Frame(card, bg=t['card'])
        btn_bar.pack(fill='x', padx=20, pady=(10, 0))
        ttk.Button(btn_bar, text='Annuler', command=win.destroy).pack(side='left')
        tk.Button(btn_bar, text='VALIDER LA VENTE', command=confirm_checkout,
                  bg=t['ok'], fg='white', relief='flat', font=('Segoe UI', 10, 'bold'), padx=14, pady=6, cursor='hand2').pack(side='right')

        win.bind('<Return>', lambda _: confirm_checkout())

    def print_ticket(self, invoice_number):
        s = self.db.conn.execute('SELECT * FROM sales WHERE invoice=?', (invoice_number,)).fetchone()
        if not s: return
        items = self.db.conn.execute('SELECT * FROM sale_items WHERE sale_id=?', (s['id'],)).fetchall()
        cur = self.db.setting('currency', 'FCFA')

        lines = [
            '=' * 42,
            f"   {self.db.setting('header', 'TOP-BOX')}".center(42),
            f"   {self.db.setting('address', '')}".center(42),
            f"   Tél: {self.db.setting('phone', '')}".center(42),
            '=' * 42,
            f"Facture : {invoice_number}",
            f"Date    : {s['date']}",
            f"Caisse  : {s['register']}",
            f"Caissier: {s['cashier']}",
            '-' * 42,
            "ARTICLE               QTÉ      TOTAL",
            '-' * 42
        ]
        for it in items:
            name = it['name'][:18].ljust(18)
            qty = f"{it['qty']:g}".rjust(5)
            tot = money(it['total'], cur).rjust(15)
            lines.append(f"{name} {qty} {tot}")

        lines.extend([
            '-' * 42,
            f"Sous-total : {money(s['subtotal'], cur)}",
            f"Remise     : {money(s['discount'], cur)}",
            f"TVA        : {money(s['tax'], cur)}",
            f"NET TOTAL  : {money(s['total'], cur)}",
            f"Reçu       : {money(s['received'], cur)}",
            f"Rendu      : {money(s['change_amt'], cur)}",
            '=' * 42,
            f"{self.db.setting('footer', 'Merci de votre visite !')}".center(42),
            '=' * 42
        ])

        ticket_text = "\n".join(lines)
        temp_file = Path(tempfile.gettempdir()) / f"ticket_{invoice_number}.txt"
        temp_file.write_text(ticket_text, encoding='utf-8')

        # Fenêtre interactive de gestion du ticket
        win = tk.Toplevel(self)
        win.title(f"Ticket de Caisse — {invoice_number}")
        self.center_window(win, 480, 620)
        win.configure(bg=self.theme['bg'])

        header_frame = tk.Frame(win, bg=self.theme['card'])
        header_frame.pack(fill='x', padx=12, pady=(12, 6))
        tk.Label(header_frame, text=f"Facture : {invoice_number}", bg=self.theme['card'], fg=self.theme['text'], font=('Segoe UI', 11, 'bold')).pack(side='left', padx=10, pady=8)
        status_lbl = tk.Label(header_frame, text="Prêt pour impression", bg=self.theme['card'], fg=self.theme['accent2'], font=('Segoe UI', 9))
        status_lbl.pack(side='right', padx=10, pady=8)

        txt_frame = tk.Frame(win, bg='white', bd=1, relief='solid')
        txt_frame.pack(fill='both', expand=True, padx=12, pady=6)
        txt = tk.Text(txt_frame, font=('Courier New', 10), bg='white', fg='black')
        txt.pack(fill='both', expand=True, padx=8, pady=8)
        txt.insert('1.0', ticket_text)
        txt.configure(state='disabled')

        def do_print():
            if os.name == 'nt':
                try:
                    os.startfile(str(temp_file), 'print')
                    status_lbl.config(text="✅ Envoyé à l'imprimante !", fg=self.theme['ok'])
                    self.db.conn.execute('UPDATE sales SET printed=1 WHERE invoice=?', (invoice_number,))
                    self.db.conn.commit()
                except Exception as e:
                    messagebox.showinfo("Impression", f"Le ticket a été enregistré dans :\n{temp_file}\nVous pouvez l'imprimer depuis votre bloc-notes.", parent=win)
            else:
                messagebox.showinfo("Impression", f"Fichier temporaire créé :\n{temp_file}", parent=win)

        def do_copy():
            self.clipboard_clear()
            self.clipboard_append(ticket_text)
            status_lbl.config(text="✅ Copié dans le presse-papier !", fg=self.theme['ok'])

        def do_save():
            f = filedialog.asksaveasfilename(
                parent=win,
                title="Enregistrer le ticket",
                defaultextension=".txt",
                initialfile=f"Ticket_{invoice_number}.txt",
                filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")]
            )
            if f:
                Path(f).write_text(ticket_text, encoding='utf-8')
                status_lbl.config(text="✅ Ticket enregistré !", fg=self.theme['ok'])

        btn_bar = tk.Frame(win, bg=self.theme['bg'])
        btn_bar.pack(fill='x', padx=12, pady=(6, 12))

        ttk.Button(btn_bar, text="🖨️ Imprimer", command=do_print).pack(side='left', padx=4)
        ttk.Button(btn_bar, text="📋 Copier", command=do_copy).pack(side='left', padx=4)
        ttk.Button(btn_bar, text="💾 Enregistrer", command=do_save).pack(side='left', padx=4)
        ttk.Button(btn_bar, text="Fermer", command=win.destroy).pack(side='right', padx=4)

        # Tentative d'impression automatique en arrière-plan sous Windows
        if os.name == 'nt':
            try:
                os.startfile(str(temp_file), 'print')
                self.db.conn.execute('UPDATE sales SET printed=1 WHERE invoice=?', (invoice_number,))
                self.db.conn.commit()
                status_lbl.config(text="✅ Envoi automatique lancé", fg=self.theme['ok'])
            except Exception:
                pass

    # ==========================================================================
    # GESTION DES PRODUITS & STOCKS
    # ==========================================================================
    def show_products(self):
        self.set_nav_active('products')
        self.page_header('Catalogue Produits & Stocks', 'Ajoutez, modifiez ou réapprovisionnez vos articles')
        t = self.theme

        bar = tk.Frame(self.main_container, bg=t['bg'])
        bar.pack(fill='x', padx=28, pady=(0, 10))

        self.prod_q_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.prod_q_var, width=32, font=('Segoe UI', 10)).pack(side='left', ipady=4)
        tk.Label(bar, text=' 🔍 Filtrer', bg=t['bg'], fg=t['muted']).pack(side='left')
        self.prod_q_var.trace_add('write', lambda *_: self.refresh_product_table())

        ttk.Button(bar, text='＋ Ajouter un Produit', command=lambda: self.product_dialog()).pack(side='right')

        card = self.create_card(self.main_container)
        card.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        cols = ('id', 'name', 'desc', 'price', 'qty', 'expiry')
        self.prod_tree = ttk.Treeview(card, columns=cols, show='headings')
        headings = [('id', '#', 45), ('name', 'Nom Article', 240), ('desc', 'Description', 340),
                    ('price', 'Prix Unitaire', 130), ('qty', 'Stock Actuel', 100), ('expiry', 'Péremption', 120)]
        for col, hname, w in headings:
            self.prod_tree.heading(col, text=hname)
            self.prod_tree.column(col, width=w, anchor='center' if col in ('id', 'price', 'qty', 'expiry') else 'w')

        sb = ttk.Scrollbar(card, orient='vertical', command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=sb.set)
        self.prod_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        sb.pack(side='right', fill='y', padx=(0, 10), pady=10)

        self.prod_tree.bind('<Double-1>', lambda _: self.edit_selected_product())
        self.refresh_product_table()

    def refresh_product_table(self):
        if not hasattr(self, 'prod_tree') or not self.prod_tree.winfo_exists(): return
        for item in self.prod_tree.get_children():
            self.prod_tree.delete(item)
        cur = self.db.setting('currency', 'FCFA')
        q = self.prod_q_var.get()
        th = safe_float(self.db.setting('stock_threshold', '5'))
        for idx, p in enumerate(self.db.products(q), 1):
            q_val = float(p['qty'])
            tag = 'zero' if q_val <= 0 else ('low' if q_val <= th else 'ok')
            self.prod_tree.insert('', 'end', iid=str(p['id']),
                                  values=(idx, p['name'], p['description'], money(p['price'], cur), f"{q_val:g}", p['expiry_date'] or '—'),
                                  tags=(tag,))

    def edit_selected_product(self):
        sel = self.prod_tree.selection()
        if not sel: return
        self.product_dialog(int(sel[0]))

    def product_dialog(self, pid=None):
        p = self.db.conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone() if pid else None
        t = self.theme
        win = tk.Toplevel(self)
        win.title('Modifier Article' if p else 'Nouveau Produit')
        win.configure(bg=t['bg'])
        self.center_window(win, 620, 520)
        win.transient(self)
        win.grab_set()

        card = self.create_card(win)
        card.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(card, text='Fiche Produit' if p else 'Création d’un Article', bg=t['card'], fg=t['text'], font=('Segoe UI', 15, 'bold')).pack(anchor='w', padx=16, pady=12)

        vars_dict = {
            'name': tk.StringVar(value=p['name'] if p else ''),
            'desc': tk.StringVar(value=p['description'] if p else ''),
            'price': tk.StringVar(value=str(p['price']) if p else '0'),
            'qty': tk.StringVar(value=str(p['qty']) if p else '10'),
            'expiry': tk.StringVar(value=p['expiry_date'] if p and p['expiry_date'] else ''),
            'image': tk.StringVar(value=p['image'] if p and p['image'] else '')
        }

        form = tk.Frame(card, bg=t['card'])
        form.pack(fill='x', padx=16, pady=6)

        fields = [
            ('Nom de l’article *', 'name'),
            ('Description', 'desc'),
            ('Prix de vente *', 'price'),
            ('Quantité en stock *', 'qty'),
            ('Date de péremption (AAAA-MM-JJ)', 'expiry'),
        ]

        for idx, (label, key) in enumerate(fields):
            tk.Label(form, text=label, bg=t['card'], fg=t['text'], font=('Segoe UI', 9, 'bold')).grid(row=idx, column=0, sticky='w', pady=6)
            ent = ttk.Entry(form, textvariable=vars_dict[key], width=36)
            ent.grid(row=idx, column=1, sticky='ew', padx=(10, 0), pady=6, ipady=3)

        def pick_image():
            f = filedialog.askopenfilename(parent=win, title='Sélectionner image', filetypes=[('Images', '*.png *.jpg *.jpeg *.webp')])
            if f:
                dest = USER_PRODUCT_DIR / f"prod_{now().strftime('%Y%m%d%H%M%S')}{Path(f).suffix.lower()}"
                try:
                    shutil.copy2(f, dest)
                    vars_dict['image'].set(str(dest))
                except Exception:
                    pass

        img_row = tk.Frame(card, bg=t['card'])
        img_row.pack(fill='x', padx=16, pady=8)
        ttk.Button(img_row, text='📷 Choisir une photo', command=pick_image).pack(side='left')
        img_status = tk.Label(img_row, textvariable=vars_dict['image'], bg=t['card'], fg=t['muted'], font=('Segoe UI', 8))
        img_status.pack(side='left', padx=10)

        def save():
            name = vars_dict['name'].get().strip()
            if not name:
                messagebox.showwarning('Nom obligatoire', 'Veuillez saisir le nom du produit.', parent=win)
                return
            price = safe_float(vars_dict['price'].get())
            qty = safe_float(vars_dict['qty'].get())
            desc = vars_dict['desc'].get().strip()
            expiry = vars_dict['expiry'].get().strip()
            image = vars_dict['image'].get().strip()

            try:
                if pid:
                    self.db.conn.execute('''UPDATE products SET name=?, description=?, price=?, qty=?, image=?, expiry_date=?
                                            WHERE id=?''', (name, desc, price, qty, image, expiry, pid))
                else:
                    self.db.conn.execute('''INSERT INTO products(name, description, price, qty, image, expiry_date)
                                            VALUES(?,?,?,?,?,?)''', (name, desc, price, qty, image, expiry))
                self.db.conn.commit()
                win.destroy()
                self.refresh_product_table()
                self.refresh_dashboard_data()
            except sqlite3.IntegrityError:
                messagebox.showerror('Doublon', 'Un article portant ce nom existe déjà.', parent=win)

        btn_box = tk.Frame(card, bg=t['card'])
        btn_box.pack(fill='x', padx=16, pady=(16, 10))
        ttk.Button(btn_box, text='Annuler', command=win.destroy).pack(side='left')
        ttk.Button(btn_box, text='Enregistrer', command=save).pack(side='right')

    # ==========================================================================
    # HISTORIQUE DES VENTES
    # ==========================================================================
    def show_history(self):
        self.set_nav_active('history')
        self.page_header('Historique des Ventes', 'Consultez, réimprimez ou vérifiez les tickets émis')
        t = self.theme

        bar = tk.Frame(self.main_container, bg=t['bg'])
        bar.pack(fill='x', padx=28, pady=(0, 10))
        ttk.Button(bar, text='🗑 Vider l’historique (Admin)', command=self.clear_history).pack(side='right')

        card = self.create_card(self.main_container)
        card.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        cols = ('inv', 'date', 'total', 'cashier', 'received', 'change')
        self.hist_tree = ttk.Treeview(card, columns=cols, show='headings')
        headers = [('inv', 'Facture', 120), ('date', 'Date & Heure', 180), ('total', 'Net Payé', 140),
                   ('cashier', 'Caissier', 160), ('received', 'Reçu', 140), ('change', 'Monnaie', 140)]
        for col, hname, w in headers:
            self.hist_tree.heading(col, text=hname)
            self.hist_tree.column(col, width=w, anchor='center' if col in ('inv', 'date', 'cashier') else 'e')

        sb = ttk.Scrollbar(card, orient='vertical', command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=sb.set)
        self.hist_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        sb.pack(side='right', fill='y', padx=(0, 10), pady=10)

        cur = self.db.setting('currency', 'FCFA')
        rows = self.db.conn.execute('SELECT * FROM sales ORDER BY id DESC').fetchall()
        for r in rows:
            self.hist_tree.insert('', 'end', iid=str(r['id']),
                                  values=(r['invoice'], r['date'], money(r['total'], cur), r['cashier'] or '—',
                                          money(r['received'], cur), money(r['change_amt'], cur)))

        self.hist_tree.bind('<Double-1>', lambda _: self.preview_selected_history())

    def preview_selected_history(self):
        sel = self.hist_tree.selection()
        if not sel: return
        row = self.db.conn.execute('SELECT invoice FROM sales WHERE id=?', (int(sel[0]),)).fetchone()
        if row:
            self.print_ticket(row['invoice'])

    def clear_history(self):
        if self.current_user and self.current_user.get('role') != 'Administrateur':
            messagebox.showerror('Accès Refusé', "La purge de l'historique des ventes est strictement réservée à l'Administrateur.", parent=self)
            return
        if not messagebox.askyesno('Confirmer suppression', 'Voulez-vous vraiment effacer l’historique des ventes ?\nLes articles et stocks seront conservés.', parent=self):
            return
        self.db.conn.execute('DELETE FROM sale_items')
        self.db.conn.execute('DELETE FROM sales')
        self.db.conn.commit()
        self.show_history()
        self.refresh_dashboard_data()

    # ==========================================================================
    # CLIENTS & CRÉDITS
    # ==========================================================================
    def show_clients(self):
        self.set_nav_active('clients')
        self.page_header('Gestion des Clients & Fidélité', 'Suivi du portefeuille client, points et crédits en cours')
        t = self.theme

        bar = tk.Frame(self.main_container, bg=t['bg'])
        bar.pack(fill='x', padx=28, pady=(0, 10))
        ttk.Button(bar, text='＋ Nouveau Client', command=self.client_dialog).pack(side='right')

        card = self.create_card(self.main_container)
        card.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        cols = ('id', 'name', 'phone', 'debt', 'points')
        self.client_tree = ttk.Treeview(card, columns=cols, show='headings')
        headers = [('id', '#', 45), ('name', 'Nom du Client', 260), ('phone', 'Téléphone', 160),
                   ('debt', 'Dette / Crédit', 140), ('points', 'Points Fidélité', 120)]
        for col, hname, w in headers:
            self.client_tree.heading(col, text=hname)
            self.client_tree.column(col, width=w, anchor='w' if col == 'name' else 'center')

        self.client_tree.pack(fill='both', expand=True, padx=10, pady=10)
        cur = self.db.setting('currency', 'FCFA')
        rows = self.db.conn.execute('SELECT * FROM clients ORDER BY name').fetchall()
        for r in rows:
            self.client_tree.insert('', 'end', iid=str(r['id']),
                                    values=(r['id'], r['name'], r['phone'] or '—', money(r['debt'], cur), r['loyalty_points']))

    def client_dialog(self):
        t = self.theme
        win = tk.Toplevel(self)
        win.title('Nouveau Client')
        win.configure(bg=t['bg'])
        self.center_window(win, 450, 320)
        win.transient(self)
        win.grab_set()

        card = self.create_card(win)
        card.pack(fill='both', expand=True, padx=16, pady=16)

        name_var = tk.StringVar()
        phone_var = tk.StringVar()

        tk.Label(card, text='Nom du client :', bg=t['card'], fg=t['text']).pack(anchor='w', padx=14, pady=(10, 2))
        ttk.Entry(card, textvariable=name_var).pack(fill='x', padx=14, pady=4, ipady=3)

        tk.Label(card, text='Téléphone :', bg=t['card'], fg=t['text']).pack(anchor='w', padx=14, pady=(10, 2))
        ttk.Entry(card, textvariable=phone_var).pack(fill='x', padx=14, pady=4, ipady=3)

        def save():
            n = name_var.get().strip()
            if not n: return
            self.db.conn.execute('INSERT INTO clients(name,phone) VALUES(?,?)', (n, phone_var.get().strip()))
            self.db.conn.commit()
            win.destroy()
            self.show_clients()

        ttk.Button(card, text='Enregistrer', command=save).pack(pady=16)

    # ==========================================================================
    # CARNET DE NOTES
    # ==========================================================================
    def show_notes(self):
        self.set_nav_active('notes')
        self.page_header('Carnet de Caisse', 'Notes de service, rappels et consignes d’équipe')
        t = self.theme

        bar = tk.Frame(self.main_container, bg=t['bg'])
        bar.pack(fill='x', padx=28, pady=(0, 10))
        ttk.Button(bar, text='＋ Nouvelle Note', command=self.note_dialog).pack(side='right')

        card = self.create_card(self.main_container)
        card.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        cols = ('date', 'time', 'note')
        tree = ttk.Treeview(card, columns=cols, show='headings')
        tree.heading('date', text='Date')
        tree.heading('time', text='Heure')
        tree.heading('note', text='Contenu de la note')
        tree.column('date', width=110, anchor='center')
        tree.column('time', width=90, anchor='center')
        tree.column('note', width=680, anchor='w')

        tree.pack(fill='both', expand=True, padx=10, pady=10)
        for n in self.db.conn.execute('SELECT * FROM notes ORDER BY id DESC').fetchall():
            tree.insert('', 'end', values=(n['date'], n['time'], n['note']))

    def note_dialog(self):
        t = self.theme
        win = tk.Toplevel(self)
        win.title('Nouvelle Note')
        win.configure(bg=t['bg'])
        self.center_window(win, 540, 360)
        win.transient(self)
        win.grab_set()

        card = self.create_card(win)
        card.pack(fill='both', expand=True, padx=16, pady=16)

        txt = tk.Text(card, font=('Segoe UI', 10), bg=t['card_inner'], fg=t['text'])
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        txt.focus_set()

        def save():
            v = txt.get('1.0', 'end').strip()
            if not v: return
            d = now()
            self.db.conn.execute('INSERT INTO notes(date,time,note) VALUES(?,?,?)',
                                 (d.strftime('%d/%m/%Y'), d.strftime('%H:%M'), v))
            self.db.conn.commit()
            win.destroy()
            self.show_notes()

        ttk.Button(card, text='Enregistrer la note', command=save).pack(pady=8)

    # ==========================================================================
    # PARAMÈTRES & CONFIGURATION DU COMMERCE
    # ==========================================================================
    def show_settings(self):
        if self.current_user and self.current_user.get('role') != 'Administrateur':
            messagebox.showerror('Accès Verrouillé', "L'accès aux Paramètres est verrouillé pour la session caissier.\nSeul l'Administrateur peut modifier la configuration du magasin.", parent=self)
            return
        self.set_nav_active('settings')
        self.page_header('Paramètres du Système', 'Personnalisation du magasin, en-tête de ticket et thèmes')
        t = self.theme

        outer = tk.Frame(self.main_container, bg=t['bg'])
        outer.pack(fill='both', expand=True, padx=28, pady=4)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)

        # En-tête & Société
        c1 = self.create_card(outer)
        c1.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=6)
        tk.Label(c1, text='Identité Commerciale', bg=t['card'], fg=t['text'], font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=10)

        keys1 = [
            ('Nom de la boutique', 'company'),
            ('Nom de la caisse', 'register'),
            ('Devise monétaire', 'currency'),
            ('Téléphone', 'phone'),
            ('Adresse', 'address')
        ]
        vars1 = {}
        for lbl, k in keys1:
            row = tk.Frame(c1, bg=t['card'])
            row.pack(fill='x', padx=14, pady=4)
            tk.Label(row, text=lbl, bg=t['card'], fg=t['text'], width=18, anchor='w').pack(side='left')
            v = tk.StringVar(value=self.db.setting(k, ''))
            ttk.Entry(row, textvariable=v).pack(side='right', fill='x', expand=True)
            vars1[k] = v

        # Ticket & Facturation
        c2 = self.create_card(outer)
        c2.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=6)
        tk.Label(c2, text='Options d’Impression & Caisse', bg=t['card'], fg=t['text'], font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=10)

        keys2 = [
            ('Ligne d’en-tête ticket', 'header'),
            ('Pied de page ticket', 'footer'),
            ('Seuil stock bas alerte', 'stock_threshold')
        ]
        vars2 = {}
        for lbl, k in keys2:
            row = tk.Frame(c2, bg=t['card'])
            row.pack(fill='x', padx=14, pady=4)
            tk.Label(row, text=lbl, bg=t['card'], fg=t['text'], width=20, anchor='w').pack(side='left')
            v = tk.StringVar(value=self.db.setting(k, ''))
            ttk.Entry(row, textvariable=v).pack(side='right', fill='x', expand=True)
            vars2[k] = v

        # Choix du thème
        theme_row = tk.Frame(c2, bg=t['card'])
        theme_row.pack(fill='x', padx=14, pady=10)
        tk.Label(theme_row, text='Thème d’affichage :', bg=t['card'], fg=t['text'], width=20, anchor='w').pack(side='left')
        theme_var = tk.StringVar(value=self.db.setting('theme', 'Bleu TOP-BOX'))
        cb = ttk.Combobox(theme_row, textvariable=theme_var, values=list(THEMES.keys()), state='readonly')
        cb.pack(side='right', fill='x', expand=True)

        def save_all():
            for k, var in {**vars1, **vars2}.items():
                self.db.set_setting(k, var.get().strip())
            self.db.set_setting('theme', theme_var.get())
            self.db.conn.commit()
            messagebox.showinfo('Succès', 'Paramètres enregistrés !', parent=self)
            self.theme = THEMES.get(theme_var.get(), THEMES['Bleu TOP-BOX'])
            self.build_ui()
            self.show_settings()

        bottom_bar = tk.Frame(self.main_container, bg=t['bg'])
        bottom_bar.pack(fill='x', padx=28, pady=14)
        ttk.Button(bottom_bar, text='💾 Enregistrer tous les paramètres', command=save_all).pack(side='right')

    # ==========================================================================
    # MODALES D'ANALYSES & OUTILS
    # ==========================================================================
    def open_calculator(self):
        win = tk.Toplevel(self)
        win.title('Calculatrice')
        self.center_window(win, 320, 420)
        disp = tk.StringVar(value='0')
        e = tk.Entry(win, textvariable=disp, font=('Segoe UI', 20, 'bold'), justify='right', bg='#1e293b', fg='white')
        e.pack(fill='x', padx=10, pady=10, ipady=10)

        grid = tk.Frame(win)
        grid.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        expr = ''
        def press(k):
            nonlocal expr
            if k == 'C': expr = ''; disp.set('0'); return
            if k == '=':
                try: expr = str(eval(expr, {'__builtins__': {}}, {})); disp.set(expr)
                except Exception: disp.set('Erreur'); expr = ''
                return
            expr += k
            disp.set(expr)

        buttons = [
            ['C', '(', ')', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '']
        ]
        for r, row in enumerate(buttons):
            for c, char in enumerate(row):
                if char:
                    tk.Button(grid, text=char, font=('Segoe UI', 12, 'bold'), command=lambda ch=char: press(ch)).grid(row=r, column=c, sticky='nsew', padx=2, pady=2)
        for i in range(5): grid.rowconfigure(i, weight=1)
        for j in range(4): grid.columnconfigure(j, weight=1)

    def open_stock_alerts(self):
        th = safe_float(self.db.setting('stock_threshold', '5'))
        rows = self.db.conn.execute('SELECT * FROM products WHERE qty <= ? ORDER BY qty ASC', (th,)).fetchall()
        win = tk.Toplevel(self)
        win.title('Alertes Rupture de Stock')
        self.center_window(win, 700, 450)
        tree = ttk.Treeview(win, columns=('name', 'qty', 'price'), show='headings')
        tree.heading('name', text='Article')
        tree.heading('qty', text='Stock Restant')
        tree.heading('price', text='Prix')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        cur = self.db.setting('currency', 'FCFA')
        for r in rows:
            tree.insert('', 'end', values=(r['name'], f"{r['qty']:g}", money(r['price'], cur)))

    def open_expiry_alerts(self):
        today = now().strftime('%Y-%m-%d')
        rows = self.db.conn.execute("SELECT * FROM products WHERE expiry_date != '' AND expiry_date <= date('now', '+30 day') ORDER BY expiry_date ASC").fetchall()
        win = tk.Toplevel(self)
        win.title('Alertes Péremption')
        self.center_window(win, 700, 450)
        tree = ttk.Treeview(win, columns=('name', 'date', 'qty'), show='headings')
        tree.heading('name', text='Article')
        tree.heading('date', text='Date de Péremption')
        tree.heading('qty', text='Quantité')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        for r in rows:
            tree.insert('', 'end', values=(r['name'], r['expiry_date'], f"{r['qty']:g}"))

    def smart_modal(self, kind):
        win = tk.Toplevel(self)
        self.center_window(win, 650, 450)
        cur = self.db.setting('currency', 'FCFA')

        if kind == 'top':
            win.title('Top 10 Produits les plus vendus')
            tree = ttk.Treeview(win, columns=('name', 'qty', 'ca'), show='headings')
            tree.heading('name', text='Article')
            tree.heading('qty', text='Total Vendu')
            tree.heading('ca', text='CA Généré')
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            rows = self.db.conn.execute('''SELECT name, SUM(qty) as sq, SUM(total) as st FROM sale_items
                                           GROUP BY product_id ORDER BY sq DESC LIMIT 10''').fetchall()
            for r in rows:
                tree.insert('', 'end', values=(r['name'], f"{r['sq']:g}", money(r['st'], cur)))

        elif kind == 'dead':
            win.title('Produits Dormants / Inactifs')
            tree = ttk.Treeview(win, columns=('name', 'qty'), show='headings')
            tree.heading('name', text='Article Jamais Vendu ou Inactif')
            tree.heading('qty', text='Stock Immobilisé')
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            rows = self.db.conn.execute('''SELECT p.name, p.qty FROM products p
                                           LEFT JOIN sale_items s ON s.product_id=p.id
                                           WHERE s.id IS NULL LIMIT 20''').fetchall()
            for r in rows:
                tree.insert('', 'end', values=(r['name'], f"{r['qty']:g}"))

        elif kind == 'day':
            win.title('Chiffre d’affaires par Jour')
            tree = ttk.Treeview(win, columns=('day', 'ca', 'count'), show='headings')
            tree.heading('day', text='Jour')
            tree.heading('ca', text='Chiffre d’affaires')
            tree.heading('count', text='Nombre de Ventes')
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            days = {0: 'Dimanche', 1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi', 6: 'Samedi'}
            rows = self.db.conn.execute('''SELECT CAST(strftime('%w', date) AS INTEGER) wd, SUM(total) ca, COUNT(*) n
                                           FROM sales GROUP BY wd ORDER BY ca DESC''').fetchall()
            for r in rows:
                tree.insert('', 'end', values=(days.get(r['wd'], '—'), money(r['ca'], cur), r['n']))

        elif kind == 'hour':
            win.title('Heures de Forte Affluence')
            tree = ttk.Treeview(win, columns=('h', 'ca', 'count'), show='headings')
            tree.heading('h', text='Tranche Horaire')
            tree.heading('ca', text='Chiffre d’affaires')
            tree.heading('count', text='Ventes')
            tree.pack(fill='both', expand=True, padx=10, pady=10)
            rows = self.db.conn.execute('''SELECT substr(date,12,2) hr, SUM(total) ca, COUNT(*) n
                                           FROM sales GROUP BY hr ORDER BY ca DESC''').fetchall()
            for r in rows:
                tree.insert('', 'end', values=(f"{r['hr']}h00 - {r['hr']}h59", money(r['ca'], cur), r['n']))

    def on_close(self):
        if self._after_id:
            try: self.after_cancel(self._after_id)
            except Exception: pass
        try:
            self.save_cart()
            self.db.conn.commit()
            self.db.conn.close()
        except Exception:
            pass
        self.destroy()

if __name__ == '__main__':
    app = TopBoxApp()
    app.mainloop()
