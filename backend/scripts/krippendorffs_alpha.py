import pandas as pd
import krippendorff

# Global variable for CSV file path
CSV_FILE_PATH = "D:/PROJECTS/trafficlaw_chatbot/data/interrater_evaluation - likert_results_k=20_run_1.csv"

df = pd.read_csv(CSV_FILE_PATH)

ratings = df[['rater_1', 'rater_2', 'rater_3']].to_numpy().T

print(krippendorff.alpha(reliability_data=ratings, level_of_measurement="ordinal"))