import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Plus, Search, MoreVertical, Edit2, Trash2, X, Mail, Phone, MapPin, Building2 } from "lucide-react";
import { z } from "zod";

const clientSchema = z.object({
  nom: z.string().min(2, "Nom requis"),
  entreprise: z.string().optional(),
  email: z.string().email("Email invalide"),
  telephone: z.string().optional(),
  adresse: z.string().optional(),
});

type Client = z.infer<typeof clientSchema> & { id: number };

export default function Clients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<Partial<Client>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = () => {
    fetch("/api/clients").then(res => res.json()).then(setClients);
  };

  const filteredClients = clients.filter(c => 
    c.nom.toLowerCase().includes(search.toLowerCase()) || 
    (c.entreprise && c.entreprise.toLowerCase().includes(search.toLowerCase()))
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = clientSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        const path = issue.path[0] as string;
        fieldErrors[path] = issue.message;
      });
      setErrors(fieldErrors);
      return;
    }

    const url = editingClient ? `/api/clients/${editingClient.id}` : "/api/clients";
    const method = editingClient ? "PUT" : "POST";

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    setIsModalOpen(false);
    setEditingClient(null);
    setFormData({});
    setErrors({});
    fetchClients();
  };

  const handleDelete = async (id: number) => {
    if (confirm("Êtes-vous sûr de vouloir supprimer ce client ?")) {
      await fetch(`/api/clients/${id}`, { method: "DELETE" });
      fetchClients();
    }
  };

  const openEdit = (client: Client) => {
    setEditingClient(client);
    setFormData(client);
    setIsModalOpen(true);
  };

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
            placeholder="Rechercher un client..." 
            value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2.5 bg-white rounded-xl border-none shadow-soft focus:ring-2 focus:ring-accent/20 outline-none w-full transition-all"
          />
        </div>
        <button 
          onClick={() => { setIsModalOpen(true); setEditingClient(null); setFormData({}); }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          <span>Nouveau Client</span>
        </button>
      </div>

      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Client</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Contact</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Entreprise</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filteredClients.map((client) => (
                <tr key={client.id} className="hover:bg-slate-50 transition-all group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold">
                        {client.nom.charAt(0)}
                      </div>
                      <span className="font-semibold text-slate-800">{client.nom}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm text-slate-600">
                        <Mail size={14} className="text-slate-400" />
                        {client.email}
                      </div>
                      {client.telephone && (
                        <div className="flex items-center gap-2 text-sm text-slate-600">
                          <Phone size={14} className="text-slate-400" />
                          {client.telephone}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Building2 size={14} className="text-slate-400" />
                      {client.entreprise || "-"}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={() => openEdit(client)}
                        className="p-2 text-slate-400 hover:text-accent hover:bg-accent/10 rounded-lg transition-all"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button 
                        onClick={() => handleDelete(client.id)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredClients.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-slate-400 italic">
                    Aucun client trouvé
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden"
            >
              <div className="flex items-center justify-between p-6 border-b border-slate-100">
                <h3 className="text-xl font-bold text-slate-800">
                  {editingClient ? "Modifier le Client" : "Nouveau Client"}
                </h3>
                <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Nom Complet</label>
                    <input 
                      type="text" 
                      value={formData.nom || ""}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, nom: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                      placeholder="Jean Dupont"
                    />
                    {errors.nom && <p className="text-xs text-red-500">{errors.nom}</p>}
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Entreprise</label>
                    <input 
                      type="text" 
                      value={formData.entreprise || ""}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, entreprise: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                      placeholder="Studio Alpha"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Email</label>
                  <input 
                    type="email" 
                    value={formData.email || ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    placeholder="jean@alpha.com"
                  />
                  {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Téléphone</label>
                  <input 
                    type="tel" 
                    value={formData.telephone || ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, telephone: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    placeholder="01 23 45 67 89"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Adresse</label>
                  <textarea 
                    value={formData.adresse || ""}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({ ...formData, adresse: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all min-h-[100px]"
                    placeholder="123 Rue de Rivoli, Paris"
                  />
                </div>
                <div className="pt-4 flex gap-3">
                  <button 
                    type="button" 
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 px-4 py-2.5 bg-slate-100 text-slate-600 rounded-xl font-medium hover:bg-slate-200 transition-all"
                  >
                    Annuler
                  </button>
                  <button 
                    type="submit" 
                    className="flex-1 btn-primary"
                  >
                    {editingClient ? "Enregistrer" : "Créer le Client"}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
