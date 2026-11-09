import React, { useState, useMemo, useRef, useEffect } from 'react';
import { usePOS } from '../context/POSContext';
import { Product } from '../types';
import { EmbeddedCalculator } from './EmbeddedCalculator';
import {
  Search,
  Barcode,
  Plus,
  Minus,
  Trash2,
  CheckCircle,
  Banknote,
  Smartphone,
  UserCheck,
  X,
  Calculator,
  ShieldCheck,
} from 'lucide-react';

export const POSScreen: React.FC = () => {
  const {
    products,
    cart,
    addToCart,
    updateCartQty,
    removeFromCart,
    clearCart,
    checkout,
    formatMoney,
    settings,
    clients,
    currentUser,
    isCalculatorVisible,
    setIsCalculatorVisible,
  } = usePOS();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('Tous');
  const [selectedCustomer, setSelectedCustomer] = useState<string>('');
  const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);

  // Checkout modal state (CASH or Congo Mobile Money)
  const [amountReceived, setAmountReceived] = useState<number>(0);
  const [discountPercent, setDiscountPercent] = useState<number>(settings.default_discount || 0);
  const [taxPercent, setTaxPercent] = useState<number>(settings.tax_rate || 0);
  const [paymentMethod, setPaymentMethod] = useState<'CASH' | 'MOMO_CONGO' | 'AIRTEL_CONGO'>('CASH');
  const [momoPhone, setMomoPhone] = useState('+242 06 ');
  const [momoRef, setMomoRef] = useState('');

  const barcodeInputRef = useRef<HTMLInputElement>(null);

  // Available categories
  const categories = useMemo(() => {
    const cats = Array.from(new Set(products.map((p) => p.category))).filter(Boolean);
    return ['Tous', ...cats];
  }, [products]);

  // Filtered products
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchCat = selectedCategory === 'Tous' || p.category === selectedCategory;
      const query = searchQuery.toLowerCase().trim();
      const matchSearch =
        !query ||
        p.name.toLowerCase().includes(query) ||
        (p.barcode && p.barcode.includes(query)) ||
        p.category.toLowerCase().includes(query);
      return matchCat && matchSearch;
    });
  }, [products, selectedCategory, searchQuery]);

  // Calculations
  const subtotal = useMemo(() => {
    return cart.reduce((acc, it) => acc + it.price * it.qty, 0);
  }, [cart]);

  const discountAmount = useMemo(() => {
    return subtotal * (Math.max(0, Math.min(100, discountPercent)) / 100);
  }, [subtotal, discountPercent]);

  const taxableBase = subtotal - discountAmount;
  const taxAmount = useMemo(() => {
    return taxableBase * (Math.max(0, Math.min(100, taxPercent)) / 100);
  }, [taxableBase, taxPercent]);

  const totalNet = taxableBase + taxAmount;
  const changeDue = Math.max(0, amountReceived - totalNet);

  // Quick cash bill shortcuts for Central African CFA Francs (FCFA / XAF)
  const cashBills = [500, 1000, 2000, 5000, 10000, 20000];

  const handleOpenCheckout = () => {
    if (cart.length === 0) return;
    setAmountReceived(totalNet);
    setIsCheckoutModalOpen(true);
  };

  const handleBarcodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    const exactMatch = products.find(
      (p) => (p.barcode && p.barcode === query) || p.name.toLowerCase() === query.toLowerCase()
    );

    if (exactMatch) {
      addToCart(exactMatch, 1);
      setSearchQuery('');
    } else if (filteredProducts.length === 1) {
      addToCart(filteredProducts[0], 1);
      setSearchQuery('');
    }
  };

  const handleConfirmPayment = () => {
    if (paymentMethod === 'CASH' && amountReceived < totalNet) {
      alert(`Le montant reçu (${formatMoney(amountReceived)}) est inférieur au net à payer.`);
      return;
    }

    checkout({
      received: paymentMethod === 'CASH' ? amountReceived : totalNet,
      discountPercent,
      taxPercent,
      paymentMethod,
      customerName: selectedCustomer || undefined,
      momoPhone: paymentMethod !== 'CASH' ? momoPhone : undefined,
      momoRef: paymentMethod !== 'CASH' ? momoRef : undefined,
    });

    setIsCheckoutModalOpen(false);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F9') {
        e.preventDefault();
        handleOpenCheckout();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [totalNet, cart]);

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* LEFT SECTION: Search, Categories & Product Grid */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950 p-6 overflow-hidden">
        {/* Top Search & Barcode Bar */}
        <div className="flex items-center gap-3 mb-4 shrink-0">
          <form onSubmit={handleBarcodeSubmit} className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              ref={barcodeInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Scanner code-barres ou rechercher un article (appuyez sur Entrée)..."
              className="w-full pl-11 pr-10 py-3 bg-slate-900 border border-slate-800 rounded-xl text-white placeholder-slate-500 font-medium text-sm focus:outline-none focus:border-blue-500 transition-colors"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </form>

          <button
            type="button"
            onClick={() => barcodeInputRef.current?.focus()}
            title="Activer la douchette code-barres"
            className="flex items-center gap-2 px-3.5 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 text-xs font-bold transition-all shrink-0 cursor-pointer"
          >
            <Barcode className="w-4 h-4 text-sky-400" />
            <span className="hidden md:inline">Scanner</span>
          </button>

          <button
            type="button"
            onClick={() => setIsCalculatorVisible((prev) => !prev)}
            title="Afficher/Masquer la calculatrice intégrée"
            className={`flex items-center gap-2 px-3.5 py-3 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer border ${
              isCalculatorVisible
                ? 'bg-blue-600 text-white border-blue-500'
                : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-white'
            }`}
          >
            <Calculator className="w-4 h-4" />
            <span className="hidden md:inline">Calculatrice</span>
          </button>
        </div>

        {/* Categories Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-3 mb-3 shrink-0 scrollbar-none">
          {categories.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800/80 hover:bg-slate-850'
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Products Grid & Optional Embedded Calculator */}
        <div className="flex-1 flex gap-4 overflow-hidden">
          <div className="flex-1 overflow-y-auto pr-1">
            {filteredProducts.length === 0 ? (
              <div className="h-64 flex flex-col items-center justify-center text-slate-500 space-y-2">
                <Search className="w-8 h-8 opacity-40" />
                <p className="text-sm font-semibold">Aucun article ne correspond à votre recherche.</p>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('Tous');
                  }}
                  className="text-xs text-blue-400 underline font-bold"
                >
                  Réinitialiser les filtres
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3.5">
                {filteredProducts.map((p) => {
                  const isOutOfStock = p.qty <= 0;
                  const isLowStock = p.qty <= settings.stock_threshold;
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        if (isOutOfStock && !settings.allow_negative_stock) return;
                        addToCart(p, 1);
                      }}
                      disabled={isOutOfStock && !settings.allow_negative_stock}
                      className={`group text-left bg-slate-900 border rounded-2xl p-3 flex flex-col justify-between transition-all select-none relative overflow-hidden ${
                        isOutOfStock && !settings.allow_negative_stock
                          ? 'opacity-40 border-slate-800 cursor-not-allowed'
                          : 'border-slate-800/90 hover:border-blue-500/80 hover:shadow-lg hover:shadow-blue-500/10 cursor-pointer active:scale-[0.98]'
                      }`}
                    >
                      {/* Image / Thumbnail Container */}
                      <div className="w-full aspect-[4/3] rounded-xl bg-slate-800/80 overflow-hidden mb-2 relative flex items-center justify-center">
                        {p.image ? (
                          <img
                            src={p.image}
                            alt={p.name}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                        ) : (
                          <span className="text-2xl font-black text-slate-600">
                            {p.name.substring(0, 2).toUpperCase()}
                          </span>
                        )}

                        {/* Stock Badge overlay */}
                        <div className="absolute top-1.5 right-1.5">
                          <span
                            className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded shadow ${
                              isOutOfStock
                                ? 'bg-rose-600 text-white'
                                : isLowStock
                                ? 'bg-amber-500 text-slate-950 font-black'
                                : 'bg-slate-900/90 text-slate-300 backdrop-blur-sm'
                            }`}
                          >
                            {p.qty} en stock
                          </span>
                        </div>
                      </div>

                      {/* Product Name & Category */}
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          {p.category}
                        </span>
                        <h3 className="text-xs font-bold text-white line-clamp-2 leading-tight group-hover:text-blue-400 transition-colors">
                          {p.name}
                        </h3>
                      </div>

                      {/* Price Tag */}
                      <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60">
                        <span className="text-xs font-mono font-black text-sky-400">
                          {formatMoney(p.price)}
                        </span>
                        <div className="w-6 h-6 rounded-lg bg-blue-600/20 text-blue-400 group-hover:bg-blue-600 group-hover:text-white flex items-center justify-center transition-all">
                          <Plus className="w-3.5 h-3.5" />
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Integrated Calculator Docked without modal popup */}
          {isCalculatorVisible && (
            <div className="hidden lg:block shrink-0">
              <EmbeddedCalculator onClose={() => setIsCalculatorVisible(false)} />
            </div>
          )}
        </div>
      </div>

      {/* RIGHT SECTION: Cart Drawer & Checkout Panel */}
      <div className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col shrink-0">
        {/* Cart Header */}
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-white text-base">Panier de Vente</h2>
              <span className="px-2 py-0.5 rounded-full bg-blue-600/20 text-blue-400 text-xs font-extrabold">
                {cart.reduce((a, b) => a + b.qty, 0)} articles
              </span>
            </div>
            {cart.length > 0 && (
              <button
                onClick={clearCart}
                className="text-xs font-semibold text-rose-400 hover:text-rose-300 transition-colors cursor-pointer"
              >
                Vider
              </button>
            )}
          </div>

          {/* Customer Assignment Dropdown */}
          <div className="flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={selectedCustomer}
              onChange={(e) => setSelectedCustomer(e.target.value)}
              className="flex-1 bg-slate-800 text-xs text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500 font-medium"
            >
              <option value="">Client de passage (Anonyme)</option>
              {clients.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.name} ({c.loyalty_points} pts)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Cart Items Scroll List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2 text-center p-6">
              <Barcode className="w-10 h-10 opacity-30" />
              <p className="text-sm font-semibold">Le panier est vide.</p>
              <p className="text-xs text-slate-400">
                Cliquez sur un article ou scannez un code-barres pour démarrer la vente.
              </p>
            </div>
          ) : (
            cart.map((item) => (
              <div
                key={item.id}
                className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3 flex items-center justify-between gap-3 group"
              >
                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-bold text-white truncate">{item.name}</h4>
                  <div className="text-[11px] font-mono text-slate-400">
                    {formatMoney(item.price)} × {item.qty}
                  </div>
                </div>

                {/* Stepper +/- */}
                <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg p-1 shrink-0">
                  <button
                    onClick={() => updateCartQty(item.id, item.qty - 1)}
                    className="w-5 h-5 rounded hover:bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer transition-colors"
                  >
                    <Minus className="w-3 h-3" />
                  </button>
                  <span className="w-6 text-center text-xs font-mono font-bold text-white">
                    {item.qty}
                  </span>
                  <button
                    onClick={() => updateCartQty(item.id, item.qty + 1)}
                    className="w-5 h-5 rounded hover:bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                </div>

                {/* Item Line Total & Delete */}
                <div className="text-right shrink-0">
                  <div className="text-xs font-mono font-bold text-sky-400">
                    {formatMoney(item.price * item.qty)}
                  </div>
                  <button
                    onClick={() => removeFromCart(item.id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition-opacity cursor-pointer"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Cart Calculation Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/90 space-y-3">
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center justify-between text-slate-400">
              <span>Sous-total HT</span>
              <span className="font-mono text-slate-200">{formatMoney(subtotal)}</span>
            </div>

            {discountPercent > 0 && (
              <div className="flex items-center justify-between text-amber-400">
                <span>Remise ({discountPercent}%)</span>
                <span className="font-mono">-{formatMoney(discountAmount)}</span>
              </div>
            )}

            {taxPercent > 0 && (
              <div className="flex items-center justify-between text-slate-400">
                <span>TVA ({taxPercent}%)</span>
                <span className="font-mono text-slate-200">+{formatMoney(taxAmount)}</span>
              </div>
            )}

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <span className="text-sm font-bold text-white">NET À PAYER</span>
              <span className="text-xl font-black font-mono text-sky-400">
                {formatMoney(totalNet)}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-2 pt-1">
            <button
              onClick={handleOpenCheckout}
              disabled={cart.length === 0}
              className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all cursor-pointer ${
                cart.length === 0
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30'
              }`}
            >
              <CheckCircle className="w-5 h-5" />
              <span>ENCAISSER (F9)</span>
            </button>
          </div>
        </div>
      </div>

      {/* MODAL: PAIEMENT & ENCAISSEMENT (CASH & MOBILE MONEY DU CONGO BRAZZAVILLE) */}
      {isCheckoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Règlement de la Vente</h3>
                <p className="text-xs text-slate-400">
                  Caissier : <strong className="text-white">{currentUser?.fullName || settings.cashier}</strong>
                </p>
              </div>
              <button
                onClick={() => setIsCheckoutModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-5">
              {/* Total to pay display */}
              <div className="p-4 rounded-2xl bg-blue-950/40 border border-blue-900/60 text-center">
                <span className="text-xs font-bold uppercase tracking-wider text-sky-300">
                  Total Net à Encaisser
                </span>
                <div className="text-3xl font-black text-white font-mono mt-1">
                  {formatMoney(totalNet)}
                </div>
              </div>

              {/* Mode de règlement: Espèces OU Mobile Money Congo Brazzaville (MTN / Airtel) */}
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-2">
                  Mode de règlement
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setPaymentMethod('CASH');
                      setAmountReceived(totalNet);
                    }}
                    className={`p-3 rounded-xl text-xs font-bold flex flex-col items-center gap-1.5 border transition-all cursor-pointer ${
                      paymentMethod === 'CASH'
                        ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-600/30'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <Banknote className="w-5 h-5" />
                    <span>Espèces (Cash)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setPaymentMethod('MOMO_CONGO');
                      setAmountReceived(totalNet);
                    }}
                    className={`p-3 rounded-xl text-xs font-bold flex flex-col items-center gap-1.5 border transition-all cursor-pointer ${
                      paymentMethod === 'MOMO_CONGO'
                        ? 'bg-amber-600 text-white border-amber-500 shadow-md shadow-amber-600/30'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <Smartphone className="w-5 h-5" />
                    <span>MTN MoMo (*105#)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setPaymentMethod('AIRTEL_CONGO');
                      setAmountReceived(totalNet);
                    }}
                    className={`p-3 rounded-xl text-xs font-bold flex flex-col items-center gap-1.5 border transition-all cursor-pointer ${
                      paymentMethod === 'AIRTEL_CONGO'
                        ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-600/30'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <Smartphone className="w-5 h-5" />
                    <span>Airtel Money (*128#)</span>
                  </button>
                </div>
              </div>

              {/* Mode Espèces (Cash) */}
              {paymentMethod === 'CASH' ? (
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-bold text-slate-300 block mb-1">
                      Montant reçu du client ({settings.currency})
                    </label>
                    <input
                      type="number"
                      value={amountReceived || ''}
                      onChange={(e) => setAmountReceived(parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-2xl font-mono font-bold text-white text-center focus:outline-none focus:border-blue-500"
                      autoFocus
                    />
                  </div>

                  {/* Banknotes shortcuts FCFA */}
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setAmountReceived(totalNet)}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-sky-300 border border-slate-700 cursor-pointer"
                    >
                      Compte Exact
                    </button>
                    {cashBills.map((bill) => (
                      <button
                        key={bill}
                        type="button"
                        onClick={() => setAmountReceived(bill)}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono font-bold text-slate-200 border border-slate-700 cursor-pointer"
                      >
                        {bill.toLocaleString()}
                      </button>
                    ))}
                  </div>

                  {/* Change due result */}
                  <div
                    className={`p-3.5 rounded-xl border flex items-center justify-between ${
                      changeDue >= 0
                        ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
                        : 'bg-rose-950/40 border-rose-800/60 text-rose-300'
                    }`}
                  >
                    <span className="text-xs font-bold">
                      {changeDue >= 0 ? 'Monnaie à rendre au client :' : 'Montant insuffisant :'}
                    </span>
                    <span className="text-xl font-mono font-black">
                      {formatMoney(Math.abs(changeDue))}
                    </span>
                  </div>
                </div>
              ) : (
                /* Mobile Money Congo Brazzaville Details */
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="text-xs font-bold text-slate-200 flex items-center gap-2">
                    <Smartphone className="w-4 h-4 text-sky-400" />
                    <span>
                      Paiement {paymentMethod === 'MOMO_CONGO' ? 'MTN MoMo Congo (*105#)' : 'Airtel Money Congo (*128#)'}
                    </span>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-slate-400 block mb-1">
                      Numéro Congo du client (ex: 06 / 05...)
                    </label>
                    <input
                      type="text"
                      value={momoPhone}
                      onChange={(e) => setMomoPhone(e.target.value)}
                      placeholder="+242 06 000 00 00"
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-slate-400 block mb-1">
                      Référence Transaction / ID SMS reçu
                    </label>
                    <input
                      type="text"
                      value={momoRef}
                      onChange={(e) => setMomoRef(e.target.value)}
                      placeholder="Ex : TXN-892418"
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => setIsCheckoutModalOpen(false)}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all cursor-pointer"
              >
                Annuler
              </button>

              <button
                type="button"
                onClick={handleConfirmPayment}
                className="flex-1 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-black text-sm shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <CheckCircle className="w-5 h-5" />
                <span>VALIDER & IMPRIMER TICKET</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
