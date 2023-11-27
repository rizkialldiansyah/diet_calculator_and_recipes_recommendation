import streamlit as st
from backend.model import recommand
from backend.generate_plan import recommend_meal
import pandas as pd
import re
import string
from assets.css import *
import plotly.express as px
st.markdown(main_style, unsafe_allow_html=True)

diet_dataset = pd.read_csv("./backend/dataset/recipes_fatsecret.csv")
# Get All Unique Ingredients Data
ingredients_data = diet_dataset['Ingredients'].apply(eval)
all_ingredients = [ingredient for ingredients in ingredients_data for ingredient in ingredients]
food_items = [re.sub(r'\d+\s*(gram|ml|sdt|sdm|siung|sedang|buah|kecil|besar|mangkok|gelas|elas|sejumput|utuh|elas|ons|porsi|g|tsp|tbsp|sachet|cup|iris|diameter|cm|l|liter|)?', '', item).strip() for item in all_ingredients]
food_items = [''.join(char for char in item if char not in string.punctuation) for item in food_items]
food_items = [item.lower() for item in food_items if item]
diet_calories =  st.session_state.diet_calories
macro_target_result = {
    "protein": st.session_state.protein,
    "carbs": st.session_state.carbs,
    "fat":  st.session_state.fat}

def generate_recommendation():
    with st.form("meal-plan"):
        col_plan, col_prep = st.columns(2)
        meal_plan = col_plan.slider("How much do you intend to consume in a day?", 3, 5, 3)
        max_prep_time = col_prep.number_input("Limit Preperation Time", min_value=10, step=5, value=10)  
        selected_ingredients = st.multiselect('Select ingredients you dislike or are allergic to', set(food_items), default="tepung terigu", max_selections=10)
        submitted_plan = st.form_submit_button("Generate")
        if submitted_plan:
            meal_schedules = recommend_meal(diet_calories, macro_target_result, meal_plan, max_prep_time)
            recomend_result = []
            for idx in range(meal_plan):
                recommended_meal = recommand(diet_dataset,meal_schedules[idx]['nutritions'],ingredient_filter=selected_ingredients, prep_time_limit=meal_schedules[idx]['prep_limit'])
                recomend_result.append(recommended_meal)
            recommendation_data = {
                "meal_plan": meal_plan,
                "recipes_recommended": recomend_result,
            }
            st.toast("Generate Model")
            st.session_state.recommendation_data = recommendation_data

def create_stacked_bar_plot(daily_macro, selected_food):
    selected_food_df = pd.DataFrame(selected_food.values(), index=selected_food.keys(), columns=['Selected Food'])
    total_selected_macro = selected_food_df['Selected Food']
    percentage_df = pd.DataFrame({
        "Selected Food": total_selected_macro,
        "Selected Food (%)": round((total_selected_macro / pd.Series(daily_macro)) * 100),
        "Daily Macro": pd.Series(daily_macro),
        "Daily Macro (%)": round(100 - ((total_selected_macro / pd.Series(daily_macro)) * 100)).clip(lower=0),
        "Exceeds": total_selected_macro > pd.Series(daily_macro)
    }, index=total_selected_macro.index)
    colors = {'Selected Food (%)': '#445D48', 'Daily Macro (%)': '#B5CB99'}
    fig = px.bar(percentage_df,
                x=percentage_df.index,
                y=['Selected Food (%)', 'Daily Macro (%)'],
                labels={'value': 'Percentage'},
                title='Macro Nutritions',
                color_discrete_map=colors
                )
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(percentage_df) - 0.5,
        y0=100,
        y1=100,
        line=dict(color="#9A4444", width=2, dash="dash"),
    )
    fig.update_layout(barmode='stack', legend_title_text='Macro Nutritions')
    fig.update_xaxes(title_text='Macro')
    fig.update_yaxes(title_text='Percentage')
    st.plotly_chart(fig)

def create_macro_micro_pie_chart(macro_values, micro_values):
    labels = list(macro_values.keys()) + list(micro_values.keys())
    values = list(macro_values.values()) + list(micro_values.values())
    # Buat pie chart dengan Plotly
    colors = ['#3A4D39', '#4F6F52', '#ACB992', '#675D50', '#A9907E', '#F3DEBA', '#9A4444']
    fig = px.pie(names=labels, values=values, title='Macro and Micro Nutrients Distribution', hole=0.4, color_discrete_sequence=colors)
    fig.update_layout(
        margin=dict(l=0, r=190, t=100, b=0),  # Mengatur margin
        legend=dict(x=0.85, y=0.5, traceorder='normal')
    )
    # Menampilkan plot menggunakan Streamlit
    st.plotly_chart(fig)

def show_all_recommendation():
    recipes = st.session_state.recommendation_data["recipes_recommended"]
    meal_plan = st.session_state.recommendation_data["meal_plan"]
    meal_schedule = ['Breakfast', 'Lunch', 'Dinner', 'Morning Snack', 'Afternoon Snack']
    st.info("The recipe information provided in the recommendation system is sourced from the FatSecret website. To support FatSecret, visit their website at: https://www.fatsecret.co.id/.", icon="ℹ️")
    # Show All Recommendation Recipes
    col_meal_result = st.columns(meal_plan)
    for idx_meal_col, recommend_reslusts in enumerate(recipes):
        with col_meal_result[idx_meal_col]:
            st.write(f"### {meal_schedule[idx_meal_col]}")
            for idx, row in recommend_reslusts.iterrows():
                with st.expander(label=row['Name']):
                    intruction_str = [f"{number+1}. {eval(row['Intructions'])[number]}" for number in range(len(eval(row['Intructions'])))]
                    ingredients_str = [f"{eval(row['Ingredients'])[number]}" for number in range(len(eval(row['Ingredients'])))]
                    st.markdown(f"<p {style_head}>Nutritions</p>", unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(row[7:21]).transpose(), hide_index=True, )

                    st.markdown(f"<p {style_head}>Serving</p>", unsafe_allow_html=True)
                    st.markdown(f"<p {style_desc}>{row['Serving']}</p>", unsafe_allow_html=True)

                    st.markdown(f"<p {style_subhead}>Preparation Time</p>", unsafe_allow_html=True)
                    st.markdown(f"<p {style_desc}>{row['Prep Time']}</p>", unsafe_allow_html=True)

                    st.markdown(f"<p {style_subhead}>Cooking Time</p>", unsafe_allow_html=True)
                    st.markdown(f"<p {style_desc}>{row['Cook Time']}</p>", unsafe_allow_html=True)

                    st.markdown(f"<p {style_head}>Intructions</p>", unsafe_allow_html=True)
                    full_instructions = "<br>".join(intruction_str)
                    st.markdown(f"<p {style_desc}>{full_instructions}</p>", unsafe_allow_html=True)

                    st.markdown(f"<p {style_head}>Ingredients</p>", unsafe_allow_html=True)
                    full_ingredients = ", ".join(ingredients_str)
                    st.markdown(f"<p {style_desc}>{full_ingredients}</p>", unsafe_allow_html=True)
    # Visualization Selected Recipes
    st.write("---")
    st.subheader("Select your recipe meal")
    col_choose_meal = st.columns(meal_plan)
    for idx, recommend_reslusts in enumerate(recipes):
        with col_choose_meal[idx]:
            name_recipes = [name for name in recommend_reslusts["Name"]]
            st.selectbox(label=f'{meal_schedule[idx]}', options=name_recipes, key=f"{meal_schedule[idx].lower()}")
  
    # Inisialisasi variabel
    calories = 0
    protein = 0
    carbs = 0
    fat = 0
    serat = 0
    cholesterol = 0
    sodium = 0
    gula = 0

    for schedule_idx, recommend_reslusts in enumerate(recipes):
        key = meal_schedule[schedule_idx].lower()
        selected_recipe = recommend_reslusts.loc[recommend_reslusts["Name"] == st.session_state[key]]
        if not selected_recipe.empty:
            calories += selected_recipe["Kalori_kkal"].values[0]
            protein += selected_recipe["Protein_g"].values[0]
            carbs += selected_recipe["Karbohidrat_g"].values[0]
            fat += selected_recipe["Lemak_g"].values[0]
            serat += selected_recipe["Serat_g"].values[0]
            cholesterol += selected_recipe["Kolesterol_mg"].values[0]
            sodium += selected_recipe["Sodium_mg"].values[0]
            gula += selected_recipe["Gula_g"].values[0]

    from backend.food_soruce_function import check_macro_balance
    st.subheader("Selected Food and Result of Nutrition")
    col_fs_calories, col_fs_protein, col_fs_carbs, col_fs_fat = st.columns(4)
    col_fs_calories.metric("Calories", f'{round(calories)} kcal', f'{round(diet_calories-calories)} kcal ({check_macro_balance(diet_calories, calories)})')
    col_fs_protein.metric("Protein", f'{round(protein)} g', f'{round(macro_target_result["protein"]-protein)} g ({check_macro_balance(macro_target_result["protein"], protein)})')
    col_fs_carbs.metric("Carbs", f'{round(carbs)} g', f'{round(macro_target_result["carbs"]-carbs)} g ({check_macro_balance(macro_target_result["carbs"], carbs)})')
    col_fs_fat.metric("Fat", f'{round(fat)} g', f'{round(macro_target_result["fat"]-fat)} g ({check_macro_balance(macro_target_result["fat"], fat)})')

    col_fs_serat, col_fs_cholesterol, col_fs_sodium, col_fs_gula = st.columns(4)
    with col_fs_serat:
        st.markdown(f'<span class="small-font">Serat</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{round(serat)} g</p>', unsafe_allow_html=True)
    with col_fs_cholesterol:
        st.markdown(f'<span class="small-font">Cholesterol</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{round(cholesterol)} mg</p>', unsafe_allow_html=True)
    with col_fs_sodium:
        st.markdown(f'<span class="small-font">Sodium</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{round(sodium)} mg</p>', unsafe_allow_html=True)
    with col_fs_gula:
        st.markdown(f'<span class="small-font">Sugar</span>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{round(gula)} g</p>', unsafe_allow_html=True)
    st.write("### Macro Nutrition of Selected Food")
    col_viz_bar, col_viz_pie = st.columns([0.55, 0.45])
    with col_viz_pie:
        create_macro_micro_pie_chart({"Protein": protein, "Carbs": carbs, "Fat": fat}, {"Serat": serat, "Cholesterol": cholesterol*0.001, "Sodium": sodium*0.001, "Sugar": gula})
    with col_viz_bar:
        daily_macro = {"Calories": diet_calories, "Protein": macro_target_result["protein"], "Carbs": macro_target_result["carbs"], "Fat": macro_target_result["fat"]}
        create_stacked_bar_plot(daily_macro, {"Calories": calories, "Protein": protein, "Carbs": carbs, "Fat": fat})  


