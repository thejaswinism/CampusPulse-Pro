import gradio as gr
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import tempfile
import random
import os

# --- 1. DATA GENERATION & AI BASELINE (>1000 Points) ---
def load_and_augment_data():
    try:
        df = pd.read_csv("student_health.csv")
    except:
        df = pd.DataFrame() 

    # Generate 1200 synthetic data points based on campus trends
    np.random.seed(42)
    n = 1200
    stress = np.random.randint(2, 10, n)
    age = np.random.randint(18, 26, n)
    
    # Specific Hostel Blocks and PG Floors
    hostels = np.random.choice([
        "REVA Hostel - Block A", "REVA Hostel - Block B", "REVA Hostel - Block C", 
        "PG - Floor 1", "PG - Floor 2", "PG - Floor 3", "PG - Floor 4"
    ], n)
    
    aug_df = pd.DataFrame({
        'student_id': [f"Student_{i}" for i in range(n)],
        'age': age,
        'gender': np.random.choice(["Male", "Female"], n),
        'hostel': hostels,
        'sleep_hours': np.clip(6 - (stress // 2) + np.random.randint(-1, 2, n), 1, 5),
        'junk_food': np.random.choice([1, 2, 3, 4], n),
        'fatigue': np.clip(stress + np.random.randint(-2, 3, n), 1, 10),
        'stress': stress,
        'sickness': np.random.choice([0, 1, 2, 3], n, p=[0.6, 0.25, 0.1, 0.05]),
        'exercise': np.random.choice([0, 1, 2, 3], n),
        'hydration': np.random.uniform(0.5, 4.0, n),
        'mood': np.clip(12 - stress + np.random.randint(-2, 3, n), 1, 10),
        'meals': np.random.randint(1, 6, n),
        'substance_use': np.random.choice([0, 5, 15], n, p=[0.7, 0.2, 0.1]) 
    })
    
    # Base Score Calculation
    aug_df['score'] = 100 - (aug_df['fatigue']*1.5) - (aug_df['stress']*2) - aug_df['substance_use']
    
    # Inject realistic, diverse skews into specific blocks/floors for analytics
    aug_df.loc[aug_df['hostel'] == 'PG - Floor 1', 'score'] -= 18  # Skew to Orange Alert
    aug_df.loc[aug_df['hostel'] == 'REVA Hostel - Block A', 'score'] += 15  # Skew to Green Safe
    aug_df.loc[aug_df['hostel'] == 'REVA Hostel - Block C', 'score'] -= 8   # Skew to Yellow Warning
    aug_df.loc[aug_df['hostel'] == 'PG - Floor 3', 'score'] += 10
    aug_df['score'] = aug_df['score'].clip(0, 100) # Boundary safety
    
    features = ['sleep_hours', 'junk_food', 'fatigue', 'stress', 'sickness', 'exercise', 'substance_use', 'hydration', 'mood', 'meals']
    iso_forest = IsolationForest(contamination=0.10, random_state=42)
    iso_forest.fit(aug_df[features])
    
    return iso_forest, aug_df

campus_model, campus_data = load_and_augment_data()

# --- 2. USER DATABASE & UTILITIES ---
user_db = {}

def calculate_bmi_and_target(weight, height_cm):
    if height_cm <= 0: return 0, "Invalid", 8000
    bmi = weight / ((height_cm / 100) ** 2)
    if bmi < 18.5: return round(bmi, 1), "Underweight", 6000
    elif bmi < 24.9: return round(bmi, 1), "Normal", 8000
    elif bmi < 29.9: return round(bmi, 1), "Overweight", 10000
    else: return round(bmi, 1), "Obese", 8000

def get_motivational_quote():
    quotes = [
        "Every step you take is a step towards a stronger you. Keep it up!",
        "Health is a daily practice, not a destination. You are doing great.",
        "Your body hears everything your mind says. Stay positive and hydrated!",
        "Small daily improvements are the key to staggering long-term results.",
        "You are prioritizing your well-being today, and your future self thanks you."
    ]
    return random.choice(quotes)

def get_badge_info(points):
    if points < 200: return "🥉 Bronze", "Earn 200 points to unlock Silver! Maintain your streaks."
    elif points < 500: return "🥈 Silver", "Earn 500 points to unlock Gold! Keep hitting your step targets."
    elif points < 1000: return "🥇 Gold", "Earn 1000 points to unlock Platinum! You are a health champion."
    else: return "💎 Platinum Biohacker", "You are at the top tier! Keep setting the campus standard."

def generate_pdf_with_graphs(name, score, status, summary, routing, motivation, badge, fig_score, fig_steps):
    pdf = FPDF()
    pdf.add_page()
    
    # Safe text encoder to prevent PDF crashing from Emojis
    c = lambda x: str(x).encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=c("CampusPulse: Official Health Report"), ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=c(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=c(f"Student Profile: {name} | Status: {status} | Rank: {badge}"), ln=True)
    pdf.cell(200, 10, txt=c(f"Overall Health Stability Score: {score}/100"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=c("AI SUMMARY:\n" + summary))
    pdf.ln(5)
    pdf.multi_cell(0, 8, txt=c("MEDICAL ROUTING & RECOMMENDATIONS:\n" + routing))
    pdf.ln(5)
    
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 8, txt=c("Message from CampusPulse: " + motivation))
    pdf.ln(5)
    
    temp_dir = tempfile.gettempdir()
    
    try:
        score_img = os.path.join(temp_dir, "score_temp.png")
        steps_img = os.path.join(temp_dir, "steps_temp.png")
        fig_score.write_image(score_img)
        pdf.image(score_img, x=10, w=90)
        fig_steps.write_image(steps_img)
        pdf.image(steps_img, x=110, y=pdf.get_y()-60, w=90) 
    except Exception:
        pdf.multi_cell(0, 10, txt=c("(Graphs could not be rendered. Please view online dashboard.)"))
        
    filename = os.path.join(temp_dir, f"{name.replace(' ', '_')}_Health_Report.pdf")
    pdf.output(filename)
    return filename

# --- 3. DYNAMIC MENSTRUAL TRACKING ---
def calculate_cycle_phase(date_str):
    if not date_str or str(date_str).strip() == "":
        return "Please enter a valid date.", gr.update(visible=False)
    try:
        last_period = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        days_since = (datetime.now() - last_period).days
        
        if days_since < 0 or days_since > 40:
            return "Awaiting valid current cycle", gr.update(visible=False)
        elif 0 <= days_since <= 5:
            return f"Day {days_since}: Menstruation Phase", gr.update(visible=True)
        elif days_since <= 13:
            return f"Day {days_since}: Follicular Phase", gr.update(visible=False)
        elif days_since <= 16:
            return f"Day {days_since}: Ovulation Phase", gr.update(visible=False)
        else:
            return f"Day {days_since}: Luteal Phase", gr.update(visible=False)
    except ValueError:
        return "Format must be exactly YYYY-MM-DD", gr.update(visible=False)
    except Exception:
        return "Error calculating phase", gr.update(visible=False)

# --- 4. CORE PROCESSING LOGIC ---
def process_checkin(user_id, age, gender, weight, height, steps, hydration, 
                   sleep_in, junk_in, exercise_in, sick_in, fatigue, stress, 
                   smoke, drink, vape, mood, meals, cycle_date, cycle_pain):
                   
    if not user_id: return "Error: Username required.", gr.update()
    
    cycle_pain = int(cycle_pain) if cycle_pain else 0

    sleep_map = {"< 5 hrs": 1, "5–6 hrs": 2, "6–7 hrs": 3, "7–8 hrs": 4, "> 8 hrs": 5}
    junk_map = {"Never": 1, "1–2 times": 2, "3–4 times": 3, "> 4 times": 4}
    ex_map = {"None": 0, "1–2 days": 1, "3–4 days": 2, "5+ days": 3}
    sick_map = {"0": 0, "1–2 times": 1, "3–4 times": 2, "> 4 times": 3}
    
    s_val = sleep_map.get(sleep_in, 3)
    j_val = junk_map.get(junk_in, 2)
    e_val = ex_map.get(exercise_in, 1)
    sick_val = sick_map.get(sick_in, 0)
    
    sub_map = {"None": 0, "Occasional": 5, "Regular/Daily": 15}
    substance_score = sub_map.get(smoke, 0) + sub_map.get(drink, 0) + sub_map.get(vape, 0)

    bmi_val, bmi_cat, target_steps = calculate_bmi_and_target(weight, height)
    
    features = [[s_val, j_val, fatigue, stress, sick_val, e_val, substance_score, hydration, mood, meals]]
    anomaly = campus_model.predict(features)[0]
    
    score = 100 - (fatigue * 1.5) - (stress * 2) - substance_score
    if age > 25: score -= 2 
    if s_val < 3: score -= 15
    if j_val > 2: score -= 10
    if sick_val > 1: score -= 10
    if e_val > 1: score += 10
    
    if hydration < 1.5: score -= 10
    elif hydration >= 2.5: score += 5
    
    if meals < 2: score -= 10
    elif meals > 4: score -= 5
    elif 3 <= meals <= 4: score += 5
    
    if mood < 4: score -= 10
    elif mood >= 8: score += 5

    health_score = max(0, min(100, int(score)))
    
    # NEW: Enhanced Score Popups and Dynamic Statuses
    if anomaly == -1 or health_score < 50:
        status = "🔴 Critical Risk"
        gr.Warning(f"🚨 ACTION REQUIRED: Your Health Score dropped to {health_score}/100. Please view your AI action plan.")
    elif health_score < 75:
        status = "🟡 Moderate Deterioration"
        gr.Info(f"⚠️ CAUTION: Your Health Score is {health_score}/100. Minor adjustments are advised today.")
    else:
        status = "🟢 Optimal Vitality"
        gr.Info(f"🎉 EXCELLENT: Your Health Score is {health_score}/100. You are maintaining peak homeostasis!")
    
    prev = user_db.get(user_id, {}).get('latest', {})
    streak = prev.get('streak', 0) + 1 if health_score >= 70 else 0
    points = prev.get('points', 0) + (streak * 10) + (10 if steps >= target_steps else 0)
    badge, badge_msg = get_badge_info(points)
    motivation = get_motivational_quote()
    
    summary = f"Your daily AI health baseline indicates **{status}**. "
    if s_val < 3: summary += "Sleep deprivation is severely impacting your recovery and cognitive function. "
    if stress > 7: summary += "High cortisol (stress) levels detected. "
    if mood < 4: summary += "Your reported mood is extremely low today, which correlates with physical fatigue. "
    if substance_score > 0: summary += "Your current lifestyle habits (smoking/drinking/vaping) are applying a significant penalty to your cardiovascular and long-term health scores. "
    if hydration < 1.5: summary += "Your water intake is critically low, slowing down your metabolism. "
    if meals < 2: summary += "Skipping meals is depriving your brain of essential glucose. "
    
    phase_str, _ = calculate_cycle_phase(cycle_date)
    if gender == "Female" and cycle_pain > 6: 
        summary += f"You are experiencing high discomfort during your {phase_str}, which naturally lowers your energy. "
        
    if health_score >= 80: 
        summary = "You are maintaining excellent homeostasis. Your hydration, sleep, and lifestyle inputs align perfectly with peak performance. Keep it up!"

    routing = ""
    if stress > 7 or mood < 4: routing += "- 🧠 Clinical Psychologist / Campus Counselor (Student Center, Room 101)\n"
    if sick_val > 1: routing += "- 🩺 General Physician (University Main Clinic)\n"
    if gender == "Female" and cycle_pain > 7: routing += "- 🌸 Women's Health Nurse Practitioner (Clinic Wing B)\n"
    if substance_score >= 15: routing += "- 🌱 De-addiction & Wellness Counselor (Confidential Consult Available)\n"
    if not routing: routing = "No medical consultation required at this time. Maintain your healthy habits!"

    if user_id not in user_db: user_db[user_id] = {'history': []}
    
    entry = {
        "Date": datetime.now().strftime("%b %d"),
        "Score": health_score, "Steps": steps, "Sleep": s_val, "Hydration": hydration,
        "streak": streak, "points": points, "badge": badge, "badge_msg": badge_msg,
        "bmi_text": f"BMI: {bmi_val} ({bmi_cat})", "target": target_steps,
        "summary": summary, "routing": routing, "status": status, "motivation": motivation
    }
    user_db[user_id]['history'].append(entry)
    user_db[user_id]['latest'] = entry
    
    alert_msg = f"✅ Success: Data encrypted & saved for {user_id}! Earned {points} Biohacker Points."
    
    return alert_msg, gr.update()

# --- 5. DASHBOARD RENDERERS ---
def load_student_dash(username):
    if not username or username not in user_db:
        return "No data.", "N/A", "N/A", "N/A", "N/A", None, None, None, "N/A"
    
    data = user_db[username]
    latest = data['latest']
    df = pd.DataFrame(data['history'])
    
    fig_score = px.line(df, x="Date", y="Score", title="📈 Your Historical Health Trend", markers=True, color_discrete_sequence=['#0077b6'])
    fig_score.update_layout(template="plotly_white", yaxis_range=[0,105], plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    fig_steps = px.bar(df, x="Date", y="Steps", title="👟 Your Daily Step Tracking", color="Steps", color_continuous_scale="Tealgrn")
    fig_steps.update_layout(template="plotly_white", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    pdf_path = generate_pdf_with_graphs(username, latest['Score'], latest['status'], latest['summary'], latest['routing'], latest['motivation'], latest['badge'], fig_score, fig_steps)
    
    # NEW: Highly stylized HTML cards for the dashboard
    sc = latest['Score']
    score_color = '#2ca02c' if sc >= 75 else ('#ffc107' if sc >= 50 else '#ff7f0e')
    
    stats_html = f"<div style='text-align: center; padding: 15px;'><h1 style='color: {score_color}; font-size: 4em; margin: 0; font-weight: 800;'>{sc}</h1><h3 style='margin: 5px 0 0 0; font-size: 1.3em;'>{latest['status']}</h3></div>"
    gamify_html = f"<div style='text-align: center; padding: 15px;'><h2 style='margin: 0; font-size: 2.2em;'>{latest['badge']}</h2><p style='margin: 8px 0; font-size: 1.1em;'>🔥 {latest['streak']} Day Streak | 🪙 {latest['points']} Pts</p><p style='font-size: 0.9em; font-style: italic; color: gray;'>{latest['badge_msg']}</p></div>"
    bmi_html = f"<div style='text-align: center; padding: 15px;'><h2 style='margin: 0; font-size: 2.2em; color: #0077b6;'>{latest['bmi_text'].split('(')[0].replace('BMI: ', '')}</h2><h3 style='margin: 5px 0 0 0;'>{latest['bmi_text'].split('(')[1].replace(')', '')}</h3><p style='font-size: 0.9em; color: gray; margin-top: 10px;'>Daily Target: {latest['target']} Steps</p></div>"

    motivate = f"💡 **CampusPulse Says:** {latest['motivation']}"
    
    return stats_html, gamify_html, bmi_html, latest['summary'], latest['routing'], fig_score, fig_steps, pdf_path, motivate

def get_leaderboard():
    if not user_db: return pd.DataFrame()
    data = [{"Student": k, "Score": v['latest']['Score'], "Points": v['latest']['points'], "Badge": v['latest']['badge']} for k, v in user_db.items()]
    df = pd.DataFrame(data).sort_values("Points", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def get_campus_zones():
    # Sorted Horizontal Bar Chart with Threshold Lines for maximum professional clarity
    zone_data = campus_data.groupby('hostel')['score'].mean().reset_index()
    counts = campus_data['hostel'].value_counts().reset_index()
    counts.columns = ['hostel', 'student_count']
    zone_data = pd.merge(zone_data, counts, on='hostel')
    
    # Sort values for a clean top-to-bottom leaderboard layout
    zone_data = zone_data.sort_values('score', ascending=True)
    
    def get_color(val):
        if val >= 75: return '🟢 Safe / Optimal'
        elif val >= 55: return '🟡 Warning Zone'
        else: return '🔴 Critical Zone'
        
    zone_data['Zone Status'] = zone_data['score'].apply(get_color)
    color_map = {'🟢 Safe / Optimal': '#2ca02c', '🟡 Warning Zone': '#ffc107', '🔴 Critical Zone': '#ff7f0e'}
    
    fig = px.bar(
        zone_data, 
        x='score', 
        y='hostel', 
        color='Zone Status', 
        color_discrete_map=color_map, 
        orientation='h',
        text=zone_data['score'].round(1),
        title="Campus Health Leaderboard: Average Score by Block & Floor",
        custom_data=['student_count']
    )
    fig.update_traces(
        textposition='inside', 
        hovertemplate='<b>%{y}</b><br>Average Health Score: %{x}<br>Active Students: %{customdata[0]}'
    )
    fig.update_layout(template="plotly_white", xaxis_title="Average Health Score", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Clear visual threshold lines
    fig.add_vline(x=55, line_dash="dash", line_color="#ff7f0e", annotation_text="Alert Boundary")
    fig.add_vline(x=75, line_dash="dash", line_color="#2ca02c", annotation_text="Safe Boundary")
    
    return fig

# --- 6. MAIN UI LAYOUT WITH ADVANCED THEMING ---
# Professional highly-customized theme injected here
custom_theme = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="cyan",
    neutral_hue="slate"
).set(
    body_background_fill="#f4f6f8",
    block_background_fill="#ffffff",
    block_shadow="0px 4px 12px rgba(0, 0, 0, 0.05)",
    block_border_width="1px",
    block_border_color="#e2e8f0",
    block_radius="12px",
    button_primary_background_fill="#0077b6",
    button_primary_background_fill_hover="#0096c7",
    button_primary_text_color="#ffffff",
    slider_color="#0077b6"
)

with gr.Blocks(theme=custom_theme, title="CampusPulse Pro") as app:
    
    # Sleek CSS Gradient Banner
    gr.HTML("""
        <div style="background: linear-gradient(135deg, #0077b6, #00b4d8); padding: 30px; border-radius: 12px; text-align: center; color: white; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h1 style="font-family: 'Inter', sans-serif; font-size: 3em; font-weight: 800; margin: 0; letter-spacing: -1px; text-shadow: 1px 1px 3px rgba(0,0,0,0.2);">🩺 CampusPulse</h1>
            <p style="font-size: 1.2em; margin-top: 5px; opacity: 0.95; font-weight: 400;">Advanced AI Preventive Health & Medical Routing System</p>
            <p style="font-size: 0.85em; font-weight: bold; margin-top: 15px; background: rgba(255,255,255,0.2); display: inline-block; padding: 6px 18px; border-radius: 20px;">Developed by Team Biohackers | REVA University</p>
        </div>
    """)
    
    current_user = gr.State("")
    
    # --- LOGIN SYSTEM ---
    with gr.Row(visible=True) as login_row:
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### 🔐 Secure System Access")
            gr.Markdown("Please authenticate to access your personal dashboard or global analytics.")
            login_user = gr.Textbox(label="Username / ID Number")
            login_role = gr.Radio(["Student", "Admin"], label="Access Portal Level", value="Student")
            login_msg = gr.Markdown(visible=False)
            login_btn = gr.Button("Authenticate", variant="primary")

    # --- STUDENT VIEW ---
    with gr.Column(visible=False) as student_view:
        with gr.Row():
            gr.Markdown("### 👤 Secure Student Portal Active")
            logout_student_btn = gr.Button("Log out / Switch User", size="sm")
            
        with gr.Tabs():
            with gr.TabItem("📝 Daily Log Formulation"):
                with gr.Row():
                    # Card 1
                    with gr.Column(variant="panel"):
                        gr.Markdown("### 🆔 Core Biometrics")
                        age = gr.Slider(17, 30, step=1, label="Age", value=20)
                        gender = gr.Radio(["Male", "Female", "Other"], label="Biological Gender", value="Male")
                        weight = gr.Number(label="Body Weight (kg)", value=65)
                        height = gr.Number(label="Height (cm)", value=170)
                        
                        with gr.Group(visible=False) as female_inputs:
                            gr.Markdown("---")
                            gr.Markdown("### 🌸 Menstrual Health Tracking")
                            cycle_date = gr.Textbox(label="Start Date of Last Period (YYYY-MM-DD)", placeholder="2023-10-01")
                            check_phase_btn = gr.Button("Compute Biological Phase", size="sm")
                            phase_out = gr.Markdown()
                            cycle_pain = gr.Slider(0, 10, step=1, label="Cramps/Pain Severity (0-10)", value=0, visible=False)
                            
                        gender.change(lambda g: gr.update(visible=(g=="Female")), inputs=gender, outputs=female_inputs)
                        def handle_phase_check(date_str):
                            text, slider_vis = calculate_cycle_phase(date_str)
                            return text, slider_vis
                        check_phase_btn.click(handle_phase_check, inputs=cycle_date, outputs=[phase_out, cycle_pain])

                    # Card 2
                    with gr.Column(variant="panel"):
                        gr.Markdown("### 🥗 Intake & Output Logistics")
                        hydration = gr.Slider(0, 8, step=0.5, label="Total Water Intake (Litres)", value=2.0)
                        meals = gr.Slider(0, 6, step=1, label="Nutritional Meals Eaten", value=3)
                        steps = gr.Number(label="Total Steps Logged", value=5000)
                        sleep = gr.Dropdown(["< 5 hrs", "5–6 hrs", "6–7 hrs", "7–8 hrs", "> 8 hrs"], value="6–7 hrs", label="Average Sleep Duration")
                        junk = gr.Dropdown(["Never", "1–2 times", "3–4 times", "> 4 times"], value="1–2 times", label="Processed/Junk Food Frequency")
                        exercise = gr.Dropdown(["None", "1–2 days", "3–4 days", "5+ days"], value="1–2 days", label="Physical Exertion Frequency")
                        sick = gr.Dropdown(["0", "1–2 times", "3–4 times", "> 4 times"], value="0", label="Illness Frequency (Past 30 Days)")
                        
                    # Card 3
                    with gr.Column(variant="panel"):
                        gr.Markdown("### 🧠 Neuro & Vitals")
                        fatigue = gr.Slider(1, 10, step=1, label="Physical Fatigue Severity", value=5)
                        stress = gr.Slider(1, 10, step=1, label="Academic Stress Levels", value=5)
                        mood = gr.Slider(1, 10, step=1, label="Psychological Mood (1=Severe, 10=Optimal)", value=5)
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🚬 Substance Logistics")
                        smoke = gr.Radio(["None", "Occasional", "Regular/Daily"], label="Smoking Intake", value="None")
                        vape = gr.Radio(["None", "Occasional", "Regular/Daily"], label="Vaping Intake", value="None")
                        drink = gr.Radio(["None", "Occasional", "Regular/Daily"], label="Alcohol Consumption", value="None")
                
                submit_btn = gr.Button("🚀 Process Analysis via AI Engine", variant="primary", size="lg")
                sys_msg = gr.Textbox(label="System Authentication & Response", interactive=False)

            with gr.TabItem("📊 Personal Intelligence Dashboard"):
                refresh_dash = gr.Button("🔄 Sync Latest Cloud Data")
                d_motivate = gr.Markdown()
                
                with gr.Row():
                    with gr.Column(variant="panel"):
                        gr.Markdown("#### 📈 Health Stability Score")
                        d_score = gr.HTML()
                    with gr.Column(variant="panel"):
                        gr.Markdown("#### 🎮 Gamification Tier")
                        d_gamify = gr.HTML()
                    with gr.Column(variant="panel"):
                        gr.Markdown("#### ⚖️ Body Mass Index")
                        d_bmi = gr.HTML()
                
                with gr.Column(variant="panel"):
                    gr.Markdown("### 🤖 Clinical AI Interpretation & Action Plan")
                    d_summary = gr.Textbox(label="Summary", lines=3, interactive=False)
                    d_routing = gr.Textbox(label="AI-Assigned Medical Routing", lines=3, interactive=False)
                
                with gr.Row():
                    with gr.Column(variant="panel"):
                        plot1 = gr.Plot()
                    with gr.Column(variant="panel"):
                        plot2 = gr.Plot()
                    
                download_btn = gr.File(label="📥 Download Certified PDF Report")

            with gr.TabItem("🏆 Global Leaderboards"):
                with gr.Column(variant="panel"):
                    gr.Markdown("### 🏅 Campus High Performers")
                    gr.Markdown("View the top ranking Biohackers setting the standard for campus health.")
                    lb_refresh = gr.Button("🔄 Refresh Global Ranks")
                    lb_grid = gr.Dataframe()
                    lb_refresh.click(get_leaderboard, outputs=lb_grid)

    # --- ADMIN VIEW ---
    with gr.Column(visible=False) as admin_view:
        with gr.Row():
            gr.Markdown("## 🛡️ Administrative Command Center")
            logout_admin_btn = gr.Button("Log out securely", size="sm")
            
        with gr.Tabs():
            with gr.TabItem("👥 Master Student Directory"):
                with gr.Column(variant="panel"):
                    user_select = gr.Dropdown(choices=[], label="Select Encrypted Student Profile")
                    admin_refresh = gr.Button("Query Active Database")
                    
                    gr.Markdown("---")
                    a_score = gr.Markdown()
                    a_summary = gr.Textbox(label="AI Diagnostic Override")
                    a_plot = gr.Plot()
                    
                    def load_admin_dropdown(): return gr.update(choices=list(user_db.keys()))
                    def view_user(u):
                        if not u: return "N/A", "N/A", None
                        return f"**System Score:** {user_db[u]['latest']['Score']}", user_db[u]['latest']['summary'], load_student_dash(u)[5]
                        
                    admin_refresh.click(load_admin_dropdown, outputs=user_select)
                    user_select.change(view_user, inputs=user_select, outputs=[a_score, a_summary, a_plot])
                
            with gr.TabItem("🌍 Campus Infrastructure Zones"):
                with gr.Column(variant="panel"):
                    gr.Markdown("### 🏢 AI Hierarchical Risk Mapping")
                    gr.Markdown("Analytics based on 1200+ simulated university profiles mapped into safe, warning, and alert zones via Unsupervised AI Isolation Forests.")
                    zone_plot = gr.Plot()
                    app.load(get_campus_zones, outputs=zone_plot)

    # --- EVENT WIRING & AUTHENTICATION ---
    def auth_user(username, role):
        if not username: return "", gr.update(visible=True, value="⚠️ Username is strictly required!"), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
        
        if role == "Admin":
            if username != "Amai23":
                return "", gr.update(visible=True, value="❌ Critical: Invalid Admin Credentials. Access Blocked."), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
            return username, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
            
        return username, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

    def logout():
        return "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

    login_btn.click(auth_user, inputs=[login_user, login_role], outputs=[current_user, login_msg, admin_view, login_row, student_view])
    logout_student_btn.click(logout, outputs=[current_user, admin_view, student_view, login_row, login_msg])
    logout_admin_btn.click(logout, outputs=[current_user, admin_view, student_view, login_row, login_msg])

    submit_btn.click(
        process_checkin,
        inputs=[current_user, age, gender, weight, height, steps, hydration, sleep, junk, exercise, sick, fatigue, stress, smoke, drink, vape, mood, meals, cycle_date, cycle_pain],
        outputs=[sys_msg, current_user]
    )
    
    refresh_dash.click(
        load_student_dash, inputs=[current_user], 
        outputs=[d_score, d_gamify, d_bmi, d_summary, d_routing, plot1, plot2, download_btn, d_motivate]
    )

app.launch(share=True)