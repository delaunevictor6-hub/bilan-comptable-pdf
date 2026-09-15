import os
from typing import List
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class BilanComptable(BaseModel):
    id_client: str
    nom_entreprise: str
    exercice_annee: str
    expert_comptable: str
    chiffre_affaires: float
    achats_charges_externes: float
    salaires_charges: float
    impots_taxes: float
    dotations_amortissements: float
    actif_immobilise: float
    stocks: float
    creances_clients: float
    tresorerie_actif: float
    capitaux_propres: float
    dettes_financieres: float
    dettes_fournisseurs: float

def generer_rapport_bilan(bilan: BilanComptable, dossier_sortie: str = "pdf_clients"):
    os.makedirs(dossier_sortie, exist_ok=True)
    nom_fichier = os.path.join(dossier_sortie, f"Bilan_{bilan.id_client}_{bilan.exercice_annee}.pdf")
    
    doc = SimpleDocTemplate(nom_fichier, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=5)
    style_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=15)
    style_sec = ParagraphStyle('Sec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#1E40AF'), spaceBefore=10, spaceAfter=8)
    style_txt = ParagraphStyle('Txt', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    
    elements = []
    elements.append(Paragraph("Bilan Comptable & Synthèse Financière", style_titre))
    elements.append(Paragraph(f"Entreprise : <b>{bilan.nom_entreprise}</b> | Exercice : <b>{bilan.exercice_annee}</b> | Cabinet : {bilan.expert_comptable}", style_sub))
    elements.append(Spacer(1, 10))
    
    # Compte de Résultat
    elements.append(Paragraph("1. Compte de Résultat Simplifié", style_sec))
    total_charges = bilan.achats_charges_externes + bilan.salaires_charges + bilan.impots_taxes + bilan.dotations_amortissements
    ebe = bilan.chiffre_affaires - (bilan.achats_charges_externes + bilan.salaires_charges)
    resultat_net = bilan.chiffre_affaires - total_charges
    
    data_cr = [
        ["Poste Comptable", "Montant (€)"],
        ["Chiffre d'Affaires HT", f"{bilan.chiffre_affaires:,.2f} €"],
        ["Achats & Charges Externes", f"- {bilan.achats_charges_externes:,.2f} €"],
        ["Salaires & Charges Sociales", f"- {bilan.salaires_charges:,.2f} €"],
        ["Excédent Brut d'Exploitation (EBE)", f"{ebe:,.2f} €"],
        ["Dotations & Impôts", f"- {(bilan.dotations_amortissements + bilan.impots_taxes):,.2f} €"],
        ["Résultat Net Comptable", f"{resultat_net:,.2f} €"]
    ]
    t_cr = Table(data_cr, colWidths=[310, 220])
    t_cr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#DCFCE7') if resultat_net >= 0 else colors.HexColor('#FEE2E2')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_cr)
    elements.append(Spacer(1, 15))
    
    # Bilan Actif / Passif
    elements.append(Paragraph("2. Structure du Bilan (Actif / Passif)", style_sec))
    total_actif = bilan.actif_immobilise + bilan.stocks + bilan.creances_clients + bilan.tresorerie_actif
    total_passif = bilan.capitaux_propres + bilan.dettes_financieres + bilan.dettes_fournisseurs + max(0, resultat_net)
    
    data_bilan = [
        ["ACTIF (Emplois)", "Montant (€)", "PASSIF (Ressources)", "Montant (€)"],
        ["Actif Immobilisé", f"{bilan.actif_immobilise:,.2f} €", "Capitaux Propres", f"{bilan.capitaux_propres:,.2f} €"],
        ["Stocks & En-cours", f"{bilan.stocks:,.2f} €", "Résultat de l'Exercice", f"{resultat_net:,.2f} €"],
        ["Créances Clients", f"{bilan.creances_clients:,.2f} €", "Dettes Financières", f"{bilan.dettes_financieres:,.2f} €"],
        ["Trésorerie", f"{bilan.tresorerie_actif:,.2f} €", "Dettes Fournisseurs", f"{bilan.dettes_fournisseurs:,.2f} €"],
        ["TOTAL ACTIF", f"{total_actif:,.2f} €", "TOTAL PASSIF", f"{total_passif:,.2f} €"]
    ]
    t_bilan = Table(data_bilan, colWidths=[160, 105, 160, 105])
    t_bilan.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#0284C7')),
        ('BACKGROUND', (2,0), (3,0), colors.HexColor('#0369A1')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_bilan)
    
    doc.build(elements)
    print(f"Bilan créé : {nom_fichier}")

if __name__ == "__main__":
    clients = [
        BilanComptable(
            id_client="CLI-001",
            nom_entreprise="Boulangerie Parisienne",
            exercice_annee="2025",
            expert_comptable="Cabinet FiduConseil",
            chiffre_affaires=320000.0,
            achats_charges_externes=110000.0,
            salaires_charges=125000.0,
            impots_taxes=8000.0,
            dotations_amortissements=12000.0,
            actif_immobilise=85000.0,
            stocks=15000.0,
            creances_clients=12000.0,
            tresorerie_actif=42000.0,
            capitaux_propres=50000.0,
            dettes_financieres=40000.0,
            dettes_fournisseurs=19000.0
        )
    ]
    for client in clients:
        generer_rapport_bilan(client)
