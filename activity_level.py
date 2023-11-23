import streamlit as st

import pandas as pd
dataset = pd.read_csv("./backend/dataset/metabolic_equivalenT_dataset.csv")
st.markdown(
    f"""
    <style>
        .dataframe {{
            width: 100%;
        }}
    </style>
    """,
    unsafe_allow_html=True
)
def calculate_duration(row, target_kalori, berat_badan_kg):
    METs = row['metabolic_equivalents']
    durasi_menit = round((target_kalori * 200) / (METs * 3.5 * berat_badan_kg), 2)
    return durasi_menit
def calculate_total_METs(row):
    total_METs = row['duration'] * row['metabolic_equivalents']
    return total_METs

def filter_and_sort_data(selected_level, selected_condition, selected_category, selected_gender, calories):
    data = dataset.copy()
    data['duration'] = dataset.apply(calculate_duration, args=(calories, st.session_state.user_data['fit_user']['weight_kg']), axis=1)
    data['total_METs'] = data.apply(calculate_total_METs, axis=1)
    data['selected_gender'] = 0
    data.loc[data['mostly'] == selected_gender, 'selected_gender'] = 1
    data.loc[data['mostly'] == 'general', 'selected_gender'] = 0.5
    filtered_data = data[
        (data['level'].isin(selected_level)) &
        (data['condition'].isin(selected_condition)) &
        (data['category'].isin(selected_category))
    ]
    sorted_data = filtered_data.sort_values(by=['selected_gender', 'duration'], ascending=[False, False])
    selected_columns = ['code', 'description', 'condition', 'metabolic_equivalents', 'level', 'category', 'total_METs', 'duration']
    sorted_data = sorted_data[selected_columns].rename(columns=lambda x: x.replace('_', ' ').title())
    
    return sorted_data

def form_activity_level():
    col_form = st.columns(3)
    col2_form, col2_form2 = st.columns([0.67, 0.33])
    selected_level = col_form[0].multiselect("Select Level", dataset['level'].unique(), default=dataset['level'].unique())
    selected_condition = col_form[1].multiselect("Select Condition", dataset['condition'].unique(), default=dataset['condition'].unique())
    calories = col2_form.slider("Burn Calories", 100, 300, 500)
    selected_category =  col_form[2].multiselect("Select Category", dataset['category'].unique(), default=dataset['category'].unique())
    routine_goal = st.session_state.user_data["fit_user"]["goal"]
    routine_advice = lambda goal: "Choose strength training as part of your **Bulking** routine for effective results and consider reducing cardio." if goal.lower() == "bulking" else "Consider incorporating cardio into your **Cutting** routine for optimal results and maintain strength training."
    advice_for_goal = routine_advice(routine_goal)
    col2_form2.info(advice_for_goal)
    
    selected_gender = st.session_state.user_data['fit_user']['gender'].lower()
    data_activity = filter_and_sort_data(selected_level, selected_condition, selected_category, selected_gender, calories)

    st.dataframe(data_activity)