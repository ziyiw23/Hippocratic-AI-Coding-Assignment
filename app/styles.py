STYLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

/* ANIMATIONS */
@keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0px); } }
@keyframes firefly-move { 0% { opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(100px, -150px); opacity: 0; } }

/* APP BASE */
.stApp {
    background-color: #1a1614;
    background-image: repeating-linear-gradient(45deg, rgba(0,0,0,0.05) 0px, rgba(0,0,0,0.05) 2px, transparent 2px, transparent 4px),
                      linear-gradient(to bottom, #2b2118, #1a120b);
}

/* TYPOGRAPHY */
h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #d4af37 !important; }
p, label, div, input, textarea { font-family: 'Cormorant Garamond', serif !important; color: #f2e6cf; font-size: 1.1rem; }

/* SIDEBAR */
section[data-testid="stSidebar"] { background-color: #261C15; border-right: 1px solid #4a3b2a; }

/* DESK HEADER & BACK COVER */
.desk-header, .back-cover {
    background: rgba(20, 15, 10, 0.90);
    border: 1px solid #4a3b2a;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 0 50px rgba(0,0,0,0.8);
    animation: float 6s ease-in-out infinite;
}

/* CUSTOM WIDGET STYLING */
div[data-baseweb="select"] > div { background-color: rgba(0,0,0,0.3) !important; border-color: #8b6c42 !important; color: white !important; }
.stTextArea textarea { background-color: rgba(0,0,0,0.3) !important; border: 1px solid #8b6c42 !important; color: #e8d5b0 !important; }

/* FIREFLIES */
.firefly { position: fixed; width: 4px; height: 4px; background: #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; pointer-events: none; opacity: 0; }

/* BUTTONS */
.stButton button {
    background: linear-gradient(to bottom, #3e2b1f, #2a1b15);
    color: #d4af37;
    border: 1px solid #8b6c42;
    font-family: 'Cinzel', serif;
    transition: all 0.3s ease;
}
.stButton button:hover { border-color: #ffd700; color: #fff; transform: scale(1.02); }

footer {visibility: hidden;}
</style>
"""

FIREFLIES_HTML = """
<div class="firefly" style="top: 80%; left: 10%; animation: firefly-move 8s infinite alternate;"></div>
<div class="firefly" style="top: 60%; left: 20%; animation: firefly-move 12s infinite alternate-reverse;"></div>
<div class="firefly" style="top: 50%; left: 50%; animation: firefly-move 20s infinite alternate;"></div>
<div class="firefly" style="top: 30%; left: 15%; animation: firefly-move 14s infinite alternate;"></div>
<div class="firefly" style="top: 25%; left: 70%; animation: firefly-move 18s infinite alternate-reverse;"></div>
<div class="firefly" style="top: 85%; left: 60%; animation: firefly-move 16s infinite alternate;"></div>
<div class="firefly" style="top: 40%; left: 85%; animation: firefly-move 22s infinite alternate-reverse;"></div>
"""

