import io
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(page_title="ComptaPro SaaS", page_icon="⚡", layout="wide")

# --- CONNEXION SUPABASE (Lignes 16 et 17 configurées) ---
SUPABASE_URL = "https://pttlfcwuqjyverbsvzzb.supabase.co"
SUPABASE_KEY = "sb_publishable_VjrsGDL0MB5J6OmqLQAq_QbgJir"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- GESTION DE LA SESSION UTILISATEUR ---
if "user" not in st.session_state:
    st.session_state["user"] = None

# ==============================================================================
# 1. ÉCRAN DE CONNEXION / INSCRIPTION
# ==============================================================================
if st.session_state["user"] is None:
    st.title("⚡ ComptaPro AI - Connexion Cabinet")
    
    tab_login, tab_signup = st.tabs(["Se connecter", "Créer un compte cabinet"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email professionnel")
            password = st.text_input("Mot de passe", type="password")
            btn_login = st.form_submit_button("Se connecter")
            
            if btn_login:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["user"] = res.user
                    st.success("Connexion réussie !")
                    st.rerun()
                except Exception as e:
                    st.error("Identifiants incorrects ou compte inexistant.")

    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email professionnel")
            new_password = st.text_input("Mot de passe (6 car. min)", type="password")
            nom_cabinet = st.text_input("Nom de votre Cabinet", "Mon Cabinet Expertise")
            btn_signup = st.form_submit_button("Créer mon espace SaaS")
            
            if btn_signup:
                try:
                    res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                    user_id = res.user.id
                    # Enregistrement des paramètres initiaux du cabinet
                    supabase.table("cabinets").insert({
                        "user_id": user_id,
                        "nom_cabinet": nom_cabinet,
                        "adresse": "À renseigner"
                    }).execute()
                    st.success("Compte créé ! Vous pouvez maintenant vous connecter.")
                except Exception as e:
                    st.error(f"Erreur lors de la création : {e}")

# ==============================================================================
# 2. ESPACE CLIENT CONNECTÉ (MULTI-CABINETS ISOLÉ)
# ==============================================================================
else:
    user_id = st.session_state["user"].id

    # Récupérer les paramètres du cabinet connecté
    cab_info = supabase.table("cabinets").select("*").eq("user_id", user_id).execute().data
    nom_cabinet_actuel = cab_info[0]["nom_cabinet"] if cab_info else "Mon Cabinet"

    # NAVIGATION SIDEBAR
    with st.sidebar:
        st.title("⚡ ComptaPro AI")
        st.caption(f"Connecté : **{nom_cabinet_actuel}**")
        if st.button("Déconnexion"):
            st.session_state["user"] = None
            st.rerun()
        st.divider()

        menu = st.radio("Navigation", ["Dashboard", "Nouveau Bilan", "Mes Clients", "Paramètres Cabinet"])

    # PAGE : DASHBOARD
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

    # PAGE : NOUVEAU BILAN
    elif menu == "Nouveau Bilan":
        st.title("📄 Édition d'un Bilan Client")
        
        with st.form("form_bilan"):
            nom_client = st.text_input("Nom du Client / Raison Sociale")
            annee = st.text_input("Exercice", "2025")
            ca = st.number_input("Chiffre d'Affaires HT (€)", value=100000.0)
            charges = st.number_input("Total des Charges (€)", value=70000.0)
            btn_save = st.form_submit_button("Enregistrer le Bilan & Générer PDF")

        if btn_save:
            resultat = ca - charges
            # Sauvegarde isolée en BDD avec le user_id du cabinet connecté
            supabase.table("bilans").insert({
                "user_id": user_id,
                "nom_client": nom_client,
                "annee": annee,
                "ca": ca,
                "resultat": resultat
            }).execute()
            st.success(f"Bilan de {nom_client} sauvegardé dans votre espace cabinet !")

    # PAGE : MES CLIENTS
    elif menu == "Mes Clients":
        st.title("📂 Liste de vos clients")
        bilans_data = supabase.table("bilans").select("*").eq("user_id", user_id).execute().data
        if bilans_data:
            st.dataframe(pd.DataFrame(bilans_data), use_container_width=True)
        else:
            st.info("Aucun bilan enregistré pour le moment.")

    # PAGE : PARAMÈTRES
    elif menu == "Paramètres Cabinet":
        st.title("⚙️ Configuration de votre Cabinet")
        nouveau_nom = st.text_input("Nom du Cabinet", value=nom_cabinet_actuel)
        if st.button("Mettre à jour"):
            supabase.table("cabinets").update({"nom_cabinet": nouveau_nom}).eq("user_id", user_id).execute()
            st.success("Paramètres mis à jour !")
            st.rerun()
