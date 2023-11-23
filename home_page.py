import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, timedelta
from backend.fit_calculators import FitnessCalculator
import plotly.express as px
import numpy as np
import re
import string

st.set_page_config(
    page_title="Fitness Diet App",
    page_icon="💪🏾",
    layout="wide",
)

st.markdown("""
<style>
body {
    font-family: 'Arial', sans-serif;
    /* Ganti 'Arial' dengan font yang diinginkan */
}
.small_font {
    font-size:12px !important;
    font-weight: 550; 
}
.big-font {
    margin-top: -0.6em;
    font-size:35px !important;
    font-weight: 350;
}
</style>
""", unsafe_allow_html=True)

def get_user_input():
    st.title("Sign Up")

    # Buat form untuk sign-up di tengah halaman
    with st.form("signup_form"):
        name = st.text_input("Name", placeholder="Enter Your Name")
        email = st.text_input("Email", placeholder="Enter Your Email")

        # Gunakan columns untuk meletakkan elemen dalam satu baris
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("Select Gender", ["Male", "Female"])
            age = st.slider("Enter Age", 18, 99, 30)
        with col2:
            height_cm = st.slider("Enter Height (cm)", 140, 220, 175)
            weight_kg = st.slider("Enter Weight (kg)", 40, 200, 80)
        
        with st.expander("Costume Neck, Hips and Waist Size"):
            st.info('Customizing neck, hips, and waist size affects Navy Fat calculation. If not customized, estimates based on typical proportions will be used.', icon="ℹ️")
            # Tentukan apakah elemen slider dinonaktifkan berdasarkan nilai agree
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
        goal = st.selectbox("Select Goal", ["Lose Weight", "Slowly Lose Weight", "Maintain Weight", "Slowly Gain Weight", "Gain Weight"])

        # Gunakan baris untuk meletakkan elemen dalam satu baris
        col3,col4 = st.columns(2)
        with col3:
            target_weight = st.slider("Enter Target Weight (kg)", 40, 200, 75)
        with col4:
            target_date = st.date_input("Select Target Date", value=pd.to_datetime('2024-03-11'))


        # Gunakan st.form_submit_button untuk menambahkan tombol submit
        submitted = st.form_submit_button("Sign Up")

    # Jika formulir sudah disubmit, simpan data pengguna ke session
    if submitted:
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
        st.session_state.user_data = user_data
        st.success("Sign-up successful!")

def show_dashboard():
    user_data = st.session_state.user_data

    st.write(f"## Hello, {user_data['name']}")
    # Lakukan kalkulasi menggunakan user_data dari session_state
    calculator = FitnessCalculator(**user_data['fit_user'])

    # Contoh penggunaan fungsi-fungsi di dalam class
    bmi_result = calculator.calculate_bmi()
    navy_body_fat_result = calculator.calculate_navy_body_fat()
    bmi_fat_result = calculator.calculate_bmi_fat()
    bmr_result = calculator.calculate_bmr()
    tdee_result = calculator.calculate_tdee()
    daily_calories_result = calculator.calculate_daily_calories()
    macro_result_standard = calculator.calculate_macro()
    weight_change_result = calculator.calculate_weight_change()
    macro_target_result = calculator.calculate_macro(tdee_result + weight_change_result['average_calories_per_day'])
    if round(weight_change_result["average_calories_per_day"] / 1100, 2) <= 0:
        add_minus= "reducing"
        kind_diet = "Deficit"
    else:
        add_minus= "increase"
        kind_diet = "Surplus"
        
    st.markdown("""---""")
    # === Body Fit ===
    with st.container():
        st.header("Body Fit")
        col_bf1, col_bf2, col_bf3, col_bf4 = st.columns(4)
        with col_bf1:
            st.markdown(f'<span class="small-font">Your Height</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{user_data["fit_user"]["height_cm"]} kg</p>', unsafe_allow_html=True)
            st.markdown(f'<span class="small-font">Healty Weight Range</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{round(bmi_result["low"], 1)} kg - {round(bmi_result["high"], 1)} kg</p>', unsafe_allow_html=True)

        with col_bf2:
            if bmi_result["condition"] in ["Obesity", "Severe Obesity", "Wasting", "Underweight", "Overweight"]: 
                color_condition = "inverse"
            else:
                color_condition = "normal"
            st.metric("Your Weight", f'{user_data["fit_user"]["weight_kg"]} kg', bmi_result["condition"], color_condition)
            st.write(f"Body Mass Index (BMI):")
            st.markdown(f'<p class="big-font">{round(bmi_result["bmi"], 1)} kg/m²</p>', unsafe_allow_html=True)
        with col_bf3:
            st.metric("Target Weight", f'{user_data["fit_user"]["target_weight"]} kg', f'{(user_data["fit_user"]["target_weight"]-user_data["fit_user"]["weight_kg"])} kg')
            st.markdown(f'<span class="small-font">Body Fat Precentage (Navy)</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{navy_body_fat_result}%</p>', unsafe_allow_html=True)
        with col_bf4:
            st.write(f"Activity Level:")
            st.markdown(f'<p class="big-font">{user_data["fit_user"]["activity_level"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<span class="small-font">Body Fat Precentage (BMI)</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{bmi_fat_result}%</p>', unsafe_allow_html=True)

    # Detail            
    with st.expander("Detail"):
        tab_date_until_target,tab_date_until_estimate, tab_weigth = st.tabs(["Weight Goals", "Daily Nutrition","Zigzag Diet"])
        with tab_date_until_target:
            st.title('Detail of your weight goals')
            col_tab_date_target1, col_tab_date_target2 = st.columns([0.55, 0.45])
            with col_tab_date_target1:
                # Generate data
                dates_data1 = pd.date_range(start=user_data["fit_user"]["start_date"], periods=weight_change_result['total_days'])
                weight_kg_data1 = user_data["fit_user"]["weight_kg"]
                weights_data1 = [weight_kg_data1]

                for day in range(1, weight_change_result['total_days']):
                    weight_kg_data1 += weight_change_result['average_calories_per_day'] / 7700
                    weights_data1.append(weight_kg_data1)

                df_data1 = pd.DataFrame({'Date': dates_data1, 'Weight': weights_data1})

                dates_data2 = pd.date_range(start=user_data["fit_user"]["start_date"], periods=weight_change_result['total_days_estimate'])
                weight_kg_data2 = user_data["fit_user"]["weight_kg"]
                weights_data2 = [weight_kg_data2]

                for day in range(1, weight_change_result['total_days_estimate']):
                    weight_kg_data2 += weight_change_result['additional_calories_per_day'] / 7700
                    weights_data2.append(weight_kg_data2)

                df_data2 = pd.DataFrame({'Date': dates_data2, 'Weight': weights_data2})

                # Merge DataFrames
                df_combined = pd.merge(df_data1, df_data2, on='Date', how='outer', suffixes=(' by Target', ' by Better Estimate'))

                # Visualization
                fig = px.line(df_combined, x='Date', y=['Weight by Target', 'Weight by Better Estimate'], labels={'value': 'Weight', 'variable': 'Data Set'}, title='Line Chart of Weight Data')
                fig.update_layout(showlegend=True, legend=dict(title='Data Set'), xaxis_title='Date', yaxis_title='Weight', height=500)
                st.plotly_chart(fig)

            with col_tab_date_target2:
                col_in1_1, col_in1_2 = st.columns(2)
                with col_in1_1:
                    st.subheader("Your Choice")
                    st.metric("Date", f'{user_data["fit_user"]["target_date"]}', f'{round(weight_change_result["average_calories_per_day"] / 1100, 2)} kg/week')
                    st.metric(f"Daily {kind_diet} Calories", f'{round(tdee_result+weight_change_result["average_calories_per_day"],1)} kcal', f'{round(weight_change_result["average_calories_per_day"], 2)} kcal')
                with col_in1_2:
                    st.subheader("Additional Choice")
                    st.metric("Date", f'{weight_change_result["estimated_end_date"]}', f'{weight_change_result["additional_calories_per_day"] / 1100} kg/week')
                    st.metric(f"Daily {kind_diet} Calories", f'{round(tdee_result+weight_change_result["additional_calories_per_day"],1)} kcal', f'{round(weight_change_result["additional_calories_per_day"], 2)} kcal')
                if abs(round(weight_change_result["average_calories_per_day"] / 1100, 2)) >= 1:
                    info_warning = "Important Information"
                    icon_info = "⚠️"
                    infromation = "We strongly recommend adhering to the provided time estimation in your diet plan. Adjusting the target date may adversely affect your health and impede the achievement of desired results. This is because the weekly weight loss exceeds 1 kg/week."
                elif abs(round(weight_change_result["average_calories_per_day"] / 1100, 2)) >= 0.7:
                    info_warning = "Additional Information"
                    icon_info = "ℹ️"
                    infromation = f"Consistency is vital for diet success. If maintaining a consistent routine is challenging, it's recommended to follow the recommended time estimation for a more sustainable approach to your weight goals"
                else:
                    info_warning = "Additional Information"
                    icon_info = "ℹ️"
                    infromation = f"For more effective diet results, it is advised to adhere to the provided time estimation by {add_minus} calories by 770 per day. This helps ensure consistency and success in achieving weight loss or gain goals in a healthy and sustainable manner."
                st.info(info_warning,icon=icon_info)
                st.write(infromation)

        with tab_date_until_estimate:
            st.title('Detail of your daily nutritions')
            col_viz, col_nutrition= st.columns([0.4, 0.6])
            with col_nutrition:
                option = st.selectbox(
                    "Choice Weight Goals",
                    ("Your Goals", "Additional Goals"),
                    )
                
                if "carbs_percentage_target" not in st.session_state:
                    t_precentage = 50
                else:
                    t_precentage = st.session_state.carbs_percentage_target

                if option == "Your Goals":
                    diet_calories = round(tdee_result+weight_change_result["average_calories_per_day"],1)
                elif option == "Additional Goals":
                    diet_calories = round(tdee_result+weight_change_result["additional_calories_per_day"],1)

                col_bmr, col_tdee, col_dcal = st.columns(3)
                with col_bmr:
                    st.markdown(f'<span class="small-font">Basal Metabolic Rate (BMR)</span>', unsafe_allow_html=True)
                    st.markdown(f'<p class="big-font">{bmr_result} kcal</p>', unsafe_allow_html=True)
                with col_tdee:
                    st.metric("Total Daily Energy Expenditure (TDEE)", f'{tdee_result} kcal', f'{round(tdee_result-bmr_result,1)} kcal ({user_data["fit_user"]["activity_level"].replace("Active", "")} Active)')
                with col_dcal:
                        st.metric("Daily Calories In", f'{diet_calories} kcal', f'{round(diet_calories - tdee_result,1)} kcal ({kind_diet} Calories)')
                with st.container():
                    st.write(f"### Macro")
                    st.session_state.carbs_percentage_target = st.slider("Carbo Percentage", 10, 100, t_precentage, key="target")
                    macro_target_result = calculator.calculate_macro(diet_calories, carbs_percentage=st.session_state.carbs_percentage_target)
                    protein = round(macro_target_result["protein"],1)
                    carbs = round(macro_target_result["carbs"],1)
                    fat = round(macro_target_result["fat"],1)
                    col_prot, col_carbs, col_fat = st.columns(3)
                    with col_prot:
                        st.markdown(f'<span class="small-font">Protein</span>', unsafe_allow_html=True)
                        st.markdown(f'<p class="big-font">{protein} gram</p>', unsafe_allow_html=True)
                    with col_carbs:
                        st.markdown(f'<span class="small-font">Carbo</span>', unsafe_allow_html=True)
                        st.markdown(f'<p class="big-font">{carbs} gram</p>', unsafe_allow_html=True)
                    with col_fat:
                        st.markdown(f'<span class="small-font">Fat</span>', unsafe_allow_html=True)
                        st.markdown(f'<p class="big-font">{fat} gram</p>', unsafe_allow_html=True)
            with col_viz:
                def display_pie_chart(protein, carbs, fat):
                    labels = ['Protein', 'Carbs', 'Fat']
                    values = [protein, carbs, fat]

                    labels = [f'Calories of {label}' for label, value in zip(labels, values)]
                    fig = px.pie(
                        names=labels,
                        values=values,
                        title='Macro Nutrition Distribution',
                        hole=0.4,
                        color=labels,
                        color_discrete_map={'Calories of Protein': '#7B8FA1', 'Calories of Carbs': '#94A684', 'Calories of Fat': '#A4907C'}
                    )

                    # Set margin atau jarak antara legenda dan visualisasi
                    fig.update_layout(
                        margin=dict(l=0, r=160, t=30, b=30),  # Mengatur margin
                        legend=dict(x=0.375, y=0.5, traceorder='normal')
                    )

                    st.plotly_chart(fig)

                protein_percentage = round(macro_target_result["protein_percentage"],1)
                carbs_percentage = round(macro_target_result["carbs_percentage"],1)
                fat_percentage = round(macro_target_result["fat_percentage"],1)
                display_pie_chart(protein_percentage, carbs_percentage, fat_percentage)

    st.markdown("""---""")
    st.header("Food Source and Recipes Recommendation")
    tab_food_source, tab_recipes_recommend = st.tabs(["Food Source", "Recipes Recommendation"])
    with tab_food_source:
        col_table, col_detail = st.columns([0.42, 0.58])
        with col_table:
            food_sources = pd.read_csv("./data/food_sources.csv")
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

    with tab_recipes_recommend:
        from backend.model import recommand
        from backend.generate_plan import recommend_meal
        with st.form("meal-plan"):
            meal_plan = st.slider("How much do you intend to consume in a day?", 3, 5, 3)
            st.write("### Limit Preperation Time")
            col_meal = st.columns(meal_plan)
            meal_schedule = ['Breakfast', 'Launch', 'Dinner', 'Morning Snack', 'Afternoon Snack']
            limit_preps = {}
            for idx in range(meal_plan):
                with col_meal[idx]:
                    limit_preps[meal_schedule[idx].lower()] = st.number_input(meal_schedule[idx], min_value=10, step=5, value=10)  
            submitted_plan = st.form_submit_button("Generate") 
        try:                
            meal_schedules = recommend_meal(diet_calories, macro_target_result, meal_plan, limit_preps)
            diet_dataset = pd.read_csv("./data/recipes_fatsecret.csv")
            ingredients_data = diet_dataset['Ingredients'].apply(eval)
            all_ingredients = [ingredient for ingredients in ingredients_data for ingredient in ingredients]
            food_items = [re.sub(r'\d+\s*(gram|ml|sdt|sdm|siung|sedang|buah|kecil|besar|mangkok|gelas|elas|sejumput|utuh|elas|ons|porsi|g|tsp|tbsp|sachet|cup|iris|diameter|cm|l|liter|)?', '', item).strip() for item in all_ingredients]
            food_items = [''.join(char for char in item if char not in string.punctuation) for item in food_items]
            food_items = [item.lower() for item in food_items if item]
            selected_foodsource = st.multiselect('Select ingredients you dislike or are allergic to', set(food_items), default="tepung terigu", max_selections=10)
            max_calories=2000
            max_daily_fat=100
            max_daily_saturatedfat=13
            max_daily_cholesterol=300
            max_daily_sodium=2300
            max_daily_carbohydrate=325
            max_daily_sugar=40
            max_daily_protein=200
            max_daily_potassium = 2000
            max_list=[max_calories,max_daily_fat,max_daily_saturatedfat,max_daily_cholesterol,max_daily_sodium,max_daily_carbohydrate,max_daily_sugar,max_daily_protein, max_daily_potassium]
            col_meal_result = st.columns(meal_plan) 
            style_desc = "style='font-size: 14px; margin-top: -0.9em'"
            style_head= "style='font-size: 18px; font-weight: 550;'"
            style_subhead= "style='font-size: 16px; font-weight: 550;'"
            recomend_result = []
            for idx in range(meal_plan):
                with col_meal_result[idx]:
                    st.write(f"### {meal_schedule[idx]}")
                    if idx < len(recomend_result):
                        recommend_meal = recomend_result[idx]
                    else:
                        recommend_meal = recommand(diet_dataset,meal_schedules[idx]['nutritions'], max_list,ingredient_filter=selected_foodsource, prep_time_limit=meal_schedules[idx]['prep_limit'])
                        recomend_result.append(recommend_meal)
            st.session_state.recomend_result = recomend_result
            for recommend_reslusts in st.session_state.recomend_result:
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
            st.write("---")
            st.subheader("Select your recipe meal")
            col_choose_meal = st.columns(meal_plan)
            if meal_plan == 5:
                with col_choose_meal[0]:
                    name_recipes_breakfest = [name for name in recomend_result[0]["Name"]]
                    select_recipes_breakfest = st.selectbox(label = f'{meal_schedule[0]}', options=name_recipes_breakfest, key="breakfest")
                with col_choose_meal[1]:
                    name_recipes_launch = [name for name in recomend_result[1]["Name"]]
                    select_recipes_launch = st.selectbox(label = f'{meal_schedule[1]}', options=name_recipes_launch, key="launch")
                with col_choose_meal[2]:
                    name_recipes_dinner = [name for name in recomend_result[2]["Name"]]
                    select_recipes_dinner = st.selectbox(label = f'{meal_schedule[2]}', options=name_recipes_dinner, key="dinner")
                with col_choose_meal[3]:
                    name_recipes_ms = [name for name in recomend_result[3]["Name"]]
                    select_recipes_ms = st.selectbox(label = f'{meal_schedule[3]}', options=name_recipes_ms, key="ms")
                with col_choose_meal[4]:
                    name_recipes_as = [name for name in recomend_result[4]["Name"]]
                    select_recipes_as = st.selectbox(label = f'{meal_schedule[4]}', options=name_recipes_as, key="as")
            if meal_plan == 4:
                with col_choose_meal[0]:
                    name_recipes_breakfest = [name for name in recomend_result[0]["Name"]]
                    select_recipes_breakfest = st.selectbox(label = f'{meal_schedule[0]}', options=name_recipes_breakfest, key="breakfest")
                with col_choose_meal[1]:
                    name_recipes_launch = [name for name in recomend_result[1]["Name"]]
                    select_recipes_launch = st.selectbox(label = f'{meal_schedule[1]}', options=name_recipes_launch, key="launch")
                with col_choose_meal[2]:
                    name_recipes_dinner = [name for name in recomend_result[2]["Name"]]
                    select_recipes_dinner = st.selectbox(label = f'{meal_schedule[2]}', options=name_recipes_dinner, key="dinner")
                with col_choose_meal[3]:
                    name_recipes_ms = [name for name in recomend_result[3]["Name"]]
                    select_recipes_ms = st.selectbox(label = f'{meal_schedule[3]}', options=name_recipes_ms, key="ms")
            if meal_plan == 3:
                with col_choose_meal[0]:
                    name_recipes_breakfest = [name for name in recomend_result[0]["Name"]]
                    select_recipes_breakfest = st.selectbox(label = f'{meal_schedule[0]}', options=name_recipes_breakfest, key="breakfest")
                with col_choose_meal[1]:
                    name_recipes_launch = [name for name in recomend_result[1]["Name"]]
                    select_recipes_launch = st.selectbox(label = f'{meal_schedule[1]}', options=name_recipes_launch, key="launch")
                with col_choose_meal[2]:
                    name_recipes_dinner = [name for name in recomend_result[2]["Name"]]
                    select_recipes_dinner = st.selectbox(label = f'{meal_schedule[2]}', options=name_recipes_dinner, key="dinner")
            col_macro_recipes = st.columns(4)
            col_sub_macro = st.columns(4)
            st.write(select_recipes_breakfest)
            st.write(select_recipes_launch)
            st.write(select_recipes_dinner)
            col_viz_macro_recipes, col_viz_macro_recipes_2 = st.columns([0.55, 0.45])
            with col_viz_macro_recipes:
                st.write("### Macro Nutrition of Selected Food")
                st.dataframe(selected_foods)
            with col_viz_macro_recipes_2:
                daily_macro = {"Calories": diet_calories, "Protein": protein, "Carbs": carbs, "Fat": fat}
                create_stacked_bar_plot(daily_macro, selected_foods.iloc[:, 1:5])
            
        except Exception as e:
            # Tangkap error dan tampilkan menggunakan st.exception
            st.exception(e)
            st.error("We apologize for the inconvenience in the recommendation process due to the applied filters limiting the dataset. To enhance recommendation accuracy, please consider adding estimated preparation time for the recipes or refining the list of disliked or allergenic ingredients. Thank you for your understanding.", icon="🚨")


        

def recommendation_recipes():
    st.title("Recipe Recommendations")

    # Ambil data pengguna dari session_state
    user_data = st.session_state.user_data
    percentage_standard = st.session_state.carbs_percentage_standard
    percentage_target = st.session_state.carbs_percentage_target
    calculator = FitnessCalculator(**user_data['fit_user'])

    macro_result = calculator.calculate_macro()
    daily_calories_result = calculator.calculate_daily_calories()

    st.write(f"### Daily Calories Result:")
    st.write(percentage_standard)
    st.write("### Daily Calories Result:")
    st.write(percentage_target)


    st.write("### Daily Calories Result:")
    st.write(daily_calories_result)

    st.write("### Macro Result:")
    st.write(macro_result)
    
    # Tampilkan rekomendasi resep di sini
    st.write("## Recommended Recipes")
    st.write("Here are some recommended recipes based on your profile:")
    # ...

if "user_data" not in st.session_state:
    get_user_input()
else:
    show_dashboard()
        
    