import streamlit as st
import os
from src.config import FILES
from src.database import initialize_databases
from src.utils import load_profile, save_profile, get_daily_stats, load_all_databases
from src.views import (
    show_dashboard, show_food_log, show_hydration, show_fitness,
    show_meal_planner, show_health_advisor, show_analytics, show_settings
)

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="FitLife Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INITIALIZATION
# ==========================================
initialize_databases()

if "user" not in st.session_state:
    st.session_state["user"] = load_profile()
user = st.session_state["user"]

# ==========================================
# 3. MAIN ROUTING
# ==========================================

# --- VIEW 1: SETUP SCREEN (If no user) ---
if user is None:
    st.title("🚀 Welcome to FitLife Pro")
    st.markdown("### Let's build your personalized health plan.")

    with st.form("setup_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("First Name")
        gender = c1.radio("Gender", ["Male", "Female"], horizontal=True)
        age = c1.number_input("Age", 10, 100, 25)
        weight = c2.number_input("Weight (kg)", 30, 200, 70)
        height = c2.number_input("Height (cm)", 100, 250, 170)
        st.markdown("---")
        act = st.selectbox("Activity Level",
                           ["Sedentary (Office)", "Lightly Active", "Moderately Active", "Very Active", "Super Active"])
        goal = st.selectbox("Your Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain"])
        w_goal = st.number_input("Daily Water Goal (ml)", 1000, 5000, 2500)

        if st.form_submit_button("Start My Journey"):
            if name:
                new_profile = save_profile(name, age, gender, height, weight, act, goal, w_goal)
                st.session_state["user"] = new_profile
                st.rerun()
            else:
                st.error("Please enter your name.")

# --- VIEW 2: MAIN DASHBOARD ---
else:
    # Load Databases
    df_food, df_ex, df_sym = load_all_databases()

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title(f"👤 {user['Name']}")
        st.caption(f"Goal: {user['Goal']}")

        page = st.radio(
            "Navigate",
            ["🏠 Dashboard", "🍎 Food Log", "💧 Hydration", "🏃 Fitness", "🔮 Meal Planner", "🩺 Health Advisor",
             "📈 Analytics", "⚙️ Settings"],
        )

        st.markdown("---")
        # Sidebar Progress
        stats = get_daily_stats()
        net = stats['eaten'] - stats['burnt']
        target = user['Targets']['Calories']

        st.metric("Net Calories", f"{net:.0f}", delta=f"{target - net:.0f} left")
        st.progress(min(max(net / target, 0.0), 1.0))

    # --- PAGE ROUTING ---
    if page == "🏠 Dashboard":
        show_dashboard(user)
    elif page == "🍎 Food Log":
        show_food_log(df_food)
    elif page == "💧 Hydration":
        show_hydration(user)
    elif page == "🏃 Fitness":
        show_fitness(user, df_ex)
    elif page == "🔮 Meal Planner":
        show_meal_planner(user, df_food)
    elif page == "🩺 Health Advisor":
        show_health_advisor(df_sym)
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "⚙️ Settings":
        show_settings(user)