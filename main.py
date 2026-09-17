import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st  # Streamlit 환경 기준 (필요시 사용)

# -------------------------------------------------------------
# [참고] 네 번째 그래프에서 만들어진 df_daily 데이터가 있다고 가정합니다.
# 만약 '기준일자'가 인덱스로 잡혀있거나 컬럼으로 내려와 있는 상황을 모두 고려한 안전한 코드입니다.
# -------------------------------------------------------------

# 1. 인덱스에 '기준일자'가 숨어있을 경우를 대비해 reset_index 실행
if '기준일자' not in df_daily.columns:
  df_daily = df_daily.reset_index()

# 2. 기준일자를 datetime 형식으로 변환 후 연-월(YYYY-MM) 단위 추출
df_daily['기준일자'] = pd.to_datetime(df_daily['기준일자'])
df_daily['연월'] = df_daily['기준일자'].dt.to_period('M')

# 3. 월별로 관객수 합산 (실제 컬럼명 '전체관객수' 또는 '관객수'에 맞게 수정 필요)
# 데이터프레임의 관객수 컬럼명에 맞춰 대괄호 안을 수정해 주세요 (예: '관객수')
target_col = (
    '전체관객수' if '전체관객수' in df_daily.columns else '관객수'
)
df_monthly = (
    df_daily.groupby('연월')[target_col].sum().reset_index()
)
df_monthly['연월'] = df_monthly['연월'].astype(
    str
)  # 그래프 X축 출력을 위해 문자열 변환

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

# Streamlit 환경에서 그래프 출력할 때 (일반 스크립트라면 plt.show() 사용)
st.pyplot(fig)
# plt.show() # 스크립트 직접 실행인 경우 이 줄 사용

# -------------------------------------------------------------
# 5. 그래프 아래에 '이 그래프로 알 수 있는 것' 추가 (Streamlit 기준 텍스트)
# -------------------------------------------------------------
st.markdown('### 💡 이 그래프로 알 수 있는 것')
st.markdown(
    """
* **계절별 및 월별 관객 수요 집중 구간 파악:** 특정 월(성수기 시즌인 방학 기간이나 연말 등)에 관객수가 집중되는 패턴을 확인할 수 있습니다.
* **거시적 트렌드 및 증감 추세:** 월 단위의 관객 수 흐름을 비교하여 전년 대비 성장세나 하락세를 한눈에 파악할 수 있습니다.
* **외부 요인 분석의 기준점 제공:** 관객수가 급감하거나 급증한 특정 월의 배경(대작 영화 개봉 여부, 사회적 이슈 등)을 심층적으로 분석하는 출발점이 됩니다.
"""
)
