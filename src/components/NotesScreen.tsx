import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { BookOpen, Plus, Trash2, Clock, User, X } from 'lucide-react';

export const NotesScreen: React.FC = () => {
  const { notes, addNote, deleteNote, settings } = usePOS();
  const [newNoteText, setNewNoteText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim()) return;
    addNote(newNoteText);
    setNewNoteText('');
    setIsModalOpen(false);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            Carnet de Caisse & Notes d’Équipe
          </h1>
          <p className="text-sm text-slate-400">
            Consignes de shift, incidents, arrivages fournisseurs et rappels internes.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Nouvelle Note</span>
        </button>
      </div>

      {/* Notes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {notes.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-500">
            <BookOpen className="w-12 h-12 mx-auto mb-2 opacity-30" />
            <p className="text-sm font-semibold">Aucune note enregistrée dans le carnet.</p>
          </div>
        ) : (
          notes.map((n) => (
            <div
              key={n.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg relative group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-1.5 font-mono text-[11px]">
                    <Clock className="w-3.5 h-3.5 text-sky-400" />
                    <span>{n.date} à {n.time}</span>
                  </div>
                  <button
                    onClick={() => deleteNote(n.id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition-opacity p-1"
                    title="Supprimer la note"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
                  {n.note}
                </p>
              </div>

              <div className="mt-4 pt-2 border-t border-slate-800/60 flex items-center gap-1.5 text-xs text-slate-400">
                <User className="w-3.5 h-3.5 text-blue-400" />
                <span>Rédigé par : <strong className="text-slate-300">{n.author || 'Caissier'}</strong></span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Note Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-base font-bold text-white">Ajouter une Note au Carnet</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAdd} className="p-6 space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Message ou consigne *
                </label>
                <textarea
                  rows={4}
                  required
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  placeholder="Écrivez ici votre message pour les prochains caissiers ou la direction..."
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs leading-relaxed focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 cursor-pointer"
                >
                  Publier la note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
