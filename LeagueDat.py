import pandas as pd
import streamlit as st

# Load the dataset
history = pd.read_csv("C:\\Users\\franc\\OneDrive\\Hawks25\\NECBLHISTORY_combined.csv")

# Filter for 2024 and valid pitch types
history_2024 = history[(history["Year"] == 2024) & (history["AutoPitchType"].notna())]

# Define groups for tab structure
groups = {
    "All Pitchers": history_2024,
    "Right-Handed Pitchers": history_2024[history_2024["PitcherThrows"] == "Right"],
    "Left-Handed Pitchers": history_2024[history_2024["PitcherThrows"] == "Left"],
    "RHP vs RHB": history_2024[(history_2024["PitcherThrows"] == "Right") & (history_2024["BatterSide"] == "Right")],
    "RHP vs LHB": history_2024[(history_2024["PitcherThrows"] == "Right") & (history_2024["BatterSide"] == "Left")],
    "LHP vs RHB": history_2024[(history_2024["PitcherThrows"] == "Left") & (history_2024["BatterSide"] == "Right")],
    "LHP vs LHB": history_2024[(history_2024["PitcherThrows"] == "Left") & (history_2024["BatterSide"] == "Left")],
}

# Streamlit UI
st.title("NECBL 2024 Pitch Type Distribution")

# Create tabs
tabs = st.tabs(list(groups.keys()))

for i, (label, df) in enumerate(groups.items()):
    with tabs[i]:
        st.subheader(f"{label} - Pitch Type % by Count")

        # Count pitches by count and pitch type
        pitch_counts = (
            df.groupby(["Balls", "Strikes", "AutoPitchType"])
            .size()
            .reset_index(name="Count")
        )

        # Pivot to wide format
        pivot = pitch_counts.pivot_table(index=["Balls", "Strikes"], 
                                         columns="AutoPitchType", 
                                         values="Count", 
                                         fill_value=0).reset_index()

        # Calculate percentages
        pitch_cols = pivot.columns.difference(["Balls", "Strikes"])
        pivot[pitch_cols] = pivot[pitch_cols].div(pivot[pitch_cols].sum(axis=1), axis=0) * 100
        pivot = pivot.round(2)

        st.dataframe(pivot)
