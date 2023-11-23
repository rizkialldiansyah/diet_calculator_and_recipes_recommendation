from datetime import datetime, timedelta
import math

class FitnessCalculator:
    def __init__(self, gender, height_cm, weight_kg, neck_size, hips_size, waist_size, age, activity_level, goal, start_date, target_date, target_weight):
        self.gender = gender.lower()
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.neck_size = neck_size
        self.hips_size = hips_size
        self.waist_size = waist_size
        self.age = age
        self.activity_level = activity_level
        self.goal = goal
        self.start_date = start_date
        self.target_date = target_date
        self.target_weight = target_weight

    def calculate_bmi(self):
        height_m = self.height_cm / 100
        bmi = self.weight_kg / (height_m ** 2)
        ideal_weight_low = (18.5 * ((self.height_cm / 100) ** 2))
        ideal_weight_high = (25 * ((self.height_cm / 100) ** 2))
        condition = "Normal"
        if bmi < 18.5:
            condition = "Underweight"
        elif bmi >= 25:
            condition = "Overweight"
            if bmi >= 30:
                condition = "Obesity"
                if bmi >= 40:
                    condition = "Severe Obesity"
        if self.weight_kg < ideal_weight_low:
            condition = "Wasting"
        return {"bmi": bmi, "low": ideal_weight_low, "high": ideal_weight_high, "condition": condition}

    def calculate_navy_body_fat(self):
        if self.neck_size == None and self.waist_size == None:
            neck = self.calculate_neck_size()
            waist = self.calculate_waist_size()
            hips = self.calculate_hips_size()
        else:
            neck = self.neck_size
            waist = self.waist_size
            hips = self.hips_size
        if self.gender == 'male':
            body_fat_percentage = (495 / (1.0324 - (0.19077 * (math.log10(waist - neck))) + (0.15456 * (math.log10(self.height_cm))))) - 450
        elif self.gender == 'female':
            body_fat_percentage = (495 / (1.29579 - (0.35004 * (math.log10(waist+hips-neck))) + (0.22100 * (math.log10(self.height_cm))))) - 450
        return round(body_fat_percentage, 2)

    def calculate_bmi_fat(self):
        bmi = self.weight_kg / ((self.height_cm / 100) ** 2)
        if self.gender == 'male':
            body_fat_percentage = 1.20 * bmi + 0.23 * self.age - 16.2
        elif self.gender == 'female':
            body_fat_percentage = 1.20 * bmi + 0.23 * self.age - 5.4
        return round(body_fat_percentage, 2)

    def calculate_bmr(self):
        bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age)
        return bmr + 5 if self.gender == 'male' else bmr - 161

    def calculate_tdee(self):
        activity_levels = {
            'sedentary': 1.2,
            'lightly active': 1.375,
            'moderately active': 1.55,
            'very active': 1.725,
            'super active': 1.9
        }
        if self.activity_level.lower() in activity_levels:
            return self.calculate_bmr() * activity_levels[self.activity_level.lower()]
        else:
            return "Invalid activity level input"

    def calculate_daily_calories(self):
        goal_levels = {
            'lose weight': -0.2,
            'slowly lose weight': -0.1,
            'maintain weight': 0,
            'slowly gain weight': 0.1,
            'gain weight': 0.2
        }
        return self.calculate_tdee() + (self.calculate_tdee() * goal_levels[self.goal.lower()])

    def calculate_macro(self, calories=None, carbs_percentage=50):
        if calories is None:
            daily_calories = self.calculate_daily_calories()
        else:
            daily_calories = calories

        pounds = self.weight_kg * 2.20462
        protein_cal = pounds * 4 # Change this value based on your desired carb percentage
        fat_percentage = 100 - carbs_percentage

        carb_cal = (daily_calories - protein_cal) * (carbs_percentage / 100)
        fat_cal = (daily_calories - protein_cal) * (fat_percentage / 100)

        protein_gram = pounds
        carbs_gram = carb_cal / 4
        fat_gram = fat_cal / 9

        return {"protein": protein_gram, "carbs": carbs_gram, "fat": fat_gram,
                "protein_percentage": protein_cal, "carbs_percentage": carb_cal, "fat_percentage": fat_cal}


    def calculate_weight_change(self):
        # Convert start_date and target_date to datetime objects
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        target_date = datetime.strptime(self.target_date, "%Y-%m-%d")

        # Calculate total days between start_date and target_date
        total_days = (target_date - start_date).days

        # Determine whether it's weight gain or weight loss
        goal = 'gain' if self.target_weight > self.weight_kg else 'loss'

        # Calculate the target weight change
        weight_change_target = self.target_weight - self.weight_kg if goal == 'gain' else self.weight_kg - self.target_weight

        # Calculate total calories needed for the weight change
        calories_per_kilogram = 7700
        total_calories = weight_change_target * calories_per_kilogram

        # Calculate average calories per day
        average_calories_per_day = total_calories / total_days
        if goal == 'loss':
            average_calories_per_day = -average_calories_per_day  # Adjust for weight loss (negative calories)

        # Calculate additional calories needed or reduced per day
        target_change_per_week = 0.7
        additional_calories_per_day = target_change_per_week * calories_per_kilogram / 7 if goal == 'gain' else -target_change_per_week * calories_per_kilogram / 7

        # Estimate time required for 0.5 kg change per week
        weeks_required = weight_change_target / target_change_per_week

        # Calculate end date based on estimated weeks required
        estimated_end_date = start_date + timedelta(weeks=weeks_required)

        # Build the result dictionary
        result = {
            "total_days": total_days,
            "total_days_estimate": int(weeks_required*7),
            "weight_change_target": weight_change_target,
            "total_calories": total_calories,
            "average_calories_per_day": round(average_calories_per_day, 2),
            "goal": goal,
            "weeks_required": weeks_required,
            "estimated_end_date": estimated_end_date.strftime("%Y-%m-%d"),  # Format end date as string
            "additional_calories_per_day": round(additional_calories_per_day, 2),
        }

        return result

    def calculate_neck_size(self):
        # Assuming neck size is 15% of height
        return self.height_cm * 0.15

    def calculate_waist_size(self):
        # Assuming waist size is 40% of height
        return self.height_cm * 0.4

    def calculate_hips_size(self):
        # Assuming hips size is 45% of height
        return self.height_cm * 0.45