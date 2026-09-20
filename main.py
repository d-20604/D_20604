import pandas as pd
import plotly.express as px

# 데이터프레임 변수명은 예시로 df라고 가정합니다.
# df에 'movie_name'(영화명), 'first_scrn'(개봉일 스크린수), 'total_audi'(총 관객), 'genre'(장르) 컬럼이 있다고 가정합니다.

fig = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",  # 장르별로 점 색상 다르게 지정
    hover_name="movie_name",  # 마우스 오버 시 영화명이 표시되도록 설정
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre": "장르",
    },
    title="개봉일 스크린수 vs 총 관객수 산점도",
)

# 레이아웃 및 툴팁 설정 보완
fig.update_traces(marker=dict(size=8, opacity=0.8))
fig.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    legend_title="장르",
)

fig.show()
