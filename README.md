# Mini CRM XKSGROUP

CRM interne Flask pour une agence audiovisuelle. Le projet ne depend que de Python, Flask, SQLAlchemy, Bootstrap et des templates Jinja. React, TypeScript, Vite et Node.js ont ete retires. L'application est maintenant prete pour PostgreSQL en deploiement.

## Stack

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- SQLite en fallback local
- Bootstrap 5

## Installation

```bash
git clone <repo>
cd mini-crm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Base de donnees

Le projet accepte `DATABASE_URL` via variable d'environnement.

Exemple PostgreSQL local :

```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/xksgroup_mini_crm
python app.py
```

Exemple fallback SQLite local :

```bash
export DATABASE_URL=sqlite:///database/crm.sqlite3
python app.py
```

## Acces

- URL: http://localhost:5000
- Responsable: `admin@xks.local` / `admin123`
- Employe: `employe@xks.local` / `employe123`

## Structure

```text
mini-crm/
├── app.py
├── config.py
├── controllers/
├── models/
├── services/
├── extensions.py
├── database/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── auth/
│   ├── clients/
│   ├── projects/
│   └── devis/
├── tests/
├── requirements.txt
└── .gitignore
```

## Fonctionnalites

- Dashboard Bootstrap avec KPIs et graphiques
- CRUD clients, projets, devis, utilisateurs
- Gestion des roles `responsable` et `employe`
- Recherche globale clients / projets / devis / factures
- QR code unique pour chaque devis via `static/images/qrcodes/`
- Export PDF des devis avec logo, lignes et QR code
- Pagination sur les principales listes

## Lancement rapide

```bash
python app.py
```

Application disponible sur `http://localhost:5000`.

Aucune commande `npm`, `node` ou `vite` n'est necessaire.

## Migrations

Le projet est compatible `Flask-Migrate`.

```bash
export FLASK_APP=app:app
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

## Tests

```bash
python -m unittest discover -s tests
```
