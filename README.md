# AeroGlass XAI
An interactive predictive maintenance dashboard utilizing Explainable AI to forecast aerospace engine failures and translate predictive accuracy into financial ROI.

[![Hosted Demo](https://img.shields.io/badge/Launch_Dashboard-00E5FF?style=for-the-badge&logo=streamlit&logoColor=white)](https://aeroglass-xai-guyrcky3rrh5drscsb9uhu.streamlit.app/)

![Hero Image](assets/hero_image.png)
*Note: If the dashboard is hibernating due to inactivity, click "Wake App" and it will boot in under 30 seconds.*

## 🚀 Quick Start
AeroGlass XAI is fully deployed on the cloud. No installation is required to view the telemetry. 
**[Launch the Hosted Dashboard Here](https://aeroglass-xai-guyrcky3rrh5drscsb9uhu.streamlit.app/)**

## 🛡️ Core Features
* **Interactive Telemetry Simulation:** Visualizing thermodynamic sensor feeds alongside dual BiLSTM predictive models using pre-computed inference.
* **Explainable AI (XAI) Audits:** Extracting sensor-level SHAP feature attribution to translate complex neural network weights into actionable mechanical insights.
* **Pre-Flight Risk Briefing:** Generating immediate "GO / NO-GO" safety diagnostics for specific aircraft engine pairings.
* **Operational ROI Calculator:** Simulating the financial break-even point between preventative maintenance and AI false-negative catastrophic failures.

## 🛠️ How to Run Locally
If you wish to run the dashboard on your local machine:

1. Clone the repository:
   ```bash
   git clone https://github.com/saminsiddiqui08-beep/AeroGlass-XAI.git
   cd AeroGlass-XAI
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Boot the Streamlit server:
   ```bash
   streamlit run app.py
   ```

## 🧠 Technical Architecture
Pure predictive accuracy is insufficient in safety-critical domains like aerospace. Human engineers must be able to audit the AI.

AeroGlass runs a Baseline Dual-Layer BiLSTM alongside a custom Temporal Attention BiLSTM. While the baseline model operates as an uninterpretable "Black Box," the AeroGlass model extracts pre-computed SHAP matrices to definitively isolate the mechanical stressors driving a failure (e.g., thermal stress vs. rotational mechanics). The front-end is engineered using Streamlit and Plotly, utilizing mmap_mode and @st.cache_resource to fluidly load and visualize heavy multi-dimensional tensor arrays without memory bloat.

## 🤝 Credits
* Built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/).
* Dataset: NASA CMAPSS (Commercial Modular Aero-Propulsion System Simulation) Turbofan Degradation Data.