# 🩺 CampusPulse Pro

**Advanced AI Preventive Health & Medical Routing System** *Developed by Team Biohackers | REVA University National Level AI Hackathon*

---

## 🛑 The Problem
When students transition to campus life, sudden changes in sleep, nutrition, and academic stress cause a silent decline in their overall well-being. Currently, university healthcare is **reactive**—problems are only addressed when a student becomes severely ill. 

## 💡 Our Solution
**CampusPulse Pro** is an AI-driven, proactive health engine. By tracking daily micro-habits (sleep patterns, hydration, meals, stress, and lifestyle substances), our unsupervised machine learning model builds a dynamic baseline for every student. It detects health deterioration *before* it becomes critical, gamifies healthy habits, and provides intelligent routing to campus medical professionals.

---

## ✨ Key Features

### 👤 For Students
* **AI Anomaly Detection:** Utilizes `Isolation Forest` machine learning to instantly flag irregular health patterns (Alert, Warning, or Safe zones).
* **Dynamic Medical Routing:** Automatically analyzes symptoms and refers students to the correct campus faculty (e.g., Clinical Psychologist for high stress, General Physician for frequent sickness).
* **Menstrual Health Tracking:** Contextualized cycle phase computation with biological pain tracking for female students.
* **Gamification Engine:** Rewards consistent healthy habits with "Biohacker Points", daily streaks, and tiered badges (Bronze to Platinum).
* **Official PDF Exports:** Generates a downloadable, highly professional medical report complete with embedded Plotly data visualizations using `FPDF`.

### 🛡️ For Campus Administration
* **Secure Admin Command Center:** Restricted portal for university management to audit student health records.
* **Interactive Risk Mapping:** A global campus leaderboard utilizing Sorted Horizontal Bar Charts to map average health scores across specific REVA Hostel Blocks and PG Floors.
* **Resource Allocation:** Allows management to instantly see which blocks require immediate attention (e.g., flu outbreaks or severe exam stress).

---

## 🛠️ Technology Stack
* **Frontend:** Python, Gradio (Custom CSS/Glassmorphism Theme)
* **Backend:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (`Isolation Forest` for Unsupervised Anomaly Detection)
* **Data Visualization:** Plotly Express (Interactive Bar & Line Charts)
* **Export Engine:** FPDF, Kaleido

---

Here’s a cleaner and professional version:

## 🚀 How to Run Locally

### 1. Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/YourUsername/CampusPulse-Pro.git
cd CampusPulse-Pro
```

### 2. Install Dependencies

Make sure you have **Python 3.8 or above** installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Launch the Application

Run the application using:

```bash
python app.py
```

### 4. Access the Web Interface

Once the application starts, open your browser and visit:

```bash
http://127.0.0.1:7860
```

### 5. Admin Dashboard Access

To test the Admin Dashboard:

* Select **Admin** on the login screen
* Use the following credentials:
  **Password:** `Amai23`

---

## 👥 Team Biohackers

–> B.Sc. Bioinformatics, Statistics & Computer Science
* **Aman Chaturvedi** 
* **Thanmai P L**
* **Thejaswini S M**
* **Spoorthi G N**

