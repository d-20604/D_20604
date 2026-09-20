import pandas as pd
import plotly.express as px
import streamlit as st

# 1) 데이터를 먼저 불러와서 df에 할당해야 합니다!
df = pd.read_csv("your_data.csv")  # 파일 경로에 맞게 수정

# 2) 그 다음에 그래프 코드가 와야 합니다.
fig = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movie_name",
)
st.plotly_chart(fig)
