import streamlit as st
import pandas as pd
import os
import json
import difflib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & CONSTANTS
# ==========================================
st.set_page_config(
    page_title="FitLife Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File System Paths
FILES = {
    "profile": "user_profile.json",
    "food_log": "food_log.csv",
    "exercise_log": "exercise_log.csv",
    "water_log": "water_log_detailed.csv",
    "weight_log": "weight_log.csv",
    "custom_food": "custom_foods.csv",
    "food_db": "Enhanced_Indian_Food_Nutrition.csv",
    "exercise_db": "Compendium_of_Physical_Activities_2024.csv",
    "symptom_db": "symptom_database.csv"
}

# Hydration Constants
HYDRATION_FACTORS = {
    "Water": 1.0, "Milk": 0.99, "Tea": 0.98, "Coffee": 0.90,
    "Juice": 0.95, "Soda": 0.90, "Alcohol": 0.80, "Sports Drink": 1.0
}


# ==========================================
# 2. DATABASE MANAGEMENT (Self-Healing)
# ==========================================
def initialize_databases():
    """Creates necessary files if they don't exist."""

    # 1. Logs
    if not os.path.exists(FILES["water_log"]):
        pd.DataFrame(columns=["Date", "Time", "Beverage", "Volume_ml", "Effective_Hydration_ml"]).to_csv(
            FILES["water_log"], index=False)

    if not os.path.exists(FILES["weight_log"]):
        pd.DataFrame(columns=["Date", "Weight"]).to_csv(FILES["weight_log"], index=False)

    if not os.path.exists(FILES["food_log"]):
        pd.DataFrame(
            columns=["Date", "Time", "Dish", "Meal Type", "Quantity", "Calories", "Protein", "Carbs", "Fats"]).to_csv(
            FILES["food_log"], index=False)

    if not os.path.exists(FILES["exercise_log"]):
        pd.DataFrame(columns=["Date", "Time", "Activity", "Duration", "Calories Burnt"]).to_csv(FILES["exercise_log"],
                                                                                                index=False)

    # 2. Databases (Defaults)
    if not os.path.exists(FILES["symptom_db"]):
        data = {
            "Symptom": ["Headache", "Fever", "Cold", "Indigestion", "Sore Throat", "Fatigue", "Acidity", "Insomnia",
                        "Muscle Pain"],
            "Possible Causes": ["Dehydration, Stress", "Viral Infection", "Virus", "Overeating", "Infection",
                                "Lack of Sleep", "Spicy Food", "Stress/Screen Time", "Overexertion"],
            "Remedies": ["Drink Water, Rest", "Paracetamol", "Steam", "Ginger Tea", "Salt Gargle", "Sleep", "Cold Milk",
                         "Meditation", "Hot Compress"],
            "Foods to Avoid": ["Caffeine", "Cold Water", "Ice Cream", "Oily Food", "Cold Drinks", "Sugar", "Fried Food",
                               "Caffeine at night", "Processed Food"],
            "Preferred Indian Meal": ["Khichdi", "Moong Dal Soup", "Hot Soup", "Curd Rice", "Warm Turmeric Milk",
                                      "Dal Chawal", "Banana/Toast", "Warm Milk", "Protein Salad"],
            "Tips / General Medicine": ["Sleep well", "Monitor temp", "Stay warm", "Walk after meal", "Rest voice",
                                        "Avoid screens", "Sit upright", "No screens 1hr before bed", "Stretch gently"],
            "Screen Time Link": ["High impact (Eye strain)", "No direct link", "No direct link",
                                 "Snacking while watching TV", "No direct link", "Blue light disrupts sleep",
                                 "Sedentary lifestyle", "Blue light blocks melatonin", "Poor posture"],
            "Severity Level": ["Mild", "Moderate", "Mild", "Mild", "Mild", "Moderate", "Mild", "Moderate", "Mild"],
            "Time to Relief": ["2-4 hours", "3-5 days", "1 week", "1 day", "2 days", "2 days", "2 hours", "Varies",
                               "2-3 days"],
            "Home Remedy Option": ["Lemon water", "Tulsi Tea", "Turmeric Milk", "Ajwain Water", "Honey Ginger",
                                   "Ashwagandha", "Fennel Seeds", "Chamomile Tea", "Turmeric Paste"]
        }
        pd.DataFrame(data).to_csv(FILES["symptom_db"], index=False)

    if not os.path.exists(FILES["food_db"]):
        data = {
            "Dish Name": ["Roti", "Dal Fry", "Rice", "Paneer Butter Masala", "Chicken Curry", "Egg Curry", "Dosa",
                          "Idli", "Upma", "Poha", "Sandwich (Veg)", "Oats"],
            "Calories per Serving": [120, 150, 130, 350, 400, 250, 180, 60, 200, 180, 220, 150],
            "Protein per Serving (g)": [3, 8, 2, 12, 25, 14, 4, 2, 5, 4, 6, 5],
            "Carbohydrates (g)": [20, 15, 28, 10, 5, 3, 25, 12, 30, 35, 30, 25],
            "Fats (g)": [1, 5, 0, 25, 20, 18, 6, 0, 7, 5, 8, 3],
            "Diet": ["Veg", "Veg", "Veg", "Veg", "Non-Veg", "Non-Veg", "Veg", "Veg", "Veg", "Veg", "Veg", "Veg"],
            "Serving Unit": ["1 piece", "1 bowl", "1 bowl", "1 bowl", "1 bowl", "1 bowl", "1 piece", "1 piece",
                             "1 plate", "1 plate", "1 piece", "1 bowl"],
            "Serving Weight (g)": [40, 150, 150, 200, 250, 200, 80, 40, 150, 150, 120, 150]
        }
        pd.DataFrame(data).to_csv(FILES["food_db"], index=False)

    if not os.path.exists(FILES["exercise_db"]):
        data = {"Description": ["Running (6mph)", "Walking (brisk)", "Yoga", "Cycling", "Weight Lifting", "Swimming"],
                "MET Value": [9.8, 3.5, 2.5, 7.5, 3.5, 8.0]}
        pd.DataFrame(data).to_csv(FILES["exercise_db"], index=False)


initialize_databases()


# ==========================================
# 3. CORE LOGIC & HELPERS
# ==========================================

def load_data_safe(filepath):
    """Safely loads CSVs handling empty files."""
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            if df.empty: return None
            return df
        except pd.errors.EmptyDataError:
            return None
    return None


def save_profile(name, age, gender, height, weight, activity, goal, water_goal):
    # BMR Calculation (Mifflin-St Jeor)
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    act_map = {"Sedentary": 1.2, "Lightly": 1.375, "Moderately": 1.55, "Very": 1.725, "Super": 1.9}
    tdee = bmr * act_map.get(activity.split()[0], 1.2)

    # Goal Adjustment
    if goal == "Weight Loss":
        target, macros = tdee - 500, (40, 40, 20)
    elif goal == "Weight Gain":
        target, macros = tdee + 500, (50, 25, 25)
    elif goal == "Muscle Gain":
        target, macros = tdee + 250, (45, 35, 20)
    else:
        target, macros = tdee, (50, 20, 30)

    rec_prot = int((target * (macros[1] / 100)) / 4)

    profile = {
        "Name": name, "Age": age, "Gender": gender, "Height": height,
        "Start_Weight": weight, "Current_Weight": weight,
        "Activity": activity, "Goal": goal,
        "Targets": {"Calories": int(target), "Protein": rec_prot, "Water": water_goal, "Macros_Split": macros}
    }

    with open(FILES["profile"], "w") as f:
        json.dump(profile, f)

    # Initialize Weight Log
    if not os.path.exists(FILES["weight_log"]) or os.stat(FILES["weight_log"]).st_size == 0:
        pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Weight": weight}]).to_csv(FILES["weight_log"],
                                                                                               index=False)

    st.session_state["user"] = profile
    st.rerun()


def load_profile():
    if os.path.exists(FILES["profile"]):
        with open(FILES["profile"], "r") as f:
            profile = json.load(f)
        # Auto-Fix for old profiles
        if "Start_Weight" not in profile:
            profile["Start_Weight"] = profile.get("Weight", 70)
            profile["Current_Weight"] = profile.get("Weight", 70)
            with open(FILES["profile"], "w") as f: json.dump(profile, f)
        return profile
    return None


def log_data(file, data_dict):
    df_new = pd.DataFrame([data_dict])
    if not os.path.exists(file) or os.stat(file).st_size == 0:
        df_new.to_csv(file, index=False)
    else:
        df_new.to_csv(file, mode='a', header=False, index=False)


def log_beverage_advanced(date_obj, time_obj, beverage, volume):
    factor = HYDRATION_FACTORS.get(beverage, 1.0)
    eff_vol = volume * factor
    log_data(FILES["water_log"], {
        "Date": date_obj.strftime("%Y-%m-%d"),
        "Time": time_obj.strftime("%H:%M:%S"),
        "Beverage": beverage, "Volume_ml": volume, "Effective_Hydration_ml": eff_vol
    })
    st.success("Logged!")


def calculate_streak(df_food):
    """Calculates consecutive days logged, handling NaT errors."""
    if df_food is None or df_food.empty: return 0

    # Convert to datetime and drop invalid dates
    df_food["DateObj"] = pd.to_datetime(df_food["Date"], errors='coerce')
    valid_dates = df_food["DateObj"].dropna().dt.date.unique()

    if len(valid_dates) == 0:
        return 0

    valid_dates.sort()

    streak = 0
    check_date = datetime.now().date()

    # Check today or yesterday to start streak
    if check_date not in valid_dates:
        check_date -= timedelta(days=1)
        if check_date not in valid_dates: return 0

    while check_date in valid_dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak


def get_daily_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {"eaten": 0, "protein": 0, "burnt": 0}

    df_food = load_data_safe(FILES["food_log"])
    if df_food is not None:
        day = df_food[df_food["Date"] == today]
        stats["eaten"] = day["Calories"].sum()
        stats["protein"] = day["Protein"].sum()

    df_ex = load_data_safe(FILES["exercise_log"])
    if df_ex is not None:
        day = df_ex[df_ex["Date"] == today]
        stats["burnt"] = day["Calories Burnt"].sum()
    return stats


def generate_meal_plan(df_food, target_cals, goal, diet_pref, days=3):
    plan = {}
    budgets = {"Breakfast": 0.25, "Lunch": 0.35, "Dinner": 0.30, "Snack": 0.10}

    if diet_pref == "Vegetarian":
        df_food = df_food[df_food["Diet"] == "Veg"]

    if goal == "Muscle Gain":
        df_food = df_food.sort_values(by="Protein per Serving (g)", ascending=False)
    elif goal == "Weight Loss":
        df_food = df_food.sort_values(by="Calories per Serving", ascending=True)

    for day in range(1, days + 1):
        day_meals = []
        total_day = 0
        for meal, ratio in budgets.items():
            budget = target_cals * ratio
            candidates = df_food[
                (df_food["Calories per Serving"] >= budget - 150) & (df_food["Calories per Serving"] <= budget + 150)]
            if candidates.empty: candidates = df_food  # Fallback

            selected = candidates.sample(1).iloc[0]
            qty = max(0.5, min(round(budget / selected["Calories per Serving"], 1), 3.0))
            cals = int(selected["Calories per Serving"] * qty)

            day_meals.append({
                "Type": meal, "Dish": selected["Dish Name"], "Qty": qty,
                "Unit": selected.get("Serving Unit", "svg"), "Cals": cals, "Diet": selected.get("Diet", "Veg")
            })
            total_day += cals
        plan[f"Day {day}"] = {"Meals": day_meals, "Total": total_day}
    return plan


# @st.cache_data
def load_databases():
    df_food = load_data_safe(FILES["food_db"])
    df_custom = load_data_safe(FILES["custom_food"])

    if df_food is not None and df_custom is not None:
        df_food = pd.concat([df_custom, df_food], ignore_index=True)
    elif df_custom is not None:
        df_food = df_custom

    df_ex = load_data_safe(FILES["exercise_db"])
    df_sym = load_data_safe(FILES["symptom_db"])

    # Ensure Diet column exists
    if df_food is not None and "Diet" not in df_food.columns:
        df_food["Diet"] = df_food["Dish Name"].apply(
            lambda x: "Non-Veg" if any(k in str(x).lower() for k in ["chicken", "egg", "fish", "mutton"]) else "Veg")

    return df_food, df_ex, df_sym


# ==========================================
# 4. MAIN APP EXECUTION
# ==========================================

if "user" not in st.session_state:
    st.session_state["user"] = load_profile()
user = st.session_state["user"]

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
                save_profile(name, age, gender, height, weight, act, goal, w_goal)
            else:
                st.error("Please enter your name.")

# --- VIEW 2: MAIN DASHBOARD ---
else:
    df_food, df_ex, df_sym = load_databases()

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

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("🏠 Your Daily Snapshot")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories Eaten", f"{stats['eaten']:.0f}", f"Target: {target}")
        with col2:
            st.metric("Calories Burnt", f"{stats['burnt']:.0f}", "Active")
        with col3:
            st.metric("Protein", f"{stats['protein']:.0f}g", f"Goal: {user['Targets']['Protein']}g")

        df_w = load_data_safe(FILES["water_log"])
        w_today = 0
        if df_w is not None:
            # Filter for today to avoid summing all history
            df_w["Date"] = pd.to_datetime(df_w["Date"], errors='coerce')
            today = datetime.now().strftime("%Y-%m-%d")
            w_today = df_w[df_w["Date"] == today]["Effective_Hydration_ml"].sum()
        with col4:
            st.metric("Hydration", f"{w_today:.0f} ml", f"Goal: {user['Targets']['Water']} ml")

        st.divider()

        c_ring, c_streak = st.columns([2, 1])
        with c_ring:
            st.subheader("🎯 Today's Progress")
            fig = go.Figure(go.Pie(
                labels=['Eaten', 'Remaining'],
                values=[net, max(0, target - net)],
                hole=.7, marker_colors=['#FF4B4B', '#F0F2F6'], sort=False
            ))
            fig.update_layout(
                annotations=[dict(text=f"{int(net)}<br>kcal", x=0.5, y=0.5, font_size=20, showarrow=False)],
                showlegend=False, height=220, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with c_streak:
            df_f = load_data_safe(FILES["food_log"])
            streak = calculate_streak(df_f)
            st.subheader("🔥 Streak")
            st.metric("Consecutive Days", f"{streak} 🔥")

            st.subheader("⚖️ Weight")
            cw = user.get("Current_Weight", user["Start_Weight"])
            st.metric("Current", f"{cw} kg", delta=f"{cw - user['Start_Weight']:.1f} kg")

    # --- 🍎 FOOD LOG ---
    elif page == "🍎 Food Log":
        st.title("🍎 Nutrition Logger")
        tab1, tab2 = st.tabs(["Log Meal", "Add Custom Food"])

        with tab1:
            c_d, c_t, c_m = st.columns(3)
            with c_d:
                log_date = st.date_input("Date", datetime.now())
            with c_t:
                log_time = st.time_input("Time", datetime.now())
            with c_m:
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            st.divider()

            search = st.text_input("Search Database", placeholder="Type 'Paneer', 'Rice', 'Chicken'...")
            if search and df_food is not None:
                matches = df_food[df_food["Dish Name"].str.lower().str.contains(search.lower())]
                if not matches.empty:
                    dish = st.selectbox("Select Dish", matches["Dish Name"].unique())
                    sel = df_food[df_food["Dish Name"] == dish].iloc[0]
                    qty = st.number_input("Quantity (Servings)", 0.5, 10.0, 1.0)
                    cals = sel.get("Calories per Serving", 0) * qty
                    st.info(f"Total: {cals:.0f} kcal | Diet: {sel.get('Diet', 'Veg')}")

                    if st.button("Add to Log"):
                        log_data(FILES["food_log"], {
                            "Date": log_date.strftime("%Y-%m-%d"),
                            "Time": log_time.strftime("%H:%M:%S"),
                            "Dish": dish, "Meal Type": meal_type, "Quantity": qty,
                            "Calories": cals, "Protein": sel.get("Protein per Serving (g)", 0) * qty,
                            "Carbs": sel.get("Carbohydrates (g)", 0) * qty, "Fats": sel.get("Fats (g)", 0) * qty
                        })
                        st.success("Logged Successfully!")

        with tab2:
            with st.form("new_food"):
                nm = st.text_input("Name");
                diet = st.radio("Type", ["Veg", "Non-Veg"])
                c1, c2 = st.columns(2)
                cal = c1.number_input("Calories", 0);
                prot = c2.number_input("Protein", 0.0)
                c3, c4 = st.columns(2)
                carb = c3.number_input("Carbs", 0.0);
                fat = c4.number_input("Fats", 0.0)
                if st.form_submit_button("Save Food"):
                    df = pd.DataFrame([{"Dish Name": nm, "Calories per Serving": cal, "Protein per Serving (g)": prot,
                                        "Carbohydrates (g)": carb, "Fats (g)": fat, "Diet": diet}])
                    mode = 'a' if os.path.exists(FILES["custom_food"]) else 'w'
                    header = not os.path.exists(FILES["custom_food"])
                    df.to_csv(FILES["custom_food"], mode=mode, header=header, index=False)
                    st.success("Saved!")
                    st.cache_data.clear()

    # --- 💧 HYDRATION ---
    elif page == "💧 Hydration":
        st.title("💧 Hydration Tracker")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Log Drink")
            h_date = st.date_input("Date", datetime.now())
            h_time = st.time_input("Time", datetime.now())
            h_bev = st.selectbox("Beverage", list(HYDRATION_FACTORS.keys()))
            h_vol = st.number_input("Volume (ml)", 50, 2000, 250, step=50)
            if st.button("Log Drink"): log_beverage_advanced(h_date, h_time, h_bev, h_vol)

            st.markdown("#### Quick Add")
            if st.button("💧 250ml Water"): log_beverage_advanced(datetime.now(), datetime.now(), "Water", 250)

        with c2:
            st.subheader("History")
            df_w = load_data_safe(FILES["water_log"])
            if df_w is not None:
                d_str = h_date.strftime("%Y-%m-%d")
                # Ensure date column is string for filtering
                df_w["Date"] = df_w["Date"].astype(str)
                day_data = df_w[df_w["Date"] == d_str]
                if not day_data.empty:
                    tot = day_data["Effective_Hydration_ml"].sum()
                    st.metric("Effective Hydration", f"{tot:.0f} ml", f"Goal: {user['Targets']['Water']} ml")
                    st.progress(min(tot / user['Targets']['Water'], 1.0))
                    st.plotly_chart(px.pie(day_data, values="Volume_ml", names="Beverage", hole=0.4),
                                    use_container_width=True)
                else:
                    st.info("No data for this date.")

    # --- 🏃 FITNESS ---
    elif page == "🏃 Fitness":
        st.title("🏃 Fitness Tracker")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Log Workout")
            ex_date = st.date_input("Date", datetime.now())
            ex_time = st.time_input("Time", datetime.now())
            search_ex = st.text_input("Search Activity")
            if search_ex and df_ex is not None:
                matches = df_ex[df_ex["Description"].str.lower().str.contains(search_ex.lower())]
                if not matches.empty:
                    act = st.selectbox("Activity", matches["Description"].unique())
                    met = matches[matches["Description"] == act].iloc[0]["MET Value"]
                    mins = st.number_input("Duration (Mins)", 10, 180, 30)
                    burn = met * user["Current_Weight"] * (mins / 60)
                    st.success(f"Estimated Burn: {burn:.0f} kcal")
                    if st.button("Log Workout"):
                        log_data(FILES["exercise_log"],
                                 {"Date": ex_date.strftime("%Y-%m-%d"), "Time": ex_time.strftime("%H:%M:%S"),
                                  "Activity": act, "Duration": mins, "Calories Burnt": burn})
                        st.success("Logged!")
        with c2:
            st.subheader("History")
            df_ex_log = load_data_safe(FILES["exercise_log"])
            if df_ex_log is not None:
                st.dataframe(df_ex_log.sort_index(ascending=False), use_container_width=True)

    # --- 🔮 MEAL PLANNER ---
    elif page == "🔮 Meal Planner":
        st.title("🔮 AI Meal Planner")
        c1, c2 = st.columns([1, 3])
        with c1:
            days = st.slider("Days", 1, 7, 3)
            pref = st.radio("Diet", ["Vegetarian", "Non-Vegetarian"])
            if st.button("Generate Plan"):
                st.session_state["plan"] = generate_meal_plan(df_food, user['Targets']['Calories'], user['Goal'], pref,
                                                              days)
        with c2:
            if "plan" in st.session_state:
                for day, det in st.session_state["plan"].items():
                    with st.expander(f"📅 {day} - {det['Total']} kcal"):
                        for m in det["Meals"]:
                            st.write(f"**{m['Type']}**: {m['Qty']} x {m['Dish']} ({m['Diet']})")
                            st.caption(f"{m['Cals']} kcal")

    # --- 🩺 HEALTH ADVISOR ---
    elif page == "🩺 Health Advisor":
        st.title("🩺 Advanced Symptom Checker")
        df_sym=load_data_safe(FILES["symptom_db"])
        if df_sym is not None:
            sym = st.selectbox("I am feeling...", ["Select..."] + sorted(df_sym["Symptom"].unique().tolist()))
            if sym != "Select...":
                res = df_sym[df_sym["Symptom"] == sym].iloc[0]
                st.info(
                    f"**Severity:** {res.get('Severity Level', 'N/A')} | **Recovery:** {res.get('Time to Relief', 'N/A')}")
                c1, c2 = st.columns(2)
                with c1:
                    st.warning(f"**Causes:** {res['Possible Causes']}")
                    st.info(f"**Remedies:** {res['Remedies']}")
                with c2:
                    st.error(f"**Avoid:** {res['Foods to Avoid']}")
                    st.success(f"**Diet:** {res['Preferred Indian Meal']}")
                with st.expander("💡 Lifestyle & Home Remedies"):
                    st.write(f"**Home Remedy:** {res.get('Home Remedy Option', 'N/A')}")
                    st.write(f"**Tip:** {res['Tips / General Medicine']}")
                    st.write(f"**Screen Time:** {res.get('Screen Time Link', 'N/A')}")

    # --- 📈 ANALYTICS ---
    elif page == "📈 Analytics":
        st.title("📈 Comprehensive Analytics")
        df_f = load_data_safe(FILES["food_log"])

        if df_f is not None:
            df_f["DateObj"] = pd.to_datetime(df_f["Date"], errors='coerce')

            # Weekly Summary
            st.subheader("📅 Weekly Summary")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            # Filter out NaT if date parsing failed
            df_f = df_f.dropna(subset=["DateObj"])
            weekly = df_f[df_f["DateObj"] >= start_date]

            if not weekly.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Cals (7d)", f"{weekly['Calories'].sum():.0f}")
                c2.metric("Avg Daily Cals", f"{weekly['Calories'].sum() / 7:.0f}")
                c3.metric("Total Protein", f"{weekly['Protein'].sum():.0f}g")

            st.divider()
            c_bar, c_pie = st.columns([2, 1])
            with c_bar:
                st.subheader("🔥 Daily Calories")
                daily_sum = df_f.groupby("Date")["Calories"].sum().reset_index()
                st.plotly_chart(px.bar(daily_sum, x="Date", y="Calories", color="Calories"), use_container_width=True)

            with c_pie:
                st.subheader("🥗 Macro Split")
                d = st.date_input("Select Date", datetime.now())
                d_str = d.strftime("%Y-%m-%d")
                d_df = df_f[df_f["Date"] == d_str]
                if not d_df.empty:
                    c, p, f = d_df.get("Carbs", 0).sum(), d_df.get("Protein", 0).sum(), d_df.get("Fats", 0).sum()
                    if c + p + f > 0: st.plotly_chart(px.pie(values=[c, p, f], names=["Carb", "Prot", "Fat"], hole=0.4),
                                                      use_container_width=True)
                else:
                    st.info("No logs for date.")

            st.divider()
            st.subheader("💧 Hydration History")
            df_w = load_data_safe(FILES["water_log"])
            if df_w is not None:
                st.plotly_chart(px.bar(df_w.groupby("Date")["Effective_Hydration_ml"].sum().reset_index(), x="Date",
                                       y="Effective_Hydration_ml"), use_container_width=True)
        else:
            st.info("Start logging food to see analytics.")

    # --- ⚙️ SETTINGS ---
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        with st.expander("✏️ Edit Profile"):
            new_w = st.number_input("Update Weight (kg)", value=float(user['Current_Weight']))
            new_h = st.number_input("Update Height (cm)", value=float(user['Height']))
            new_age = st.number_input("Update Age", value=int(user['Age']))
            new_act = st.selectbox("Update Activity",
                                   ["Sedentary (Office)", "Lightly Active", "Moderately Active", "Very Active",
                                    "Super Active"], index=0)
            new_goal = st.selectbox("Update Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain"], index=0)

            if st.button("Save Profile Changes"):
                save_profile(user['Name'], new_age, user['Gender'], new_h, new_w, new_act, new_goal,
                             user['Targets']['Water'])
                st.success("Profile Updated!")

        st.divider()
        st.subheader("⬇️ Export Data")
        c1, c2, c3 = st.columns(3)
        if os.path.exists(FILES["food_log"]):
            with open(FILES["food_log"], "rb") as f: c1.download_button("Download Food Log", f, "food_log.csv")
        if os.path.exists(FILES["exercise_log"]):
            with open(FILES["exercise_log"], "rb") as f: c2.download_button("Download Exercise Log", f,
                                                                            "exercise_log.csv")
        if os.path.exists(FILES["weight_log"]):
            with open(FILES["weight_log"], "rb") as f: c3.download_button("Download Weight Log", f, "weight_log.csv")

        st.divider()
        if st.button("🗑️ Reset All Data (Irreversible)", type="primary"):
            for f in FILES.values():
                if "db" not in f and os.path.exists(f): os.remove(f)
            del st.session_state["user"]
            st.rerun()