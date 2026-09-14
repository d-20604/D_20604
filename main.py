import streamlit as st
import pandas as pd
import plotly.express as px

# 웹앱 기본 설정 (페이지 제목 및 레이아웃 넓게)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석")

# [1. 데이터 불러오기 및 2. 날짜 전처리]
# @st.cache_data를 사용하여 데이터 불러온 결과를 메모리에 저장(캐싱)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # CSV 파일 읽어오기
    df = pd.read_csv(url)
    
    # 결측치(빈 값)가 포함된 행을 모두 삭제
    df = df.dropna()
    
    # '기준일자' 컬럼을 문자열에서 날짜(datetime) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 전체 데이터를 '기준일자' 오름차순(과거->최근)으로 정렬
    df = df.sort_values("기준일자")
    
    return df

# 데이터 불러오기 함수 호출
df = load_data()

# [3. 영화 선택 기능]
# 영화별 누적관객수의 최대값을 기준으로 내림차순 정렬하여 영화 목록 생성
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 사이드바 메뉴 생성
st.sidebar.header("🔍 영화 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요", movie_order)

# 사용자가 선택한 영화 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]

# [5. 기타 - 구역 나누기]
# 탭(Tab)을 생성하여 세 개의 그래프 구역 분리
tab1, tab2, tab3 = st.tabs(["📈 일별 관객수 추이", "📊 누적 관객수 추이", "🏆 장기 흥행 TOP 5 영화 비교"])

# 첫 번째 구역: 일별 관객수 선그래프
with tab1:
    st.subheader(f"'{selected_movie}' 일별 관객수 변화")
    
    # [4. 선그래프 그리기]
    fig_line = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"{selected_movie} - 일별 관객수 추이 그래프",
        labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
        markers=True  # 데이터 점 표시
    )
    
    # 화면에 Plotly 그래프 출력
    st.plotly_chart(fig_line, use_container_width=True)
    
    # 그래프 하단 설명 문구 자리
    st.caption("💡 이 그래프로 알 수 있는 것: 개봉 일자별 관객수의 흥행 추이와 관객수가 가장 많이 몰린 날을 한눈에 파악할 수 있습니다.")

# 두 번째 구역: 누적 관객수 영역차트
with tab2:
    st.subheader(f"'{selected_movie}' 누적 관객수 변화")
    
    # [영역차트(Area Chart) 그리기]
    fig_area = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"{selected_movie} - 누적 관객수 추이 그래프",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)"}
    )
    
    # 화면에 Plotly 그래프 출력
    st.plotly_chart(fig_area, use_container_width=True)
    
    # 그래프 하단 설명 문구 자리
    st.caption("💡 이 그래프로 알 수 있는 것: 시간이 흐름에 따른 관객수의 전체적인 누적 성장 곡선과 주요 관객 수 돌파 시점을 파악할 수 있습니다.")

# 세 번째 구역: TOP10 20일 이상 등장 영화 중 누적관객수 TOP 5 다중 선그래프
with tab3:
    st.subheader("🏆 20일 이상 차트인 영화 중 누적 관객수 TOP 5 추이 비교")
    
    # 1. 영화별 TOP10 차트인 일수(데이터 등장 횟수) 계산
    movie_counts = df["영화명"].value_counts()
    
    # 2. 20일 이상 등장한 영화만 필터링
    movies_over_20days = movie_counts[movie_counts >= 20].index
    
    # 3. 20일 이상 등장한 영화 중에서 누적 관객수가 가장 높은 상위 5개 영화 선정
    top5_long_run_movies = (
        df[df["영화명"].isin(movies_over_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index
        .tolist()
    )
    
    # 4. 해당 5개 영화 데이터만 추출
    top5_df = df[df["영화명"].isin(top5_long_run_movies)]
    
    # [다중 선그래프 그리기]
    # color 옵션에 '영화명'을 지정하여 영화별 색상 구분 및 범례 자동 생성
    fig_multi = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 차트인한 상위 5개 영화의 기준일자별 누적 관객수 변화 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)", "영화명": "영화 제목"}
    )
    
    # 화면에 Plotly 그래프 출력
    st.plotly_chart(fig_multi, use_container_width=True)
    
    # 그래프 하단 설명 문구 자리
    st.caption("💡 이 그래프로 알 수 있는 것: TOP10 차트에 20일 이상 장기 잔류한 대표 흥행작 5편의 누적 관객수 성장 추이와 상호 성과 비교를 확인할 수 있습니다.")
