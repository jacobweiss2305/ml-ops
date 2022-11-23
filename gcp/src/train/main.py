import pandas as pd
from utils import split_data, train_model, evaluate_model

data = pd.read_csv("model_input_table.csv")
x_train, x_test, y_train, y_test = split_data(data)
regressor = train_model(x_train, y_train)
evaluate_model(regressor, x_test, y_test)