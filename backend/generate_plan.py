from random import uniform as rnd

def meals_plan(number_of_meals):
    if number_of_meals==3:
        return {'breakfast':0.35,'launch':0.40,'dinner':0.25}
    elif number_of_meals==4:
        return {'breakfast':0.30,'launch':0.40,'dinner':0.25,'morning snack':0.05}
    else:
        return {'breakfast':0.30,'launch':0.40,'dinner':0.20,'morning snack':0.05,'afternoon snack':0.05}
    
def recommend_meal(calories, macro, number_of_meals, prep_food_time):
    meals_calories_perc = meals_plan(number_of_meals)
    recommended_meal = []
    for meal in meals_calories_perc:
        meal_calories=meals_calories_perc[meal]*calories
        meal_protein=meals_calories_perc[meal]*macro["protein"]
        meal_carbs=meals_calories_perc[meal]*macro["carbs"]
        meal_fat=meals_calories_perc[meal]*macro["fat"]
        if meal=='breakfast':        
            recommended_nutrition = {'nutritions': [meal_calories, meal_fat, rnd(0,4), rnd(0,30), rnd(0,400), meal_carbs, rnd(0,10), meal_protein, rnd(100,500)], 'prep_limit': prep_food_time}
        elif meal=='launch':
            recommended_nutrition = {'nutritions': [meal_calories, meal_fat, rnd(0,4), rnd(0,30), rnd(0,400), meal_carbs, rnd(0,10), meal_protein, rnd(100,500)], 'prep_limit': prep_food_time}
        elif meal=='dinner':
            recommended_nutrition = {'nutritions': [meal_calories, meal_fat, rnd(0,4), rnd(0,30), rnd(0,400), meal_carbs, rnd(0,10), meal_protein, rnd(100,500)], 'prep_limit': prep_food_time}
        else:
            recommended_nutrition = {'nutritions': [meal_calories, meal_fat, rnd(0,4), rnd(0,30), rnd(0,400), meal_carbs, rnd(0,10), meal_protein, rnd(100,500)], 'prep_limit': prep_food_time}
        recommended_meal.append(recommended_nutrition)
    return recommended_meal
