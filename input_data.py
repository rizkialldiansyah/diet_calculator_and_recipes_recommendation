import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_user_input():
    st.title("Sign Up")

    with st.form("signup_form"):
        name = st.text_input("Name", placeholder="Enter Your Name")
        email = st.text_input("Email", placeholder="Enter Your Email")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("Select Gender", ["Male", "Female"])
            age = st.slider("Enter Age", 18, 99, 30)
        with col2:
            height_cm = st.slider("Enter Height (cm)", 140, 220, 175)
            weight_kg = st.slider("Enter Weight (kg)", 40, 200, 80)
        with st.expander("Costume Neck, Hips and Waist Size"):
            st.info('Customizing neck, hips, and waist size affects Navy Fat calculation. If not customized, estimates based on typical proportions will be used.', icon="ℹ️")
            col1, col2, col3 = st.columns(3)
            with col1:
                neck_size = st.slider("Enter Neck Size (cm)", 10, 50, 20)
            with col2:
                waist_size = st.slider("Enter Waist Size (kg)", 30, 150, 100)
            with col3:
                hips_size = st.slider("Enter Hips Size (kg)", 30, 150, 100)
            agree = st.checkbox('Click if you want to customize your neck, hips, and waist size')
            if not agree:
                hips_size = None
                neck_size = None
                waist_size = None  
        activity_level = st.selectbox("Select Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
        col3,col4 = st.columns(2)
        with col3:
            target_weight = st.slider("Enter Target Weight (kg)", 40, 200, 75)
        with col4:
            target_date = st.date_input("Select Target Date", value=pd.to_datetime('2024-03-11'))
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        goal = (lambda weight_kg, target_weight: "Cutting" if weight_kg > target_weight else "Bulking")(weight_kg, target_weight)
        user_data = {
            "name": name,
            "email": email,
            "fit_user": {
                "gender": gender,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "neck_size": neck_size,
                "hips_size": hips_size,
                "waist_size": waist_size,
                "age": age,
                "activity_level": activity_level,
                "goal": goal,
                "start_date": str(datetime.now().date()),
                "target_date": str(target_date),
                "target_weight": target_weight}
        }
        st.toast("Sign-up successful!")
        st.session_state.user_data = user_data
        