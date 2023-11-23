import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

max_calories=2000
max_daily_fat=100
max_daily_saturatedfat=13
max_daily_cholesterol=300
max_daily_sodium=2300
max_daily_carbohydrate=325
max_daily_sugar=40
max_daily_protein=200
max_daily_potassium = 2000
max_nutritional_values=[max_calories,max_daily_fat,max_daily_saturatedfat,max_daily_cholesterol,max_daily_sodium,max_daily_carbohydrate,max_daily_sugar,max_daily_protein, max_daily_potassium]

feature_selected = ["Kalori_kkal", "Lemak_g", "Lemak Jenuh_g", "Kolesterol_mg", "Sodium_mg", "Karbohidrat_g", "Gula_g", "Protein_g", "Kalium_mg"]

def convert_to_minutes(time_str):
    try:
        # Pisahkan angka dan satuan
        value, unit = time_str.split()
        value = int(value)
        if unit == 'menit':
            return value
        elif unit == 'jam':
            return value * 60
    except ValueError:
        return 0
    
def scaling(dataframe):
    scaler=StandardScaler()
    prep_data=scaler.fit_transform(dataframe[feature_selected].to_numpy())
    return prep_data,scaler

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh,scaler,params):
    transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
    pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
    return pipeline

def extract_data(dataframe,ingredient_filter, prep_time_limit, max_nutritional_values):
    extracted_data=dataframe.copy()
    numeric_columns = extracted_data.columns[7:]
    for col in numeric_columns:
        extracted_data[col] = extracted_data[col].str.replace(r'[^\d,.]+', '', regex=True).str.replace(',', '.', regex=False).astype(float).round(1)
    prep_time = extracted_data['Prep Time'].apply(convert_to_minutes)
    cook_time = extracted_data['Cook Time'].apply(convert_to_minutes)

    extracted_data['total_prep_food'] = prep_time + cook_time
    
    for column,maximum in zip(feature_selected,max_nutritional_values):
        extracted_data_max=extracted_data[extracted_data[column]<maximum]
    if ingredient_filter!=None:
        extracted_data_max = extracted_data_max[~extracted_data_max['Ingredients'].str.contains('|'.join(ingredient_filter), case=False, regex=True)]
    if prep_time_limit!=None:
        extracted_data_max = extracted_data_max.loc[extracted_data_max['total_prep_food'] <= prep_time_limit]

    return extracted_data_max

def extract_ingredient_filtered_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    regex_string=''.join(map(lambda x:f'(?=.*{x})',ingredients))
    extracted_data=extracted_data[extracted_data['Ingredients'].str.contains(regex_string,regex=True,flags=re.IGNORECASE)]
    return extracted_data

def apply_pipeline(pipeline,_input,extracted_data):
    _input=np.array(_input).reshape(1,-1)
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def recommand(dataframe,_input,ingredient_filter=None, prep_time_limit=None, params={'n_neighbors':10,'return_distance':False}):
    extracted_data=extract_data(dataframe,ingredient_filter, prep_time_limit ,max_nutritional_values)
    if len(extracted_data) <= 11:
        return "Error"
    else:
        prep_data,scaler=scaling(extracted_data)
        neigh=nn_predictor(prep_data)
        pipeline=build_pipeline(neigh,scaler,params)
        return apply_pipeline(pipeline,_input,extracted_data)

def extract_quoted_strings(s):
    # Find all the strings inside double quotes
    strings = re.findall(r'"([^"]*)"', s)
    # Join the strings with 'and'
    return strings

def output_recommended_recipes(dataframe):
    if dataframe is not None:
        output=dataframe.copy()
        output=output.to_dict("records")
        for recipe in output:
            recipe['Ingredients']=extract_quoted_strings(recipe['Ingredients'])
            recipe['RecipeInstructions']=extract_quoted_strings(recipe['RecipeInstructions'])
    else:
        output=None
    return output