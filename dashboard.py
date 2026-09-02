import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="GeoAlert Dashboard", page_icon="⛰️", layout="wide")

API_URL = "http://localhost:5000"

st.title("⛰️ GeoAlert - Landslide Early Warning System")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Simulation Controls")
    node_id = st.text_input("Node ID", value="demo-node-01")
    scenario = st.selectbox("Scenario", ["safe", "warning", "critical", "random"])
    
    if st.button("Trigger Simulation Event", type="primary"):
        try:
            res = requests.post(f"{API_URL}/api/simulate", json={"node_id": node_id, "scenario": scenario})
            if res.status_code == 200:
                st.success("Reading injected successfully!")
            else:
                st.error("Failed to inject simulation reading.")
        except Exception as e:
            st.error(f"Connection error: {e}")

with col2:
    st.subheader("Live Status")
    try:
        res = requests.get(f"{API_URL}/api/latest", params={"node_id": node_id})
        if res.status_code == 200 and res.json():
            latest = res.json()
            risk = latest.get("risk_name", "Unknown")
            color = "green" if risk == "Safe" else ("orange" if risk == "Warning" else "red")
            st.markdown(f"### Current Risk Level: :{color}[{risk}]")
            st.metric("Soil Moisture", f"{latest.get('soil_moisture_pct', 0)}%")
            st.metric("Tilt Angle", f"{latest.get('tilt_deg', 0)}°")
            st.metric("24h Rainfall", f"{latest.get('rainfall_24h_mm', 0)} mm")
        else:
            st.info("No sensor data available yet. Trigger a simulation.")
    except Exception:
        st.warning("Backend server offline. Start Flask (`python app.py`).")

st.divider()
st.subheader("Recent Sensor History")
try:
    hist_res = requests.get(f"{API_URL}/api/history", params={"node_id": node_id, "hours": 24})
    if hist_res.status_code == 200:
        data = hist_res.json()
        if data:
            df = pd.DataFrame(data)
            st.line_chart(df, x="timestamp", y=["soil_moisture_pct", "tilt_deg"])
        else:
            st.info("No historical data found.")
except Exception:
    pass

st.subheader("System Alerts & Gemini Agent Logs")
try:
    alert_res = requests.get(f"{API_URL}/api/alerts")
    if alert_res.status_code == 200:
        alerts = alert_res.json()
        if alerts:
            for a in alerts:
                st.warning(f"**[{a['timestamp']}] Node {a['node_id']} ({a['severity']})**: {a['message']}\n\n*Narrative:* {a['narrative']}")
        else:
            st.success("No active alerts.")
except Exception:
    pass
