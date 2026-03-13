import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Plus, Search, MoreVertical, Edit2, Trash2, X, Briefcase, Calendar, User, Tag } from "lucide-react";

interface Project {
  id: number;
  nom: string;
  client_id: number;
  client_nom: string;
  type: string;
  statut: string;
  date_debut: string;
  date_fin: string;
}

interface Client {
  id: number;
  nom: string;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<Project>>({
    type: "Clip",
    statut: "En attente"
  });

  useEffect(() => {
    fetchProjects();
    fetch("/api/clients").then(res => res.json()).then(setClients);
  }, []);

  const fetchProjects = () => {
    fetch("/api/projets").then(res => res.json()).then(setProjects);
  };

  const filteredProjects = projects.filter(p => 
    p.nom.toLowerCase().includes(search.toLowerCase()) || 
    (p.client_nom && p.client_nom.toLowerCase().includes(search.toLowerCase()))
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch("/api/projets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    setIsModalOpen(false);
    setFormData({ type: "Clip", statut: "En attente" });
    fetchProjects();
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
            placeholder="Rechercher un projet..." 
            value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2.5 bg-white rounded-xl border-none shadow-soft focus:ring-2 focus:ring-accent/20 outline-none w-full transition-all"
          />
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          <span>Nouveau Projet</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <motion.div 
            key={project.id}
            layout
            className="card group hover:scale-[1.02] transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                project.type === 'Clip' ? 'bg-purple-50 text-purple-600' :
                project.type === 'Spectacle' ? 'bg-blue-50 text-blue-600' :
                'bg-amber-50 text-amber-600'
              }`}>
                <Briefcase size={24} />
              </div>
              <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                project.statut === 'Terminé' ? 'bg-emerald-50 text-emerald-600' :
                project.statut === 'En cours' ? 'bg-amber-50 text-amber-600' :
                'bg-slate-100 text-slate-500'
              }`}>
                {project.statut}
              </span>
            </div>
            
            <h3 className="text-lg font-bold text-slate-800 mb-1">{project.nom}</h3>
            <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
              <User size={14} />
              <span>{project.client_nom}</span>
            </div>

            <div className="space-y-3 pt-4 border-t border-slate-50">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-slate-400">
                  <Tag size={14} />
                  <span>Type</span>
                </div>
                <span className="font-semibold text-slate-700">{project.type}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-slate-400">
                  <Calendar size={14} />
                  <span>Début</span>
                </div>
                <span className="font-semibold text-slate-700">{project.date_debut}</span>
              </div>
            </div>
          </motion.div>
        ))}
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
                <h3 className="text-xl font-bold text-slate-800">Nouveau Projet</h3>
                <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Nom du Projet</label>
                  <input 
                    type="text" 
                    required
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, nom: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    placeholder="Clip Musical - Summer"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Client</label>
                  <select 
                    required
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFormData({ ...formData, client_id: parseInt(e.target.value) })}
                    className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                  >
                    <option value="">Sélectionner un client</option>
                    {clients.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Type</label>
                    <select 
                      value={formData.type}
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    >
                      <option value="Clip">Clip</option>
                      <option value="Spectacle">Spectacle</option>
                      <option value="Documentaire">Documentaire</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Statut</label>
                    <select 
                      value={formData.statut}
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFormData({ ...formData, statut: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    >
                      <option value="En attente">En attente</option>
                      <option value="En cours">En cours</option>
                      <option value="Terminé">Terminé</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Date Début</label>
                    <input 
                      type="date" 
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, date_debut: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Date Fin</label>
                    <input 
                      type="date" 
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, date_fin: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 rounded-xl border-none focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                    />
                  </div>
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
                    Créer le Projet
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
