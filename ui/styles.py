"""
Tactical Flow UI Components
Industrial Utilitarian design system for StadiumFlow AI.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;900&family=Roboto+Mono:wght@500&display=swap');

/* Base System Tokens */
:root {
    --primary: #FFD700;
    --bg-dark: #0A0A0A;
    --bg-panel: #1A1A1A;
    --text-main: #FFFFFF;
    --success: #00FF41;
    --warning: #FF4B4B;
    --border-width: 3px;
}

/* Global Reset */
.stApp {
    background-color: var(--bg-dark);
    color: var(--text-main);
}

/* Typography Overrides */
h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: -1px;
    font-weight: 900 !important;
}

h1 { font-size: 3.5rem !important; line-height: 0.9 !important; border-bottom: 8px solid var(--primary); padding-bottom: 1rem; margin-bottom: 2rem !important; }
h2 { font-size: 2rem !important; color: var(--primary); }

/* Industrial Data Strips */
.data-strip {
    background-color: var(--bg-panel);
    border-left: 10px solid var(--primary);
    padding: 1.5rem;
    margin-bottom: 1rem;
    font-family: 'Roboto Mono', monospace;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
}

.data-strip:hover {
    background-color: #252525;
    transform: translateX(5px);
}

.status-badge {
    padding: 0.5rem 1rem;
    font-weight: 700;
    text-transform: uppercase;
    border: 2px solid currentColor;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 2px solid #333;
}

/* Button Styling: Tactical High-Vis */
.stButton > button {
    background-color: var(--primary) !important;
    color: black !important;
    border: none !important;
    border-radius: 0px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 900 !important;
    text-transform: uppercase;
    font-size: 1.2rem !important;
    height: 60px !important;
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #FFFFFF !important;
    transform: scale(1.02);
}

/* Custom Metrics */
[data-testid="stMetricValue"] {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 2.5rem !important;
    color: var(--primary) !important;
}

</style>
"""

def apply_custom_styles(st):
    st.markdown(CSS, unsafe_allow_html=True)
