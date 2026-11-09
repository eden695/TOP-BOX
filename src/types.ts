export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  qty: number;
  category: string;
  image?: string;
  expiry_date?: string;
  barcode?: string;
}

export interface CartItem {
  id: number;
  name: string;
  price: number;
  qty: number;
  max_qty: number;
}

export interface SaleItem {
  product_id?: number;
  name: string;
  qty: number;
  unit_price: number;
  total: number;
}

export interface Sale {
  id: number;
  invoice: string;
  date: string;
  subtotal: number;
  discount: number;
  tax_rate: number;
  tax: number;
  total: number;
  received: number;
  change_amt: number;
  cashier: string;
  register: string;
  printed: number;
  items: SaleItem[];
  customer_name?: string;
  payment_method: 'CASH' | 'MOMO_CONGO' | 'AIRTEL_CONGO';
  momo_phone?: string;
  momo_ref?: string;
}

export interface Client {
  id: number;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  loyalty_points: number;
  debt: number;
  purchases_count: number;
  total_spent: number;
}

export interface CashClosing {
  id: number;
  closed_at: string;
  total_sales: number;
  cash_received: number;
  change_given: number;
  discount_total: number;
  sales_count: number;
  notes?: string;
  cashier?: string;
}

export interface Note {
  id: number;
  date: string;
  time: string;
  note: string;
  author?: string;
}

export interface User {
  id: number;
  username: string;
  fullName: string;
  passwordHash: string; // or plain pin
  role: 'Administrateur' | 'Caissier';
  active: boolean;
  createdAt: string;
}

export interface Settings {
  company: string;
  register: string;
  cashier: string;
  currency: string;
  header: string;
  address: string;
  phone: string;
  email: string;
  footer: string;
  stock_threshold: number;
  discount_enabled: boolean;
  default_discount: number;
  tax_rate: number;
  theme: string;
  allow_negative_stock: boolean;
}

export type PageId =
  | 'dashboard'
  | 'pos'
  | 'products'
  | 'history'
  | 'clients'
  | 'closings'
  | 'users'
  | 'notes'
  | 'settings';
