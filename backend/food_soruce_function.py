import streamlit as st
import plotly.express as px
import pandas as pd

def calculate_selected_foods(faktor, food_sources):
    selected_foods = food_sources.loc[food_sources["Name"].isin(list(faktor.keys())), ["Name", "Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)"]]
    for bahan, nilai in faktor.items():
        selected_foods.loc[selected_foods["Name"] == bahan, ["Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)",]] = (selected_foods.loc[selected_foods["Name"] == bahan, ["Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)",]] / 100) * nilai
        selected_foods.loc[selected_foods["Name"] == bahan, "Portion (g)"] = nilai
    return selected_foods

def check_macro_balance(diet_macro, total_food_calories):
    calorie_balance = round(diet_macro - total_food_calories)
    if calorie_balance < 0:
        return "Over"
    elif calorie_balance > 0:
        return "Less"
    else:
        return "Good"
        
def create_stacked_bar_plot(daily_macro, selected_food):
    selected_food.rename(columns={
        "Calories (kcal)": "Calories",
        "Protein (g)": "Protein",
        "Carbs (g)": "Carbs",
        "Fat (g)": "Fat"
    }, inplace=True)

    total_selected_macro = round(selected_food.sum(),1)

    percentage_df = pd.DataFrame({
        "Selected Food": total_selected_macro.values,
        "Selected Food (%)": round((total_selected_macro / pd.Series(daily_macro)) * 100),
        "Daily Macro": pd.Series(daily_macro),
        "Daily Macro (%)": round(100 - ((total_selected_macro / pd.Series(daily_macro)) * 100)).clip(lower=0),
        "Exceeds": total_selected_macro.values > pd.Series(daily_macro)
    }, index=total_selected_macro.index)
    colors = {'Selected Food (%)': '#445D48', 'Daily Macro (%)': '#B5CB99'}
    fig = px.bar(percentage_df,
                x=percentage_df.index,
                y=['Selected Food (%)', 'Daily Macro (%)'],
                labels={'value': 'Percentage'},
                title='Macro Nutritions',
                color_discrete_map=colors
                )

    # Menambahkan garis horizontal pada nilai 100
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(percentage_df) - 0.5,
        y0=100,
        y1=100,
        line=dict(color="#9A4444", width=2, dash="dash"),
    )

    # Menyesuaikan tata letak dan penamaan legenda
    fig.update_layout(barmode='stack', legend_title_text='Macro Nutritions')
    fig.update_xaxes(title_text='Macro')
    fig.update_yaxes(title_text='Percentage')

    # Menampilkan plot menggunakan Streamlit
    st.plotly_chart(fig)
    