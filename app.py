import pandas as pd
import plotly.express as px
import streamlit as st

# page layout
st.set_page_config(
    page_title="world cup matches dashboard", layout="wide"
)
st.title("word cup matches dashboard")
st.markdown("word cup dataset to explore fifa worldcup matches data")

# load and clean data set
@st.cache_data
def load_data():
    df = pd.read_csv("WorldCupMatches.csv")
    df = df.drop_duplicates(subset=["MatchID"])
    df = df.dropna(subset=["Home Team Name", "Away Team Name"])
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    df["Total Goals"] = df["Home Team Goals"] + df["Away Team Goals"]
    return df

df = load_data()

# Side bar filters
st.sidebar.header("Filter options")
years = sorted(df["Year"].unique())
year_range = st.sidebar.slider("Year range", min(years), max(years), (min(years), max(years)))

stages = sorted(df["Stage"].unique())
selected_stages = st.sidebar.multiselect("Stage", stages, default=stages)

teams = sorted(set(df["Home Team Name"]) | set(df["Away Team Name"]))
selected_team = st.sidebar.selectbox("Team (optional)", ["All"] + teams)

# Apply filters
filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
filtered = filtered[filtered["Stage"].isin(selected_stages)]

if selected_team != "All":
    filtered = filtered[
        (filtered["Home Team Name"] == selected_team) |
        (filtered["Away Team Name"] == selected_team)
    ]

# Header
st.title("fifa word cup matches dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", len(filtered))
col2.metric("Total Goals", int(filtered["Total Goals"].sum()))
col3.metric("Avg Goals/Match", round(filtered["Total Goals"].mean(), 2))
col4.metric("Total Attendance", f"{int(filtered['Attendance'].sum()):,}")

# Charts
st.subheader("Goals per Year")
goals_year = filtered.groupby("Year")["Total Goals"].sum().reset_index()
fig1 = px.bar(goals_year, x="Year", y="Total Goals", color="Total Goals", color_continuous_scale="viridis")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Top 10 Teams by Wins")
home_wins = filtered[filtered["Home Team Goals"] > filtered["Away Team Goals"]]["Home Team Name"]
away_wins = filtered[filtered["Away Team Goals"] > filtered["Home Team Goals"]]["Away Team Name"]
wins = pd.concat([home_wins, away_wins]).value_counts().head(10).reset_index()
wins.columns = ["Team", "Wins"]
fig2 = px.bar(wins, x="Wins", y="Team", orientation="h", color="Wins", color_continuous_scale="Blues")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Attendance Over Time")
fig3 = px.scatter(filtered, x="Year", y="Attendance", color="Stage", size="Total Goals", hover_data=["Home Team Name", "Away Team Name"])
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Match List")
st.dataframe(
    filtered[["Year", "Stage", "Home Team Name", "Home Team Goals", "Away Team Goals", "Away Team Name", "Attendance"]]
    .sort_values("Year"),
    use_container_width=True
)