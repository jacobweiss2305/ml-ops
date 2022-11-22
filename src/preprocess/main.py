import pandas as pd
from utils import preprocess_companies, preprocess_shuttles, create_model_input_table

companies = pd.read_csv('companies.csv', nrows = 100)
shuttles = pd.read_csv('shuttles.csv', nrows = 100)
reviews = pd.read_csv('reviews.csv', nrows = 100)

preprocessed_companies = preprocess_companies(companies)
print("Preprocessed companies...")
preprocessed_shuttles = preprocess_shuttles(shuttles)
print("Preprocessed shuttles...")
model_input_table = create_model_input_table(preprocessed_shuttles, preprocessed_companies, reviews)
model_input_table.to_csv('model_input_table.csv', index = False)
print("All done!")
