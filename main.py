import streamlit as st


st.set_page_config(
    page_title="Fitness Diet App",
    page_icon="💪🏾",
    layout="wide",
)

from assets.css import *

st.markdown(main_style, unsafe_allow_html=True)

# =====Input Data====
from input_data import get_user_input

if "user_data" not in st.session_state:
    get_user_input()
else:
    from body_condition import show_body_condition
    show_body_condition()
    st.markdown("""---""")
    st.header("Food Source and Recipes Recommendation")
    tab_food_source, tab_recipes_recommend = st.tabs(["Food Source", "Recipes Recommendation"])
    with tab_food_source:
        from food_source import show_food_source
        show_food_source()
    with tab_recipes_recommend:
        from recommend_system import *
        generate_recommendation()
        if "recommendation_data" in st.session_state:
            show_all_recommendation()


