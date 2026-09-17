import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# [안전장치 1] 네 번째 그래프 데이터(df_daily)가 아직 메모리에 없다면 원본(df)에서 직접 생성합니다.
if 'df_daily' not in locals() and 'df_daily' not in globals():
  try:
    # 원본 데이터프레임 이름이 'df'이고, 날짜/관객수 컬럼이 있다고 가정합니다.
    # 본인의 실제 원본 데이터프레임 변수명이나 컬럼명(예: '상영일자', '관객수')에 맞게 수정하세요.
    df_daily = df.groupby('기준일자')['관객수'].sum()
  except Exception as e:
    st.error(
        "네 번째 그래프의 데이터(df_daily)를 찾을 수 없습니다. 원본 데이터명이나"
        " 컬럼명을 확인해 주세요."
    )
    st.stop()

# [안전장치 2] df_daily가 Series 형태라면 DataFrame으로 변환
if isinstance(df_daily, pd.Series):
  df_daily = df_daily.reset_index()

# [안전장치 3] '기준일자'가 컬럼에 없다면 인덱스 리셋
if '기준일자' not in df_daily.columns:
  df_daily = df_daily.reset_index()

# 1. 기준일자를 datetime 형식으로 변환 후 연-월(YYYY-MM) 단위 추출
df_daily['기준일자'] = pd.to_datetime(df_daily['기준일자'])
df_daily['연월'] = df_daily['기준일자'].dt.to_period('M')

# 2. 관객수 관련 컬럼 자동 탐지
target_col = None
for col in ['전체관객수', '관객수', '합계']:
  if col in df_daily.columns:
    target_col = col
    break
if target_col is None:
  numeric_cols = df_daily.select_dtypes(include='number').columns
  target_col = numeric_cols[0] if len(numeric_cols) > 0 else df_daily.columns[-1]

# 3. 월별로 관객수 합산
df_monthly = df_daily.groupby('연월')[target_col].sum().reset_index()
df_monthly['연월'] = df_monthly['연월'].astype(str)

# -------------------------------------------------------------
# 4. 다섯 번째 그래프 시각화 (Matplotlib)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(
    df_monthly['연월'],
    df_monthly[target_col],
    color='skyblue',
    edgecolor='black',
)

ax.set_title(
    '다섯 번째 그래프: 월별 전체 관객수 합계', fontsize=14, fontweight='bold'
)
ax.set_xlabel('월 (연-월)', fontsize=12)
ax.set_ylabel('전체 관객수', fontsize=12)
plt.xticks(rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Streamlit 환경에서 그래프 출력
st.pyplot(fig)

# -------------------------------------------------------------
# 5. 그래프 아래에 '이 그래프로 알 수 있는 것' 추가
# -------------------------------------------------------------
st.markdown('### 💡 이 그래프로 알 수 있는 것')
st.markdown(
    """
* **계절별 및 월별 관객 수요 집중 구간 파악:** 특정 월(성수기 시즌인 방학 기간이나 연말 등)에 관객수가 집중되는 패턴을 확인할 수 있습니다.
* **거시적 트렌드 및 증감 추세:** 월 단위의 관객 수 흐름을 비교하여 전년 대비 성장세나 하락세를 한눈에 파악할 수 있습니다.
* **외부 요인 분석의 기준점 제공:** 관객수가 급감하거나 급증한 특정 월의 배경(대작 영화 개봉 여부, 사회적 이슈 등)을 심층적으로 분석하는 출발점이 됩니다.
"""
)
