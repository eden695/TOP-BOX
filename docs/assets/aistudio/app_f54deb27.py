import os, sys, sqlite3, shutil, datetime, math, json, hashlib, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Les ressources restent a cote de l'EXE, mais la base active est dans le profil
# Windows de l'utilisateur : elle reste accessible en ecriture et persiste apres fermeture
# ou redemarrage, meme si l'EXE est installe dans un dossier protege.
APP_DIR=Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
RESOURCE_DIR=Path(getattr(sys, '_MEIPASS', str(Path(__file__).resolve().parent)))
BUNDLED_DATA_DIR=RESOURCE_DIR/'data'
DATA_DIR=APP_DIR/'data'; ASSET_DIR=DATA_DIR/'assets'; PROD_DIR=ASSET_DIR/'products'
BUNDLED_ASSET_DIR=BUNDLED_DATA_DIR/'assets'
USER_ASSET_DIR=Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData'/'Local')))/'MINI_SUPERMARCHE'/'assets'
USER_PRODUCT_DIR=USER_ASSET_DIR/'products'
for d in (USER_ASSET_DIR, USER_PRODUCT_DIR): d.mkdir(parents=True,exist_ok=True)
LOCAL_APPDATA=Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData'/'Local')))
USER_DATA_DIR=LOCAL_APPDATA/'MINI_SUPERMARCHE'
BACKUP_DIR=USER_DATA_DIR/'backups'
for d in (DATA_DIR,ASSET_DIR,PROD_DIR,USER_DATA_DIR,BACKUP_DIR): d.mkdir(parents=True,exist_ok=True)
DB_PATH=USER_DATA_DIR/'caisse.db'
# Premiere execution : importer la base existante a cote de l'EXE une seule fois.
# Ensuite, ne jamais ecraser la base active de ce client.
LEGACY_DB_PATH=DATA_DIR/'caisse.db'
BUNDLED_DB_PATH=BUNDLED_DATA_DIR/'caisse.db'
if not DB_PATH.exists():
    for candidate in (LEGACY_DB_PATH, BUNDLED_DB_PATH):
        if candidate.exists():
            try: shutil.copy2(candidate, DB_PATH); break
            except OSError: pass

THEMES={
 'Bleu': {'bg':'#f4f7fb','card':'#ffffff','nav':'#0b1f3a','accent':'#2563eb','accent2':'#60a5fa','soft':'#eaf2ff','text':'#0f172a','muted':'#64748b','line':'#d9e2ef','warn':'#f59e0b','danger':'#dc2626','ok':'#16a34a'},
 'Bleu Royal': {'bg':'#f5f8ff','card':'#ffffff','nav':'#122b5c','accent':'#315ee7','accent2':'#7aa2ff','soft':'#eaf0ff','text':'#102044','muted':'#66779b','line':'#dbe4f7','warn':'#f59e0b','danger':'#dc2626','ok':'#16a34a'},
 'Bleu Nuit': {'bg':'#eef3f9','card':'#ffffff','nav':'#071426','accent':'#3b82f6','accent2':'#93c5fd','soft':'#e5eefc','text':'#0f172a','muted':'#64748b','line':'#d7e0ec','warn':'#f59e0b','danger':'#dc2626','ok':'#16a34a'},
 'Turquoise': {'bg':'#f1fbfb','card':'#ffffff','nav':'#073b45','accent':'#0f9d9a','accent2':'#5eead4','soft':'#e0f7f5','text':'#0d2f35','muted':'#5f777b','line':'#d4e9e9','warn':'#d97706','danger':'#dc2626','ok':'#159a68'},
 'Émeraude': {'bg':'#f2faf6','card':'#ffffff','nav':'#0d3527','accent':'#169b62','accent2':'#5ee6a6','soft':'#e0f7eb','text':'#10281e','muted':'#60766a','line':'#d6e9de','warn':'#d97706','danger':'#dc2626','ok':'#15803d'},
 'Violet': {'bg':'#f7f5fb','card':'#ffffff','nav':'#21153b','accent':'#7c3aed','accent2':'#c4b5fd','soft':'#eee8ff','text':'#1f1633','muted':'#756b86','line':'#e5def1','warn':'#d97706','danger':'#dc2626','ok':'#16a34a'},
 'Orange': {'bg':'#fff8f1','card':'#ffffff','nav':'#3b2414','accent':'#ea580c','accent2':'#fb923c','soft':'#ffeddc','text':'#28170d','muted':'#806756','line':'#f0dfd1','warn':'#d97706','danger':'#dc2626','ok':'#16a34a'},
 'Graphite': {'bg':'#f3f4f6','card':'#ffffff','nav':'#20242b','accent':'#4b5563','accent2':'#9ca3af','soft':'#e5e7eb','text':'#17191d','muted':'#6b7280','line':'#d7d9dd','warn':'#d97706','danger':'#dc2626','ok':'#16a34a'},
 'Sombre': {'bg':'#0f172a','card':'#172033','nav':'#07111f','accent':'#3b82f6','accent2':'#93c5fd','soft':'#1d3557','text':'#f8fafc','muted':'#a8b3c5','line':'#29364c','warn':'#f59e0b','danger':'#f87171','ok':'#4ade80'}
}

def now(): return datetime.datetime.now()
def safe_float(s):
    try: return float(str(s).replace(' ','').replace(',','.'))
    except: return 0.0
def money(v,cur):
    try: v=float(v)
    except: v=0
    return f'{v:,.0f}'.replace(',',' ') + (f' {cur}' if cur else '')

def make_image(path,name,idx):
    """Create a product visual with food/object forms and textures, never using the product name as the image."""
    import random
    random.seed(idx*9173)
    w,h=800,560
    img=Image.new('RGB',(w,h),(238,242,246)); d=ImageDraw.Draw(img)
    # soft studio background / table
    for y in range(h):
        c=int(238 + (y/h)*10); d.line((0,y,w,y),fill=(c,c,c))
    d.ellipse((90,355,710,505),fill=(205,210,216))
    key=name.lower()
    # generic helpers
    def ellipse(box,fill,outline=None,width=1): d.ellipse(box,fill=fill,outline=outline,width=width)
    def rect(box,fill,outline=None,width=1): d.rounded_rectangle(box,radius=22,fill=fill,outline=outline,width=width)
    def plate(): ellipse((120,120,680,500),(248,248,247),(220,224,228),8); ellipse((165,155,635,465),(232,234,236))
    if any(x in key for x in ['poulet','hamburger','amburger','jambon','saucisse','viande']):
        plate();
        for j in range(7):
            x=245+random.randint(-55,190); y=250+random.randint(-30,90); ww=random.randint(80,150); hh=random.randint(45,85)
            ellipse((x,y,x+ww,y+hh),(145+random.randint(0,45),65+random.randint(0,35),25),(105,55,25),3)
        for j in range(18):
            x=random.randint(190,590); y=random.randint(190,430); ellipse((x,y,x+random.randint(6,15),y+random.randint(4,10)),(235,155,55))
    elif any(x in key for x in ['poisson']):
        plate();
        ellipse((225,220,575,400),(205,130,55),(120,75,35),4); ellipse((510,280,575,340),(235,180,90));
        for j in range(9): d.line((255+j*32,245,275+j*32,375),fill=(240,180,85),width=4)
        ellipse((520,300,535,315),(30,30,30))
    elif any(x in key for x in ['spaghetti','pâtes','pasta','semoule']):
        plate();
        for j in range(34):
            pts=[]; x0=random.randint(220,520); y0=random.randint(230,370)
            for k in range(12): pts.append((x0+math.sin(k*.8+j)*55+k*6,y0+math.cos(k*.7+j)*28+k*1))
            d.line(pts,fill=(224,178,75),width=random.randint(3,6),joint='curve')
        ellipse((300,245,470,345),(175,55,35))
    elif any(x in key for x in ['jus','orange','grenadine','limonade','eau','lait','thé','café']):
        rect((255,115,545,455),(250,250,250),(215,220,225),6)
        if 'orange' in key: liquid=(242,148,25)
        elif 'grenadine' in key: liquid=(190,35,65)
        elif 'café' in key: liquid=(75,43,25)
        elif 'thé' in key: liquid=(110,145,65)
        elif 'eau' in key: liquid=(155,205,235)
        else: liquid=(245,245,235)
        d.rounded_rectangle((275,220,525,430),radius=25,fill=liquid)
        ellipse((275,195,525,245),(255,255,255),(215,215,215),4)
        if 'orange' in key: ellipse((185,170,310,295),(247,145,25),(180,95,15),5)
    elif any(x in key for x in ['ananas','bananes','mangues','pommes','avocat','zeste']):
        colors={'ananas':(215,170,35),'bananes':(244,218,65),'mangues':(242,155,45),'pommes':(205,55,45),'avocat':(80,145,60),'zeste':(230,205,35)}
        c=next((v for k,v in colors.items() if k in key),(100,160,70))
        for j in range(7):
            x=170+(j%4)*130+random.randint(-20,20); y=170+(j//4)*120+random.randint(-20,20); ellipse((x,y,x+150,y+120),c,(80,90,60),3)
        if 'ananas' in key:
            d.polygon([(350,120),(390,35),(410,115),(455,55),(450,145),(500,100),(470,180),(330,180)],fill=(60,125,65))
    elif any(x in key for x in ['tomate','poivre','maïs','haricots','champignons','olives']):
        plate();
        c=(205,50,45) if 'tomate' in key else (70,70,70) if 'champignons' in key else (80,125,55)
        for j in range(18):
            x=random.randint(200,570); y=random.randint(205,405); sz=random.randint(30,65); ellipse((x,y,x+sz,y+sz),c,(255,255,255),2)
    elif any(x in key for x in ['pain','beignets','gâteau','biscuits','chips','corn flakes','céréales','farine','sucre','sel']):
        rect((145,150,655,440),(221,183,125),(150,110,70),5)
        if 'chips' in key:
            for j in range(30):
                x=random.randint(180,610); y=random.randint(180,410); ellipse((x,y,x+random.randint(20,45),y+random.randint(10,25)),(222,176,65))
        elif 'pain' in key or 'gâteau' in key or 'beignets' in key:
            for j in range(8):
                x=190+(j%4)*105; y=205+(j//4)*105; ellipse((x,y,x+100,y+85),(190,115,55))
        else:
            for j in range(45):
                x=random.randint(175,625); y=random.randint(175,415); ellipse((x,y,x+random.randint(8,18),y+random.randint(8,18)),(220,180,75))
    elif any(x in key for x in ['beurre','fromage','crème','yaourt']):
        rect((180,160,620,420),(245,239,200),(210,195,135),5)
        if 'fromage' in key: 
            d.polygon([(220,370),(360,185),(590,370)],fill=(244,198,65));
        elif 'beurre' in key: rect((245,205,555,375),(248,218,105))
        else: ellipse((235,205,565,390),(245,245,225),(205,205,195),4)
    elif any(x in key for x in ['riz','riz parfumé']):
        plate(); ellipse((210,185,590,430),(248,248,242));
        for j in range(350):
            x=random.randint(245,555); y=random.randint(220,400); ellipse((x,y,x+random.randint(3,7),y+random.randint(2,5)),(245,242,220))
    else:
        plate();
        for j in range(22):
            x=random.randint(190,570); y=random.randint(200,410); ellipse((x,y,x+random.randint(30,70),y+random.randint(20,55)),(100+random.randint(0,120),70+random.randint(0,120),45+random.randint(0,80)))
    # Photographic finish: soft vignette, fine grain and natural highlights; never any product name/text.
    noise=Image.effect_noise((w,h),3).convert('RGB')
    img=Image.blend(img,noise,0.035)
    overlay=Image.new('RGBA',(w,h),(255,255,255,0)); od=ImageDraw.Draw(overlay); od.ellipse((95,45,455,285),fill=(255,255,255,18)); img=Image.alpha_composite(img.convert('RGBA'),overlay).convert('RGB')
    img.save(path,quality=94)

def fit_image(path,max_w,max_h,master=None):
    try:
        raw=Path(path); candidates=[raw] if raw.is_absolute() else [APP_DIR/raw, RESOURCE_DIR/raw]
        # Fallbacks keep images/logo visible in PyInstaller --onefile builds.
        candidates += [USER_ASSET_DIR/raw.name, BUNDLED_ASSET_DIR/raw.name]
        found=next((x for x in candidates if x.is_file()),None)
        if found is None: return None
        im=Image.open(found).convert('RGB'); im.thumbnail((max_w,max_h),Image.Resampling.LANCZOS)
        canvas=Image.new('RGB',(max_w,max_h),'white'); x=(max_w-im.width)//2; y=(max_h-im.height)//2; canvas.paste(im,(x,y)); return ImageTk.PhotoImage(canvas, master=master)
    except Exception: return None

class DB:
    def __init__(self):
        self.conn=sqlite3.connect(DB_PATH); self.conn.row_factory=sqlite3.Row; self.init(); old_theme=self.setting('theme','Bleu'); migrated={'Bleu FASUCE':'Bleu','Sombre FASUCE':'Sombre'}.get(old_theme,old_theme);
        if migrated!=old_theme: self.set_setting('theme',migrated); self.conn.commit()
    def init(self):
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,description TEXT DEFAULT '',price REAL DEFAULT 0,qty REAL DEFAULT 0,image TEXT DEFAULT '',expiry_date TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY AUTOINCREMENT,invoice TEXT UNIQUE,date TEXT,subtotal REAL,discount REAL,tax_rate REAL,tax REAL,total REAL,received REAL,change_amt REAL,cashier TEXT,register TEXT);
        CREATE TABLE IF NOT EXISTS sale_items(id INTEGER PRIMARY KEY AUTOINCREMENT,sale_id INTEGER,product_id INTEGER,name TEXT,qty REAL,unit_price REAL,total REAL);
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT,time TEXT,note TEXT);
        CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);
        ''');
        cols=[r['name'] for r in self.conn.execute('PRAGMA table_info(sales)').fetchall()];
        if 'printed' not in cols: self.conn.execute("ALTER TABLE sales ADD COLUMN printed INTEGER DEFAULT 0");
        pcols=[r['name'] for r in self.conn.execute('PRAGMA table_info(products)').fetchall()];
        if 'expiry_date' not in pcols: self.conn.execute("ALTER TABLE products ADD COLUMN expiry_date TEXT DEFAULT ''");
        self.conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'Caissier',active INTEGER NOT NULL DEFAULT 1)");
        self.conn.execute("CREATE TABLE IF NOT EXISTS cash_closings(id INTEGER PRIMARY KEY AUTOINCREMENT,closed_at TEXT,total_sales REAL,cash_received REAL,change_given REAL,discount_total REAL,sales_count INTEGER,notes TEXT DEFAULT '')");
        self.conn.commit(); self.seed(); self.normalize_product_ids(); self.set_setting('tax_enabled','0'); self.set_setting('tax_rate','0'); self.conn.commit()
    def normalize_product_ids(self):
        rows=self.conn.execute('SELECT id FROM products ORDER BY id').fetchall()
        ids=[int(r['id']) for r in rows]
        expected=list(range(1,len(ids)+1))
        if ids==expected:return {}
        mapping={old:new for new,old in enumerate(ids,1) if old!=new}
        self.conn.execute('BEGIN')
        try:
            for old in ids:self.conn.execute('UPDATE products SET id=? WHERE id=?',(-old,old))
            for new,old in enumerate(ids,1):self.conn.execute('UPDATE products SET id=? WHERE id=?',(new,-old))
            for old,new in mapping.items():self.conn.execute('UPDATE sale_items SET product_id=? WHERE product_id=?',(new,old))
            self.conn.commit();return mapping
        except Exception:
            self.conn.rollback();raise
    def setting(self,k,default=''):
        r=self.conn.execute('SELECT v FROM settings WHERE k=?',(k,)).fetchone(); return r['v'] if r else default
    def set_setting(self,k,v): self.conn.execute('INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v',(k,str(v)))
    def products(self,q=''):
        if q: return self.conn.execute('SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name COLLATE NOCASE',(f'%{q}%',f'%{q}%')).fetchall()
        return self.conn.execute('SELECT * FROM products ORDER BY name COLLATE NOCASE').fetchall()
    def seed(self):
        # Une nouvelle caisse démarre vide : aucun produit ou stock de démonstration.
        defaults={'company':'MINI SUPERMARCHÉ','register':'CAISSE 02','cashier':'','currency':'FCFA','header':'MINI SUPERMARCHÉ','address':'','phone':'','email':'','footer':'Merci pour votre achat','logo':'','icon':'','tax_enabled':'0','tax_rate':'0','discount_enabled':'1','default_discount':'0','ticket_format':'80MM','stock_threshold':'5','allow_negative_stock':'0','auto_ticket':'1','theme':'Bleu','require_login':'1'}
        for k,v in defaults.items():
            if self.conn.execute('SELECT 1 FROM settings WHERE k=?',(k,)).fetchone() is None:
                self.set_setting(k,v)
        self.conn.commit()

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.db=DB(); self.theme=THEMES.get({'Bleu FASUCE':'Bleu','Sombre FASUCE':'Sombre'}.get(self.db.setting('theme','Bleu'),self.db.setting('theme','Bleu')),THEMES['Bleu']); self.title(self.db.setting('company','MINI SUPERMARCHÉ')); self.geometry('1320x780'); self.minsize(1120,700); self.cart=self.load_saved_cart(); self._after=None; self._blink=False; self.current_user=None
        self.withdraw(); self.protocol('WM_DELETE_WINDOW',self.on_close); self.apply_window_icon()
        if self.db.setting('require_login','1') != '1':
            self.current_user={'id':0,'username':'Accès direct','role':'Administrateur'}
            authenticated=True
        else:
            authenticated=self.authenticate()
        if not authenticated:
            self.db.conn.close(); self.destroy(); return
        self.deiconify(); self.build(); self.show_dashboard(); self.live()
    def authenticate(self):
        # Fenêtre de connexion modernisée, avec vérification explicite de l’état du compte.
        count=self.db.conn.execute('SELECT COUNT(*) n FROM users').fetchone()['n']
        t=self.theme
        win=tk.Toplevel(self)
        win.title('Connexion — '+self.db.setting('company','MINI SUPERMARCHÉ'))
        self.apply_icon_to_window(win)
        win.configure(bg=t['bg']); win.resizable(False,False)
        win.protocol('WM_DELETE_WINDOW',lambda: (setattr(self,'current_user',None),win.destroy()))
        self.centered(win,460,440 if count else 470)
        # Ne pas rendre la fenêtre de connexion dépendante d'une fenêtre principale masquée sous Windows.
        try: win.transient('')
        except Exception: pass
        win.deiconify(); win.lift()
        try: win.attributes('-topmost', True); win.after(500, lambda: win.attributes('-topmost', False))
        except Exception: pass
        win.grab_set()
        shell=tk.Frame(win,bg=t['bg']); shell.pack(fill='both',expand=True,padx=20,pady=18)
        hero=tk.Frame(shell,bg=t['nav'],height=112); hero.pack(fill='x'); hero.pack_propagate(False)
        logo_path=self.db.setting('logo','').strip() or str(BUNDLED_ASSET_DIR/'logo_caisse.png')
        logo_img=fit_image(logo_path,52,52,master=win)
        if logo_img:
            logo_label=tk.Label(hero,image=logo_img,bg=t['nav'],borderwidth=0); logo_label.image=logo_img; logo_label.pack(pady=(8,0))
        else:
            tk.Label(hero,text='▣',bg=t['nav'],fg=t['accent2'],font=('Segoe UI Symbol',25,'bold')).pack(pady=(12,0))
        tk.Label(hero,text=self.db.setting('company','MINI SUPERMARCHÉ'),bg=t['nav'],fg='#ffffff',font=('Segoe UI',17,'bold')).pack(pady=(0,2))
        tk.Label(shell,text='Créer le premier compte administrateur' if not count else 'Connecte-toi pour accéder à ta caisse',bg=t['bg'],fg=t['muted'],font=('Segoe UI',10)).pack(pady=(13,14))
        card=tk.Frame(shell,bg=t['card'],highlightbackground=t['line'],highlightthickness=1)
        card.pack(fill='x',padx=5)
        form=tk.Frame(card,bg=t['card']); form.pack(fill='x',padx=18,pady=16)
        tk.Label(form,text='IDENTIFIANT',bg=t['card'],fg=t['muted'],font=('Segoe UI',8,'bold')).pack(anchor='w')
        user=tk.StringVar(); user_entry=ttk.Entry(form,textvariable=user); user_entry.pack(fill='x',pady=(4,12),ipady=4)
        tk.Label(form,text='MOT DE PASSE',bg=t['card'],fg=t['muted'],font=('Segoe UI',8,'bold')).pack(anchor='w')
        pw=tk.StringVar(); ent=ttk.Entry(form,textvariable=pw,show='•'); ent.pack(fill='x',pady=(4,2),ipady=4)
        result={'ok':False}
        def submit(event=None):
            name=user.get().strip(); password=pw.get()
            if not name or not password:
                messagebox.showwarning('Connexion','Saisis ton identifiant et ton mot de passe.',parent=win); return
            digest=hashlib.sha256(password.encode('utf-8')).hexdigest()
            if count==0:
                if len(password)<6:
                    messagebox.showwarning('Sécurité','Choisis un mot de passe d’au moins 6 caractères.',parent=win); return
                try:
                    self.db.conn.execute('INSERT INTO users(username,password_hash,role,active) VALUES(?,?,?,1)',(name,digest,'Administrateur')); self.db.conn.commit()
                except sqlite3.IntegrityError:
                    messagebox.showerror('Compte','Ce nom existe déjà.',parent=win); return
                row=self.db.conn.execute('SELECT id,username,role FROM users WHERE username=?',(name,)).fetchone()
            else:
                row=self.db.conn.execute('SELECT id,username,role,password_hash,active FROM users WHERE lower(trim(username))=lower(trim(?))',(name,)).fetchone()
                if not row:
                    messagebox.showerror('Connexion','Identifiant ou mot de passe incorrect.',parent=win); pw.set(''); ent.focus_set(); return
                active_value=row['active']
                is_active=(active_value is True or str(active_value).strip().lower() in ('1','1.0','true','actif','active','oui','yes'))
                if not is_active:
                    messagebox.showerror('Compte désactivé','Ce compte est désactivé. Dans « Comptes utilisateurs et permissions », sélectionne-le puis clique sur « Activer / désactiver ».',parent=win); pw.set(''); ent.focus_set(); return
                if row['password_hash']!=digest:
                    messagebox.showerror('Connexion','Identifiant ou mot de passe incorrect.',parent=win); pw.set(''); ent.focus_set(); return
            self.current_user={'id':row['id'],'username':row['username'],'role':row['role']}; result['ok']=True; win.destroy()
        button=tk.Frame(shell,bg=t['bg']); button.pack(fill='x',padx=5,pady=(14,0))
        ttk.Button(button,text='Créer le compte administrateur' if not count else 'Se connecter',command=submit).pack(fill='x',ipady=4)
        tk.Label(shell,text='Accès local sécurisé • MINI SUPERMARCHÉ',bg=t['bg'],fg=t['muted'],font=('Segoe UI',8)).pack(pady=(12,0))
        win.bind('<Return>',submit); user_entry.focus_set(); self.wait_window(win); return result['ok']
    def require_admin(self,action='effectuer cette action'):
        if not self.current_user or self.current_user.get('role')!='Administrateur':
            messagebox.showwarning('Permission refusée',f'Seul un administrateur peut {action}.',parent=self); return False
        return True
    def load_saved_cart(self):
        raw=self.db.setting('cart_state','[]')
        try:data=json.loads(raw)
        except Exception:return []
        if not isinstance(data,list):return []
        valid=[]
        for x in data:
            try:
                pid=int(x.get('id'));q=safe_float(x.get('qty',0));p=self.db.conn.execute('SELECT id,name,price FROM products WHERE id=?',(pid,)).fetchone()
                if p and q>0:valid.append({'id':p['id'],'name':p['name'],'qty':q,'price':float(p['price'])})
            except Exception:continue
        self.save_cart(valid,commit=True);return valid
    def save_cart(self,cart=None,commit=True):
        data=self.cart if cart is None else cart
        payload=[{'id':int(x['id']),'name':x['name'],'qty':float(x['qty']),'price':float(x['price'])} for x in data]
        self.db.set_setting('cart_state',json.dumps(payload,ensure_ascii=False))
        if commit:self.db.conn.commit()
    def apply_icon_to_window(self, window):
        # Priorite a l'icone choisie dans les parametres, puis a l'icone incluse avec l'application.
        candidates=[]
        try:
            configured=self.db.setting('icon','').strip()
            if configured: candidates.append(Path(configured))
        except Exception: pass
        candidates.extend([USER_ASSET_DIR/'app.ico', ASSET_DIR/'app.ico', BUNDLED_ASSET_DIR/'app.ico'])
        for candidate in candidates:
            try:
                if candidate.is_file():
                    window.iconbitmap(str(candidate))
                    return True
            except Exception:
                continue
        return False

    def apply_window_icon(self):
        self.apply_icon_to_window(self)
    def style(self):
        t=self.theme; s=ttk.Style(self); s.theme_use('clam'); s.configure('.',font=('Segoe UI',10),foreground=t['text']); s.configure('TButton',padding=(9,5),background=t['card'],relief='flat',borderwidth=0,font=('Segoe UI',9,'bold')); s.map('TButton',background=[('active',t['accent']),('pressed',t['nav'])],foreground=[('active','white'),('pressed','white')]); s.configure('Treeview',rowheight=34,background=t['card'],fieldbackground=t['card'],foreground=t['text']); s.configure('Treeview.Heading',font=('Segoe UI',9,'bold'),background=t['line']); s.configure('TEntry',padding=7); s.configure('TCombobox',padding=6)
    def build(self):
        self.style(); self.clear(); t=self.theme
        nav=tk.Frame(self,bg=t['nav'],width=225); nav.pack(side='left',fill='y'); nav.pack_propagate(False)
        brand=(self.db.setting('company','MINI SUPERMARCHÉ').strip() or 'MINI SUPERMARCHÉ'); tk.Label(nav,text=brand,bg=t['nav'],fg='white',font=('Segoe UI',14,'bold'),wraplength=190,justify='left').pack(anchor='w',padx=18,pady=(24,18))
        items=[('Tableau de bord',self.show_dashboard),('Nouvelle vente',self.show_sale),('Produits & stock',self.show_products),('Historique des ventes',self.show_history),('Carnet',self.show_notes),('Paramètres',self.show_settings)]
        for label,fn in items: tk.Button(nav,text=label,command=fn,bg=t['nav'],fg='white',activebackground=t['accent'],activeforeground='white',relief='flat',anchor='w',font=('Segoe UI',10,'bold'),padx=18,pady=11).pack(fill='x',padx=8,pady=2)
        if self.current_user: tk.Label(nav,text=f"Connecté : {self.current_user['username']}\n{self.current_user['role']}",bg=t['nav'],fg='#cbd5e1',font=('Segoe UI',9),justify='left').pack(side='bottom',anchor='w',padx=18,pady=18)
        main=tk.Frame(self,bg=t['bg']); main.pack(side='left',fill='both',expand=True); self.main=main
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def page_header(self,title,sub=''):
        for w in self.main.winfo_children(): w.destroy()
        h=tk.Frame(self.main,bg=self.theme['bg']); h.pack(fill='x',padx=28,pady=(22,10)); tk.Label(h,text=title,bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',24,'bold')).pack(anchor='w');
        if sub: tk.Label(h,text=sub,bg=self.theme['bg'],fg=self.theme['muted']).pack(anchor='w',pady=(2,0))
    def card(self,p): return tk.Frame(p,bg=self.theme['card'],highlightthickness=1,highlightbackground=self.theme['line'])
    def centered(self,w,width,height):
        # Centrage par rapport à l'écran, fiable même si la fenêtre racine est masquée.
        try:
            w.update_idletasks()
            sw=w.winfo_screenwidth(); sh=w.winfo_screenheight()
            x=max(0,(sw-width)//2); y=max(0,(sh-height)//2)
            w.geometry(f'{width}x{height}+{x}+{y}')
        except Exception:
            w.geometry(f'{width}x{height}+80+60')
    def show_dashboard(self):
        self.page_header('Tableau de bord','Pilotage en temps réel et intelligence de caisse')
        t=self.theme; wrap=tk.Frame(self.main,bg=t['bg']); wrap.pack(fill='both',expand=True,padx=28,pady=4)
        self.dash_values=[]
        row=tk.Frame(wrap,bg=t['bg']); row.pack(fill='x',pady=(0,12))
        kpis=[('Chiffre d’affaires du jour','—',t['accent']),('Ventes du jour','—',t['accent2']),('Articles en stock','—',t['ok']),('Stock faible','—',t['warn'])]
        for title,val,accent in kpis:
            c=self.card(row); c.pack(side='left',fill='x',expand=True,padx=(0,12));
            tk.Frame(c,bg=accent,height=5).pack(fill='x')
            tk.Label(c,text=title,bg=t['card'],fg=t['muted'],font=('Segoe UI',9,'bold')).pack(anchor='w',padx=16,pady=(10,1))
            v=tk.Label(c,text=val,bg=t['card'],fg=t['text'],font=('Segoe UI',22,'bold')); v.pack(anchor='w',padx=16,pady=(0,12)); self.dash_values.append(v)
        smart=self.card(wrap); smart.pack(fill='x',pady=(0,12)); tk.Frame(smart,bg=t['accent'],height=4).pack(fill='x')
        tk.Label(smart,text='Analyse intelligente',bg=t['card'],fg=t['text'],font=('Segoe UI',13,'bold')).pack(side='left',padx=16,pady=12)
        for txt,fn in [('Top produits',lambda:self.smart_view('top')),('Produits morts',lambda:self.smart_view('dead')),('Meilleur jour',lambda:self.smart_view('day')),('Heures fortes',lambda:self.smart_view('hour'))]:
            tk.Button(smart,text=txt,command=fn,bg=t['soft'],fg=t['accent'],activebackground=t['accent'],activeforeground='white',relief='flat',font=('Segoe UI',9,'bold'),padx=12,pady=7,cursor='hand2').pack(side='left',padx=4,pady=8)
        tk.Button(smart,text='Alertes péremption',command=self.expiry_alert_dialog,bg=t['accent2'],fg='white',activebackground=t['accent'],activeforeground='white',relief='flat',font=('Segoe UI',9,'bold'),padx=12,pady=7,cursor='hand2').pack(side='right',padx=5,pady=8)
        tk.Button(smart,text='Alertes de stock',command=self.stock_alert_dialog,bg=t['warn'],fg='white',activebackground=t['accent'],activeforeground='white',relief='flat',font=('Segoe UI',9,'bold'),padx=12,pady=7,cursor='hand2').pack(side='right',padx=5,pady=8)
        tk.Button(smart,text='Calculatrice',command=self.calculator,bg=t['accent'],fg='white',activebackground=t['nav'],activeforeground='white',relief='flat',font=('Segoe UI',9,'bold'),padx=12,pady=7,cursor='hand2').pack(side='right',padx=14,pady=8)
        body=self.card(wrap); body.pack(fill='both',expand=True); tk.Frame(body,bg=t['accent2'],height=4).pack(fill='x')
        tk.Label(body,text='État du stock',bg=t['card'],fg=t['text'],font=('Segoe UI',13,'bold')).pack(anchor='w',padx=18,pady=12)
        tv=ttk.Treeview(body,columns=('id','name','qty','price','status','expiry'),show='headings'); self.dash_stock=tv
        for c,h,w in [('id','ID',55),('name','Article',330),('qty','Stock',100),('price','Prix',150),('status','Statut',140),('expiry','Péremption',130)]: tv.heading(c,text=h); tv.column(c,width=w,anchor='center' if c!='name' else 'w')
        sb=ttk.Scrollbar(body,orient='vertical',command=tv.yview); tv.configure(yscrollcommand=sb.set); tv.pack(side='left',fill='both',expand=True,padx=(14,0),pady=(0,14)); sb.pack(side='right',fill='y',padx=(0,14),pady=(0,14)); self.refresh_dashboard()
    def refresh_dashboard(self):
        if not getattr(self,'dash_values',None): return
        try:
            cur=self.db.setting('currency','FCFA'); today=now().strftime('%Y-%m-%d'); r=self.db.conn.execute('SELECT COALESCE(SUM(total),0)t,COUNT(*)n FROM sales WHERE date LIKE ?',(today+'%',)).fetchone(); nprod=self.db.conn.execute('SELECT COUNT(*) n FROM products').fetchone()['n']; th=safe_float(self.db.setting('stock_threshold','5')); low=self.db.conn.execute('SELECT COUNT(*) n FROM products WHERE qty<=?',(th,)).fetchone()['n']; vals=[money(r['t'],cur),str(r['n']),str(nprod),str(low)]
            for lab,val in zip(self.dash_values,vals):
                try: lab.configure(text=val)
                except tk.TclError: pass
            tv=getattr(self,'dash_stock',None)
            if tv and tv.winfo_exists():
                for x in tv.get_children(): tv.delete(x)
                for num,p in enumerate(self.db.products(),1):
                    q=float(p['qty']); status='RUPTURE' if q<=0 else ('STOCK FAIBLE' if q<=th else 'OK'); tv.insert('', 'end',values=(num,p['name'],int(q) if q.is_integer() else q,money(p['price'],cur),status,p['expiry_date'] or '—'),tags=('zero' if q<=0 else 'low' if q<=th else 'ok'))
                blink=getattr(self,'_blink',False)
                tv.tag_configure('zero',background=('#ef4444' if blink else '#fee2e2'),foreground=('white' if blink else '#991b1b')); tv.tag_configure('low',background=('#f59e0b' if blink else '#fff7ed'),foreground=('#ffffff' if blink else '#9a3412')); tv.tag_configure('ok',background=self.theme['card'])
        except (tk.TclError,sqlite3.Error): pass
    def live(self):
        try:
            self._blink=not getattr(self,'_blink',False)
            self.refresh_dashboard()
            self.refresh_products()
        except: pass
        self._after=self.after(650,self.live)
    def show_products(self):
        self.page_header('Produits & stock','Catalogue alphabétique, images et stock en temps réel')
        bar=tk.Frame(self.main,bg=self.theme['bg']); bar.pack(fill='x',padx=28); q=tk.StringVar(); tk.Label(bar,text='Rechercher',bg=self.theme['bg'],fg=self.theme['text']).pack(side='left'); ttk.Entry(bar,textvariable=q,width=36).pack(side='left',padx=8); q.trace_add('write',lambda *_:self.refresh_products(q.get())); ttk.Button(bar,text='Ajouter un produit',command=self.product_dialog).pack(side='right')
        box=self.card(self.main); box.pack(fill='both',expand=True,padx=28,pady=14); tv=ttk.Treeview(box,columns=('id','name','desc','price','qty','expiry'),show='headings'); self.prod_tv=tv
        for c,h,w in [('id','Produit',70),('name','Article',260),('desc','Description',430),('price','Prix',150),('qty','Stock',100),('expiry','Péremption',130)]: tv.heading(c,text=h); tv.column(c,width=w,anchor='center' if c in ('id','price','qty','expiry') else 'w')
        sb=ttk.Scrollbar(box,orient='vertical',command=tv.yview); tv.configure(yscrollcommand=sb.set); tv.pack(side='left',fill='both',expand=True,padx=(12,0),pady=12); sb.pack(side='right',fill='y',padx=(0,12),pady=12); tv.bind('<Double-1>',lambda e:self.edit_selected_product()); self.refresh_products()
    def refresh_products(self,q=''):
        tv=getattr(self,'prod_tv',None)
        if not tv:return
        try:
            for x in tv.get_children():tv.delete(x)
            cur=self.db.setting('currency','FCFA'); th=safe_float(self.db.setting('stock_threshold','5'))
            for num,p in enumerate(self.db.products(q),1):
                qv=float(p['qty']); tv.insert('', 'end',iid=str(p['id']),values=(num,p['name'],p['description'],money(p['price'],cur),int(qv) if qv.is_integer() else qv,p['expiry_date'] or '—'),tags=('zero' if qv<=0 else 'low' if qv<=th else 'ok'))
            blink=getattr(self,'_blink',False)
            tv.tag_configure('zero',background=('#ef4444' if blink else '#fee2e2'),foreground=('white' if blink else '#991b1b')); tv.tag_configure('low',background=('#f59e0b' if blink else '#fff7ed'),foreground=('#ffffff' if blink else '#9a3412')); tv.tag_configure('ok',background=self.theme['card'])
        except tk.TclError: pass
    def edit_selected_product(self):
        if not self.require_admin('modifier les produits et le stock'): return
        sel=self.prod_tv.selection();
        if sel:self.product_dialog(int(sel[0]))
    def product_dialog(self,pid=None):
        if not self.require_admin('modifier les produits et le stock'): return
        p=self.db.conn.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone() if pid else None
        win=tk.Toplevel(self); win.title('Modifier le produit' if p else 'Ajouter un produit'); win.configure(bg=self.theme['bg']); self.centered(win,820,610); win.transient(self); win.grab_set()
        t=self.theme; outer=tk.Frame(win,bg=t['bg']); outer.pack(fill='both',expand=True,padx=22,pady=20); outer.columnconfigure(0,weight=3); outer.columnconfigure(1,weight=2); outer.rowconfigure(1,weight=1)
        tk.Label(outer,text='Modifier le produit' if p else 'Nouveau produit',bg=t['bg'],fg=t['text'],font=('Segoe UI',20,'bold')).grid(row=0,column=0,columnspan=2,sticky='w'); tk.Label(outer,text='Fiche article et image',bg=t['bg'],fg=t['muted']).grid(row=0,column=1,sticky='e')
        left=self.card(outer); left.grid(row=1,column=0,sticky='nsew',padx=(0,10),pady=16); left.columnconfigure(1,weight=1)
        vals={k:tk.StringVar(value=str(p[k] or '') if p else '') for k in ['name','description','price','qty','image','expiry_date']}
        fields=[('name','Nom de l’article'),('description','Description'),('price','Prix'),('qty','Quantité en stock'),('expiry_date','Date de péremption (AAAA-MM-JJ)')]
        for i,(k,l) in enumerate(fields): tk.Label(left,text=l,bg=t['card'],fg=t['text'],font=('Segoe UI',10,'bold')).grid(row=i,column=0,sticky='w',padx=16,pady=12); ttk.Entry(left,textvariable=vals[k]).grid(row=i,column=1,sticky='ew',padx=(5,16),pady=10)
        prev=self.card(outer); prev.grid(row=1,column=1,sticky='nsew',pady=16); tk.Label(prev,text='Image du produit',bg=t['card'],fg=t['text'],font=('Segoe UI',12,'bold')).pack(pady=(14,8)); image_label=tk.Label(prev,text='Aucune image',bg='white',fg=t['muted'],width=34,height=16); image_label.pack(fill='both',expand=True,padx=14,pady=6)
        def show_img(path):
            ph=fit_image(path,340,300,master=image_label)
            if ph:image_label.configure(image=ph,text=''); image_label.image=ph
            else:image_label.configure(image='',text='Aucune image')
        def choose():
            f=filedialog.askopenfilename(parent=win,title='Choisir une image',filetypes=[('Images','*.png *.jpg *.jpeg *.webp')])
            if f:
                dest=PROD_DIR/f'prod_{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}{Path(f).suffix.lower()}'; shutil.copy2(f,dest); vals['image'].set(str(dest)); show_img(str(dest))
        ttk.Button(prev,text='Choisir / remplacer l’image',command=choose).pack(pady=(5,14))
        if p and p['image'] and Path(p['image']).exists():show_img(p['image'])
        elif not p:
            temp=PROD_DIR/'placeholder.png';
            if not temp.exists():make_image(temp,'Produit',999)
            vals['image'].set(str(temp)); show_img(str(temp))
        actions=tk.Frame(outer,bg=t['bg']); actions.grid(row=2,column=0,columnspan=2,sticky='e'); ttk.Button(actions,text='Annuler',command=win.destroy).pack(side='left',padx=5); ttk.Button(actions,text='Enregistrer le produit',command=lambda:self.save_product(pid,vals,win)).pack(side='left',padx=5)
    def save_product(self,pid,vals,win):
        if not self.require_admin('enregistrer les modifications de produits'): return
        name=vals['name'].get().strip();
        if not name:messagebox.showwarning('Produit','Le nom est obligatoire.',parent=win);return
        price=safe_float(vals['price'].get()); qty=safe_float(vals['qty'].get()); image=vals['image'].get();
        if not image or not Path(image).exists(): image=str(PROD_DIR/f'auto_{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.png'); make_image(image,name,pid or 1)
        try:
            expiry=vals['expiry_date'].get().strip();
            if expiry:
                datetime.date.fromisoformat(expiry)
            if pid:self.db.conn.execute('UPDATE products SET name=?,description=?,price=?,qty=?,image=?,expiry_date=? WHERE id=?',(name,vals['description'].get(),price,qty,image,expiry,pid))
            else:self.db.conn.execute('INSERT INTO products(name,description,price,qty,image,expiry_date) VALUES(?,?,?,?,?,?)',(name,vals['description'].get(),price,qty,image,expiry))
            self.db.conn.commit(); mapping=self.db.normalize_product_ids(); self.db.conn.commit()
            if mapping:
                for item in self.cart:
                    if int(item['id']) in mapping:item['id']=mapping[int(item['id'])]
                self.save_cart()
            win.destroy(); self.refresh_products(); self.refresh_dashboard()
            if hasattr(self,'sale_tv') and self.sale_tv.winfo_exists():self.refresh_sale_products()
        except sqlite3.IntegrityError:messagebox.showerror('Produit','Un article portant ce nom existe déjà.',parent=win)
        except ValueError:messagebox.showerror('Date invalide','Saisis une date au format AAAA-MM-JJ, par exemple 2026-12-31.',parent=win)
    def show_sale(self):
        self.page_header('Nouvelle vente','Choisissez les articles, contrôlez leur image puis encaissez')
        root=tk.Frame(self.main,bg=self.theme['bg']); root.pack(fill='both',expand=True,padx=28,pady=2); root.columnconfigure(0,weight=5); root.columnconfigure(1,weight=3); root.columnconfigure(2,weight=3); root.rowconfigure(1,weight=1)
        top=tk.Frame(root,bg=self.theme['bg']); top.grid(row=0,column=0,columnspan=3,sticky='ew',pady=(0,8)); self.sale_search=tk.StringVar(); ttk.Entry(top,textvariable=self.sale_search,width=42).pack(side='left'); tk.Label(top,text='  Rechercher un article',bg=self.theme['bg'],fg=self.theme['muted']).pack(side='left'); self.sale_search.trace_add('write',lambda *_:self.refresh_sale_products()); ttk.Button(top,text='Calculatrice',command=self.calculator).pack(side='right')
        left=self.card(root); left.grid(row=1,column=0,sticky='nsew',padx=(0,8)); left.rowconfigure(1,weight=1); left.columnconfigure(0,weight=1); tk.Label(left,text='Articles',bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',13,'bold')).grid(row=0,column=0,sticky='w',padx=14,pady=10)
        tv=ttk.Treeview(left,columns=('id','name','price','stock'),show='headings'); self.sale_tv=tv
        for c,h,w in [('id','Produit',65),('name','Article',260),('price','Prix',115),('stock','Stock',80)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center' if c!='name' else 'w')
        sb=ttk.Scrollbar(left,orient='vertical',command=tv.yview);tv.configure(yscrollcommand=sb.set);tv.grid(row=1,column=0,sticky='nsew',padx=(12,0),pady=(0,12));sb.grid(row=1,column=1,sticky='ns',pady=(0,12),padx=(0,10));tv.bind('<<TreeviewSelect>>',self.sale_select);tv.bind('<Double-1>',self.sale_double_click);self.refresh_sale_products()
        mid=self.card(root); mid.grid(row=1,column=1,sticky='nsew',padx=4); tk.Label(mid,text='Aperçu',bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',13,'bold')).pack(anchor='w',padx=14,pady=10); self.sale_preview=tk.Label(mid,text='Sélectionnez un article',bg='white',fg=self.theme['muted']); self.sale_preview.pack(fill='both',expand=True,padx=12,pady=(0,12))
        right=self.card(root); right.grid(row=1,column=2,sticky='nsew',padx=(8,0)); right.rowconfigure(1,weight=1); tk.Label(right,text='Panier',bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',13,'bold')).pack(anchor='w',padx=14,pady=10); self.cart_tv=ttk.Treeview(right,columns=('name','qty','total'),show='headings',height=8); self.cart_tv.heading('name',text='Article');self.cart_tv.heading('qty',text='Qté');self.cart_tv.heading('total',text='Total');self.cart_tv.column('name',width=175);self.cart_tv.column('qty',width=50,anchor='center');self.cart_tv.column('total',width=105,anchor='center');self.cart_tv.pack(fill='both',expand=True,padx=12); self.sale_total=tk.Label(right,text='Total : 0',bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',17,'bold'));self.sale_total.pack(anchor='e',padx=14,pady=8)
        btn=tk.Frame(right,bg=self.theme['card']);btn.pack(fill='x',padx=10,pady=(0,12));ttk.Button(btn,text='Vider le panier',command=self.clear_cart).pack(side='left',padx=3);ttk.Button(btn,text='Supprimer',command=self.remove_cart).pack(side='left',padx=3);ttk.Button(btn,text='ENCAISSER',command=self.checkout).pack(side='right',padx=3)
    def refresh_sale_products(self):
        tv=getattr(self,'sale_tv',None)
        if not tv:return
        try:
            for x in tv.get_children():tv.delete(x)
            cur=self.db.setting('currency','FCFA'); q=self.sale_search.get() if hasattr(self,'sale_search') else ''
            for num,p in enumerate(self.db.products(q),1):tv.insert('', 'end',iid=str(p['id']),values=(num,p['name'],money(p['price'],cur),int(float(p['qty'])) if float(p['qty']).is_integer() else p['qty']))
        except tk.TclError:pass
    def sale_select(self,e=None):
        sel=self.sale_tv.selection();
        if sel:
            p=self.db.conn.execute('SELECT * FROM products WHERE id=?',(int(sel[0]),)).fetchone();ph=fit_image(p['image'],360,400,master=self.sale_preview);self.sale_preview.configure(image=ph,text=p['name'] if not ph else '');self.sale_preview.image=ph
    def quantity_dialog(self,p):
        win=tk.Toplevel(self);win.title('Ajouter au panier');win.configure(bg=self.theme['bg']);self.centered(win,390,250);win.transient(self);win.grab_set();tk.Label(win,text='Quantité',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',19,'bold')).pack(pady=(28,5));tk.Label(win,text=p['name'],bg=self.theme['bg'],fg=self.theme['muted']).pack(); v=tk.StringVar(value='1');e=ttk.Entry(win,textvariable=v,justify='center',font=('Segoe UI',16));e.pack(pady=18,ipady=5);e.focus_set();bar=tk.Frame(win,bg=self.theme['bg']);bar.pack(); ttk.Button(bar,text='Annuler',command=win.destroy).pack(side='left',padx=5); ttk.Button(bar,text='Ajouter au panier',command=lambda:self.finish_quantity(win,p,v)).pack(side='left',padx=5)
    def finish_quantity(self,win,p,v):
        q=safe_float(v.get());
        if q<=0:return
        ex=next((x for x in self.cart if x['id']==p['id']),None)
        if ex:ex['qty']+=q
        else:self.cart.append({'id':p['id'],'name':p['name'],'qty':q,'price':float(p['price'])})
        self.save_cart(); win.destroy();self.refresh_cart()
    def sale_double_click(self,e=None):
        sel=self.sale_tv.selection();
        if sel:self.quantity_dialog(self.db.conn.execute('SELECT * FROM products WHERE id=?',(int(sel[0]),)).fetchone())
    def refresh_cart(self):
        tv=getattr(self,'cart_tv',None)
        if not tv:return
        for x in tv.get_children():tv.delete(x)
        cur=self.db.setting('currency','FCFA');total=0
        for x in self.cart:
            t=x['qty']*x['price'];total+=t;tv.insert('', 'end',values=(x['name'],x['qty'],money(t,cur)))
        self.sale_total.configure(text=f'Total : {money(total,cur)}')
    def clear_cart(self):self.cart=[];self.save_cart();self.refresh_cart()
    def remove_cart(self):
        s=self.cart_tv.selection();
        if s:self.cart.pop(self.cart_tv.index(s[0]));self.save_cart();self.refresh_cart()
    def checkout(self):
        if not self.cart:messagebox.showwarning('Vente','Le panier est vide.',parent=self);return
        subtotal=sum(x['qty']*x['price'] for x in self.cart);cur=self.db.setting('currency','FCFA')
        # 1) Montant reçu, proposé à 0 par défaut
        received=self.amount_received_dialog(subtotal,cur)
        if received is None:return
        # 2) Remise, seulement si activée
        pct=0.0
        if self.db.setting('discount_enabled','1')=='1':
            pct=self.discount_dialog(safe_float(self.db.setting('default_discount','0')),subtotal)
            if pct is None:return
        disc=subtotal*max(0,min(100,pct))/100
        # 3) TVA demandée à chaque vente, taux proposé à 0 %
        tax_pct=self.tax_rate_dialog(safe_float(self.db.setting('tax_rate','0')))
        if tax_pct is None:return
        base=subtotal-disc; tax=base*max(0,min(100,tax_pct))/100; total=base+tax
        if received+1e-9<total:
            messagebox.showerror('Encaissement',f'Montant reçu insuffisant.\nTotal à encaisser : {money(total,cur)}\nReçu : {money(received,cur)}',parent=self);return
        allow=self.db.setting('allow_negative_stock','0')=='1'
        for x in self.cart:
            q=self.db.conn.execute('SELECT qty FROM products WHERE id=?',(x['id'],)).fetchone()['qty']
            if not allow and q<x['qty']:messagebox.showerror('Stock',f'Stock insuffisant : {x["name"]}\nDisponible : {q}',parent=self);return
        inv=f'FAC-{self.db.conn.execute("SELECT COALESCE(MAX(id),0)+1 n FROM sales").fetchone()["n"]:06d}';ts=now().strftime('%Y-%m-%d %H:%M:%S');change=received-total;c=self.db.conn.cursor()
        try:
            c.execute('INSERT INTO sales(invoice,date,subtotal,discount,tax_rate,tax,total,received,change_amt,cashier,register,printed) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(inv,ts,subtotal,disc,tax_pct,tax,total,received,change,self.db.setting('cashier',''),self.db.setting('register',''),0));sid=c.lastrowid
            for x in self.cart:
                c.execute('INSERT INTO sale_items(sale_id,product_id,name,qty,unit_price,total) VALUES(?,?,?,?,?,?)',(sid,x['id'],x['name'],x['qty'],x['price'],x['qty']*x['price']))
                c.execute('UPDATE products SET qty=qty-? WHERE id=?',(x['qty'],x['id']))
            self.db.conn.commit()
        except Exception as e:self.db.conn.rollback();messagebox.showerror('Vente',f'Vente non enregistrée : {e}',parent=self);return
        self.cart=[];self.save_cart();self.refresh_cart();self.refresh_sale_products();self.refresh_dashboard();self.refresh_products()
        self.print_prompt(inv)
    def tax_rate_dialog(self,default=0):
        win=tk.Toplevel(self);win.title('TVA');win.configure(bg=self.theme['bg']);self.centered(win,420,245);win.transient(self);win.grab_set()
        tk.Label(win,text='TVA de la vente (%)',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',18,'bold')).pack(pady=(24,8))
        tk.Label(win,text='Saisis 0 si aucune TVA ne s’applique.',bg=self.theme['bg'],fg=self.theme['muted']).pack()
        v=tk.StringVar(value=str(default if default else 0));e=ttk.Entry(win,textvariable=v,justify='center',font=('Segoe UI',16));e.pack(pady=18,ipady=5);e.focus_set();result={'v':None}
        def ok():
            try:n=float(v.get().replace(',','.'))
            except ValueError:messagebox.showerror('TVA','Entre un pourcentage valide.',parent=win);return
            if n<0 or n>100:messagebox.showerror('TVA','Le taux doit être compris entre 0 et 100 %.',parent=win);return
            result['v']=n;self.db.set_setting('tax_rate',str(n));self.db.conn.commit();win.destroy()
        bar=tk.Frame(win,bg=self.theme['bg']);bar.pack();ttk.Button(bar,text='Annuler',command=win.destroy).pack(side='left',padx=5);ttk.Button(bar,text='Continuer',command=ok).pack(side='left',padx=5);self.wait_window(win);return result['v']
    def discount_dialog(self,default,subtotal):
        win=tk.Toplevel(self);win.title('Remise');win.configure(bg=self.theme['bg']);self.centered(win,420,260);win.transient(self);win.grab_set()
        tk.Label(win,text='Remise de la vente',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',19,'bold')).pack(pady=(25,7))
        tk.Label(win,text=f'Sous-total : {money(subtotal,self.db.setting("currency","FCFA"))}',bg=self.theme['bg'],fg=self.theme['muted']).pack()
        v=tk.StringVar(value=str(default));e=ttk.Entry(win,textvariable=v,justify='center',font=('Segoe UI',16));e.pack(pady=18,ipady=5);e.focus_set()
        result={'v':None}
        def validate():
            n=safe_float(v.get())
            if n<0 or n>100:messagebox.showwarning('Remise','Le pourcentage doit être compris entre 0 et 100.',parent=win);return
            result['v']=n;win.destroy()
        bar=tk.Frame(win,bg=self.theme['bg']);bar.pack();ttk.Button(bar,text='Annuler',command=win.destroy).pack(side='left',padx=5);ttk.Button(bar,text='Valider la remise',command=validate).pack(side='left',padx=5)
        win.bind('<Return>',lambda e:validate());self.wait_window(win);return result['v']
    def print_prompt(self,inv):
        ok=messagebox.askyesno('Impression','Vente enregistrée.\n\nVoulez-vous imprimer le ticket ?',parent=self)
        if ok:self.choose_print_format(inv)
        else:messagebox.showinfo('Vente','Vente enregistrée.',parent=self)
    def choose_print_format(self,inv):
        win=tk.Toplevel(self); win.title('Format d’impression'); win.configure(bg=self.theme['bg']); self.centered(win,500,300); win.transient(self); win.grab_set()
        t=self.theme; tk.Label(win,text='Choisir le format du ticket',bg=t['bg'],fg=t['text'],font=('Segoe UI',20,'bold')).pack(pady=(30,8))
        tk.Label(win,text='Le format est demandé à chaque impression.',bg=t['bg'],fg=t['muted']).pack(pady=(0,22))
        bar=tk.Frame(win,bg=t['bg']); bar.pack()
        ttk.Button(bar,text='A4',command=lambda:(win.destroy(),self.print_ticket(inv,'A4'))).pack(side='left',padx=8,ipadx=25,ipady=8)
        ttk.Button(bar,text='80 mm',command=lambda:(win.destroy(),self.print_ticket(inv,'80MM'))).pack(side='left',padx=8,ipadx=20,ipady=8)
        ttk.Button(win,text='Annuler',command=win.destroy).pack(pady=24)
    def print_ticket(self,inv,fmt):
        s=self.db.conn.execute('SELECT * FROM sales WHERE invoice=?',(inv,)).fetchone(); items=self.db.conn.execute('SELECT * FROM sale_items WHERE sale_id=?',(s['id'],)).fetchall(); cur=self.db.setting('currency','FCFA')
        width=92 if fmt=='A4' else 42
        lines=[self.db.setting('header','MINI SUPERMARCHÉ'),self.db.setting('address',''),self.db.setting('phone',''),self.db.setting('email',''),f'FACTURE : {inv}',f'DATE : {s["date"]}',f'CAISSE : {s["register"]}',f'VENDEUR : {s["cashier"]}','-'*width,'ARTICLE'.ljust(max(12,width-23))+' QTÉ     TOTAL']
        for x in items:
            nm=str(x['name'])[:max(12,width-23)]; lines.append(nm.ljust(max(12,width-23))+f" {x['qty']:>4g} {money(x['total'],cur):>{max(10,width-18)}}")
        lines += ['-'*width,f'SOUS-TOTAL : {money(s["subtotal"],cur)}',f'REMISE : {money(s["discount"],cur)}',f'TVA ({s["tax_rate"]:.2f} %) : {money(s["tax"],cur)}',f'NET : {money(s["total"],cur)}',f'REÇU : {money(s["received"],cur)}',f'MONNAIE : {money(s["change_amt"],cur)}','',self.db.setting('footer','Merci pour votre achat')]
        import tempfile
        suffix='.txt'; path=Path(tempfile.gettempdir())/f'{inv}_{fmt}.txt'; path.write_text('\n'.join(x for x in lines if x),encoding='utf-8')
        try:
            if os.name=='nt':
                os.startfile(str(path),'print')
                self.db.conn.execute('UPDATE sales SET printed=1 WHERE invoice=?',(inv,)); self.db.conn.commit()
                messagebox.showinfo('Impression',f'Le ticket {inv} a été envoyé à l’impression.',parent=self)
            else:
                self.ticket_preview(inv)
        except Exception:
            self.ticket_preview(inv)
    def amount_received_dialog(self,base,cur):
        win=tk.Toplevel(self);win.title('Encaissement');win.configure(bg=self.theme['bg']);self.centered(win,440,285);win.transient(self);win.grab_set();tk.Label(win,text='Montant reçu',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',20,'bold')).pack(pady=(25,6));tk.Label(win,text=f'Sous-total avant remise et TVA : {money(base,cur)}',bg=self.theme['bg'],fg=self.theme['muted']).pack();v=tk.StringVar(value='0');e=ttk.Entry(win,textvariable=v,justify='center',font=('Segoe UI',16));e.pack(pady=22,ipady=6);e.focus_set();result={'v':None};bar=tk.Frame(win,bg=self.theme['bg']);bar.pack();ttk.Button(bar,text='Annuler',command=win.destroy).pack(side='left',padx=5);ttk.Button(bar,text='Continuer',command=lambda:self._finish_amount(win,v,result)).pack(side='left',padx=5);self.wait_window(win);return result['v']
    def _finish_amount(self,win,v,result):
        n=safe_float(v.get());
        if n<0:return
        result['v']=n;win.destroy()
    def ticket_preview(self,inv):
        s=self.db.conn.execute('SELECT * FROM sales WHERE invoice=?',(inv,)).fetchone();items=self.db.conn.execute('SELECT * FROM sale_items WHERE sale_id=?',(s['id'],)).fetchall();cur=self.db.setting('currency','FCFA');win=tk.Toplevel(self);win.title(f'Ticket {inv}');self.centered(win,600,700);win.transient(self);txt=tk.Text(win,font=('Consolas',10),wrap='word');txt.pack(fill='both',expand=True,padx=14,pady=14);lines=[self.db.setting('header','MINI SUPERMARCHÉ'),self.db.setting('address',''),self.db.setting('phone',''),f'FACTURE : {inv}',f'DATE : {s["date"]}',f'CAISSE : {s["register"]}',f'VENDEUR : {s["cashier"]}','-'*52,'PRODUIT | QTÉ | TOTAL']
        for x in items:lines.append(f'{x["name"]} | {x["qty"]} | {money(x["total"],cur)}')
        lines += ['-'*52,f'SOUS-TOTAL : {money(s["subtotal"],cur)}',f'REMISE : {money(s["discount"],cur)}',f'TVA ({s["tax_rate"]:.2f} %) : {money(s["tax"],cur)}',f'NET : {money(s["total"],cur)}',f'REÇU : {money(s["received"],cur)}',f'MONNAIE : {money(s["change_amt"],cur)}','',self.db.setting('footer','Merci pour votre achat')];txt.insert('1.0','\n'.join(x for x in lines if x));txt.configure(state='disabled');bar=tk.Frame(win,bg=self.theme['bg']);bar.pack(fill='x',padx=14,pady=(0,14));
        printed=self.db.conn.execute('SELECT COALESCE(printed,0) FROM sales WHERE invoice=?',(inv,)).fetchone()[0];
        ttk.Button(bar,text='Imprimer le ticket' if not printed else 'Réimprimer le ticket',command=lambda:(win.destroy(),self.choose_print_format(inv))).pack(side='left');ttk.Button(bar,text='Fermer',command=win.destroy).pack(side='right')
    def show_history(self):
        self.page_header('Historique des ventes','Toutes les ventes enregistrées localement');bar=tk.Frame(self.main,bg=self.theme['bg']);bar.pack(fill='x',padx=28,pady=(0,8));ttk.Button(bar,text='Supprimer uniquement l’historique',command=self.clear_history).pack(side='right');box=self.card(self.main);box.pack(fill='both',expand=True,padx=28,pady=10)
        tv=ttk.Treeview(box,columns=('invoice','date','products','subtotal','discount','total','received','change'),show='headings')
        for c,h,w in [('invoice','Facture',100),('date','Date',145),('products','Produits',300),('subtotal','Sous-total',105),('discount','Remise',95),('total','Net',105),('received','Reçu',105),('change','Monnaie',105)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center' if c!='products' else 'w')
        sb=ttk.Scrollbar(box,orient='vertical',command=tv.yview);tv.configure(yscrollcommand=sb.set);tv.pack(side='left',fill='both',expand=True,padx=(12,0),pady=12);sb.pack(side='right',fill='y',padx=(0,12),pady=12);cur=self.db.setting('currency','FCFA')
        rows=self.db.conn.execute("SELECT s.*, GROUP_CONCAT(si.name, ' , ') AS products FROM sales s LEFT JOIN sale_items si ON si.sale_id=s.id GROUP BY s.id ORDER BY s.id DESC").fetchall()
        for s in rows:tv.insert('', 'end',iid=str(s['id']),values=(s['invoice'],s['date'],s['products'] or '',money(s['subtotal'],cur),money(s['discount'],cur),money(s['total'],cur),money(s['received'],cur),money(s['change_amt'],cur)))
        tv.bind('<Double-1>',lambda e:self.ticket_preview(self.db.conn.execute('SELECT invoice FROM sales WHERE id=?',(int(tv.selection()[0]),)).fetchone()['invoice']) if tv.selection() else None)
    def stock_alert_dialog(self):
        th=safe_float(self.db.setting('stock_threshold','5'))
        win=tk.Toplevel(self); win.title('Alertes de stock'); win.configure(bg=self.theme['bg']); self.centered(win,900,680); win.transient(self)
        t=self.theme; outer=tk.Frame(win,bg=t['bg']); outer.pack(fill='both',expand=True,padx=18,pady=18)
        tk.Label(outer,text='Surveillance du stock',bg=t['bg'],fg=t['text'],font=('Segoe UI',18,'bold')).pack(anchor='w',pady=(0,5))
        tk.Label(outer,text='Double-cliquez sur un produit pour ouvrir sa fiche et modifier sa quantité.',bg=t['bg'],fg=t['muted'],font=('Segoe UI',9)).pack(anchor='w',pady=(0,12))
        low=self.db.conn.execute('SELECT id,name,qty FROM products WHERE qty>0 AND qty<=? ORDER BY qty,name',(th,)).fetchall()
        zero=self.db.conn.execute('SELECT id,name,qty FROM products WHERE qty<=0 ORDER BY name').fetchall()
        panels=tk.Frame(outer,bg=t['bg']);panels.pack(fill='both',expand=True);panels.columnconfigure(0,weight=1);panels.columnconfigure(1,weight=1);panels.rowconfigure(0,weight=1)
        for col,title,rows,bg,fg in [(0,'EN RUPTURE',zero,'#fee2e2','#991b1b'),(1,'STOCK FAIBLE',low,'#ffedd5','#9a3412')]:
            card=tk.Frame(panels,bg=bg,highlightthickness=1,highlightbackground=fg);card.grid(row=0,column=col,sticky='nsew',padx=6);card.rowconfigure(1,weight=1);card.columnconfigure(0,weight=1)
            tk.Label(card,text=f'{title}  •  {len(rows)}',bg=bg,fg=fg,font=('Segoe UI',12,'bold')).grid(row=0,column=0,sticky='w',padx=12,pady=12)
            table=tk.Frame(card,bg=bg);table.grid(row=1,column=0,sticky='nsew',padx=10,pady=(0,12));table.rowconfigure(0,weight=1);table.columnconfigure(0,weight=1)
            tv=ttk.Treeview(table,columns=('name','qty'),show='headings',selectmode='browse');tv.heading('name',text='Nom du produit');tv.heading('qty',text='Quantité');tv.column('name',width=220,anchor='w');tv.column('qty',width=80,anchor='center')
            sb=ttk.Scrollbar(table,orient='vertical',command=tv.yview);tv.configure(yscrollcommand=sb.set);tv.grid(row=0,column=0,sticky='nsew');sb.grid(row=0,column=1,sticky='ns')
            for r in rows:tv.insert('','end',iid=str(r['id']),values=(r['name'],f"{float(r['qty']):g}"))
            if not rows:tv.insert('','end',values=('Aucun produit concerné','—'))
            tv.bind('<Double-1>',lambda e,tableview=tv:self._edit_alert_product(tableview))
        ttk.Button(outer,text='Fermer',command=win.destroy).pack(anchor='e',pady=(12,0))
    def _edit_alert_product(self, tv):
        sel=tv.selection()
        if not sel:return
        try: pid=int(sel[0])
        except (TypeError,ValueError):return
        self.product_dialog(pid)
    def clear_history(self):
        if not self.require_admin('supprimer l’historique des ventes'): return
        if not messagebox.askyesno('Supprimer l’historique','Cette action supprimera uniquement l’historique des ventes et les lignes de tickets associées. Les produits, stocks, paramètres et notes seront conservés. Continuer ?',icon='warning',parent=self):return
        try:
            self.db.conn.execute('DELETE FROM sale_items'); self.db.conn.execute('DELETE FROM sales'); self.db.conn.commit()
            messagebox.showinfo('Historique','L’historique des ventes a été supprimé. Les autres données sont conservées.',parent=self); self.show_history(); self.refresh_dashboard()
        except Exception as e: messagebox.showerror('Historique',f'Impossible de supprimer l’historique : {e}',parent=self)
    def show_notes(self):
        self.page_header('Carnet','Notes locales de caisse');bar=tk.Frame(self.main,bg=self.theme['bg']);bar.pack(fill='x',padx=28);ttk.Button(bar,text='Nouvelle note',command=self.note_dialog).pack(side='right');box=self.card(self.main);box.pack(fill='both',expand=True,padx=28,pady=14);tv=ttk.Treeview(box,columns=('date','time','note'),show='headings')
        for c,h,w in [('date','Date',120),('time','Heure',100),('note','Note',800)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='w')
        sb=ttk.Scrollbar(box,orient='vertical',command=tv.yview);tv.configure(yscrollcommand=sb.set);tv.pack(side='left',fill='both',expand=True,padx=(12,0),pady=12);sb.pack(side='right',fill='y',padx=(0,12),pady=12)
        for n in self.db.conn.execute('SELECT * FROM notes ORDER BY id DESC').fetchall():tv.insert('', 'end',iid=str(n['id']),values=(n['date'],n['time'],n['note']))
        tv.bind('<Double-1>',lambda e:self.note_dialog(int(tv.selection()[0])) if tv.selection() else None)
    def note_dialog(self,nid=None):
        n=self.db.conn.execute('SELECT * FROM notes WHERE id=?',(nid,)).fetchone() if nid else None
        win=tk.Toplevel(self); win.title('Modifier la note' if n else 'Nouvelle note'); win.configure(bg=self.theme['bg']); self.centered(win,720,470); win.resizable(False,False); win.transient(self); win.grab_set()
        win.columnconfigure(0,weight=1); win.rowconfigure(1,weight=1)
        tk.Label(win,text='Nouvelle note' if not n else 'Modifier la note',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',20,'bold')).grid(row=0,column=0,sticky='w',padx=20,pady=(18,8))
        txt=tk.Text(win,font=('Segoe UI',11),wrap='word',relief='flat',highlightthickness=1,highlightbackground=self.theme['line'],bg=self.theme['card'],fg=self.theme['text'],insertbackground=self.theme['text'])
        txt.grid(row=1,column=0,sticky='nsew',padx=20,pady=(0,10))
        if n: txt.insert('1.0',n['note'])
        bar=tk.Frame(win,bg=self.theme['bg']); bar.grid(row=2,column=0,sticky='ew',padx=20,pady=(2,15)); bar.columnconfigure(0,weight=1)
        ttk.Button(bar,text='Annuler',command=win.destroy).grid(row=0,column=1,padx=5)
        def save():
            val=txt.get('1.0','end').strip()
            if not val: messagebox.showwarning('Carnet','Écris une note avant d’enregistrer.',parent=win); return
            dt=now()
            if nid:self.db.conn.execute('UPDATE notes SET note=? WHERE id=?',(val,nid))
            else:self.db.conn.execute('INSERT INTO notes(date,time,note) VALUES(?,?,?)',(dt.strftime('%d/%m/%Y'),dt.strftime('%H:%M'),val))
            self.db.conn.commit(); win.destroy(); self.show_notes()
        ttk.Button(bar,text='Enregistrer la note',command=save).grid(row=0,column=2,padx=5)
        txt.focus_set()
    def show_settings(self):
        if not self.require_admin('ouvrir les paramètres'): return
        self.page_header('Paramètres','Identité, en-tête, remise et apparence');outer=tk.Frame(self.main,bg=self.theme['bg']);outer.pack(fill='both',expand=True,padx=28,pady=4);outer.columnconfigure(0,weight=1);outer.columnconfigure(1,weight=1)
        def section(title,col,row):
            f=self.card(outer);f.grid(row=row,column=col,sticky='nsew',padx=(0,8) if col==0 else (8,0),pady=8);f.columnconfigure(1,weight=1);tk.Label(f,text=title,bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',12,'bold')).grid(row=0,column=0,columnspan=3,sticky='w',padx=14,pady=(12,8));return f
        ident=section('Identité de la caisse',0,0);head=section('En-tête de caisse & remise',1,0);appearance=section('Apparence',0,1);opts=section('Options de caisse',1,1)
        vals={k:tk.StringVar(value=self.db.setting(k,'')) for k in ['company','register','cashier','currency','header','address','phone','email','footer','logo','icon','default_discount','theme']}
        def row(f,r,k,label):tk.Label(f,text=label,bg=self.theme['card'],fg=self.theme['text']).grid(row=r,column=0,sticky='w',padx=14,pady=5);ttk.Entry(f,textvariable=vals[k]).grid(row=r,column=1,sticky='ew',padx=8,pady=5)
        for i,(k,l) in enumerate([('company','Nom'),('register','Caisse'),('cashier','Vendeur'),('currency','Devise')],1):row(ident,i,k,l)
        row(ident,5,'logo','Logo');row(ident,6,'icon','Icône .ico')
        ttk.Button(ident,text='Choisir',command=lambda:self.choose_asset(vals['logo'],'logo')).grid(row=5,column=2,padx=4);ttk.Button(ident,text='Choisir',command=lambda:self.choose_asset(vals['icon'],'icon')).grid(row=6,column=2,padx=4)
        for i,(k,l) in enumerate([('header','En-tête'),('address','Adresse'),('phone','Téléphone'),('email','E-mail'),('footer','Pied de ticket')],1):row(head,i,k,l)
        discount=tk.BooleanVar(value=self.db.setting('discount_enabled','1')=='1');tk.Label(head,text='Remise par défaut (%)',bg=self.theme['card'],fg=self.theme['text']).grid(row=6,column=0,sticky='w',padx=14,pady=5);ttk.Entry(head,textvariable=vals['default_discount']).grid(row=6,column=1,sticky='ew',padx=8,pady=5);tk.Checkbutton(head,text='Activer les remises et demander le pourcentage à chaque vente',variable=discount,bg=self.theme['card'],activebackground=self.theme['card']).grid(row=7,column=0,columnspan=3,sticky='w',padx=14,pady=6)
        tk.Label(appearance,text='Thèmes visuels',bg=self.theme['card'],fg=self.theme['text'],font=('Segoe UI',10,'bold')).grid(row=1,column=0,sticky='nw',padx=14,pady=10)
        sw=tk.Frame(appearance,bg=self.theme['card']);sw.grid(row=1,column=1,columnspan=2,sticky='ew',padx=8,pady=8);sw.columnconfigure(0,weight=1);sw.columnconfigure(1,weight=1);sw.columnconfigure(2,weight=1)
        names=list(THEMES.keys())
        for i,name in enumerate(names):
            th=THEMES[name]; holder=tk.Frame(sw,bg=th['bg'],highlightthickness=2,highlightbackground=th['accent'],cursor='hand2',width=142,height=58);holder.grid(row=i//3,column=i%3,padx=5,pady=5,sticky='ew');holder.grid_propagate(False)
            tk.Frame(holder,bg=th['nav'],width=24,height=58).pack(side='left',fill='y');body=tk.Frame(holder,bg=th['bg']);body.pack(side='left',fill='both',expand=True);tk.Label(body,text=name,bg=th['bg'],fg=th['text'],font=('Segoe UI',9,'bold')).pack(anchor='w',padx=7,pady=(7,2));swatch=tk.Frame(body,bg=th['accent'],height=8);swatch.pack(fill='x',padx=7);swatch.bind('<Button-1>',lambda e,n=name:vals['theme'].set(n));body.bind('<Button-1>',lambda e,n=name:vals['theme'].set(n));holder.bind('<Button-1>',lambda e,n=name:vals['theme'].set(n))
        tk.Label(appearance,text='Le thème choisi sera appliqué à la barre latérale, aux boutons, cartes, listes, formulaires et fenêtres.',bg=self.theme['card'],fg=self.theme['muted'],wraplength=390,justify='left').grid(row=5,column=0,columnspan=3,sticky='w',padx=14,pady=(5,2));tk.Label(appearance,textvariable=vals['theme'],bg=self.theme['soft'],fg=self.theme['accent'],font=('Segoe UI',10,'bold'),padx=10,pady=5).grid(row=6,column=0,columnspan=3,sticky='w',padx=14,pady=(4,10))
        auto=tk.BooleanVar(value=self.db.setting('auto_ticket','1')=='1');tk.Checkbutton(opts,text='Ouvrir automatiquement le ticket après vente',variable=auto,bg=self.theme['card'],activebackground=self.theme['card']).grid(row=1,column=0,columnspan=2,sticky='w',padx=14,pady=7)
        require_login=tk.BooleanVar(value=self.db.setting('require_login','1')=='1');tk.Checkbutton(opts,text='Demander une identification au lancement',variable=require_login,bg=self.theme['card'],activebackground=self.theme['card']).grid(row=4,column=0,columnspan=2,sticky='w',padx=14,pady=7)
        opts.columnconfigure(0,weight=1);opts.columnconfigure(1,weight=1)
        actions=tk.Frame(self.main,bg=self.theme['bg']);actions.pack(fill='x',padx=28,pady=(4,10));ttk.Button(actions,text='Sauvegarder maintenant',command=self.backup).pack(side='left',padx=3);ttk.Button(actions,text='Ouvrir les sauvegardes',command=lambda:os.startfile(BACKUP_DIR) if os.name=='nt' else None).pack(side='left',padx=3);ttk.Button(actions,text='Vérifier la base',command=self.verify_db).pack(side='right',padx=3);ttk.Button(actions,text='Réinitialiser',command=self.reset_db).pack(side='right',padx=3);ttk.Button(actions,text='Enregistrer tous les paramètres',command=lambda:self.save_settings(vals,discount,auto,require_login)).pack(side='right',padx=3);ttk.Button(opts,text='Clôture de caisse',command=self.cash_closing).grid(row=2,column=0,sticky='ew',padx=12,pady=5);ttk.Button(opts,text='Historique des clôtures',command=self.cash_closing_history).grid(row=2,column=1,sticky='ew',padx=12,pady=5);ttk.Button(opts,text='Comptes utilisateurs et permissions',command=self.user_management).grid(row=3,column=0,columnspan=2,sticky='ew',padx=12,pady=5)
    def expiry_alert_dialog(self):
        today=datetime.date.today(); cutoff=today+datetime.timedelta(days=30)
        rows=self.db.conn.execute("SELECT id,name,qty,expiry_date FROM products WHERE expiry_date IS NOT NULL AND expiry_date<>'' ORDER BY expiry_date,name").fetchall()
        expired=[]; upcoming=[]
        for r in rows:
            try:d=datetime.date.fromisoformat(r['expiry_date'])
            except ValueError:continue
            if d<today:expired.append(r)
            elif d<=cutoff:upcoming.append(r)
        win=tk.Toplevel(self);win.title('Alertes de péremption');win.configure(bg=self.theme['bg']);self.centered(win,850,560);win.transient(self)
        tk.Label(win,text='Surveille les produits à retirer ou à écouler',bg=self.theme['bg'],fg=self.theme['text'],font=('Segoe UI',16,'bold')).pack(anchor='w',padx=18,pady=(16,8))
        for title,items,color in [('Déjà périmés',expired,'#b91c1c'),('Péremption dans les 30 jours',upcoming,'#c2410c')]:
            frame=self.card(win);frame.pack(fill='both',expand=True,padx=18,pady=6);tk.Label(frame,text=f'{title} ({len(items)})',bg=self.theme['card'],fg=color,font=('Segoe UI',11,'bold')).pack(anchor='w',padx=10,pady=6)
            tree=ttk.Treeview(frame,columns=('name','qty','date'),show='headings',height=4);tree.heading('name',text='Produit');tree.heading('qty',text='Quantité');tree.heading('date',text='Date de péremption');tree.column('name',width=400);tree.column('qty',width=100,anchor='center');tree.column('date',width=180,anchor='center')
            sb=ttk.Scrollbar(frame,orient='vertical',command=tree.yview);tree.configure(yscrollcommand=sb.set);tree.pack(side='left',fill='both',expand=True,padx=(10,0),pady=(0,10));sb.pack(side='right',fill='y',padx=(0,10),pady=(0,10))
            for r in items:tree.insert('', 'end',iid=str(r['id']),values=(r['name'],r['qty'],r['expiry_date']))
            tree.bind('<Double-1>',lambda e,t=tree:self._edit_from_tree(t))
        ttk.Button(win,text='Fermer',command=win.destroy).pack(pady=(4,12))
    def _edit_from_tree(self,tree):
        sel=tree.selection()
        if sel:self.product_dialog(int(sel[0]))
    def cash_closing(self):
        if not self.require_admin('enregistrer la clôture de caisse'): return
        today=now().strftime('%Y-%m-%d')
        r=self.db.conn.execute("SELECT COUNT(*) n,COALESCE(SUM(total),0) total,COALESCE(SUM(received),0) received,COALESCE(SUM(change_amt),0) change_amt,COALESCE(SUM(discount),0) discount FROM sales WHERE date LIKE ?",(today+'%',)).fetchone()
        t=self.theme
        win=tk.Toplevel(self); win.title('Clôture de caisse'); win.configure(bg=t['bg']); self.centered(win,820,610); win.transient(self); win.grab_set()
        outer=tk.Frame(win,bg=t['bg']); outer.pack(fill='both',expand=True,padx=22,pady=20)
        tk.Label(outer,text='Clôture de caisse',bg=t['bg'],fg=t['text'],font=('Segoe UI',20,'bold')).pack(anchor='w')
        tk.Label(outer,text=f"Bilan des opérations du {today}",bg=t['bg'],fg=t['muted'],font=('Segoe UI',10)).pack(anchor='w',pady=(3,14))
        card=self.card(outer); card.pack(fill='both',expand=True)
        items=[('Nombre de ventes',str(r['n'])),('Chiffre d’affaires',money(r['total'],self.db.setting('currency','FCFA'))),('Montants reçus',money(r['received'],self.db.setting('currency','FCFA'))),('Monnaie rendue',money(r['change_amt'],self.db.setting('currency','FCFA'))),('Remises accordées',money(r['discount'],self.db.setting('currency','FCFA')))]
        # Chaque ligne de texte occupe sa propre rangée; les séparateurs
        # sont placés sur les rangées intermédiaires pour ne jamais barrer le texte.
        for i,(label,value) in enumerate(items):
            row = i * 2
            tk.Label(card,text=label,bg=t['card'],fg=t['muted'],font=('Segoe UI',10)).grid(row=row,column=0,sticky='w',padx=22,pady=10)
            tk.Label(card,text=value,bg=t['card'],fg=t['text'],font=('Segoe UI',11,'bold')).grid(row=row,column=1,sticky='e',padx=22,pady=10)
            if i<len(items)-1:
                ttk.Separator(card,orient='horizontal').grid(row=row+1,column=0,columnspan=2,sticky='ew',padx=20,pady=0)
        card.columnconfigure(0,weight=1); card.columnconfigure(1,weight=1)
        bar=tk.Frame(outer,bg=t['bg']); bar.pack(fill='x',pady=(14,0))
        def save():
            if not messagebox.askyesno('Confirmer la clôture','Enregistrer la clôture de caisse de cette journée ?',parent=win): return
            self.db.conn.execute('INSERT INTO cash_closings(closed_at,total_sales,cash_received,change_given,discount_total,sales_count) VALUES(?,?,?,?,?,?)',(now().strftime('%Y-%m-%d %H:%M:%S'),r['total'],r['received'],r['change_amt'],r['discount'],r['n']))
            self.db.conn.commit(); win.destroy(); messagebox.showinfo('Clôture','Clôture de caisse enregistrée.',parent=self)
        ttk.Button(bar,text='Annuler',command=win.destroy).pack(side='right',padx=4)
        ttk.Button(bar,text='Enregistrer la clôture',command=save).pack(side='right',padx=4)
    def cash_closing_history(self):
        """Consulter et imprimer les clôtures de caisse déjà enregistrées."""
        if not self.require_admin('consulter l’historique des clôtures de caisse'):
            return
        t = self.theme
        win = tk.Toplevel(self)
        win.title('Historique des clôtures de caisse')
        win.configure(bg=t['bg'])
        self.centered(win, 1050, 620)
        win.transient(self)
        tk.Label(win, text='Historique des clôtures de caisse', bg=t['bg'], fg=t['text'],
                 font=('Segoe UI', 18, 'bold')).pack(anchor='w', padx=18, pady=(16, 3))
        tk.Label(win, text='Sélectionne une clôture pour consulter son bilan détaillé ou l’imprimer.',
                 bg=t['bg'], fg=t['muted']).pack(anchor='w', padx=18, pady=(0, 10))
        box = tk.Frame(win, bg=t['card'], highlightbackground=t['line'], highlightthickness=1)
        box.pack(fill='both', expand=True, padx=18, pady=4)
        cols = ('date', 'count', 'sales', 'received', 'change', 'discount')
        tree = ttk.Treeview(box, columns=cols, show='headings', selectmode='browse')
        headings = [('date','Date et heure',190), ('count','Ventes',85), ('sales','Chiffre d’affaires',170),
                    ('received','Montants reçus',170), ('change','Monnaie rendue',160), ('discount','Remises',150)]
        for col, label, width in headings:
            tree.heading(col, text=label)
            tree.column(col, width=width, anchor='w' if col == 'date' else 'e')
        sb = ttk.Scrollbar(box, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True, padx=(6, 0), pady=6)
        sb.pack(side='right', fill='y', padx=(0, 6), pady=6)
        currency = self.db.setting('currency', 'FCFA')
        rows = self.db.conn.execute('SELECT * FROM cash_closings ORDER BY closed_at DESC, id DESC').fetchall()
        for row in rows:
            tree.insert('', 'end', iid=str(row['id']), values=(row['closed_at'], row['sales_count'] or 0,
                money(row['total_sales'] or 0, currency), money(row['cash_received'] or 0, currency),
                money(row['change_given'] or 0, currency), money(row['discount_total'] or 0, currency)))
        if not rows:
            tk.Label(win, text='Aucune clôture enregistrée pour le moment.', bg=t['bg'], fg=t['muted']).pack(pady=8)

        def details(print_it=False):
            sel = tree.selection()
            if not sel:
                messagebox.showinfo('Historique', 'Sélectionne une clôture dans la liste.', parent=win)
                return
            row = self.db.conn.execute('SELECT * FROM cash_closings WHERE id=?', (int(sel[0]),)).fetchone()
            if not row:
                messagebox.showerror('Historique', 'Cette clôture est introuvable.', parent=win)
                return
            lines = [
                self.db.setting('company', 'MINI SUPERMARCHÉ') or 'MINI SUPERMARCHÉ',
                'RAPPORT DE CLÔTURE DE CAISSE', '=' * 42,
                f'Date et heure : {row["closed_at"]}',
                f'Nombre de ventes : {row["sales_count"] or 0}',
                f'Chiffre d’affaires : {money(row["total_sales"] or 0, currency)}',
                f'Montants reçus : {money(row["cash_received"] or 0, currency)}',
                f'Monnaie rendue : {money(row["change_given"] or 0, currency)}',
                f'Remises accordées : {money(row["discount_total"] or 0, currency)}',
                '', 'Document généré par MINI SUPERMARCHÉ']
            if print_it:
                import tempfile
                path = Path(tempfile.gettempdir()) / f'cloture_caisse_{row["id"]}.txt'
                path.write_text('\n'.join(lines), encoding='utf-8')
                try:
                    if os.name == 'nt':
                        os.startfile(str(path), 'print')
                    else:
                        messagebox.showinfo('Rapport prêt', f'Rapport enregistré ici : {path}', parent=win)
                except Exception as exc:
                    messagebox.showerror('Impression', f'Impossible de lancer l’impression : {exc}\nLe rapport est conservé ici : {path}', parent=win)
                return
            detail = tk.Toplevel(win)
            detail.title('Détail de la clôture')
            detail.configure(bg=t['bg'])
            self.centered(detail, 540, 430)
            detail.transient(win)
            card = tk.Frame(detail, bg=t['card'], highlightbackground=t['line'], highlightthickness=1)
            card.pack(fill='both', expand=True, padx=18, pady=18)
            tk.Label(card, text='Détail de la clôture', bg=t['card'], fg=t['text'], font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=18, pady=(16, 10))
            for line in lines[3:9]:
                tk.Label(card, text=line, bg=t['card'], fg=t['text'], font=('Segoe UI', 11)).pack(anchor='w', padx=18, pady=5)
            ttk.Button(detail, text='Imprimer cette clôture', command=lambda: details(True)).pack(pady=(0, 14))

        bar = tk.Frame(win, bg=t['bg'])
        bar.pack(fill='x', padx=18, pady=(8, 14))
        ttk.Button(bar, text='Fermer', command=win.destroy).pack(side='right', padx=4)
        ttk.Button(bar, text='Imprimer la clôture sélectionnée', command=lambda: details(True)).pack(side='right', padx=4)
        ttk.Button(bar, text='Consulter le détail', command=details).pack(side='right', padx=4)
        tree.bind('<Double-1>', lambda _e: details())

    def user_management(self):
        if not self.require_admin('gérer les comptes utilisateurs'): return
        win=tk.Toplevel(self); win.title('Comptes utilisateurs et permissions'); win.configure(bg=self.theme['bg']); self.centered(win,900,680); win.transient(self)
        t=self.theme
        tk.Label(win,text='Comptes utilisateurs et permissions',bg=t['bg'],fg=t['text'],font=('Segoe UI',16,'bold')).pack(anchor='w',padx=18,pady=(14,3))
        tk.Label(win,text='Sélectionne un compte pour modifier son nom, son rôle ou son mot de passe.',bg=t['bg'],fg=t['muted'],font=('Segoe UI',9)).pack(anchor='w',padx=18,pady=(0,10))
        tablebox=tk.Frame(win,bg=t['card'],highlightbackground=t['line'],highlightthickness=1); tablebox.pack(fill='both',expand=True,padx=18,pady=4)
        tree=ttk.Treeview(tablebox,columns=('user','role','active'),show='headings',selectmode='browse',height=8)
        for c,h,w in [('user','Utilisateur',300),('role','Rôle',220),('active','État',120)]: tree.heading(c,text=h); tree.column(c,width=w,anchor='w')
        sb=ttk.Scrollbar(tablebox,orient='vertical',command=tree.yview); tree.configure(yscrollcommand=sb.set); tree.pack(side='left',fill='both',expand=True,padx=(5,0),pady=5); sb.pack(side='right',fill='y',padx=(0,5),pady=5)
        def refresh(select=None):
            tree.delete(*tree.get_children())
            for r in self.db.conn.execute('SELECT id,username,role,active FROM users ORDER BY username'):
                tree.insert('', 'end',iid=str(r['id']),values=(r['username'],r['role'],'Actif' if r['active'] else 'Désactivé'))
            if select and tree.exists(str(select)): tree.selection_set(str(select)); tree.focus(str(select))
        refresh()
        form=tk.Frame(win,bg=t['bg']); form.pack(fill='x',padx=18,pady=9)
        u=tk.StringVar(); pw=tk.StringVar(); role=tk.StringVar(value='Caissier')
        for col,label in enumerate(('Utilisateur','Mot de passe','Rôle')):
            tk.Label(form,text=label,bg=t['bg'],fg=t['text'],font=('Segoe UI',9,'bold')).grid(row=0,column=col,sticky='w',padx=(0 if col==0 else 8,0),pady=(0,3))
        ttk.Entry(form,textvariable=u,width=27).grid(row=1,column=0,sticky='ew',padx=(0,8))
        ttk.Entry(form,textvariable=pw,show='*',width=24).grid(row=1,column=1,sticky='ew',padx=8)
        ttk.Combobox(form,textvariable=role,values=['Administrateur','Caissier'],state='readonly',width=18).grid(row=1,column=2,sticky='ew',padx=8)
        for col in range(3): form.grid_columnconfigure(col,weight=1)
        def selected_id():
            sel=tree.selection(); return int(sel[0]) if sel else None
        def selected(_event=None):
            uid=selected_id()
            if not uid:return
            row=self.db.conn.execute('SELECT username,role FROM users WHERE id=?',(uid,)).fetchone()
            if row: u.set(row['username']); role.set(row['role']); pw.set('')
        tree.bind('<<TreeviewSelect>>',selected)
        def add():
            name=u.get().strip(); password=pw.get()
            if not name or len(password)<6: messagebox.showwarning('Compte','Nom obligatoire et mot de passe d’au moins 6 caractères.',parent=win); return
            try:
                cur=self.db.conn.execute('INSERT INTO users(username,password_hash,role,active) VALUES(?,?,?,1)',(name,hashlib.sha256(password.encode('utf-8')).hexdigest(),role.get())); self.db.conn.commit(); uid=cur.lastrowid; u.set(''); pw.set(''); role.set('Caissier'); refresh(uid); messagebox.showinfo('Compte','Nouvel utilisateur enregistré.',parent=win)
            except sqlite3.IntegrityError: messagebox.showerror('Compte','Ce nom existe déjà.',parent=win)
        def save_user():
            uid=selected_id(); name=u.get().strip()
            if not uid: messagebox.showinfo('Compte','Sélectionne un compte à modifier.',parent=win); return
            if not name: messagebox.showwarning('Compte','Le nom d’utilisateur est obligatoire.',parent=win); return
            if uid==self.current_user['id'] and role.get()!='Administrateur': messagebox.showwarning('Compte','Tu ne peux pas retirer ton propre rôle administrateur pendant la session.',parent=win); return
            try:
                self.db.conn.execute('UPDATE users SET username=?,role=? WHERE id=?',(name,role.get(),uid))
                if pw.get():
                    if len(pw.get())<6: messagebox.showwarning('Mot de passe','Le mot de passe doit contenir au moins 6 caractères.',parent=win); return
                    self.db.conn.execute('UPDATE users SET password_hash=? WHERE id=?',(hashlib.sha256(pw.get().encode('utf-8')).hexdigest(),uid))
                self.db.conn.commit()
                if uid==self.current_user['id']: self.current_user['username']=name; self.current_user['role']=role.get()
                pw.set(''); refresh(uid); messagebox.showinfo('Compte','Informations enregistrées.',parent=win)
            except sqlite3.IntegrityError: messagebox.showerror('Compte','Ce nom d’utilisateur existe déjà.',parent=win)
        def toggle():
            uid=selected_id()
            if not uid: messagebox.showinfo('Compte','Sélectionne un compte.',parent=win); return
            if uid==self.current_user['id']: messagebox.showwarning('Compte','Tu ne peux pas désactiver ton propre compte pendant la session.',parent=win); return
            r=self.db.conn.execute('SELECT active FROM users WHERE id=?',(uid,)).fetchone(); self.db.conn.execute('UPDATE users SET active=? WHERE id=?',(0 if r['active'] else 1,uid)); self.db.conn.commit(); refresh(uid)
        def delete_user():
            uid=selected_id()
            if not uid: messagebox.showinfo('Compte','Sélectionne un compte.',parent=win); return
            if uid==self.current_user['id']: messagebox.showwarning('Compte','Tu ne peux pas supprimer le compte actuellement connecté.',parent=win); return
            if not messagebox.askyesno('Supprimer le compte','Supprimer ce compte utilisateur ?',parent=win): return
            self.db.conn.execute('DELETE FROM users WHERE id=?',(uid,)); self.db.conn.commit(); u.set(''); pw.set(''); refresh()
        buttons=tk.Frame(win,bg=t['bg']); buttons.pack(fill='x',padx=18,pady=(2,14))
        style_names=[('＋ Nouvel utilisateur',add),('Enregistrer les modifications',save_user),('Activer / désactiver',toggle),('Supprimer',delete_user),('Fermer',win.destroy)]
        for label,cmd in style_names:
            ttk.Button(buttons,text=label,command=cmd).pack(side='left' if label!='Fermer' else 'right',padx=4,ipadx=1,ipady=0)
    def choose_asset(self,var,kind):
        f=filedialog.askopenfilename(parent=self,title='Choisir un logo' if kind=='logo' else 'Choisir une icône',filetypes=[('Images','*.png *.jpg *.jpeg *.webp')] if kind=='logo' else [('Icône','*.ico')]);
        if f:
            dest=USER_ASSET_DIR/('logo'+Path(f).suffix.lower() if kind=='logo' else 'app.ico');shutil.copy2(f,dest);var.set(str(dest))
    def save_settings(self,vals,discount,auto,require_login=None):
        for k,v in vals.items():self.db.set_setting(k,v.get())
        if require_login is not None:self.db.set_setting('require_login','1' if require_login.get() else '0')
        self.db.set_setting('tax_enabled','0');self.db.set_setting('tax_rate','0');self.db.set_setting('discount_enabled','1' if discount.get() else '0');self.db.set_setting('auto_ticket','1' if auto.get() else '0');self.db.conn.commit();self.theme=THEMES.get({'Bleu FASUCE':'Bleu','Sombre FASUCE':'Sombre'}.get(self.db.setting('theme','Bleu'),self.db.setting('theme','Bleu')),THEMES['Bleu']);self.apply_window_icon();messagebox.showinfo('Paramètres','Paramètre(s) enregistré(s).',parent=self);self.build();self.show_settings()
    def smart_view(self,kind):
        title={'top':'Top produits','dead':'Produits morts','day':'Meilleur jour','hour':'Heures fortes'}[kind];win=tk.Toplevel(self);win.title(title);win.configure(bg=self.theme['bg']);self.centered(win,720,500);win.transient(self);box=self.card(win);box.pack(fill='both',expand=True,padx=18,pady=18);tv=ttk.Treeview(box,show='headings')
        cur=self.db.setting('currency','FCFA')
        if kind=='top':
            tv['columns']=('name','qty','ca');
            for c,h,w in [('name','Produit',380),('qty','Quantité vendue',140),('ca','Chiffre d’affaires',160)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center' if c!='name' else 'w')
            rows=self.db.conn.execute('SELECT name,SUM(qty) qty,SUM(total) ca FROM sale_items GROUP BY product_id,name ORDER BY qty DESC LIMIT 15').fetchall();
            for r in rows:tv.insert('', 'end',values=(r['name'],r['qty'],money(r['ca'],cur)))
        elif kind=='dead':
            tv['columns']=('name','stock','last');
            for c,h,w in [('name','Produit',380),('stock','Stock actuel',140),('last','Dernière vente',160)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center' if c!='name' else 'w')
            rows=self.db.conn.execute('''SELECT p.name,p.qty,MAX(s.date) last FROM products p LEFT JOIN sale_items si ON si.product_id=p.id LEFT JOIN sales s ON s.id=si.sale_id GROUP BY p.id ORDER BY last IS NOT NULL,last ASC,p.name LIMIT 20''').fetchall();
            for r in rows:tv.insert('', 'end',values=(r['name'],r['qty'],r['last'] or 'Jamais'))
        elif kind=='day':
            tv['columns']=('jour','ca','ventes');
            for c,h,w in [('jour','Jour',300),('ca','Chiffre d’affaires',220),('ventes','Ventes',150)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center')
            day_names={0:'Dimanche',1:'Lundi',2:'Mardi',3:'Mercredi',4:'Jeudi',5:'Vendredi',6:'Samedi'}
            rows=self.db.conn.execute("SELECT CAST(strftime('%w',date) AS INTEGER) wd,SUM(total) ca,COUNT(*) ventes FROM sales GROUP BY wd ORDER BY ca DESC").fetchall();
            for r in rows:tv.insert('', 'end',values=(day_names.get(r['wd'],'—'),money(r['ca'],cur),r['ventes']))
        else:
            tv['columns']=('heure','ca','ventes');
            for c,h,w in [('heure','Heure',300),('ca','Chiffre d’affaires',220),('ventes','Ventes',150)]:tv.heading(c,text=h);tv.column(c,width=w,anchor='center')
            rows=self.db.conn.execute('SELECT substr(date,12,2) heure,SUM(total) ca,COUNT(*) ventes FROM sales GROUP BY heure ORDER BY ca DESC LIMIT 15').fetchall();
            for r in rows:tv.insert('', 'end',values=(r['heure']+' h',money(r['ca'],cur),r['ventes']))
        tv.pack(fill='both',expand=True,padx=12,pady=12);ttk.Button(win,text='Fermer',command=win.destroy).pack(pady=(0,14))
    def calculator(self):
        win=tk.Toplevel(self);win.title('Calculatrice de caisse');win.configure(bg=self.theme['bg']);self.centered(win,360,500);win.transient(self);display=tk.StringVar(value='0');e=tk.Entry(win,textvariable=display,justify='right',font=('Segoe UI',25,'bold'),relief='flat',bg='white');e.pack(fill='x',padx=18,pady=18,ipady=12);grid=tk.Frame(win,bg=self.theme['bg']);grid.pack(fill='both',expand=True,padx=18,pady=4)
        expr=''
        def press(v):
            nonlocal expr
            if v=='C':expr='';display.set('0');return
            if v=='⌫':expr=expr[:-1];display.set(expr or '0');return
            if v=='=':
                try:expr=str(round(eval(expr,{'__builtins__':{}},{}),10));display.set(expr)
                except:expr='';display.set('Erreur')
                return
            expr+=v;display.set(expr)
        keys=[('C',0,0),('⌫',0,1),('/',0,2),('*',0,3),('7',1,0),('8',1,1),('9',1,2),('-',1,3),('4',2,0),('5',2,1),('6',2,2),('+',2,3),('1',3,0),('2',3,1),('3',3,2),('=',3,3),('0',4,0),('.',4,1)]
        for k,r,c in keys:tk.Button(grid,text=k,command=lambda x=k:press(x),font=('Segoe UI',13,'bold'),relief='flat',bg=self.theme['card'],fg=self.theme['text'],activebackground=self.theme['accent'],activeforeground='white').grid(row=r,column=c,sticky='nsew',padx=4,pady=4)
        for i in range(5):grid.rowconfigure(i,weight=1)
        for i in range(4):grid.columnconfigure(i,weight=1)
    def backup(self):
        if not self.require_admin('créer une sauvegarde manuelle'): return
        dest=BACKUP_DIR/f'caisse_{now().strftime("%Y%m%d_%H%M%S")}.db';self.db.conn.commit();shutil.copy2(DB_PATH,dest);messagebox.showinfo('Sauvegarde','Sauvegarde créée.',parent=self)
    def verify_db(self):
        if not self.require_admin('vérifier la base de données'): return
        r=self.db.conn.execute('PRAGMA integrity_check').fetchone()[0];messagebox.showinfo('Vérification','Base saine.' if r=='ok' else r,parent=self)
    def reset_db(self):
        if not self.require_admin('réinitialiser complètement la caisse'): return
        if not messagebox.askyesno('Réinitialisation complète','Cette action effacera définitivement les produits et leurs quantités en stock, ventes, tickets, notes, clôtures et comptes utilisateurs. Le logo et les paramètres de présentation seront conservés. Continuer ?',icon='warning',parent=self): return
        if not messagebox.askyesno('Confirmation finale','La caisse redeviendra vierge, sans aucun produit ni stock. Cette action est irréversible. Confirmer ?',icon='warning',parent=self): return
        try:
            self.db.conn.execute('BEGIN')
            for table in ('sale_items','sales','cash_closings','notes','products','users'):
                self.db.conn.execute(f'DELETE FROM {table}')
            # Réinitialiser les paramètres métier, tout en gardant le logo, l'icône,
            # le thème et le choix explicite de demander (ou non) une identification.
            keep={k:self.db.setting(k,'') for k in ('logo','icon','theme','require_login')}
            defaults={'company':'MINI SUPERMARCHÉ','register':'CAISSE 02','cashier':'','currency':'FCFA','header':'MINI SUPERMARCHÉ','address':'','phone':'','email':'','footer':'Merci pour votre achat','tax_enabled':'0','tax_rate':'0','discount_enabled':'1','default_discount':'0','ticket_format':'80MM','stock_threshold':'5','allow_negative_stock':'0','auto_ticket':'1','cart_state':'[]'}
            for key,value in defaults.items(): self.db.set_setting(key,value)
            for key,value in keep.items(): self.db.set_setting(key,value)
            self.db.set_setting('cart_state','[]')
            self.db.conn.commit()
            for table in ('sale_items','sales','cash_closings','notes','products','users'):
                try:self.db.conn.execute(f'DELETE FROM sqlite_sequence WHERE name=?',(table,))
                except sqlite3.Error:pass
            self.db.conn.commit()
            self.cart=[]; self.current_user={'id':0,'username':'Accès direct','role':'Administrateur'} if self.db.setting('require_login','1')!='1' else None
            messagebox.showinfo('Réinitialisation','La caisse est maintenant vierge. Le logo et les paramètres de présentation ont été conservés. '+('L’identification est désactivée : accès direct au lancement.' if self.db.setting('require_login','1')!='1' else 'Au prochain lancement, le premier compte administrateur pourra être créé.'),parent=self)
            if self.db.setting('require_login','1')=='1':
                self.destroy(); return
            self.theme=THEMES.get(self.db.setting('theme','Bleu'),THEMES['Bleu']);self.build();self.show_dashboard()
        except Exception as exc:
            try:self.db.conn.rollback()
            except Exception:pass
            messagebox.showerror('Réinitialisation','La réinitialisation a échoué : '+str(exc),parent=self)
    def on_close(self):
        if self._after:
            try:self.after_cancel(self._after)
            except:pass
        try:self.save_cart();self.db.conn.commit();self.db.conn.close()
        except:pass
        self.destroy()

if __name__=='__main__':App().mainloop()
