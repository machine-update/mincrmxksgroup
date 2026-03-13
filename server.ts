import express from "express";
import { createServer as createViteServer } from "vite";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const db = new Database("crm.db");

// Initialize Database Schema
db.exec(`
  CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    entreprise TEXT,
    email TEXT NOT NULL,
    telephone TEXT,
    adresse TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS projets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    client_id INTEGER,
    type TEXT CHECK(type IN ('Clip', 'Spectacle', 'Documentaire')),
    statut TEXT CHECK(statut IN ('En attente', 'En cours', 'Terminé')),
    date_debut DATE,
    date_fin DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS devis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    statut TEXT CHECK(statut IN ('Envoyé', 'Accepté', 'Refusé')),
    total REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS devis_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    devis_id INTEGER,
    description TEXT NOT NULL,
    quantite INTEGER NOT NULL,
    prix_unitaire REAL NOT NULL,
    sous_total REAL NOT NULL,
    FOREIGN KEY (devis_id) REFERENCES devis(id) ON DELETE CASCADE
  );
`);

// Seed Data if empty
const clientCount = db.prepare("SELECT COUNT(*) as count FROM clients").get() as { count: number };
if (clientCount.count === 0) {
  const insertClient = db.prepare("INSERT INTO clients (nom, entreprise, email, telephone, adresse) VALUES (?, ?, ?, ?, ?)");
  const client1 = insertClient.run("Jean Dupont", "Studio Alpha", "jean@alpha.com", "0123456789", "Paris");
  const client2 = insertClient.run("Marie Curie", "Science Prod", "marie@science.com", "0987654321", "Lyon");

  const insertProject = db.prepare("INSERT INTO projets (nom, client_id, type, statut, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?)");
  insertProject.run("Clip Musical - Summer", client1.lastInsertRowid, "Clip", "En cours", "2024-06-01", "2024-06-15");
  insertProject.run("Documentaire Nature", client2.lastInsertRowid, "Documentaire", "En attente", "2024-07-01", "2024-08-30");
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  
  // Clients
  app.get("/api/clients", (req, res) => {
    const clients = db.prepare("SELECT * FROM clients ORDER BY created_at DESC").all();
    res.json(clients);
  });

  app.post("/api/clients", (req, res) => {
    const { nom, entreprise, email, telephone, adresse } = req.body;
    const info = db.prepare("INSERT INTO clients (nom, entreprise, email, telephone, adresse) VALUES (?, ?, ?, ?, ?)").run(nom, entreprise, email, telephone, adresse);
    res.json({ id: info.lastInsertRowid });
  });

  app.put("/api/clients/:id", (req, res) => {
    const { nom, entreprise, email, telephone, adresse } = req.body;
    db.prepare("UPDATE clients SET nom = ?, entreprise = ?, email = ?, telephone = ?, adresse = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").run(nom, entreprise, email, telephone, adresse, req.params.id);
    res.json({ success: true });
  });

  app.delete("/api/clients/:id", (req, res) => {
    db.prepare("DELETE FROM clients WHERE id = ?").run(req.params.id);
    res.json({ success: true });
  });

  // Projects
  app.get("/api/projets", (req, res) => {
    const projets = db.prepare(`
      SELECT p.*, c.nom as client_nom 
      FROM projets p 
      LEFT JOIN clients c ON p.client_id = c.id 
      ORDER BY p.created_at DESC
    `).all();
    res.json(projets);
  });

  app.post("/api/projets", (req, res) => {
    const { nom, client_id, type, statut, date_debut, date_fin } = req.body;
    const info = db.prepare("INSERT INTO projets (nom, client_id, type, statut, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?)").run(nom, client_id, type, statut, date_debut, date_fin);
    res.json({ id: info.lastInsertRowid });
  });

  // Quotes
  app.get("/api/devis", (req, res) => {
    const devis = db.prepare(`
      SELECT d.*, c.nom as client_nom 
      FROM devis d 
      LEFT JOIN clients c ON d.client_id = c.id 
      ORDER BY d.created_at DESC
    `).all();
    res.json(devis);
  });

  app.get("/api/devis/:id", (req, res) => {
    const devis = db.prepare(`
      SELECT d.*, c.nom as client_nom, c.entreprise as client_entreprise, c.email as client_email
      FROM devis d 
      LEFT JOIN clients c ON d.client_id = c.id 
      WHERE d.id = ?
    `).get(req.params.id);
    
    const items = db.prepare("SELECT * FROM devis_items WHERE devis_id = ?").all(req.params.id);
    res.json({ ...devis, items });
  });

  app.post("/api/devis", (req, res) => {
    const { client_id, statut, items } = req.body;
    const total = items.reduce((acc: number, item: any) => acc + (item.quantite * item.prix_unitaire), 0);
    
    const transaction = db.transaction(() => {
      const info = db.prepare("INSERT INTO devis (client_id, statut, total) VALUES (?, ?, ?)").run(client_id, statut, total);
      const devisId = info.lastInsertRowid;
      
      const insertItem = db.prepare("INSERT INTO devis_items (devis_id, description, quantite, prix_unitaire, sous_total) VALUES (?, ?, ?, ?, ?)");
      for (const item of items) {
        insertItem.run(devisId, item.description, item.quantite, item.prix_unitaire, item.quantite * item.prix_unitaire);
      }
      return devisId;
    });

    const devisId = transaction();
    res.json({ id: devisId });
  });

  // Stats
  app.get("/api/stats", (req, res) => {
    const clientCount = db.prepare("SELECT COUNT(*) as count FROM clients").get() as any;
    const projectCount = db.prepare("SELECT COUNT(*) as count FROM projets WHERE statut = 'En cours'").get() as any;
    const quoteCount = db.prepare("SELECT COUNT(*) as count FROM devis WHERE statut = 'Envoyé'").get() as any;
    
    res.json({
      clients: clientCount.count,
      activeProjects: projectCount.count,
      sentQuotes: quoteCount.count
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, "dist")));
    app.get("*", (req, res) => {
      res.sendFile(path.join(__dirname, "dist", "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
