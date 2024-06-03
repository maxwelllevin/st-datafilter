import pandas as pd
import seaborn as sns  # pip install seaborn
import streamlit as st

from st_datafilter import filter_dataframe

df = sns.load_dataset("iris")
df["species"] = pd.Categorical(df["species"])

with st.sidebar:
    df = filter_dataframe(df, show_histograms=True)

st.scatter_chart(df, x="petal_width", y="petal_length", color="species")
st.dataframe(df, use_container_width=True)
