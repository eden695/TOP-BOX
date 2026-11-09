import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { Printer, X, FileText, CheckCircle2, Copy, Download, Check } from 'lucide-react';

export const ReceiptModal: React.FC = () => {
  const { selectedReceipt, setSelectedReceipt, settings, formatMoney } = usePOS();
  const [printFormat, setPrintFormat] = useState<'80MM' | 'A4'>('80MM');
  const [copied, setCopied] = useState(false);
  const [printFeedback, setPrintFeedback] = useState('');

  if (!selectedReceipt) return null;

  const buildPlainText = () => {
    const cur = settings.currency || 'FCFA';
    const lines: string[] = [
      '==========================================',
      `   ${settings.company || 'TOP-BOX'}`.padStart(28),
      `   ${settings.header || 'SUPERMARCHÉ & CAISSE'}`.padStart(30),
      settings.address ? `   ${settings.address}` : '',
      settings.phone ? `   Tél: ${settings.phone}` : '',
      '==========================================',
      `Facture  : ${selectedReceipt.invoice}`,
      `Date     : ${selectedReceipt.date}`,
      `Caisse   : ${selectedReceipt.register}`,
      `Caissier : ${selectedReceipt.cashier}`,
      selectedReceipt.customer_name ? `Client   : ${selectedReceipt.customer_name}` : '',
      `Paiement : ${
        selectedReceipt.payment_method === 'CASH'
          ? 'ESPÈCES'
          : selectedReceipt.payment_method === 'MOMO_CONGO'
          ? `MTN MoMo ${selectedReceipt.momo_phone || ''}`
          : `Airtel Money ${selectedReceipt.momo_phone || ''}`
      }`,
      selectedReceipt.momo_ref ? `Réf MoMo : ${selectedReceipt.momo_ref}` : '',
      '------------------------------------------',
      'ARTICLE               QTE       TOTAL',
      '------------------------------------------',
    ].filter(Boolean);

    selectedReceipt.items.forEach((item) => {
      const name = item.name.substring(0, 18).padEnd(19);
      const qty = String(item.qty).padStart(4);
      const tot = `${Math.round(item.total).toLocaleString('fr-FR')} ${cur}`.padStart(16);
      lines.push(`${name} ${qty} ${tot}`);
    });

    lines.push(
      '------------------------------------------',
      `Sous-total : ${formatMoney(selectedReceipt.subtotal)}`,
      selectedReceipt.discount > 0 ? `Remise     : -${formatMoney(selectedReceipt.discount)}` : '',
      selectedReceipt.tax > 0 ? `TVA        : +${formatMoney(selectedReceipt.tax)}` : '',
      `TOTAL NET  : ${formatMoney(selectedReceipt.total)}`,
      `Reçu       : ${formatMoney(selectedReceipt.received)}`,
      `Rendu      : ${formatMoney(selectedReceipt.change_amt)}`,
      '==========================================',
      `   ${settings.footer || 'Merci de votre visite !'}`.padStart(30),
      '=========================================='
    );

    return lines.filter(Boolean).join('\n');
  };

  const handleCopyText = () => {
    const text = buildPlainText();
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    const text = buildPlainText();
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Ticket_${selectedReceipt.invoice}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    setPrintFeedback("Envoi à l'imprimante...");
    const printEl = document.getElementById('printable-receipt');
    if (!printEl) {
      window.print();
      return;
    }

    try {
      const frame = document.createElement('iframe');
      frame.style.position = 'fixed';
      frame.style.right = '0';
      frame.style.bottom = '0';
      frame.style.width = '0';
      frame.style.height = '0';
      frame.style.border = '0';
      document.body.appendChild(frame);

      const doc = frame.contentWindow?.document;
      if (doc) {
        doc.open();
        doc.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>Ticket ${selectedReceipt.invoice}</title>
            <style>
              @page {
                size: ${printFormat === '80MM' ? '80mm auto' : 'A4'};
                margin: ${printFormat === '80MM' ? '2mm' : '15mm'};
              }
              body {
                font-family: ${printFormat === '80MM' ? 'monospace' : 'system-ui, sans-serif'};
                font-size: ${printFormat === '80MM' ? '12px' : '13px'};
                color: #000;
                background: #fff;
                margin: 0;
                padding: ${printFormat === '80MM' ? '2mm' : '10mm'};
              }
              * { box-sizing: border-box; }
              .barcode { display: flex; justify-content: center; gap: 2px; height: 32px; margin: 8px 0; }
              .bar { background: #000; display: inline-block; height: 100%; }
            </style>
          </head>
          <body>
            ${printEl.innerHTML}
          </body>
          </html>
        `);
        doc.close();

        setTimeout(() => {
          frame.contentWindow?.focus();
          frame.contentWindow?.print();
          setTimeout(() => {
            if (document.body.contains(frame)) {
              document.body.removeChild(frame);
            }
            setPrintFeedback('');
          }, 2000);
        }, 300);
        return;
      }
    } catch (e) {
      console.warn('Iframe print error, falling back to window.print()', e);
    }

    // Direct fallback
    window.print();
    setTimeout(() => setPrintFeedback(''), 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 select-none">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95">
        {/* Header toolbar */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <h3 className="text-base font-bold text-white">Ticket de Caisse Validé</h3>
          </div>
          <div className="flex items-center gap-2">
            {/* Format toggle: 80mm vs A4 */}
            <div className="flex items-center bg-slate-800 p-0.5 rounded-lg text-xs font-bold">
              <button
                onClick={() => setPrintFormat('80MM')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  printFormat === '80MM' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                80 mm
              </button>
              <button
                onClick={() => setPrintFormat('A4')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  printFormat === 'A4' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                A4
              </button>
            </div>
            <button
              onClick={() => setSelectedReceipt(null)}
              className="text-slate-400 hover:text-white p-1 rounded-lg ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Receipt Body */}
        <div className="flex-1 overflow-y-auto p-6 flex justify-center bg-slate-950/60">
          {printFormat === '80MM' ? (
            /* 80mm Realistic Thermal Receipt */
            <div
              id="printable-receipt"
              className="w-full max-w-[340px] bg-white text-slate-900 p-6 rounded-md shadow-2xl font-mono text-xs border border-slate-300 relative select-text"
            >
              {/* Receipt Header */}
              <div className="text-center space-y-1 mb-4 border-b border-dashed border-slate-400 pb-3">
                <h2 className="text-base font-extrabold tracking-tight uppercase">
                  {settings.company}
                </h2>
                <p className="text-[11px] text-slate-600">{settings.header}</p>
                {settings.address && <p className="text-[10px] text-slate-600">{settings.address}</p>}
                {settings.phone && <p className="text-[10px] text-slate-600">Tél : {settings.phone}</p>}
                <div className="pt-2 text-[10px] text-slate-500 flex justify-between">
                  <span>Facture : <strong>{selectedReceipt.invoice}</strong></span>
                  <span>{selectedReceipt.date.substring(0, 10)}</span>
                </div>
                <div className="text-[10px] text-slate-500 flex justify-between">
                  <span>Caisse : {selectedReceipt.register}</span>
                  <span>{selectedReceipt.date.substring(11, 16)}</span>
                </div>
                <div className="text-[10px] text-slate-500 text-left">
                  Caissier : {selectedReceipt.cashier}
                </div>
                {selectedReceipt.customer_name && (
                  <div className="text-[10px] text-slate-700 text-left font-bold">
                    Client : {selectedReceipt.customer_name}
                  </div>
                )}
              </div>

              {/* Items Table */}
              <div className="space-y-1.5 mb-4 border-b border-dashed border-slate-400 pb-3 text-[11px]">
                <div className="flex justify-between font-bold border-b border-slate-300 pb-1 text-[10px] uppercase">
                  <span>Article</span>
                  <span className="text-right">Qté × PU</span>
                  <span className="text-right">Total</span>
                </div>
                {selectedReceipt.items.map((it, idx) => (
                  <div key={idx} className="flex justify-between items-start text-[11px] leading-tight">
                    <span className="flex-1 pr-2 truncate">{it.name}</span>
                    <span className="text-slate-600 text-right pr-2">
                      {it.qty} × {formatMoney(it.unit_price)}
                    </span>
                    <span className="font-bold text-right shrink-0">
                      {formatMoney(it.total)}
                    </span>
                  </div>
                ))}
              </div>

              {/* Totals Breakdown */}
              <div className="space-y-1 text-[11px] mb-4 border-b border-dashed border-slate-400 pb-3">
                <div className="flex justify-between text-slate-600">
                  <span>Sous-total HT :</span>
                  <span>{formatMoney(selectedReceipt.subtotal)}</span>
                </div>
                {selectedReceipt.discount > 0 && (
                  <div className="flex justify-between text-slate-700 font-semibold">
                    <span>Remise accordée :</span>
                    <span>-{formatMoney(selectedReceipt.discount)}</span>
                  </div>
                )}
                {selectedReceipt.tax > 0 && (
                  <div className="flex justify-between text-slate-600">
                    <span>TVA ({selectedReceipt.tax_rate}%) :</span>
                    <span>+{formatMoney(selectedReceipt.tax)}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm font-extrabold pt-1.5 border-t border-slate-800 text-black">
                  <span>TOTAL NET :</span>
                  <span>{formatMoney(selectedReceipt.total)}</span>
                </div>
                <div className="flex justify-between text-[11px] text-slate-700 pt-1">
                  <span>Montant Reçu :</span>
                  <span>{formatMoney(selectedReceipt.received)}</span>
                </div>
                <div className="flex justify-between text-xs font-bold text-slate-900">
                  <span>Monnaie Rendue :</span>
                  <span>{formatMoney(selectedReceipt.change_amt)}</span>
                </div>
                <div className="flex justify-between text-[10px] text-slate-700 pt-1">
                  <span>Règlement :</span>
                  <span className="font-bold">
                    {selectedReceipt.payment_method === 'CASH'
                      ? 'Espèces'
                      : selectedReceipt.payment_method === 'MOMO_CONGO'
                      ? 'MTN MoMo (*105#)'
                      : 'Airtel Money (*128#)'}
                  </span>
                </div>
                {selectedReceipt.momo_phone && (
                  <div className="text-[9px] text-slate-500 text-right">
                    Tél : {selectedReceipt.momo_phone} {selectedReceipt.momo_ref ? `(Réf: ${selectedReceipt.momo_ref})` : ''}
                  </div>
                )}
              </div>

              {/* Barcode & Footer */}
              <div className="text-center space-y-2">
                {/* Simulated Barcode */}
                <div className="py-1 flex justify-center">
                  <div className="flex items-center gap-[2px] h-8">
                    {[3, 1, 2, 1, 4, 1, 2, 3, 1, 3, 2, 1, 1, 4, 2, 1, 3, 1, 2, 4, 1, 2].map((w, i) => (
                      <span key={i} style={{ width: `${w}px` }} className="h-full bg-slate-900 inline-block" />
                    ))}
                  </div>
                </div>
                <p className="text-[10px] tracking-widest font-mono text-slate-600">
                  *{selectedReceipt.invoice}*
                </p>
                <p className="text-[10px] text-slate-600 pt-1 leading-snug">
                  {settings.footer}
                </p>
              </div>
            </div>
          ) : (
            /* A4 Formal Invoice Format */
            <div
              id="printable-receipt"
              className="w-full bg-white text-slate-900 p-8 rounded-md shadow-2xl font-sans text-xs border border-slate-300 select-text"
            >
              <div className="flex justify-between items-start border-b border-slate-300 pb-4 mb-6">
                <div>
                  <h1 className="text-xl font-black uppercase text-blue-900">{settings.company}</h1>
                  <p className="text-xs text-slate-600 font-medium">{settings.header}</p>
                  <p className="text-xs text-slate-600">{settings.address}</p>
                  <p className="text-xs text-slate-600">Tél : {settings.phone} • {settings.email}</p>
                </div>
                <div className="text-right">
                  <h2 className="text-lg font-bold text-slate-900">FACTURE DE VENTE</h2>
                  <p className="text-sm font-mono font-bold text-blue-600">{selectedReceipt.invoice}</p>
                  <p className="text-xs text-slate-600">Date : {selectedReceipt.date}</p>
                  <p className="text-xs text-slate-600">Caisse : {selectedReceipt.register}</p>
                </div>
              </div>

              {selectedReceipt.customer_name && (
                <div className="mb-6 p-3 rounded bg-slate-100 border border-slate-200">
                  <span className="text-[10px] font-bold uppercase text-slate-500">Facturé à :</span>
                  <p className="text-sm font-bold text-slate-900">{selectedReceipt.customer_name}</p>
                </div>
              )}

              <table className="w-full text-left mb-6 border border-slate-200">
                <thead className="bg-slate-100 text-[11px] font-bold text-slate-700">
                  <tr>
                    <th className="p-2 border-b">Désignation</th>
                    <th className="p-2 border-b text-center">Quantité</th>
                    <th className="p-2 border-b text-right">Prix Unitaire</th>
                    <th className="p-2 border-b text-right">Total HT</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-xs">
                  {selectedReceipt.items.map((it, i) => (
                    <tr key={i}>
                      <td className="p-2 font-medium">{it.name}</td>
                      <td className="p-2 text-center">{it.qty}</td>
                      <td className="p-2 text-right font-mono">{formatMoney(it.unit_price)}</td>
                      <td className="p-2 text-right font-mono font-bold">{formatMoney(it.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="flex justify-end mb-6">
                <div className="w-64 space-y-1.5 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Sous-total HT :</span>
                    <span className="font-mono">{formatMoney(selectedReceipt.subtotal)}</span>
                  </div>
                  {selectedReceipt.discount > 0 && (
                    <div className="flex justify-between text-emerald-600 font-semibold">
                      <span>Remise :</span>
                      <span className="font-mono">-{formatMoney(selectedReceipt.discount)}</span>
                    </div>
                  )}
                  {selectedReceipt.tax > 0 && (
                    <div className="flex justify-between text-slate-600">
                      <span>TVA ({selectedReceipt.tax_rate}%) :</span>
                      <span className="font-mono">+{formatMoney(selectedReceipt.tax)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm font-bold pt-2 border-t border-slate-400">
                    <span>TOTAL TTC :</span>
                    <span className="font-mono text-blue-900">{formatMoney(selectedReceipt.total)}</span>
                  </div>
                </div>
              </div>

              <div className="text-center text-[10px] text-slate-500 border-t border-slate-200 pt-4">
                {settings.footer}
              </div>
            </div>
          )}
        </div>

        {/* Action bar */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => setSelectedReceipt(null)}
              className="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all cursor-pointer"
            >
              Fermer
            </button>
            <button
              onClick={handleCopyText}
              className="flex-1 sm:flex-initial px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              title="Copier le texte du ticket"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-sky-400" />}
              <span>{copied ? 'Copié !' : 'Copier'}</span>
            </button>
            <button
              onClick={handleDownloadTxt}
              className="flex-1 sm:flex-initial px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              title="Télécharger le ticket au format .txt"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span>Télécharger (.txt)</span>
            </button>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {printFeedback && (
              <span className="text-xs text-emerald-400 font-semibold animate-pulse hidden md:inline">
                {printFeedback}
              </span>
            )}
            <button
              onClick={handlePrint}
              className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
            >
              <Printer className="w-4 h-4" />
              <span>Imprimer ({printFormat})</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
