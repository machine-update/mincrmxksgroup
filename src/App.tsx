import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Users, 
  Briefcase, 
  FileText, 
  Calendar as CalendarIcon,
  Plus,
  Search,
  ChevronRight,
  Menu,
  X
} from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import Dashboard from "./pages/Dashboard";
import Clients from "./pages/Clients";
import Projects from "./pages/Projects";
import Quotes from "./pages/Quotes";
import QuoteEditor from "./pages/QuoteEditor";

function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  
  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Dashboard" },
    { to: "/clients", icon: Users, label: "Clients" },
    { to: "/projects", icon: Briefcase, label: "Projets" },
    { to: "/quotes", icon: FileText, label: "Devis" },
  ];

  return (
    <>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <motion.aside 
        initial={false}
        animate={{ width: isOpen ? 260 : 0, opacity: isOpen ? 1 : 0 }}
        className="fixed left-0 top-0 h-screen bg-white border-r border-slate-100 z-40 overflow-hidden"
      >
        <div className="p-8">
          <h1 className="text-xl font-bold text-accent tracking-tight">XKSGROUP</h1>
          <p className="text-xs text-slate-400 font-medium mt-1">Mini CRM Audiovisuel</p>
        </div>

        <nav className="px-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => 
                `sidebar-item ${isActive ? 'active' : ''}`
              }
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-8 px-8 w-full">
          <div className="p-4 bg-slate-50 rounded-2xl">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Support</p>
            <p className="text-sm text-slate-600 mt-1">Besoin d'aide ?</p>
          </div>
        </div>
      </motion.aside>
    </>
  );
}

function Topbar() {
  const location = useLocation();
  const getTitle = () => {
    switch(location.pathname) {
      case "/": return "Dashboard";
      case "/clients": return "Clients";
      case "/projects": return "Projets";
      case "/quotes": return "Devis";
      case "/quotes/new": return "Nouveau Devis";
      default: return "CRM";
    }
  };

  return (
    <header className="h-20 flex items-center justify-between px-8 bg-transparent">
      <h2 className="text-2xl font-semibold text-slate-800">{getTitle()}</h2>
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Rechercher..." 
            className="pl-10 pr-4 py-2 bg-white rounded-xl border-none shadow-soft focus:ring-2 focus:ring-accent/20 outline-none w-64 transition-all"
          />
        </div>
        <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold">
          AB
        </div>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-bg-soft">
        <Sidebar />
        <main className="flex-1 lg:ml-[260px] transition-all">
          <Topbar />
          <div className="p-8 pt-0">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/clients" element={<Clients />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/quotes" element={<Quotes />} />
                <Route path="/quotes/new" element={<QuoteEditor />} />
                <Route path="/quotes/edit/:id" element={<QuoteEditor />} />
              </Routes>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </Router>
  );
}
