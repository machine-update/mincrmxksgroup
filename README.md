# Mini CRM XKSGROUP (Flask)

Migration du projet vers la stack du cahier des charges:
- Backend: Python + Flask
- Base de donnees: SQLite (via SQLAlchemy)
- Frontend: Templates HTML/CSS + Bootstrap
- Securite: login + roles `responsable` / `employe`

## Fonctionnalites

- Authentification par email / mot de passe
- Gestion des roles:
  - `responsable`: acces complet + stats + gestion utilisateurs
  - `employe`: acces operationnel (consultation clients, gestion projets/devis)
- Modules:
  - Dashboard
  - Clients
  - Projets (avec budget)
  - Devis (lignes de devis et total automatique)
  - Utilisateurs (admin responsable)

## Installation

Prerequis: Python 3.10+

```bash
cd /Users/papaabou/Downloads/xksgroup-mini-crm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Mode debug optionnel:

```bash
FLASK_DEBUG=1 python app.py
```

Variables d'environnement:

```bash
cp .env.example .env
```

Application locale:
- http://localhost:3000

## Comptes de demo

- Responsable: `admin@xks.local` / `admin123`
- Employe: `employe@xks.local` / `employe123`

## Notes

- La base SQLite est creee automatiquement dans `instance/crm.sqlite3`.
- L'ancien code React/Node est conserve dans le repo mais n'est plus necessaire pour lancer la version Flask.
- Les templates HTML sont charges depuis `templates/` et les assets depuis `static/`.

## Structure

```text
app.py
crm/
  controllers/
  models/
  services/
  decorators.py
  extensions.py
templates/
static/
tests/
```

## Tests

```bash
source .venv/bin/activate
python -m unittest discover -s tests
```
