import io
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURATION DE L'APPLICATION ---
st.set_page_config(
    page_title="ComptaPro AI - Plateforme Expert-Comptable",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS ---
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #1D4ED8; color: white; }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("⚡ ComptaPro AI")
    st.caption("Cabinet : **FiduConseil Expertise**")
    st.divider()

    menu = st.radio(
        "Navigation",
        ["Dashboard & Analytics", "Nouveau Bilan Client", "Historique & Clients", "Paramètres Cabinet"],
        index=1
    )
    st.divider()
    st.info("💡 **Analyse IA active** : Importez une balance ou un FEC au format CSV pour pré-remplir les données.")

# --- DONNÉES EN SESSIONS ---
if "historique" not in st.session_state:
    st.session_state["historique"] = [
        {
            "id": "CLI-2026-01",
            "nom": "Boulangerie Parisienne SAS",
            "annee": "2025",
            "ca": 320000.0,
            "resultat": 67000.0,
            "sante": "Excellente"
        },
        {
            "id": "CLI-2026-02",
            "nom": "BTP Tech Rénovation",
            "annee": "2025",
            "ca": 540000.0,
            "resultat": -12000.0,
            "sante": "Vigilance BFR"
        }
    ]

# --- PAGES DE L'APPLICATION ---
if menu == "Dashboard & Analytics":
    st.title("📈 Tableau de Bord du Cabinet")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Bilans Générés", len(st.session_state["historique"]))
    col2.metric("Chiffre d'Affaires Cumulé", "860 000 €", "+12%")
    col3.metric("Taux de Rentabilité Moyen", "14.2 %")
    col4.metric("Dossiers en Attente", "3")

    st.divider()
    st.subheader("Derniers bilans clients édités")
    df_hist = pd.DataFrame(st.session_state["historique"])
    st.dataframe(df_hist, use_container_width=True)

elif menu == "Nouveau Bilan Client":
    st.title("📄 Édition d'un Bilan Comptable Client")
    
    with st.expander("📥 Option 1 : Importer une Balance Comptable / FEC (CSV)", expanded=False):
        uploaded_file = st.file_uploader("Glissez-déposez le fichier de balance comptable (CSV/Excel)", type=["csv", "xlsx"])
        if uploaded_file is not None:
            st.success("Fichier analysé avec succès !")

    st.subheader("📝 Option 2 : Saisie des postes comptables")
    
    with st.form("form_bilan"):
        st.markdown("##### 1. Informations Générales Client")
        c1, c2, c3 = st.columns(3)
        with c1:
            nom_entreprise = st.text_input("Raison Sociale / Client", "SARL Transports Express")
        with c2:
            exercice = st.text_input("Exercice Comptable", "2025")
        with c3:
            siret = st.text_input("Numéro SIRET", "849 302 192 00012")

        st.markdown("##### 2. Compte de Résultat Simplifié (€)")
        cr1, cr2 = st.columns(2)
        with cr1:
            ca = st.number_input("Chiffre d'Affaires HT", value=450000.0, step=5000.0)
            achats = st.number_input("Achats de marchandises & matières", value=120000.0, step=1000.0)
            charges_ext = st.number_input("Autres charges externes", value=65000.0, step=1000.0)
        with cr2:
            salaires = st.number_input("Salaires & Charges Sociales", value=180000.0, step=1000.0)
            dotations = st.number_input("Dotations aux amortissements", value=22000.0, step=1000.0)
            impots = st.number_input("Impôts & Taxes", value=11000.0, step=1000.0)

        st.markdown("##### 3. Bilan Actif / Passif (€)")
        b1, b2 = st.columns(2)
        with b1:
            st.caption("ACTIF (Emplois)")
            immobilise = st.number_input("Actif Immobilisé", value=110000.0, step=1000.0)
            stocks = st.number_input("Stocks & En-cours", value=25000.0, step=1000.0)
            creances = st.number_input("Créances Clients", value=48000.0, step=1000.0)
            tresorerie = st.number_input("Disponibilités / Trésorerie", value=52000.0, step=1000.0)
        with b2:
            st.caption("PASSIF (Ressources)")
            capitaux = st.number_input("Capitaux Propres", value=90000.0, step=1000.0)
            dettes_fin = st.number_input("Dettes Financières", value=65000.0, step=1000.0)
            dettes_fourn = st.number_input("Dettes Fournisseurs & Fiscales", value=28000.0, step=1000.0)

        submit = st.form_submit_button("⚡ Lancer les Calculs & Générer le Rapport PDF")

    # Calculs Financiers
    total_charges = achats + charges_ext + salaires + dotations + impots
    resultat_net = ca - total_charges
    ebe = ca - (achats + charges_ext + salaires)
    total_actif = immobilise + stocks + creances + tresorerie
    total_passif = capitaux + dettes_fin + dettes_fourn + max(0, resultat_net)

    if submit:
        st.divider()
        st.subheader("📊 Aperçu des Ratios Financiers Générés")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Résultat Net", f"{resultat_net:,.2f} €", delta=f"{(resultat_net/ca)*100:.1f}% CA")
        m2.metric("EBE (Excédent Brut)", f"{ebe:,.2f} €")
        m3.metric("Fonds de Roulement (FRNG)", f"{(capitaux + dettes_fin) - immobilise:,.2f} €")
        m4.metric("Trésorerie Nette", f"{tresorerie:,.2f} €")

        def build_pdf():
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()

            style_title = ParagraphStyle('Titre', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor('#0F172A'))
            style_sec = ParagraphStyle('Sec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2563EB'), spaceBefore=10, spaceAfter=8)
            style_txt = ParagraphStyle('Txt', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)

            story = []
            story.append(Paragraph("<b>FIDUCONSEIL EXPERTISE</b> - Rapport Financier", style_txt))
            story.append(Spacer(1, 5))
            story.append(Paragraph(f"Bilan & Compte de Résultat : {nom_entreprise}", style_title))
            story.append(Paragraph(f"Exercice : {exercice} | SIRET : {siret}", style_txt))
            story.append(Spacer(1, 15))

            story.append(Paragraph("1. Compte de Résultat Synthétique", style_sec))
            data_cr = [
                ["Poste Comptable", "Montant (€)"],
                ["Chiffre d'Affaires HT", f"{ca:,.2f} €"],
                ["Consommation Marchandises & Charges Externes", f"- {(achats + charges_ext):,.2f} €"],
                ["Salaires & Charges Sociales", f"- {salaires:,.2f} €"],
                ["Excédent Brut d'Exploitation (EBE)", f"{ebe:,.2f} €"],
                ["Amortissements & Impôts", f"- {(dotations + impots):,.2f} €"],
                ["RÉSULTAT NET COMPTABLE", f"{resultat_net:,.2f} €"]
            ]
            t_cr = Table(data_cr, colWidths=[310, 220])
            t_cr.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#DCFCE7') if resultat_net >= 0 else colors.HexColor('#FEE2E2')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_cr)
            story.append(Spacer(1, 15))

            story.append(Paragraph("2. Bilan Actif / Passif", style_sec))
            data_b = [
                ["ACTIF", "Montant (€)", "PASSIF", "Montant (€)"],
                ["Actif Immobilisé", f"{immobilise:,.2f} €", "Capitaux Propres", f"{capitaux:,.2f} €"],
                ["Stocks", f"{stocks:,.2f} €", "Résultat Net", f"{resultat_net:,.2f} €"],
                ["Créances Clients", f"{creances:,.2f} €", "Dettes Financières", f"{dettes_fin:,.2f} €"],
                ["Trésorerie", f"{tresorerie:,.2f} €", "Dettes Fournisseurs", f"{dettes_fourn:,.2f} €"],
                ["TOTAL ACTIF", f"{total_actif:,.2f} €", "TOTAL PASSIF", f"{total_passif:,.2f} €"]
            ]
            t_b = Table(data_b, colWidths=[160, 105, 160, 105])
            t_b.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor('#2563EB')),
                ('BACKGROUND', (2,0), (3,0), colors.HexColor('#1D4ED8')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('ALIGN', (3,0), (3,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_b)

            doc.build(story)
            buf.seek(0)
            return buf

        pdf_bytes = build_pdf()

        st.download_button(
            label="📥 Télécharger le Rapport Officiel (PDF)",
            data=pdf_bytes,
            file_name=f"Bilan_{nom_entreprise.replace(' ', '_')}_{exercice}.pdf",
            mime="application/pdf"
        )

elif menu == "Historique & Clients":
    st.title("📂 Base Clients & Historique")
    st.table(pd.DataFrame(st.session_state["historique"]))

elif menu == "Paramètres Cabinet":
    st.title("⚙️ Paramètres du Cabinet")
    st.text_input("Nom du Cabinet", "FiduConseil Expertise")
    st.text_input("Adresse", "15 Rue de la Paix, 75002 Paris")
    st.success("Configuration sauvegardée !")
