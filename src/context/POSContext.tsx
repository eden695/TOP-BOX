import React, { createContext, useContext, useState, useEffect } from 'react';
import { Product, CartItem, Sale, Client, CashClosing, Note, Settings, PageId, User } from '../types';
import {
  INITIAL_PRODUCTS,
  INITIAL_CLIENTS,
  INITIAL_SALES,
  INITIAL_CLOSINGS,
  INITIAL_NOTES,
  INITIAL_SETTINGS,
  INITIAL_USERS,
} from '../data/initialData';

interface POSContextType {
  currentPage: PageId;
  setCurrentPage: (page: PageId) => void;
  // User & Sessions
  currentUser: User | null;
  users: User[];
  loginUser: (username: string, pass: string) => boolean;
  logoutUser: () => void;
  switchCashier: (userId: number) => void;
  addUser: (user: Omit<User, 'id' | 'createdAt'>) => void;
  updateUser: (id: number, user: Partial<User>) => void;
  deleteUser: (id: number) => void;
  // Products
  products: Product[];
  addProduct: (product: Omit<Product, 'id'>) => void;
  updateProduct: (id: number, product: Partial<Product>) => void;
  deleteProduct: (id: number) => void;
  adjustStock: (id: number, delta: number) => void;
  // Cart & POS
  cart: CartItem[];
  addToCart: (product: Product, qty?: number) => void;
  updateCartQty: (productId: number, qty: number) => void;
  removeFromCart: (productId: number) => void;
  clearCart: () => void;
  sales: Sale[];
  checkout: (details: {
    received: number;
    discountPercent: number;
    taxPercent: number;
    paymentMethod: 'CASH' | 'MOMO_CONGO' | 'AIRTEL_CONGO';
    customerName?: string;
    momoPhone?: string;
    momoRef?: string;
  }) => Sale | null;
  clearSalesHistory: () => void;
  // Clients
  clients: Client[];
  addClient: (client: Omit<Client, 'id' | 'loyalty_points' | 'debt' | 'purchases_count' | 'total_spent'>) => void;
  updateClient: (id: number, client: Partial<Client>) => void;
  // Closings
  closings: CashClosing[];
  performDailyClosing: (notes?: string) => CashClosing;
  // Notes
  notes: Note[];
  addNote: (noteText: string, author?: string) => void;
  deleteNote: (id: number) => void;
  // Settings & Utilities
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  resetAllData: () => void;
  formatMoney: (val: number) => string;
  playBeep: () => void;
  playSuccess: () => void;
  selectedReceipt: Sale | null;
  setSelectedReceipt: (sale: Sale | null) => void;
  isCalculatorVisible: boolean;
  setIsCalculatorVisible: (visible: boolean | ((prev: boolean) => boolean)) => void;
  isAdmin: boolean;
  quickAlertsCount: { lowStock: number; expiredSoon: number };
}

const POSContext = createContext<POSContextType | undefined>(undefined);

// Web Audio API Synth sound generator for tactile feedback
function playSound(freq: number, type: OscillatorType, duration: number) {
  try {
    const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch {
    // Ignore audio restrictions
  }
}

function safeParse<T>(key: string, fallback: T): T {
  try {
    const saved = localStorage.getItem(key);
    if (!saved) return fallback;
    const parsed = JSON.parse(saved);
    if (parsed === null || parsed === undefined) return fallback;
    return parsed;
  } catch (err) {
    console.warn(`[TOP-BOX] Corrupt data in localStorage for "${key}", resetting to fallback.`, err);
    return fallback;
  }
}

export const POSProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPage, setCurrentPage] = useState<PageId>('dashboard');

  // Users state
  const [users, setUsers] = useState<User[]>(() => {
    const parsed = safeParse<User[]>('topbox_users', INITIAL_USERS);
    return Array.isArray(parsed) && parsed.length > 0 ? parsed : INITIAL_USERS;
  });

  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const user = safeParse<User | null>('topbox_current_user', null);
    if (user && user.username) {
      return {
        ...user,
        fullName: user.fullName || user.username,
        role: user.role || 'Administrateur',
      };
    }
    return INITIAL_USERS[0]; // Admin by default
  });

  const [products, setProducts] = useState<Product[]>(() => {
    const parsed = safeParse<Product[]>('topbox_products', INITIAL_PRODUCTS);
    return Array.isArray(parsed) && parsed.length > 0 ? parsed : INITIAL_PRODUCTS;
  });

  const [cart, setCart] = useState<CartItem[]>(() => {
    const parsed = safeParse<CartItem[]>('topbox_cart', []);
    return Array.isArray(parsed) ? parsed : [];
  });

  const [sales, setSales] = useState<Sale[]>(() => {
    const parsed = safeParse<Sale[]>('topbox_sales', INITIAL_SALES);
    return Array.isArray(parsed) ? parsed : INITIAL_SALES;
  });

  const [clients, setClients] = useState<Client[]>(() => {
    const parsed = safeParse<Client[]>('topbox_clients', INITIAL_CLIENTS);
    return Array.isArray(parsed) ? parsed : INITIAL_CLIENTS;
  });

  const [closings, setClosings] = useState<CashClosing[]>(() => {
    const parsed = safeParse<CashClosing[]>('topbox_closings', INITIAL_CLOSINGS);
    return Array.isArray(parsed) ? parsed : INITIAL_CLOSINGS;
  });

  const [notes, setNotes] = useState<Note[]>(() => {
    const parsed = safeParse<Note[]>('topbox_notes', INITIAL_NOTES);
    return Array.isArray(parsed) ? parsed : INITIAL_NOTES;
  });

  const [settings, setSettings] = useState<Settings>(() => {
    const parsed = safeParse<Settings>('topbox_settings', INITIAL_SETTINGS);
    return parsed && typeof parsed === 'object' ? { ...INITIAL_SETTINGS, ...parsed } : INITIAL_SETTINGS;
  });

  const [selectedReceipt, setSelectedReceipt] = useState<Sale | null>(null);
  const [isCalculatorVisible, setIsCalculatorVisible] = useState<boolean>(false);

  useEffect(() => {
    localStorage.removeItem('topbox_theme_mode');
    document.documentElement.classList.remove('theme-light');
    document.documentElement.removeAttribute('data-theme');
  }, []);

  const isAdmin = currentUser?.role === 'Administrateur';

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('topbox_users', JSON.stringify(users));
  }, [users]);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('topbox_current_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('topbox_current_user');
    }
  }, [currentUser]);

  useEffect(() => {
    localStorage.setItem('topbox_products', JSON.stringify(products));
  }, [products]);

  useEffect(() => {
    localStorage.setItem('topbox_cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    localStorage.setItem('topbox_sales', JSON.stringify(sales));
  }, [sales]);

  useEffect(() => {
    localStorage.setItem('topbox_clients', JSON.stringify(clients));
  }, [clients]);

  useEffect(() => {
    localStorage.setItem('topbox_closings', JSON.stringify(closings));
  }, [closings]);

  useEffect(() => {
    localStorage.setItem('topbox_notes', JSON.stringify(notes));
  }, [notes]);

  useEffect(() => {
    localStorage.setItem('topbox_settings', JSON.stringify(settings));
  }, [settings]);

  const formatMoney = (val: number): string => {
    const formatted = Math.round(val).toLocaleString('fr-FR');
    return `${formatted} ${settings.currency}`;
  };

  const playBeep = () => {
    playSound(1400, 'sine', 0.08);
  };

  const playSuccess = () => {
    playSound(880, 'triangle', 0.12);
    setTimeout(() => playSound(1320, 'triangle', 0.18), 120);
  };

  // User & Sessions Management
  const loginUser = (username: string, pass: string): boolean => {
    const found = users.find(
      (u) => u.username.toLowerCase() === username.toLowerCase().trim() && u.passwordHash === pass && u.active
    );
    if (found) {
      setCurrentUser(found);
      updateSettings({ cashier: `${found.fullName} (${found.role})` });
      return true;
    }
    return false;
  };

  const logoutUser = () => {
    setCurrentUser(null);
  };

  const switchCashier = (userId: number) => {
    const found = users.find((u) => u.id === userId && u.active);
    if (found) {
      setCurrentUser(found);
      updateSettings({ cashier: `${found.fullName} (${found.role})` });
    }
  };

  const addUser = (userData: Omit<User, 'id' | 'createdAt'>) => {
    const nextId = users.length > 0 ? Math.max(...users.map((u) => u.id)) + 1 : 1;
    const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const newUser: User = {
      ...userData,
      id: nextId,
      createdAt: nowStr,
    };
    setUsers((prev) => [...prev, newUser]);
  };

  const updateUser = (id: number, updateData: Partial<User>) => {
    setUsers((prev) =>
      prev.map((u) => {
        if (u.id === id) {
          const updated = { ...u, ...updateData };
          if (currentUser?.id === id) {
            setCurrentUser(updated);
            if (updateData.fullName || updateData.role) {
              updateSettings({ cashier: `${updated.fullName} (${updated.role})` });
            }
          }
          return updated;
        }
        return u;
      })
    );
  };

  const deleteUser = (id: number) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
    if (currentUser?.id === id) {
      const remaining = users.filter((u) => u.id !== id);
      setCurrentUser(remaining.length > 0 ? remaining[0] : null);
    }
  };

  // Products
  const addProduct = (p: Omit<Product, 'id'>) => {
    const nextId = products.length > 0 ? Math.max(...products.map((x) => x.id)) + 1 : 1;
    const newProduct: Product = { ...p, id: nextId };
    setProducts((prev) => [newProduct, ...prev]);
  };

  const updateProduct = (id: number, p: Partial<Product>) => {
    setProducts((prev) => prev.map((item) => (item.id === id ? { ...item, ...p } : item)));
  };

  const deleteProduct = (id: number) => {
    setProducts((prev) => prev.filter((item) => item.id !== id));
  };

  const adjustStock = (id: number, delta: number) => {
    setProducts((prev) =>
      prev.map((item) => (item.id === id ? { ...item, qty: Math.max(0, item.qty + delta) } : item))
    );
  };

  // Cart
  const addToCart = (product: Product, qty: number = 1) => {
    playBeep();
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + qty } : item
        );
      }
      return [
        ...prev,
        {
          id: product.id,
          name: product.name,
          price: product.price,
          qty: qty,
          max_qty: product.qty,
        },
      ];
    });
  };

  const updateCartQty = (productId: number, qty: number) => {
    if (qty <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart((prev) =>
      prev.map((item) => (item.id === productId ? { ...item, qty } : item))
    );
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((item) => item.id !== productId));
  };

  const clearCart = () => {
    setCart([]);
  };

  // Checkout
  const checkout = (details: {
    received: number;
    discountPercent: number;
    taxPercent: number;
    paymentMethod: 'CASH' | 'MOMO_CONGO' | 'AIRTEL_CONGO';
    customerName?: string;
    momoPhone?: string;
    momoRef?: string;
  }): Sale | null => {
    if (cart.length === 0) return null;

    const subtotal = cart.reduce((acc, item) => acc + item.price * item.qty, 0);
    const disc = subtotal * (Math.max(0, Math.min(100, details.discountPercent)) / 100);
    const taxableBase = subtotal - disc;
    const taxAmt = taxableBase * (Math.max(0, Math.min(100, details.taxPercent)) / 100);
    const total = taxableBase + taxAmt;
    const changeAmt = Math.max(0, details.received - total);

    const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const nextInvoiceNum = sales.length + 101;
    const invoice = `FAC-${String(nextInvoiceNum).padStart(6, '0')}`;

    const cashierName = currentUser?.fullName || settings.cashier;

    const newSale: Sale = {
      id: sales.length > 0 ? Math.max(...sales.map((s) => s.id)) + 1 : 1,
      invoice,
      date: nowStr,
      subtotal,
      discount: disc,
      tax_rate: details.taxPercent,
      tax: taxAmt,
      total,
      received: details.received,
      change_amt: changeAmt,
      cashier: cashierName,
      register: settings.register,
      printed: 1,
      customer_name: details.customerName,
      payment_method: details.paymentMethod,
      momo_phone: details.momoPhone,
      momo_ref: details.momoRef,
      items: cart.map((c) => ({
        product_id: c.id,
        name: c.name,
        qty: c.qty,
        unit_price: c.price,
        total: c.price * c.qty,
      })),
    };

    // Deduct stock from products
    setProducts((prev) =>
      prev.map((p) => {
        const inCart = cart.find((c) => c.id === p.id);
        if (inCart) {
          return { ...p, qty: Math.max(0, p.qty - inCart.qty) };
        }
        return p;
      })
    );

    // Update customer stats if assigned
    if (details.customerName) {
      setClients((prev) =>
        prev.map((cl) => {
          if (cl.name.toLowerCase() === details.customerName?.toLowerCase()) {
            return {
              ...cl,
              purchases_count: cl.purchases_count + 1,
              total_spent: cl.total_spent + total,
              loyalty_points: cl.loyalty_points + Math.floor(total / 100),
            };
          }
          return cl;
        })
      );
    }

    setSales((prev) => [newSale, ...prev]);
    clearCart();
    playSuccess();
    setSelectedReceipt(newSale);
    return newSale;
  };

  const clearSalesHistory = () => {
    setSales([]);
    localStorage.setItem('topbox_sales', '[]');
  };

  // Clients
  const addClient = (c: Omit<Client, 'id' | 'loyalty_points' | 'debt' | 'purchases_count' | 'total_spent'>) => {
    const nextId = clients.length > 0 ? Math.max(...clients.map((x) => x.id)) + 1 : 1;
    const newClient: Client = {
      ...c,
      id: nextId,
      loyalty_points: 0,
      debt: 0,
      purchases_count: 0,
      total_spent: 0,
    };
    setClients((prev) => [...prev, newClient]);
  };

  const updateClient = (id: number, c: Partial<Client>) => {
    setClients((prev) => prev.map((item) => (item.id === id ? { ...item, ...c } : item)));
  };

  // Cash Closing (Z-Report)
  const performDailyClosing = (notesText?: string): CashClosing => {
    const todayPrefix = new Date().toISOString().substring(0, 10);
    const todaySales = sales.filter((s) => s.date.startsWith(todayPrefix));

    const totalSales = todaySales.reduce((acc, s) => acc + s.total, 0);
    const cashReceived = todaySales.reduce((acc, s) => acc + s.received, 0);
    const changeGiven = todaySales.reduce((acc, s) => acc + s.change_amt, 0);
    const discountTotal = todaySales.reduce((acc, s) => acc + s.discount, 0);

    const newClosing: CashClosing = {
      id: closings.length > 0 ? Math.max(...closings.map((c) => c.id)) + 1 : 1,
      closed_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
      total_sales: totalSales,
      cash_received: cashReceived,
      change_given: changeGiven,
      discount_total: discountTotal,
      sales_count: todaySales.length,
      cashier: currentUser?.fullName || settings.cashier,
      notes: notesText || `Clôture de caisse effectuée par ${currentUser?.fullName || settings.cashier}.`,
    };

    setClosings((prev) => [newClosing, ...prev]);
    return newClosing;
  };

  // Notes
  const addNote = (noteText: string, author?: string) => {
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-FR');
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    const nextId = notes.length > 0 ? Math.max(...notes.map((n) => n.id)) + 1 : 1;
    const newNote: Note = {
      id: nextId,
      date: dateStr,
      time: timeStr,
      note: noteText,
      author: author || currentUser?.fullName || settings.cashier,
    };
    setNotes((prev) => [newNote, ...prev]);
  };

  const deleteNote = (id: number) => {
    setNotes((prev) => prev.filter((n) => n.id !== id));
  };

  // Settings
  const updateSettings = (newSettings: Partial<Settings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  const resetAllData = () => {
    setProducts(INITIAL_PRODUCTS);
    setCart([]);
    setSales(INITIAL_SALES);
    setClients(INITIAL_CLIENTS);
    setClosings(INITIAL_CLOSINGS);
    setNotes(INITIAL_NOTES);
    setSettings(INITIAL_SETTINGS);
    setUsers(INITIAL_USERS);
    setCurrentUser(INITIAL_USERS[0]);
  };

  // Quick alerts computation
  const lowStockCount = products.filter((p) => p.qty <= settings.stock_threshold).length;
  const expiredSoonCount = products.filter((p) => {
    if (!p.expiry_date) return false;
    const exp = new Date(p.expiry_date).getTime();
    const limit = Date.now() + 30 * 24 * 3600 * 1000;
    return exp <= limit;
  }).length;

  return (
    <POSContext.Provider
      value={{
        currentPage,
        setCurrentPage,
        currentUser,
        users,
        loginUser,
        logoutUser,
        switchCashier,
        addUser,
        updateUser,
        deleteUser,
        products,
        addProduct,
        updateProduct,
        deleteProduct,
        adjustStock,
        cart,
        addToCart,
        updateCartQty,
        removeFromCart,
        clearCart,
        sales,
        checkout,
        clearSalesHistory,
        clients,
        addClient,
        updateClient,
        closings,
        performDailyClosing,
        notes,
        addNote,
        deleteNote,
        settings,
        updateSettings,
        resetAllData,
        formatMoney,
        playBeep,
        playSuccess,
        selectedReceipt,
        setSelectedReceipt,
        isCalculatorVisible,
        setIsCalculatorVisible,
        isAdmin,
        quickAlertsCount: { lowStock: lowStockCount, expiredSoon: expiredSoonCount },
      }}
    >
      {children}
    </POSContext.Provider>
  );
};

export const usePOS = (): POSContextType => {
  const context = useContext(POSContext);
  if (!context) {
    throw new Error('usePOS must be used within a POSProvider');
  }
  return context;
};
