🩺 CampusPulse Pro

Advanced AI Preventive Health & Medical Routing System

Originally developed by Team Biohackers for the REVA University National Level AI Hackathon.

This repository is maintained by Thejaswini S M and contains ongoing improvements, bug fixes, and future implementations.

---

🛑 The Problem

When students transition to campus life, sudden changes in sleep, nutrition, and academic stress cause a silent decline in their overall well-being. Currently, university healthcare is reactive—problems are only addressed when a student becomes severely ill.

💡 Our Solution

CampusPulse Pro is an AI-driven, proactive health engine. By tracking daily micro-habits (sleep patterns, hydration, meals, stress, and lifestyle substances), our unsupervised machine learning model builds a dynamic baseline for every student. It detects health deterioration before it becomes critical, gamifies healthy habits, and provides intelligent routing to campus medical professionals.

✨ Key Features

👤 For Students

• AI Anomaly Detection: Utilizes Isolation Forest machine learning to instantly flag irregular health patterns (Alert, Warning, or Safe zones).

• Dynamic Medical Routing: Automatically analyzes symptoms and refers students to the correct campus faculty.

• Menstrual Health Tracking: Contextualized cycle phase computation with biological pain tracking for female students.

• Gamification Engine: Rewards consistent healthy habits with Biohacker Points, daily streaks, and tiered badges.

• Official PDF Exports: Generates a downloadable medical report complete with embedded Plotly data visualizations using FPDF.

🛡️ For Campus Administration

• Secure Admin Command Center.

• Interactive Risk Mapping.

• Resource Allocation.

🛠️ Technology Stack

• Frontend: Python, Gradio (Custom CSS/Glassmorphism Theme)

• Backend: Pandas, NumPy

• Machine Learning: Scikit-Learn (Isolation Forest for Unsupervised Anomaly Detection)

• Data Visualization: Plotly Express

• Export Engine: FPDF, Kaleido

🚀 How to Run Locally

1. Clone the repository.

2. Install dependencies using:

pip install -r requirements.txt

3. Launch the application:

python app.py

4. Open:

http://127.0.0.1:7860

5. Admin Dashboard Access

Select Admin on the login screen and use the administrator credentials configured by the maintainers.

👥 Team Biohackers

B.Sc. Bioinformatics, Statistics & Computer Science

• Aman Chaturvedi
• Thanmai P L
• Thejaswini S M
• Spoorthi G N

📌 Repository Information

Credits for the original hackathon project belong to Team Biohackers.

This repository is maintained by Thejaswini S M and includes future enhancements, bug fixes, and additional implementations.

