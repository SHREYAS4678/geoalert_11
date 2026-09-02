import os
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)

def run_agent(node_id: str, features: dict, label: int, name: str, confidence: float, per_model: dict):
    narrative = f"Node {node_id} reported status as {name} with {confidence*100:.1f}% model confidence. Soil moisture is at {features.get('soil_moisture_pct')}% and tilt is {features.get('tilt_deg')}°."
    
    alert_triggered = label > 0
    send_log = []
    
    if alert_triggered:
        severity = "HIGH" if label == 2 else "MEDIUM"
        send_log.append({
            "severity": severity,
            "message": f"GeoAlert Warning: Ground movement or soil saturation detected at {node_id}.",
            "sent": 1
        })

    if API_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Summarize this geotechnical sensor state into a 2-sentence emergency field report: Node {node_id}, Status: {name}, Soil Moisture: {features.get('soil_moisture_pct')}%, Rainfall 24h: {features.get('rainfall_24h_mm')}mm, Tilt: {features.get('tilt_deg')}°."
            response = model.generate_content(prompt)
            if response and response.text:
                narrative = response.text.strip()
        except Exception:
            pass

    return {
        "alert_triggered": alert_triggered,
        "send_log": send_log,
        "narrative": narrative
    }
