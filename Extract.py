import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

# Mapping of team URLs to team abbreviations
team_urls = {
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=89490&seasonid=33860&view=batting&bset=0&orderby=avg": "BRI_B",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6402&seasonid=33860&view=batting&bset=0&orderby=avg": "DAN_WES",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6401&seasonid=33860&view=batting&bset=0&orderby=avg": "KEE_SWA",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=142675&seasonid=33860&view=batting&bset=0&orderby=avg": "MAR_VIN",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=11912&seasonid=33860&view=batting&bset=0&orderby=avg": "MYS_SCH",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6458&seasonid=33860&view=batting&bset=0&orderby=avg": "NEW_GUL",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6404&seasonid=33860&view=batting&bset=0&orderby=avg": "NOR_ADA",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=154432&seasonid=33860&view=batting&bset=0&orderby=avg": "NSH_N",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=51489&seasonid=33860&view=batting&bset=0&orderby=avg": "OCE_STA6",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6459&seasonid=33860&view=batting&bset=0&orderby=avg": "SAN_MAI",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=104040&seasonid=33860&view=batting&bset=0&orderby=avg": "UPP_VAL",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6403&seasonid=33860&view=batting&bset=0&orderby=avg": "VAL_BLU",
    "http://necbl.wttbaseball.pointstreak.com/team_stats.html?teamid=6405&seasonid=33860&view=batting&bset=0&orderby=avg": "VER_MOU"
}

# Collect and tag each table
all_dataframes = []

for url, team_abbr in team_urls.items():
    print(f"Scraping: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if table:
        df = pd.read_html(io.StringIO(str(table)))[0]
        df['Team'] = team_abbr  # Add team column
        all_dataframes.append(df)
    else:
        print(f"Warning: No table found at {url}")

# Combine and export
final_df = pd.concat(all_dataframes, ignore_index=True)
# Clean column names (in case they vary)
final_df.columns = final_df.columns.str.strip()

# Convert necessary columns to numeric
cols_to_numeric = ['AB', 'H', '2B', '3B', 'HR', 'BB', 'HBP', 'SF', 'SH']
for col in cols_to_numeric:
    final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0)

# Calculate derived stats
final_df['1B'] = final_df['H'] - final_df['2B'] - final_df['3B'] - final_df['HR']
final_df['PA'] = final_df['AB'] + final_df['BB'] + final_df['HBP'] + final_df['SF'] + final_df['SH']
final_df['OBP'] = (final_df['H'] + final_df['BB'] + final_df['HBP']) / final_df['PA']
final_df['SLG'] = (final_df['1B'] + 2*final_df['2B'] + 3*final_df['3B'] + 4*final_df['HR']) / final_df['AB']
final_df['OPS'] = final_df['OBP'] + final_df['SLG']

# Round new columns for display
final_df[['OBP', 'SLG', 'OPS']] = final_df[['OBP', 'SLG', 'OPS']].round(3)

# Save the enriched data
final_df.to_csv("C:/Users/franc/OneDrive/Hawks25/necbl_combined_batting_stats.csv", index=False)

print("✅ Stats enhanced with OBP, SLG, OPS, and PA.")
print(final_df[['Player', 'Team', 'PA', 'OBP', 'SLG', 'OPS']].head())

final_df.to_csv("C:/Users/franc/OneDrive/Hawks25/necbl_combined_batting_stats.csv", index=False)

print("Saved combined batting stats to CSV.")
print(final_df.head())


