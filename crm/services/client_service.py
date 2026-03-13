from __future__ import annotations

import csv
import io
from datetime import datetime

from flask import Response
from sqlalchemy import or_

from ..models import Client


def build_client_query(search: str, entreprise: str, with_phone: bool):
    query = Client.query
    if search:
        like_q = f"%{search}%"
        query = query.filter(
            or_(
                Client.nom.ilike(like_q),
                Client.entreprise.ilike(like_q),
                Client.email.ilike(like_q),
            )
        )
    if entreprise:
        query = query.filter(Client.entreprise.ilike(f"%{entreprise}%"))
    if with_phone:
        query = query.filter(Client.telephone.isnot(None)).filter(Client.telephone != "")
    return query


def export_clients_csv(clients) -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nom", "Entreprise", "Email", "Telephone", "Adresse"])
    for client in clients:
        writer.writerow([client.nom, client.entreprise or "", client.email, client.telephone or "", client.adresse or ""])

    csv_data = output.getvalue()
    output.close()
    filename = f"clients_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
