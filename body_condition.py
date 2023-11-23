import streamlit as st
from backend.fit_calculators import FitnessCalculator
import pandas as pd
import plotly.express as px

def show_body_condition():
    user_data = st.session_state.user_data

    st.write(f"## Hello, {user_data['name']}")
    calculator = FitnessCalculator(**user_data['fit_user'])

    # Inisilazation Variable
    bmi_result = calculator.calculate_bmi()
    navy_body_fat_result = calculator.calculate_navy_body_fat()
    bmi_fat_result = calculator.calculate_bmi_fat()
    bmr_result = calculator.calculate_bmr()
    tdee_result = calculator.calculate_tdee()
    weight_change_result = calculator.calculate_weight_change()
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
            st.markdown(f'<p class="big-font">{user_data["fit_user"]["height_cm"]} cm</p>', unsafe_allow_html=True)
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
            st.metric("Target Weight", f'{user_data["fit_user"]["target_weight"]} kg', f'{(user_data["fit_user"]["target_weight"]-user_data["fit_user"]["weight_kg"])} kg ({user_data["fit_user"]["goal"]})')
            st.markdown(f'<span class="small-font">Body Fat Precentage (Navy)</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{navy_body_fat_result}% </p>', unsafe_allow_html=True)
        with col_bf4:
            st.write(f"Activity Level:")
            st.markdown(f'<p class="big-font">{user_data["fit_user"]["activity_level"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<span class="small-font">Body Fat Precentage (BMI)</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{bmi_fat_result}%</p>', unsafe_allow_html=True)

    # Detail            
    with st.expander("Detail"):
        tab_date_until_target,tab_date_until_estimate, tab_activity = st.tabs(["Weight Goals", "Daily Nutrition","Activity Level"])
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
                df_combined = pd.merge(df_data1, df_data2, on='Date', how='outer', suffixes=(' by Target', ' by Better Estimate'))
                # Set warna yang diinginkan
                colors = {'Weight by Target': '#E9E5D6', 'Weight by Better Estimate': '#464E2E'}

                # Buat grafik garis dengan Plotly Express
                fig = px.line(df_combined, x='Date', y=['Weight by Target', 'Weight by Better Estimate'], 
                            labels={'value': 'Weight', 'variable': 'Data Set'}, 
                            title='Line Chart of Weight Data', color_discrete_map=colors)
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
                    st.markdown(f'<p class="big-font">{round(bmr_result,1)} kcal</p>', unsafe_allow_html=True)
                with col_tdee:
                    st.metric("Total Daily Energy Expenditure (TDEE)", f'{round(tdee_result,1)} kcal', f'{round(tdee_result-bmr_result,1)} kcal ({user_data["fit_user"]["activity_level"].replace("Active", "")} Active)')
                with col_dcal:
                        st.metric("Daily Calories In", f'{round(diet_calories,1)} kcal', f'{round(diet_calories - tdee_result,1)} kcal ({kind_diet} Calories)')
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
                    st.session_state.protein = protein
                    st.session_state.carbs = carbs
                    st.session_state.fat = fat
                    st.session_state.diet_calories = diet_calories
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
                    fig.update_layout(
                        margin=dict(l=0, r=160, t=30, b=30),  # Mengatur margin
                        legend=dict(x=0.375, y=0.5, traceorder='normal')
                    )
                    st.plotly_chart(fig)

                protein_percentage = round(macro_target_result["protein_percentage"],1)
                carbs_percentage = round(macro_target_result["carbs_percentage"],1)
                fat_percentage = round(macro_target_result["fat_percentage"],1)
                display_pie_chart(protein_percentage, carbs_percentage, fat_percentage)
            st.info("""
                Important Note: Your daily calorie choice and macronutrient composition will influence the recommended meal recipes and food sources you select. It is advised to carefully determine your daily calorie target and the percentage distribution between fat and carbohydrates based on your health or fitness goals. This information will assist in filtering and presenting meal recipes that align with your desired daily nutritional needs.

                ⚠️ Please consider these factors when making your choices.
                """)
            
        with tab_activity:
            from activity_level import form_activity_level
            form_activity_level()