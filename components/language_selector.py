import streamlit as st
from modules.translations import get_translation

def language_selector():
    if 'language' not in st.session_state:
        st.session_state.language = "de"  # Default to german
    
    current_lang = st.session_state.language
    
    langs = {
        "de": get_translation("german", current_lang),
        "fr": get_translation("french", current_lang),
        "it": get_translation("italian", current_lang),
        "en": get_translation("english", current_lang)
    }
    
    selected_lang = st.selectbox(
        get_translation("language", current_lang),
        options=list(langs.keys()),
        format_func=lambda x: langs[x],
        index=list(langs.keys()).index(current_lang),
        key="lang_selector"
    )
    
    if selected_lang != current_lang:
        st.session_state.language = selected_lang
        st.rerun()