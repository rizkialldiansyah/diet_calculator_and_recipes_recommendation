import streamlit as st
import pandas as pd

def show_food_source():
    diet_calories, protein, carbs, fat = st.session_state.diet_calories, st.session_state.protein, st.session_state.carbs, st.session_state.fat
    col_table, col_detail = st.columns([0.42, 0.58])
    with col_table:
        food_sources = pd.read_csv("./backend/dataset/food_sources.csv")
        selected_categories = st.multiselect('Select Food Categories', food_sources['Category'].unique(), food_sources['Category'].unique())
        filtered_data = food_sources[food_sources['Category'].isin(selected_categories)]
        st.dataframe(filtered_data)

    with col_detail:
        if "Plant Based" in selected_categories :
            default_food = ["nasi"]
        elif "Animal Based" in selected_categories :
            default_food = ["ayam"]
        selected_food = st.multiselect('Select Food Categories', filtered_data['Name'].unique(), default=default_food, max_selections=8)
        list_selected_food = {}
        num_columns = min(len(selected_food), 2)
        col_select = st.columns(num_columns)
        for idx, food in enumerate(selected_food):
            with col_select[idx % num_columns]:
                list_selected_food[food] = st.number_input(food)

    from backend.food_soruce_function import create_stacked_bar_plot, calculate_selected_foods,check_macro_balance
    selected_foods = calculate_selected_foods(list_selected_food, filtered_data)
    st.subheader("Selected Food and Result of Nutrition")
    col_fs_calories, col_fs_protein, col_fs_carbs, col_fs_fat = st.columns(4)
    col_fs_calories.metric("Calories", f'{round(selected_foods.iloc[:, 1].sum())} kcal', f'{round(diet_calories-selected_foods.iloc[:, 1].sum())} kcal ({check_macro_balance(diet_calories, selected_foods.iloc[:, 1].sum())})')
    col_fs_protein.metric("Protein", f'{round(selected_foods.iloc[:, 2].sum())} g', f'{round(protein-selected_foods.iloc[:, 2].sum())} g ({check_macro_balance(protein, selected_foods.iloc[:, 2].sum())})')
    col_fs_carbs.metric("Carbs", f'{round(selected_foods.iloc[:, 3].sum())} g', f'{round(carbs-selected_foods.iloc[:, 3].sum())} g ({check_macro_balance(carbs, selected_foods.iloc[:, 3].sum())})')
    col_fs_fat.metric("Fat", f'{round(selected_foods.iloc[:, 4].sum())} g', f'{round(fat-selected_foods.iloc[:, 4].sum())} g ({check_macro_balance(fat, selected_foods.iloc[:, 4].sum())})')

    col_viz_macro, col_table_food = st.columns([0.55, 0.45])
    with col_table_food:
        st.write("### Macro Nutrition of Selected Food")
        st.dataframe(selected_foods)
    with col_viz_macro:
        daily_macro = {"Calories": diet_calories, "Protein": protein, "Carbs": carbs, "Fat": fat}
        create_stacked_bar_plot(daily_macro, selected_foods.iloc[:, 1:5])