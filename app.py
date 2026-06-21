# pyrefly: ignore [missing-import]
import streamlit as st
import sqlite3
import json
import math
from datetime import datetime

# Setup Page Configuration
st.set_page_config(
    page_title="CarbonPulse - Carbon Footprint Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "carbonpulse.db"

# Emission Conversion Constants (EPA / GHG Protocol)
EMISSION_FACTORS = {
    "transport": {
        "Petrol": 0.170,
        "Diesel": 0.171,
        "Hybrid": 0.100,
        "EV": 0.050,
        "None": 0.0,
        "publicTransit": 0.030,
        "shortHaulFlight": 150.0,
        "longHaulFlight": 800.0
    },
    "energy": {
        "electricityGrid": 0.380,
        "Natural Gas": 0.200,
        "Heating Oil": 0.270,
        "Electricity": 0.130,
        "Biomass": 0.020,
        "None": 0.0
    },
    "diet": {
        "High Meat": 2500.0,
        "Medium Meat": 2000.0,
        "Low Meat": 1500.0,
        "Pescatarian": 1300.0,
        "Vegetarian": 1100.0,
        "Vegan": 700.0
    },
    "goodsAndWaste": {
        "spendingPerDollar": 0.120,
        "wasteBaseAnnual": 500.0,
        "compostingReduction": 0.10,
        "recyclingReduction": {
            "None": 0.0,
            "Some": 0.10,
            "Most": 0.20,
            "All": 0.30
        }
    }
}

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            transport REAL NOT NULL,
            energy REAL NOT NULL,
            diet REAL NOT NULL,
            waste REAL NOT NULL,
            total REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Database Functions
def save_calculation(transport, energy, diet, waste, total):
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO calculations (timestamp, transport, energy, diet, waste, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, transport, energy, diet, waste, total))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calculations ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history

def delete_entry(entry_id):
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calculations WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

# Theme CSS Injection
def inject_custom_styles(theme_mode):
    if theme_mode == "Dark":
        bg_color = "#090D10"
        card_bg = "rgba(18, 26, 33, 0.6)"
        card_border = "rgba(255, 255, 255, 0.05)"
        text_color = "#F8FAFC"
        text_dim = "#94A3B8"
        accent_color = "#10B981"
        st_card = "#121A21"
    else:
        bg_color = "#F8FAFC"
        card_bg = "#FFFFFF"
        card_border = "#E2E8F0"
        text_color = "#0F172A"
        text_dim = "#64748B"
        accent_color = "#059669"
        st_card = "#FFFFFF"

    css = f"""
    <style>
    /* Global Overrides */
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    h1, h2, h3, h4, p, span, label, div {{
        color: {text_color} !important;
    }}
    .stHeader {{
        background-color: transparent !important;
    }}
    
    /* Sleek Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {card_bg} !important;
        border: 1px solid {card_border} !important;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.03) !important;
        border-radius: 0.75rem !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Styled Input Boxes */
    input, select, textarea, div[role="combobox"] {{
        background-color: {st_card} !important;
        border: 1px solid {card_border} !important;
        color: {text_color} !important;
        border-radius: 0.375rem !important;
    }}
    
    /* Helper styling */
    .helper-text {{
        font-size: 9px !important;
        color: {text_dim} !important;
        margin-top: 2px !important;
        display: block !important;
        line-height: normal !important;
    }}
    
    .section-title {{
        font-size: 12px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        border-bottom: 1px solid {card_border} !important;
        padding-bottom: 0.25rem !important;
        margin-bottom: 0.75rem !important;
        color: {accent_color} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Main Application Initialization
init_db()

# Sidebar controls
with st.sidebar:
    st.markdown("### Settings")
    theme = st.selectbox("Theme Mode", ["Light", "Dark"], index=0)
    if st.button("Reset Estimator"):
        st.rerun()

# Apply the theme styling
inject_custom_styles(theme)

if theme == "Dark":
    bg_color = "#090D10"
    card_border = "rgba(255, 255, 255, 0.05)"
    text_color = "#F8FAFC"
else:
    bg_color = "#F8FAFC"
    card_border = "#E2E8F0"
    text_color = "#0F172A"

# Header Section
col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.markdown(
        f'<div style="background: rgba(5,150,105,0.1); border: 1px solid rgba(5,150,105,0.25); border-radius: 6px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: #059669; font-size: 18px;">🌱</div>',
        unsafe_allow_html=True
    )
with col_title:
    st.markdown(
        f'<h1 style="font-size: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; padding-top: 4px;">CarbonPulse</h1>',
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Split Layout
col_left, col_right = st.columns([5, 7])

# LEFT COLUMN: Estimator Form
with col_left:
    with st.container(border=True):
        st.markdown("<h2 style='font-size: 16px; font-weight: 700; margin-bottom: 2px;'>Footprint Estimator</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 11px; margin-bottom: 20px;'>Adjust inputs below to update your metrics in real-time.</p>", unsafe_allow_html=True)

        # Category 1: Transportation
        st.markdown('<div class="section-title">1. Transportation</div>', unsafe_allow_html=True)
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            car_dist = st.number_input("Car Travel (km / week)", min_value=0.0, value=0.0, step=10.0, help="Commutes, weekend trips, etc.")
            st.markdown('<span class="helper-text">Weekly driving distance</span>', unsafe_allow_html=True)
        with t_col2:
            car_fuel = st.selectbox("Car Fuel Type", ["None", "Petrol", "Diesel", "Hybrid", "EV"])
            st.markdown('<span class="helper-text">Fuel efficiency factor</span>', unsafe_allow_html=True)

        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            transit_dist = st.number_input("Transit (km / week)", min_value=0.0, value=0.0, step=5.0)
            st.markdown('<span class="helper-text">Bus, train, rail</span>', unsafe_allow_html=True)
        with f_col2:
            short_flights = st.number_input("Short Flights (/ yr)", min_value=0, value=0, step=1)
            st.markdown('<span class="helper-text">Under 3 hours</span>', unsafe_allow_html=True)
        with f_col3:
            long_flights = st.number_input("Long Flights (/ yr)", min_value=0, value=0, step=1)
            st.markdown('<span class="helper-text">Over 3 hours</span>', unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Category 2: Home Energy
        st.markdown('<div class="section-title">2. Home Energy</div>', unsafe_allow_html=True)
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            elec_kwh = st.number_input("Grid Electricity (kWh / month)", min_value=0.0, value=0.0, step=50.0)
            st.markdown('<span class="helper-text">Monthly power bill usage</span>', unsafe_allow_html=True)
        with e_col2:
            green_pct = st.number_input("Green Share (%)", min_value=0, max_value=100, value=0, step=5)
            st.markdown('<span class="helper-text">Renewable tariff portion</span>', unsafe_allow_html=True)

        h_col1, h_col2 = st.columns(2)
        with h_col1:
            heat_fuel = st.selectbox("Heating Fuel", ["None", "Natural Gas", "Heating Oil", "Electricity", "Biomass"])
            st.markdown('<span class="helper-text">Heating method</span>', unsafe_allow_html=True)
        with h_col2:
            heat_kwh = st.number_input(
                "Heating Usage (kWh / month)", 
                min_value=0.0, 
                value=0.0, 
                step=50.0,
                disabled=(heat_fuel == "None")
            )
            st.markdown('<span class="helper-text">Monthly heating consumption</span>', unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Category 3: Dietary Habits
        st.markdown('<div class="section-title">3. Dietary Habits</div>', unsafe_allow_html=True)
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            diet_type = st.selectbox(
                "Diet Profile", 
                ["Medium Meat", "High Meat", "Low Meat", "Pescatarian", "Vegetarian", "Vegan"]
            )
            st.markdown('<span class="helper-text">Primary food profile</span>', unsafe_allow_html=True)
        with d_col2:
            local_food = st.slider("Local Food Focus (%)", min_value=0, max_value=100, value=0, step=10)
            st.markdown('<span class="helper-text">Ration from regional farms</span>', unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Category 4: Goods & Waste
        st.markdown('<div class="section-title">4. Goods & Waste</div>', unsafe_allow_html=True)
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            goods_spend = st.number_input("Goods Spend ($ / month)", min_value=0.0, value=0.0, step=20.0)
            st.markdown('<span class="helper-text">Clothes, electronics, appliances</span>', unsafe_allow_html=True)
        with w_col2:
            recycle_level = st.selectbox("Recycling Level", ["None", "Some", "Most", "All"])
            st.markdown('<span class="helper-text">Trash separation level</span>', unsafe_allow_html=True)

        compost_waste = st.checkbox("We compost organic food waste", value=False)
        st.markdown('<span class="helper-text">Prevents organic landfill gas generation</span>', unsafe_allow_html=True)

# Calculate Emissions Real-time
# Transport
weeks_per_year = 52
months_per_year = 12

car_factor = EMISSION_FACTORS["transport"][car_fuel]
car_emissions = car_dist * weeks_per_year * car_factor
transit_emissions = transit_dist * weeks_per_year * EMISSION_FACTORS["transport"]["publicTransit"]
short_flight_emissions = short_flights * EMISSION_FACTORS["transport"]["shortHaulFlight"]
long_flight_emissions = long_flights * EMISSION_FACTORS["transport"]["longHaulFlight"]
transport_total = car_emissions + transit_emissions + short_flight_emissions + long_flight_emissions

# Energy
grid_factor = EMISSION_FACTORS["energy"]["electricityGrid"]
net_grid_multiplier = 1.0 - (green_pct / 100.0)
electricity_emissions = (elec_kwh * months_per_year) * grid_factor * net_grid_multiplier

heating_factor = EMISSION_FACTORS["energy"][heat_fuel]
heating_emissions = (heat_kwh * months_per_year) * heating_factor
energy_total = electricity_emissions + heating_emissions

# Diet
diet_base = EMISSION_FACTORS["diet"][diet_type]
local_reduction_multiplier = 1.0 - (local_food / 100.0) * 0.10
diet_total = diet_base * local_reduction_multiplier

# Waste & Goods
spending_emissions = (goods_spend * months_per_year) * EMISSION_FACTORS["goodsAndWaste"]["spendingPerDollar"]
waste_base = EMISSION_FACTORS["goodsAndWaste"]["wasteBaseAnnual"]
recycling_pct = EMISSION_FACTORS["goodsAndWaste"]["recyclingReduction"][recycle_level]
composting_pct = EMISSION_FACTORS["goodsAndWaste"]["compostingReduction"] if compost_waste else 0.0
waste_emissions = waste_base * (1.0 - recycling_pct - composting_pct)
waste_total = spending_emissions + waste_emissions

raw_total = transport_total + energy_total + diet_total + waste_total

# Dynamically generate personalized recommendations list
recommendations = []
if car_fuel in ["Petrol", "Diesel"]:
    ev_saving = round(car_dist * weeks_per_year * (car_factor - EMISSION_FACTORS["transport"]["EV"]))
    if ev_saving > 200:
        recommendations.append({
            "id": "switch_to_ev",
            "category": "transport",
            "title": "Switch to an Electric Vehicle (EV)",
            "description": f"Replace your {car_fuel.lower()} car with an EV to reduce direct commuting fuel emissions.",
            "savingValue": ev_saving,
            "icon": "Zap"
        })
    transit_saving = round(car_dist * 0.5 * weeks_per_year * (car_factor - EMISSION_FACTORS["transport"]["publicTransit"]))
    if transit_saving > 100:
        recommendations.append({
            "id": "commute_by_transit",
            "category": "transport",
            "title": "Opt for Public Transit",
            "description": "Shift 50% of your weekly car commute to public transportation (rail, bus).",
            "savingValue": transit_saving,
            "icon": "Train"
        })

if short_flights > 0 or long_flights > 0:
    flight_savings = round(
        (short_flights * EMISSION_FACTORS["transport"]["shortHaulFlight"] * 0.5) +
        (long_flights * EMISSION_FACTORS["transport"]["longHaulFlight"] * 0.25)
    )
    if flight_savings > 50:
        recommendations.append({
            "id": "reduce_flights",
            "category": "transport",
            "title": "Reduce and Offset Air Travel",
            "description": "Avoid 50% of short-haul flights by using high-speed rail, and reduce long-haul flights by 25%.",
            "savingValue": flight_savings,
            "icon": "Plane"
        })

if green_pct < 100 and elec_kwh > 50:
    green_tariff_saving = round(electricity_emissions)
    if green_tariff_saving > 100:
        recommendations.append({
            "id": "green_electricity",
            "category": "energy",
            "title": "Switch to a 100% Green Energy Tariff",
            "description": "Request a renewable energy plan from your utility provider or purchase local solar credits.",
            "savingValue": green_tariff_saving,
            "icon": "Sun"
        })

if heat_fuel in ["Natural Gas", "Heating Oil"]:
    heat_pump_saving = round((heat_kwh * months_per_year) * (heating_factor - EMISSION_FACTORS["energy"]["Electricity"]))
    if heat_pump_saving > 200:
        recommendations.append({
            "id": "install_heat_pump",
            "category": "energy",
            "title": "Upgrade to an Electric Heat Pump",
            "description": "Replace natural gas/oil furnaces with a high-efficiency electric heat pump.",
            "savingValue": heat_pump_saving,
            "icon": "Wind"
        })

if diet_type in ["High Meat", "Medium Meat"]:
    veg_saving = round(diet_base - EMISSION_FACTORS["diet"]["Vegetarian"])
    recommendations.append({
        "id": "transition_vegetarian",
        "category": "diet",
        "title": "Transition to a Vegetarian Diet",
        "description": "Replace red meat and poultry with eggs, dairy, and plant-based protein options.",
        "savingValue": veg_saving,
        "icon": "Salad"
    })
elif diet_type == "Vegetarian":
    vegan_saving = round(EMISSION_FACTORS["diet"]["Vegetarian"] - EMISSION_FACTORS["diet"]["Vegan"])
    recommendations.append({
        "id": "transition_vegan",
        "category": "diet",
        "title": "Transition to a 100% Vegan Diet",
        "description": "Eliminate eggs, dairy, and animal-derived ingredients for a fully plant-based footprint.",
        "savingValue": vegan_saving,
        "icon": "Flower"
    })

if not compost_waste:
    compost_saving = round(waste_base * EMISSION_FACTORS["goodsAndWaste"]["compostingReduction"])
    recommendations.append({
        "id": "compost_waste",
        "category": "waste",
        "title": "Start Composting Food Waste",
        "description": "Divert kitchen organic scraps from landfills to prevent methane emissions.",
        "savingValue": compost_saving,
        "icon": "Leaf"
    })

if recycle_level in ["None", "Some"]:
    recycling_saving = round(waste_base * 0.15)
    recommendations.append({
        "id": "maximize_recycling",
        "category": "waste",
        "title": "Improve Home Recycling Habits",
        "description": "Strictly separate paper, glass, metals, and plastics to maximize landfill diversion.",
        "savingValue": recycling_saving,
        "icon": "RefreshCw"
    })

if len(recommendations) < 2:
    recommendations.append({
        "id": "led_lighting",
        "category": "energy",
        "title": "Upgrade to Smart LED Bulbs",
        "description": "Replace older incandescent lighting fixtures with energy-saving smart LED bulbs.",
        "savingValue": 45,
        "icon": "Lightbulb"
    })

recommendations = sorted(recommendations, key=lambda x: x["savingValue"], reverse=True)

# RIGHT COLUMN: Visual Dashboard and Ledger History Tabs
with col_right:
    tab_dash, tab_ledger = st.tabs(["Dashboard", "History Ledger"])
    
    with tab_dash:
        with st.container(border=True):

            # Simulated Offset Selection checkboxes
            simulated_savings = 0
            adopted_ids = []

            # Display recommendations side list (offset checklist)
            st.markdown("<h3 style='font-size: 11px; font-weight: 700; margin-top: 15px; margin-bottom: 8px;'>Offset Savings Simulator</h3>", unsafe_allow_html=True)
            for rec in recommendations[:3]:
                # Adopt checkbox
                if st.checkbox(f"Adopt: {rec['title']} (-{rec['savingValue']} kg)", value=False, key=f"adopt_{rec['id']}"):
                    simulated_savings += rec["savingValue"]
                    adopted_ids.append(rec["id"])

            projected_total = max(0.0, raw_total - simulated_savings)
            projected_tons = projected_total / 1000.0

            # Visual indicator
            st.markdown("<h2 style='font-size: 15px; font-weight: 700; margin-bottom: 2px;'>Metrics Overview</h2>", unsafe_allow_html=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric(
                    label="Simulated Footprint",
                    value=f"{projected_tons:.2f} t CO2e",
                    delta=f"-{simulated_savings / 1000.0:.2f} t" if simulated_savings > 0 else None,
                    delta_color="inverse"
                )
            with m_col2:
                target_limit = 2.0
                is_under = projected_tons <= target_limit
                if is_under:
                    st.markdown(
                        f'<div style="background: rgba(5,150,105,0.08); border: 1px solid rgba(5,150,105,0.2); border-radius: 4px; padding: 8px 12px; font-size: 11px; color: #059669; font-weight: bold; text-align: center; margin-top: 10px;">✅ Below Sustainable target ({target_limit:.1f} t)</div>',
                        unsafe_allow_html=True
                    )
                else:
                    pct_over = ((projected_tons - target_limit) / target_limit) * 100
                    st.markdown(
                        f'<div style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); border-radius: 4px; padding: 8px 12px; font-size: 11px; color: #EF4444; font-weight: bold; text-align: center; margin-top: 10px;">⚠️ {pct_over:.0f}% Above Sustainable target ({target_limit:.1f} t)</div>',
                        unsafe_allow_html=True
                    )

            # Comparison Gauges
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #64748B;'>Comparative Gauges</span>", unsafe_allow_html=True)

            # Sustainable Limit Progress
            st.markdown(f"<div style='font-size: 10px; margin-top: 5px;'>Sustainable Limit: 2.0 t</div>", unsafe_allow_html=True)
            st.progress(min(1.0, projected_tons / 2.0))

            # Global Average Progress
            st.markdown(f"<div style='font-size: 10px; margin-top: 5px;'>Global Average Baseline: 4.5 t</div>", unsafe_allow_html=True)
            st.progress(min(1.0, projected_tons / 4.5))

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # Category Breakdown Progress
            st.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #64748B;'>Category Breakdown (Simulated)</span>", unsafe_allow_html=True)

            # Adjust simulated total values for progress bar display
            sim_total = max(1.0, projected_total)
            # Apply simulated proportional offsets to categories for approximation
            sim_trans = max(0.0, transport_total - (simulated_savings if "switch_to_ev" in adopted_ids or "commute_by_transit" in adopted_ids or "reduce_flights" in adopted_ids else 0.0))
            sim_energ = max(0.0, energy_total - (simulated_savings if "green_electricity" in adopted_ids or "install_heat_pump" in adopted_ids else 0.0))
            sim_diet = max(0.0, diet_total - (simulated_savings if "transition_vegetarian" in adopted_ids or "transition_vegan" in adopted_ids or "meatless_mondays" in adopted_ids else 0.0))
            sim_waste = max(0.0, waste_total - (simulated_savings if "compost_waste" in adopted_ids or "maximize_recycling" in adopted_ids or "buy_secondhand" in adopted_ids else 0.0))

            # Draw category rows
            cat_data = [
                ("Transport", sim_trans, "#059669"),
                ("Home Energy", sim_energ, "#D97706"),
                ("Diet", sim_diet, "#2563EB"),
                ("Goods & Waste", sim_waste, "#DB2777")
            ]

            for name, val, color in cat_data:
                pct = (val / sim_total) * 100.0
                st.markdown(f"<div style='font-size: 10px; margin-top: 6px; display: flex; justify-content: space-between;'><span>{name}</span><span>{val/1000.0:.2f} t ({pct:.0f}%)</span></div>", unsafe_allow_html=True)
                st.progress(val / sim_total)

            # SVG Donut Chart Visualizer (Crisp & high-performance)
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # Draw dynamic donut chart inside streamlit using markdown HTML
            radius = 60
            circumference = 2 * math.pi * radius
            accumulated_pct = 0.0
            svg_circles = ""

            colors = ["#059669", "#D97706", "#2563EB", "#DB2777"]
            values = [sim_trans, sim_energ, sim_diet, sim_waste]

            for i, val in enumerate(values):
                pct = val / sim_total
                stroke_dash = pct * circumference
                stroke_offset = circumference - (accumulated_pct / 100.0) * circumference
                accumulated_pct += pct * 100.0

                svg_circles += f'<circle cx="80" cy="80" r="{radius}" fill="none" stroke="{colors[i]}" stroke-width="12" stroke-dasharray="{stroke_dash} {circumference}" stroke-dashoffset="{stroke_offset}" stroke-linecap="round" />'

            donut_html = (
                f'<div style="display: flex; justify-content: center; align-items: center; margin-top: 10px; margin-bottom: 10px;">'
                f'<div style="position: relative; width: 140px; height: 140px;">'
                f'<svg class="transform" style="transform: rotate(-90deg); width: 140px; height: 140px;" viewBox="0 0 160 160">'
                f'<circle cx="80" cy="80" r="{radius}" fill="none" stroke="#F1F5F9" stroke-width="12" />'
                f'{svg_circles}'
                f'</svg>'
                f'<div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">'
                f'<span style="font-size: 8px; font-weight: bold; text-transform: uppercase; color: #64748B;">Total CO2e</span>'
                f'<span style="font-size: 16px; font-weight: 800; color: {text_color};">{projected_tons:.2f}t</span>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(donut_html, unsafe_allow_html=True)

            # Save Button
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Commit to History Ledger", use_container_width=True, key="save_btn"):
                if raw_total > 0:
                    # Save the simulated total projected values to history DB
                    save_calculation(sim_trans, sim_energ, sim_diet, sim_waste, projected_total)
                    st.success("Successfully committed footprint calculations to ledger!")
                    st.rerun()
                else:
                    st.error("Calculations must be greater than zero to save.")

        
    with tab_ledger:
        with st.container(border=True):

            # Load history
            hist = get_history()

            # Sparkline trend progression (SVG render)
            if len(hist) >= 2:
                st.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #64748B;'>Emission Trend Sparkline</span>", unsafe_allow_html=True)

                # Sort oldest to newest
                sorted_hist = sorted(hist, key=lambda x: x["timestamp"])

                width = 500
                height = 80
                padding = 10

                min_time = datetime.fromisoformat(sorted_hist[0]["timestamp"]).timestamp()
                max_time = datetime.fromisoformat(sorted_hist[-1]["timestamp"]).timestamp()
                time_range = max_time - min_time if max_time != min_time else 1.0

                totals = [e["total"] / 1000.0 for e in sorted_hist]
                max_val = max(max(totals), 4.0)
                min_val = min(min(totals), 0.0)
                val_range = max_val - min_val if max_val != min_val else 1.0

                svg_points = []
                for entry in sorted_hist:
                    time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    x = padding + ((time - min_time) / time_range) * (width - 2 * padding)
                    y = height - padding - ((entry["total"]/1000.0 - min_val) / val_range) * (height - 2 * padding)
                    svg_points.append(f"{x},{y}")

                points_str = " ".join(svg_points)
                target_y = height - padding - ((2.0 - min_val) / val_range) * (height - 2 * padding)

                sparkline_html = (
                    f'<div style="background: {bg_color}; border: 1px solid {card_border}; border-radius: 4px; padding: 4px; margin-top: 5px; margin-bottom: 10px;">'
                    f'<svg viewBox="0 0 500 80" style="width: 100%; height: 80px;" preserveAspectRatio="none">'
                    f'<line x1="10" y1="{target_y}" x2="490" y2="{target_y}" stroke="#EF4444" stroke-width="1" stroke-dasharray="3 3" opacity="0.6" />'
                    f'<polyline fill="none" stroke="#059669" stroke-width="2.5" points="{points_str}" stroke-linecap="round" stroke-linejoin="round" />'
                    f'</svg>'
                    f'</div>'
                )
                st.markdown(sparkline_html, unsafe_allow_html=True)

            st.markdown("<h3 style='font-size: 11px; font-weight: 700; margin-bottom: 10px;'>Calculation Entries Ledger</h3>", unsafe_allow_html=True)

            if len(hist) == 0:
                st.info("No saved entries found. Estimate and save your calculations to track history.")
            else:
                for entry in hist:
                    dt = datetime.fromisoformat(entry["timestamp"])
                    formatted_date = dt.strftime("%b %d, %Y - %H:%M")

                    # Render clean ledger row card
                    st.markdown(
                        f'<div style="border: 1px solid {card_border}; border-radius: 4px; padding: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; background: {bg_color};">'
                        f'<div>'
                        f'<span style="font-size: 11px; font-weight: bold; color: {text_color};">{formatted_date}</span><br/>'
                        f'<span style="font-size: 9px; color: #64748B;">'
                        f'Trans: {entry["transport"]/1000.0:.1f}t | '
                        f'Energy: {entry["energy"]/1000.0:.1f}t | '
                        f'Diet: {entry["diet"]/1000.0:.1f}t | '
                        f'Waste: {entry["waste"]/1000.0:.1f}t'
                        f'</span>'
                        f'</div>'
                        f'<div style="display: flex; align-items: center; gap: 15px;">'
                        f'<span style="font-size: 11px; font-weight: 800; color: #059669;">{entry["total"]/1000.0:.2f} t</span>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Delete button under row
                    if st.button("Delete Entry", key=f"del_{entry['id']}", type="secondary"):
                        delete_entry(entry["id"])
                        st.success("Entry deleted!")
                        st.rerun()

