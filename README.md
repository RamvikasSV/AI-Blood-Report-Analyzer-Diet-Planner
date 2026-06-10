# Health Analysis Streamlit App

This folder contains a health analysis project built with Streamlit and LangChain.

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
