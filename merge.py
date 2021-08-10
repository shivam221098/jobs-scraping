import pandas as pd
import os

dir_contents = os.listdir()
full_df = []

for filename in dir_contents:
    if filename.startswith("jobs") and filename.endswith(".csv"):
        df = pd.read_csv(filename)
        full_df.append(df)

full_df = pd.concat(full_df).drop_duplicates(keep="last")
full_df = full_df.sort_values(by=['on_page'], ascending=True)

try:
    os.mkdir("Final Job")
except FileExistsError:
    pass

full_df.to_csv("Final Job/Jobs.csv", index=False)