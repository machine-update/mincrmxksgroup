import React, { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Plus, Search, FileText, ChevronRight, Download, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";

interface Quote {
  id: number;
  client_nom: string;
  statut: string;
  total: number;
  created_at: string;
}

export default function Quotes() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/devis").then(res => res.json()).then(setQuotes);
  }, []);

  const filteredQuotes = quotes.filter(q => 
    (q.client_nom && q.client_nom.toLowerCase().includes(search.toLowerCase())) || 
    q.id.toString().includes(search)
  );

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Rechercher un devis..." 
            value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2.5 bg-white rounded-xl border-none shadow-soft focus:ring-2 focus:ring-accent/20 outline-none w-full transition-all"
          />
        </div>
        <Link 
          to="/quotes/new"
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          <span>Nouveau Devis</span>
        </Link>
      </div>

      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">N° Devis</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Client</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Date</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Total</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Statut</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filteredQuotes.map((quote) => (
                <tr key={quote.id} className="hover:bg-slate-50 transition-all group">
                  <td className="px-6 py-4 font-mono text-sm text-slate-500">
                    #DEV-{quote.id.toString().padStart(4, '0')}
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-semibold text-slate-800">{quote.client_nom}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    {new Date(quote.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-800">
                    {quote.total.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      quote.statut === 'Accepté' ? 'bg-emerald-50 text-emerald-600' :
                      quote.statut === 'Refusé' ? 'bg-red-50 text-red-600' :
                      'bg-blue-50 text-blue-600'
                    }`}>
                      {quote.statut}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Link 
                        to={`/quotes/edit/${quote.id}`}
                        className="p-2 text-slate-400 hover:text-accent hover:bg-accent/10 rounded-lg transition-all"
                      >
                        <ExternalLink size={16} />
                      </Link>
                      <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-all">
                        <Download size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredQuotes.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400 italic">
                    Aucun devis trouvé
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
