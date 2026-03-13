import React, { useState, useEffect, useMemo } from "react";
import { motion } from "motion/react";
import { Plus, Trash2, Save, ArrowLeft, Calculator, User, FileText } from "lucide-react";
import { useNavigate, useParams, Link } from "react-router-dom";

interface Client {
  id: number;
  nom: string;
  entreprise: string;
}

interface QuoteItem {
  id?: number;
  description: string;
  quantite: number;
  prix_unitaire: number;
}

export default function QuoteEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [clientId, setClientId] = useState<string>("");
  const [statut, setStatut] = useState("Envoyé");
  const [items, setItems] = useState<QuoteItem[]>([
    { description: "", quantite: 1, prix_unitaire: 0 }
  ]);

  useEffect(() => {
    fetch("/api/clients").then(res => res.json()).then(setClients);
    if (id) {
      fetch(`/api/devis/${id}`).then(res => res.json()).then(data => {
        setClientId(data.client_id.toString());
        setStatut(data.statut);
        setItems(data.items);
      });
    }
  }, [id]);

  const addItem = () => {
    setItems([...items, { description: "", quantite: 1, prix_unitaire: 0 }]);
  };

  const removeItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const updateItem = (index: number, field: keyof QuoteItem, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const total = useMemo(() => {
    return items.reduce((acc, item) => acc + (item.quantite * item.prix_unitaire), 0);
  }, [items]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId) return alert("Veuillez sélectionner un client");
    
    const payload = {
      client_id: parseInt(clientId),
      statut,
      items
    };

    const url = id ? `/api/devis/${id}` : "/api/devis";
    const method = id ? "PUT" : "POST";

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    navigate("/quotes");
  };

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-5xl mx-auto space-y-8"
    >
      <div className="flex items-center justify-between">
        <Link to="/quotes" className="flex items-center gap-2 text-slate-400 hover:text-accent transition-all">
          <ArrowLeft size={20} />
          <span className="font-medium">Retour aux devis</span>
        </Link>
        <div className="flex items-center gap-3">
          <select 
            value={statut}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setStatut(e.target.value)}
            className="px-4 py-2 bg-white rounded-xl border-none shadow-soft focus:ring-2 focus:ring-accent/20 outline-none text-sm font-bold uppercase tracking-wider"
          >
            <option value="Envoyé">Envoyé</option>
            <option value="Accepté">Accepté</option>
            <option value="Refusé">Refusé</option>
          </select>
          <button 
            onClick={handleSubmit}
            className="btn-primary flex items-center gap-2"
          >
            <Save size={18} />
            <span>Enregistrer</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Client & Info */}
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center">
                <User size={20} />
              </div>
              <h3 className="text-lg font-semibold text-slate-800">Informations Client</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sélectionner un Client</label>
                <select 
                  value={clientId}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setClientId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                >
                  <option value="">Choisir un client...</option>
                  {clients.map(c => <option key={c.id} value={c.id}>{c.nom} ({c.entreprise})</option>)}
                </select>
              </div>
              {clientId && (
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                  <p className="text-sm font-semibold text-slate-800">
                    {clients.find(c => c.id === parseInt(clientId))?.nom}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {clients.find(c => c.id === parseInt(clientId))?.entreprise}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="card bg-accent text-white">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <Calculator size={20} />
              </div>
              <h3 className="text-lg font-semibold">Récapitulatif</h3>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center opacity-80">
                <span className="text-sm">Sous-total HT</span>
                <span className="font-mono">{(total * 0.8).toFixed(2)} €</span>
              </div>
              <div className="flex justify-between items-center opacity-80">
                <span className="text-sm">TVA (20%)</span>
                <span className="font-mono">{(total * 0.2).toFixed(2)} €</span>
              </div>
              <div className="pt-4 border-t border-white/20 flex justify-between items-center">
                <span className="text-lg font-bold">Total TTC</span>
                <span className="text-2xl font-bold font-mono">{total.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Items */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center">
                  <FileText size={20} />
                </div>
                <h3 className="text-lg font-semibold text-slate-800">Lignes de Prestation</h3>
              </div>
              <button 
                onClick={addItem}
                className="flex items-center gap-2 text-accent font-bold text-sm hover:bg-accent/5 px-4 py-2 rounded-xl transition-all"
              >
                <Plus size={18} />
                <span>Ajouter une ligne</span>
              </button>
            </div>

            <div className="space-y-4">
              {items.map((item, index) => (
                <motion.div 
                  key={index}
                  layout
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-12 gap-4 items-end p-4 bg-slate-50 rounded-2xl border border-slate-100 group"
                >
                  <div className="col-span-6 space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Description</label>
                    <input 
                      type="text" 
                      value={item.description}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateItem(index, "description", e.target.value)}
                      className="w-full px-4 py-2 bg-white rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all text-sm"
                      placeholder="Ex: Tournage Clip 4K"
                    />
                  </div>
                  <div className="col-span-2 space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Qté</label>
                    <input 
                      type="number" 
                      value={item.quantite}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateItem(index, "quantite", parseInt(e.target.value) || 0)}
                      className="w-full px-4 py-2 bg-white rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all text-sm font-mono"
                    />
                  </div>
                  <div className="col-span-2 space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">PU (€)</label>
                    <input 
                      type="number" 
                      value={item.prix_unitaire}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateItem(index, "prix_unitaire", parseFloat(e.target.value) || 0)}
                      className="w-full px-4 py-2 bg-white rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all text-sm font-mono"
                    />
                  </div>
                  <div className="col-span-2 flex items-center justify-between gap-2">
                    <div className="text-right flex-1">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Total</p>
                      <p className="text-sm font-bold text-slate-800 font-mono">{(item.quantite * item.prix_unitaire).toFixed(2)} €</p>
                    </div>
                    <button 
                      onClick={() => removeItem(index)}
                      className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
