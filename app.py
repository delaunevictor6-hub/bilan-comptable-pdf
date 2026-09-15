import io
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(
    page_title="ComptaPro SaaS - Plateforme Expert-Comptable",
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

# --- CONNEXION SUPABASE ---
SUPABASE_URL = "https://pttlfcwuqjyverbsvzzb.supabase.co"
SUPABASE_KEY = "sb_publishable_VjrsGDL0MB5J6OmqLQAq_QbgJir"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- GESTION DES ÉTATS DE SESSION ---
if "user" not in st.session_state:
    st.session_state["user"] = None
if "otp_step" not in st.session_state:
    st.session_state["otp_step"] = False
if "pending_email" not in st.session_state:
    st.session_state["pending_email"] = ""
if "pending_nom_cabinet" not in st.session_state:
    st.session_state["pending_nom_cabinet"] = ""
if "is_signup" not in st.session_state:
    st.session_state["is_signup"] = False

# ==============================================================================
# 1. AUTHENTIFICATION AVEC VÉRIFICATION E-MAIL PAR CODE OTP
# ==============================================================================
if st.session_state["user"] is None:
    st.title("⚡ ComptaPro AI - Espace Cabinet")
    st.caption("Plateforme SaaS sécurisée de gestion et de génération de bilans comptables")
    
    # Étape 2 : Saisie du code reçu par e-mail
    if st.session_state["otp_step"]:
        st.subheader("🔑 Vérification de votre identité")
        st.info(f"Un code de vérification a été envoyé à : **{st.session_state['pending_email']}**")
        
        with st.form("verify_code_form"):
            code_input = st.text_input("Entrez le code reçu par e-mail", placeholder="Ex: 123456")
            btn_verify = st.form_submit_button("Valider et accéder à l'espace")
            
            if btn_verify:
                if not code_input:
                    st.warning("Veuillez saisir le code.")
                else:
                    try:
                        res = supabase.auth.verify_otp({
                            "email": st.session_state["pending_email"],
                            "token": code_input.strip(),
                            "type": "email"
                        })
                        
                        if res.user:
                            st.session_state["user"] = res.user
                            user_id = res.user.id
                            
                            if st.session_state["is_signup"]:
                                existing_cab = supabase.table("cabinets").select("*").eq("user_id", user_id).execute().data
                                if not existing_cab:
                                    supabase.table("cabinets").insert({
                                        "user_id": user_id,
                                        "nom_cabinet": st.session_state["pending_nom_cabinet"] or "Mon Cabinet",
                                        "adresse": "À renseigner"
                                    }).execute()
                            
                            st.session_state["otp_step"] = False
                            st.session_state["is_signup"] = False
                            st.success("Vérification réussie !")
                            st.rerun()
                        else:
                            st.error("Échec de la vérification. Code invalide.")
                    except Exception as e:
                        st.error(f"Code invalide ou expiré : {e}")
        
        if st.button("← Changer d'adresse e-mail"):
            st.session_state["otp_step"] = False
            st.session_state["is_signup"] = False
            st.rerun()

    # Étape 1 : Demande d'envoi du code par mail
    else:
        tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte cabinet"])
        
        with tab_login:
            with st.form("login_request_form"):
                email = st.text_input("Adresse e-mail du cabinet")
                btn_login = st.form_submit_button("Recevoir mon code de connexion")
                
                if btn_login:
                    if "@" not in email:
                        st.error("Veuillez entrer une adresse e-mail valide.")
                    else:
                        try:
                            supabase.auth.sign_in_with_otp({"email": email})
                            st.session_state["pending_email"] = email
                            st.session_state["otp_step"] = True
                            st.session_state["is_signup"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur d'envoi du code : {e}")

        with tab_signup:
            with st.form("signup_request_form"):
                new_email = st.text_input("Adresse e-mail professionnelle")
                nom_cabinet = st.text_input("Nom de votre Cabinet", "Mon Cabinet Expertise")
                btn_signup = st.form_submit_button("Créer mon espace & recevoir le code")
                
                if btn_signup:
                    if "@" not in new_email:
                        st.error("Veuillez entrer une adresse e-mail valide.")
                    else:
                        try:
                            supabase.auth.sign_in_with_otp({"email": new_email})
                            st.session_state["pending_email"] = new_email
                            st.session_state["pending_nom_cabinet"] = nom_cabinet
                            st.session_state["otp_step"] = True
                            st.session_state["is_signup"] = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de l'inscription : {e}")

# ==============================================================================
# 2. ESPACE CLIENT CONNECTÉ
# ==============================================================================
else:
    user_id = st.session_state["user"].id

    cab_info = supabase.table("cabinets").select("*").eq("user_id", user_id).execute().data
    nom_cabinet_actuel = cab_info[0]["nom_cabinet"] if cab_info else "Mon Cabinet"

    with st.sidebar:
        st.title("⚡ ComptaPro AI")
        st.caption(f"Cabinet connecté : **{nom_cabinet_actuel}**")
        if st.button("Déconnexion"):
            st.session_state["user"] = None
            st.session_state["otp_step"] = False
            st.rerun()
        st.divider()

        menu = st.radio("Navigation", ["Dashboard", "Nouveau Bilan Client", "Mes Clients", "Paramètres Cabinet"])

    if menu == "Dashboard":
        st.title(f"📈 Tableau de bord - {nom_cabinet_actuel}")
        bilans_data = supabase.table("bilans").select("*").eq("user_id", user_id).execute().data
        
        col1, col2 = st.columns(2)
        col1.metric("Nombre de bilans enregistrés", len(bilans_data))
        
        if bilans_data:
            df = pd.DataFrame(bilans_data)
            col2.metric("Chiffre d'Affaires total géré", f"{df['ca'].sum():,.2f} €")
            st.divider()
            st.subheader("Historique de vos dossiers")
            st.dataframe(df[["nom_client", "annee", "ca", "resultat"]], use_container_width=True)
        else:
            col2.metric("Chiffre d'Affaires total géré", "0,00 €")
            st.info("Aucun bilan comptable n'a encore été généré.")

    elif menu == "Nouveau Bilan Client":
        st.title("📄 Édition d'un Bilan Comptable Client")

        with st.form("form_bilan"):
            st.markdown("##### 1. Informations Générales Client")
            c1, c2, c3 = st.columns(3)
            with c1:
                nom_client = st.text_input("Raison Sociale / Client", "SARL Transports Express")
            with c2:
                annee = st.text_input("Exercice Comptable", "2025")
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

            btn_save = st.form_submit_button("⚡ Enregistrer le Bilan & Générer PDF")

        total_charges = achats + charges_ext + salaires + dotations + impots
        resultat_net = ca - total_charges
        ebe = ca - (achats + charges_ext + salaires)
        total_actif = immobilise + stocks + creances + tresorerie
        total_passif = capitaux + dettes_fin + dettes_fourn + max(0, resultat_net)

        if btn_save:
            supabase.table("bilans").insert({
                "user_id": user_id,
                "nom_client": nom_client,
                "annee": annee,
                "ca": ca,
                "resultat": resultat_net
            }).execute()

            st.success(f"Bilan de {nom_client} sauvegardé !")
            st.divider()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Résultat Net", f"{resultat_net:,.2f} €", delta=f"{(resultat_net/ca)*100:.1f}% CA")
            m2.metric("EBE (Excédent Brut)", f"{ebe:,.2f} €")
            m3.metric("FRNG", f"{(capitaux + dettes_fin) - immobilise:,.2f} €")
            m4.metric("Trésorerie Nette", f"{tresorerie:,.2f} €")

            def build_pdf():
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()

                style_title = ParagraphStyle('Titre', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#0F172A'))
                style_sec = ParagraphStyle('Sec', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2563EB'), spaceBefore=10, spaceAfter=8)
                style_txt = ParagraphStyle('Txt', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)

                story = []
                story.append(Paragraph(f"<b>{nom_cabinet_actuel}</b> - Rapport Financier Client", style_txt))
                story.append(Spacer(1, 5))
                story.append(Paragraph(f"Bilan & Compte de Résultat : {nom_client}", style_title))
                story.append(Paragraph(f"Exercice : {annee} | SIRET : {siret}", style_txt))
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
                file_name=f"Bilan_{nom_client.replace(' ', '_')}_{annee}.pdf",
                mime="application/pdf"
            )

    elif menu == "Mes Clients":
        st.title("📂 Base de données Clients")
        bilans_data = supabase.table("bilans").select("*").eq("user_id", user_id).execute().data
        if bilans_data:
            df = pd.DataFrame(bilans_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun client n'est encore associé à votre cabinet.")

    elif menu == "Paramètres Cabinet":
        st.title("⚙️ Configuration du Cabinet")
        nouveau_nom = st.text_input("Nom du Cabinet", value=nom_cabinet_actuel)
        if st.button("Sauvegarder les modifications"):
            supabase.table("cabinets").update({"nom_cabinet": nouveau_nom}).eq("user_id", user_id).execute()
            st.success("Nom du cabinet mis à jour !")
            st.rerun()
