PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	nom VARCHAR(120) NOT NULL, 
	email VARCHAR(180) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
INSERT INTO users VALUES(1,'Samba Kanté - PDG','samba@xksprod.com','scrypt:32768:8:1$yMcqeoyF6MpQB4FL$65184aac77600e596adfe5b648504bf63c201ff69868f4d23be5420ad5f9e7c00cfea6d2b06c55b7b46544934424ef8b06e46c7596b4cb8aa38c581d0ebc99ab','responsable','2026-03-06 10:08:44.650471');
INSERT INTO users VALUES(2,'Papa Abou Mbaye - Stagiaire','papeaboumbaye@gmail.com','scrypt:32768:8:1$z5dMnWyUhdN5Z5Cu$05ea9ff63b4bfe4da486b8f7bfa015ce1053cde70546d6c2507175f810c9363c7bc49fa6c8354afcbb2413dada79a33d45a2ff8fd9ca0e559a1aff7ec3c77f7a','employe','2026-03-06 10:08:44.650481');
INSERT INTO users VALUES(3,'Abasse','abasse@gmail.com','scrypt:32768:8:1$dPXTltlxSu6bivrA$da8b7014e410dc60c16ee3a7afad31815948697f759d2654bb677389209834b8a129adc432ef104c91eaa891e56411f9d852ce3fbf6fae33bcf0d7c273747f12','employe','2026-03-06 10:46:10.405401');
INSERT INTO users VALUES(4,'Ntsiassila','ghedeon@gmail.com','scrypt:32768:8:1$37HRRbHbcf7TCSz7$6a4b3490e828e4cac266d3e52248bd9fb806ebfab53521f9cd0b5d1741a6e1772e2150dda867d50cdabb564ff0c07a54a5b4ebc7f6b1d67298f4dae43328ee01','employe','2026-03-12 14:30:30.296229');
CREATE TABLE clients (
	id INTEGER NOT NULL, 
	nom VARCHAR(120) NOT NULL, 
	entreprise VARCHAR(180), 
	email VARCHAR(180) NOT NULL, 
	telephone VARCHAR(60), 
	adresse TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO clients VALUES(1,'Jean Dupont','Studio Alpha','jean@alpha.com','0123456789','Paris','2026-03-06 10:08:44.672089','2026-03-06 10:08:44.672093');
INSERT INTO clients VALUES(2,'Marie Curie','Science Prod','marie@science.com','0987654321','Lyon','2026-03-06 10:08:44.672095','2026-03-06 10:08:44.672096');
INSERT INTO clients VALUES(3,'abasse','xksgroup','abasse@gmail.com','0746440220','pj','2026-03-06 10:41:46.729677','2026-03-06 10:41:46.729683');
INSERT INTO clients VALUES(4,'MBAYE','AIRBUS','papeaboumbaye@gmail.com','0746440220','7 route de choisy','12/03/2026','12/03/2026');
CREATE TABLE projets (
	id INTEGER NOT NULL, 
	titre VARCHAR(180) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	statut VARCHAR(50) NOT NULL, 
	budget NUMERIC(12, 2), 
	date_debut DATE, 
	date_fin DATE, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	client_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES clients (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO projets VALUES(1,'Clip Musical - Summer','Clip','En cours',4500,'2026-03-01','2026-03-15','2026-03-06 10:08:44.703097','2026-03-06 10:08:44.703103',1,1);
INSERT INTO projets VALUES(2,'@specatcle','Spectacle','En attente',2000,'2026-03-07','2026-03-15','2026-03-06 10:42:31.195562','2026-03-06 10:42:31.195567',3,1);
CREATE TABLE devis (
	id INTEGER NOT NULL, 
	reference VARCHAR(40) NOT NULL, 
	date_devis DATE NOT NULL, 
	montant_total NUMERIC(12, 2) NOT NULL, 
	statut VARCHAR(50) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	client_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (reference), 
	FOREIGN KEY(client_id) REFERENCES clients (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO devis VALUES(1,'DEV-20260306-49D422','2026-03-08',2000,'Envoye','2026-03-06 10:47:53.003710','2026-03-06 10:47:53.003715',3,1);
CREATE TABLE devis_items (
	id INTEGER NOT NULL, 
	designation VARCHAR(255) NOT NULL, 
	quantite INTEGER NOT NULL, 
	prix_unitaire NUMERIC(12, 2) NOT NULL, 
	total NUMERIC(12, 2) NOT NULL, 
	devis_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(devis_id) REFERENCES devis (id)
);
INSERT INTO devis_items VALUES(1,'biongvre',1,2000,2000,1);
COMMIT;
