import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { Delete, X } from 'lucide-react';

export const EmbeddedCalculator: React.FC<{ onClose?: () => void }> = ({ onClose }) => {
  const [display, setDisplay] = useState('0');
  const [equation, setEquation] = useState('');

  const handleKey = (char: string) => {
    if (char === 'C') {
      setDisplay('0');
      setEquation('');
      return;
    }

    if (char === 'DEL') {
      if (display.length <= 1) {
        setDisplay('0');
      } else {
        setDisplay(display.slice(0, -1));
      }
      return;
    }

    if (char === '=') {
      try {
        const fullExpr = equation + display;
        const sanitized = fullExpr.replace(/[^0-9+\-*/.]/g, '');
        const result = Function(`'use strict'; return (${sanitized})`)();
        const formatted = String(Math.round(result * 10000) / 10000);
        setDisplay(formatted);
        setEquation('');
      } catch {
        setDisplay('Erreur');
        setEquation('');
      }
      return;
    }

    if (['+', '-', '*', '/'].includes(char)) {
      setEquation((prev) => prev + display + ` ${char} `);
      setDisplay('0');
      return;
    }

    if (char === '.') {
      if (!display.includes('.')) {
        setDisplay((prev) => prev + '.');
      }
      return;
    }

    if (display === '0' || display === 'Erreur') {
      setDisplay(char);
    } else {
      setDisplay((prev) => prev + char);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl flex flex-col shrink-0 select-none w-72">
      <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
        <span className="text-xs font-bold text-white uppercase tracking-wider">Calculatrice Caisse</span>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-md"
            title="Masquer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Screen display */}
      <div className="p-3 bg-slate-950 border-b border-slate-800 text-right">
        <div className="text-[10px] font-mono text-slate-500 h-3.5 truncate">
          {equation}
        </div>
        <div className="text-2xl font-black font-mono text-white tracking-tight truncate mt-0.5">
          {display}
        </div>
      </div>

      {/* Grid keys */}
      <div className="p-2.5 grid grid-cols-4 gap-1 bg-slate-900 text-xs">
        {['C', 'DEL', '/', '*'].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => handleKey(k)}
            className="h-9 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 font-black flex items-center justify-center cursor-pointer transition-all active:scale-95"
          >
            {k === 'DEL' ? <Delete className="w-3.5 h-3.5" /> : k}
          </button>
        ))}

        {['7', '8', '9', '-'].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => handleKey(k)}
            className={`h-9 rounded-lg font-bold flex items-center justify-center cursor-pointer transition-all active:scale-95 ${
              k === '-' ? 'bg-slate-800 text-sky-400 font-black' : 'bg-slate-950 text-white hover:bg-slate-800'
            }`}
          >
            {k}
          </button>
        ))}

        {['4', '5', '6', '+'].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => handleKey(k)}
            className={`h-9 rounded-lg font-bold flex items-center justify-center cursor-pointer transition-all active:scale-95 ${
              k === '+' ? 'bg-slate-800 text-sky-400 font-black' : 'bg-slate-950 text-white hover:bg-slate-800'
            }`}
          >
            {k}
          </button>
        ))}

        {['1', '2', '3', '='].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => handleKey(k)}
            className={`h-9 rounded-lg font-bold flex items-center justify-center cursor-pointer transition-all active:scale-95 ${
              k === '=' ? 'row-span-2 h-[76px] bg-blue-600 hover:bg-blue-500 text-white font-black' : 'bg-slate-950 text-white hover:bg-slate-800'
            }`}
          >
            {k}
          </button>
        ))}

        {['0', '.'].map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => handleKey(k)}
            className={`h-9 rounded-lg font-bold flex items-center justify-center cursor-pointer transition-all active:scale-95 ${
              k === '0' ? 'col-span-2 bg-slate-950 text-white hover:bg-slate-800' : 'bg-slate-950 text-white hover:bg-slate-800'
            }`}
          >
            {k}
          </button>
        ))}
      </div>
    </div>
  );
};
