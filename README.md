# Health Analysis Streamlit App

This project contains a Streamlit application that accepts a patient's blood report (plain text) and returns a health summary and a practical diet plan.

Project workflow (two stages):

- **Extract and Flag Abnormal Values**: parses the blood report and extracts every test value, labeling each as `HIGH`, `LOW`, or `NORMAL` based on the reference ranges present in the report.
- **Health Summary and Indian Diet Plan**: produces a concise 4–5 line health summary and a practical Indian diet plan with two sections: `Foods to avoid` and `Foods to eat more of`.

The app supports a quick one-click analysis mode and a step-by-step mode where you can view extracted values before generating the diet plan.

## Files
- `blood_work_analysis.ipynb`: notebook version of the blood report analysis workflow
- `blood_work.txt`: sample blood report used for demo mode
- `streamlit_app/app.py`: Streamlit application
- `requirements.txt`: Python dependencies for deployment
- `.gitignore`: ignores `.env` and Python cache files

## Run locally
1. Create and activate a Python environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in this folder with your API credentials.
4. Run the app:
   ```bash
   streamlit run streamlit_app/app.py
   ```

## Deploy on Streamlit Cloud
1. Push this folder to a GitHub repository.
2. Set the main file path to `streamlit_app/app.py`.
3. Add required secrets in Streamlit Cloud settings.

Live demo: https://blood-work-analysis-project.streamlit.app/
