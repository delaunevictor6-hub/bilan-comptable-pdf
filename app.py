import io
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURATION DE LA PAGE STREAMLIT ---
st.set_page_config(page_title="Générateur de Bilan Comptable", page_icon="📊", layout="wide")

st.title("📊 Générateur de Bilan Comptable & Synthèse PDF")
st.write("Remplissez les informations ci-dessous pour générer le bilan comptable pour votre client.")

# --- FORMULAIRE D'ENTRÉE ---
with st.form("form_compta"):
    st.subheader("1. Informations Générales")
    col1, col2, col3 = st.columns(3)
    with col1:
        nom_entreprise = st.text_input("Nom du Client / Entreprise", "Boulangerie Parisienne")
    with col2:
        exercice_annee = st.text_input("Exercice Comptable", "2025")
    with col3:
        expert_comptable = st.text_input("Cabinet / Expert-Comptable", "Cabinet FiduConseil")

    st.subheader("2. Compte de Résultat (€)")
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        chiffre_affaires = st.number_input("Chiffre d'Affaires HT", value=320000.0, step=1000.0)
        achats_charges = st.number_input("Achats & Charges Externes", value=110000.0, step=1000.0)
    with col_cr2:
        salaires_charges = st.number_input("Salaires & Charges Sociales", value=125000.0, step=1000.0)
        dotations_impots = st.number_input("Dotations & Impôts", value=20000.0, step=1000.0)

    st.subheader("3. Bilan Actif / Passif (€)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("**ACTIF**")
        actif_immobilise = st.number_input("Actif Immobilisé", value=85000.0, step=1000.0)
        stocks = st.number_input("Stocks & En-cours", value=15000.0, step=1000.0)
        creances = st.number_input("Créances Clients", value=12000.0, step=1000.0)
        tresorerie = st.number_input("Trésorerie Disponible", value=42000.0, step=1000.0)
    with col_b2:
        st.markdown("**PASSIF**")
        capitaux_propres = st.number_input("Capitaux Propres", value=50000.0, step=1000.0)
        dettes_financieres = st.number_input("Dettes Financières", value=40000.0, step=1000.0)
        dettes_fournisseurs = st.number_input("Dettes Fournisseurs", value=19000.0, step=1000.0)

    submit = st.form_submit_button("Calculer et Générer le PDF")

# --- GÉNÉRATION DU PDF EN MÉMOIRE ---
def generer_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=5)
    style_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=15)
    style_sec = ParagraphStyle('Sec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#1E40AF'), spaceBefore=10, spaceAfter=8)
    
    elements = []
    elements.append(Paragraph("Bilan Comptable & Synthèse Financière", style_titre))
    elements.append(Paragraph(f"Entreprise : <b>{nom_entreprise}</b> | Exercice : <b>{exercice_annee}</b> | Cabinet : {expert_comptable}", style_sub))
    elements.append(Spacer(1, 10))
    
    # Calculs
    total_charges = achats_charges + salaires_charges + dotations_impots
    ebe = chiffre_affaires - (achats_charges + salaires_charges)
    resultat_net = chiffre_affaires - total_charges
    
    # Compte de Résultat
    elements.append(Paragraph("1. Compte de Résultat Simplifié", style_sec))
    data_cr = [
        ["Poste Comptable", "Montant (€)"],
        ["Chiffre d'Affaires HT", f"{chiffre_affaires:,.2f} €"],
        ["Achats & Charges Externes", f"- {achats_charges:,.2f} €"],
        ["Salaires & Charges Sociales", f"- {salaires_charges:,.2f} €"],
        ["Excédent Brut d'Exploitation (EBE)", f"{ebe:,.2f} €"],
        ["Dotations & Impôts", f"- {dotations_impots:,.2f} €"],
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
    total_actif = actif_immobilise + stocks + creances + tresorerie
    total_passif = capitaux_propres + dettes_financieres + dettes_fournisseurs + max(0, resultat_net)
    
    data_bilan = [
        ["ACTIF (Emplois)", "Montant (€)", "PASSIF (Ressources)", "Montant (€)"],
        ["Actif Immobilisé", f"{actif_immobilise:,.2f} €", "Capitaux Propres", f"{capitaux_propres:,.2f} €"],
        ["Stocks & En-cours", f"{stocks:,.2f} €", "Résultat de l'Exercice", f"{resultat_net:,.2f} €"],
        ["Créances Clients", f"{creances:,.2f} €", "Dettes Financières", f"{dettes_financieres:,.2f} €"],
        ["Trésorerie", f"{tresorerie:,.2f} €", "Dettes Fournisseurs", f"{dettes_fournisseurs:,.2f} €"],
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
    buffer.seek(0)
    return buffer

# --- TÉLÉCHARGEMENT ---
if submit:
    st.success("✅ Rapport généré avec succès !")
    pdf_data = generer_pdf()
    st.download_button(
        label="📥 Télécharger le Bilan PDF",
        data=pdf_data,
        file_name=f"Bilan_{nom_entreprise.replace(' ', '_')}_{exercice_annee}.pdf",
        mime="application/pdf"
    )
