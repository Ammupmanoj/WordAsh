import streamlit as st
import nltk
from nltk.corpus import wordnet
import random

# -------- Download WordNet if not present --------
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# -------- Page Setup --------
st.set_page_config(page_title="WordAsh", page_icon="📖", layout="wide")
st.title("📖 WordAsh — Your Personal Dictionary")

# -------- Session State --------
if 'history' not in st.session_state:
    st.session_state.history = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# -------- CSS Styling --------
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
}
.stButton>button {
    background-color: #1f77b4; 
    color:white; 
    border-radius:12px; 
    font-weight:bold; 
    padding:10px 25px;
    margin-top:5px;
}
.card {
    border-radius:15px; 
    padding:15px; 
    margin-bottom:15px; 
    background-color:rgba(255,255,255,0.9); 
    border:1px solid #ccc;
}
.wordofday {
    background: linear-gradient(90deg, #43cea2, #185a9d); 
    padding:18px; 
    border-radius:15px; 
    color:white; 
    font-size:20px;
    font-weight:bold;
}
.idiom {
    background: #fff1c1; 
    padding:15px; 
    border-radius:15px; 
    margin-bottom:15px;
}
.css-1d391kg {background-color: rgba(255,255,255,0.95);}
</style>
""", unsafe_allow_html=True)

POS_MAP = {'n':'Noun','v':'Verb','a':'Adjective','s':'Adj (sat)','r':'Adverb'}

# -------- Cached Lookup --------
@st.cache_data
def lookup_word(w: str):
    w = w.strip().lower()
    synsets = wordnet.synsets(w)
    if not synsets: return None
    results=[]
    synonyms=set()
    antonyms=set()
    for syn in synsets:
        pos_readable = POS_MAP.get(syn.pos(), syn.pos())
        definition = syn.definition()
        examples = syn.examples()
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_',' '))
            for a in lemma.antonyms():
                antonyms.add(a.name().replace('_',' '))
        results.append({"pos":pos_readable,"definition":definition,"examples":examples})
    return {"synsets": results, "synonyms": sorted(synonyms), "antonyms": sorted(antonyms)}

# -------- Word of the Day --------
word_list = ["happy","run","bank","light","power","dream","time","love","knowledge"]
if 'word_of_day' not in st.session_state:
    st.session_state.word_of_day = random.choice(word_list)
st.markdown(f'<div class="wordofday">🌟 Word of the Day: {st.session_state.word_of_day}</div>', unsafe_allow_html=True)

# -------- Main Layout --------
col1, col2 = st.columns([3,1])
with col1:
    word_input = st.text_input("🔤 Enter a word", placeholder="e.g. happy")
with col2:
    search_clicked = st.button("🔍 Search")

# -------- Search Logic --------
if search_clicked and word_input.strip():
    word = word_input.strip().lower()
    if word not in st.session_state.history:
        st.session_state.history.insert(0, word)
    st.session_state.history = st.session_state.history[:12]

    data = lookup_word(word)
    if not data:
        st.error(f"No results found for **{word}**")
    else:
        col_add = st.columns([1,5])
        with col_add[0]:
            if st.button("⭐ Add to Favorites"):
                if word not in st.session_state.favorites:
                    st.session_state.favorites.append(word)
                    st.success(f"Added **{word}** to Favorites!")

        st.subheader("📌 Meanings & POS")
        for i,s in enumerate(data['synsets'][:3],start=1):
            st.markdown(f'<div class="card"><b>{i}. ({s["pos"]})</b> — {s["definition"]}', unsafe_allow_html=True)
            if s['examples']:
                for ex in s['examples']:
                    st.markdown(f"> {ex}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟢 Synonyms")
        st.write(", ".join(data['synonyms'][:50]) if data['synonyms'] else "No synonyms found.")

        st.subheader("🔴 Antonyms")
        st.write(", ".join(data['antonyms'][:50]) if data['antonyms'] else "No antonyms found.")

        idioms = [
            "Break the ice — To initiate conversation in a social setting",
            "Bite the bullet — To endure a painful experience",
            "Hit the sack — Go to sleep",
            "Let the cat out of the bag — Reveal a secret",
            "Once in a blue moon — Rarely happens"
        ]
        st.subheader("💡 Random Idiom / Quote")
        st.markdown(f'<div class="idiom">{random.choice(idioms)}</div>', unsafe_allow_html=True)

# -------- Sidebar: History & Favorites --------
st.sidebar.header("🔎 Search History")
for h in st.session_state.history:
    if st.sidebar.button(h):
        st.session_state['last_clicked'] = h
        st.experimental_rerun()

st.sidebar.subheader("⭐ Favorites")
for fav in st.session_state.favorites:
    st.sidebar.write(fav)

if 'last_clicked' in st.session_state:
    st.info(f"Prefilled: **{st.session_state['last_clicked']}** — press Search to run")
    st.session_state['last_clicked_temp'] = st.session_state['last_clicked']
    del st.session_state['last_clicked']

# -------- Footer --------
st.markdown("---")
st.caption("Built by Ashu — GitHub: [Ammupmanoj](https://github.com/Ammupmanoj) • Powered by NLTK WordNet")
