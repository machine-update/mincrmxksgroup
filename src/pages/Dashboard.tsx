import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Users, Briefcase, FileText, ChevronRight } from "lucide-react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";

interface Stats {
  clients: number;
  activeProjects: number;
  sentQuotes: number;
}

interface Project {
  id: number;
  nom: string;
  client_nom: string;
  statut: string;
  date_debut: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({ clients: 0, activeProjects: 0, sentQuotes: 0 });
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    fetch("/api/stats").then(res => res.json()).then(setStats);
    fetch("/api/projets").then(res => res.json()).then(data => setProjects(data.slice(0, 5)));
  }, []);

  const statCards = [
    { label: "Clients", value: stats.clients, icon: Users, color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Projets Actifs", value: stats.activeProjects, icon: Briefcase, color: "text-indigo-600", bg: "bg-indigo-50" },
    { label: "Devis Envoyés", value: stats.sentQuotes, icon: FileText, color: "text-emerald-600", bg: "bg-emerald-50" },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-8"
    >
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statCards.map((stat, i) => (
          <motion.div 
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card flex items-center gap-6"
          >
            <div className={`w-14 h-14 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center`}>
              <stat.icon size={28} />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">{stat.label}</p>
              <h3 className="text-3xl font-bold text-slate-800 mt-1">{stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Calendar Section */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-800">Calendrier Hebdomadaire</h3>
            <button className="text-sm text-accent font-medium hover:underline">Voir tout</button>
          </div>
          <div className="calendar-container">
            {/* @ts-ignore - FullCalendar type mismatch in some environments */}
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView="timeGridWeek"
              headerToolbar={false}
              height="500px"
              slotMinTime="08:00:00"
              slotMaxTime="20:00:00"
              allDaySlot={false}
              locale="fr"
              events={projects.map(p => ({
                title: p.nom,
                start: p.date_debut,
                className: "bg-accent border-none text-white p-1 rounded text-xs"
              }))}
            />
          </div>
        </div>

        {/* Recent Projects Section */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-800">Derniers Projets</h3>
            <button className="text-sm text-accent font-medium hover:underline">Voir tout</button>
          </div>
          <div className="space-y-4">
            {projects.map((project) => (
              <div key={project.id} className="group flex items-center justify-between p-4 rounded-2xl hover:bg-slate-50 transition-all cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 group-hover:bg-accent/10 group-hover:text-accent transition-all">
                    <Briefcase size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-800">{project.nom}</h4>
                    <p className="text-xs text-slate-400">{project.client_nom}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    project.statut === 'Terminé' ? 'bg-emerald-50 text-emerald-600' :
                    project.statut === 'En cours' ? 'bg-amber-50 text-amber-600' :
                    'bg-slate-100 text-slate-500'
                  }`}>
                    {project.statut}
                  </span>
                  <ChevronRight size={16} className="text-slate-300 group-hover:text-accent transition-all" />
                </div>
              </div>
            ))}
            {projects.length === 0 && (
              <p className="text-center text-slate-400 py-8 text-sm italic">Aucun projet récent</p>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
