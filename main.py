import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# 1. 페이지 제목 및 기본 레이아웃 설정
st.set_page_config(
    page_title="어제 박스오피스 순위", page_icon="🎬", layout="wide"
)


# 2. API 데이터 가져오기 함수 (1시간 캐싱 적용)
# @st.cache_data(ttl=3600)를 사용해 동일한 조건 요청 시 1시간(3600초) 동안 결과를 재사용합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key: str, target_date: str):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
    return response.json()


# 3. 한국 시간(KST) 기준 '어제' 날짜 자동 계산
# 배포 서버가 해외 시계 기준이어도 한국 표준시(Asia/Seoul)를 기준으로 계산합니다.
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.datetime.now(kst)
yesterday_kst = now_kst - datetime.timedelta(days=1)

# API 요청용 날짜 형식 (YYYYMMDD)
target_dt = yesterday_kst.strftime("%Y%m%d")
# 화면 출력용 날짜 형식 (YYYY년 MM월 DD일)
display_dt = yesterday_kst.strftime("%Y년 %m월 %d일")

# 화면 상단 제목 표시
st.title("🎬 어제 일별 박스오피스")
st.caption(f"기준 날짜: {display_dt} (한국 시간 기준)")


# 4. secrets에서 API 키 불러오기
if "KOBIS_KEY" not in st.secrets or not st.secrets["KOBIS_KEY"]:
    st.error("⚠️ API 키가 설정되지 않았습니다.")
    st.markdown(
        """
    **확인해야 할 사항:**
    1. Streamlit Cloud 앱 관리 페이지의 **Secrets** 메뉴로 이동하세요.
    2. 아래와 같이 `KOBIS_KEY` 이름으로 발급받은 인증키를 추가해 주세요.
    ```toml
    KOBIS_KEY = "여기에_발급받은_키_입력"
    ```
    """
    )
else:
    api_key = st.secrets["KOBIS_KEY"]

    try:
        # API 요청 수행
        data = fetch_box_office_data(api_key, target_dt)

        # case 1: 인증키 오류 또는 KOBIS 오류 상자(faultInfo) 반환 시
        if "faultInfo" in data:
            fault = data["faultInfo"]
            st.error("⚠️ API 서비스 오류가 발생했습니다.")
            st.write(f"**오류 메시지:** {fault.get('message', '알 수 없는 오류')}")
            st.markdown(
                """
            **확인해야 할 사항:**
            - Secrets에 입력한 `KOBIS_KEY` 값에 오타가 없는지 확인해 보세요.
            - 영화진흥위원회 오픈API 마이페이지에서 키의 승인 상태 및 사용량을 점검해 보세요.
            """
            )

        # case 2: 응답 데이터 구조가 올바르지 않은 경우
        elif (
            "boxOfficeResult" not in data
            or "dailyBoxOfficeList" not in data["boxOfficeResult"]
        ):
            st.error("⚠️ 박스오피스 데이터를 불러올 수 없습니다.")
            st.markdown(
                """
            **확인해야 할 사항:**
            - 영화진흥위원회 API 서비스의 일시적인 장애일 수 있습니다. 잠시 후 다시 시도해 보세요.
            """
            )

        else:
            daily_list = data["boxOfficeResult"]["dailyBoxOfficeList"]

            # case 3: 영화 목록 데이터가 비어 있는 경우
            if not daily_list:
                st.warning("⚠️ 해당 날짜의 박스오피스 집계 데이터가 없습니다.")
                st.markdown(
                    """
                **확인해야 할 사항:**
                - 아직 어제 일자의 박스오피스 집계가 마무리되지 않았을 수 있습니다.
                - 영화진흥위원회 공식 웹사이트에서 해당 날짜 조회가 가능한지 확인해 보세요.
                """
                )

            # 정상 데이터 처리
            else:
                # 판다스 데이터프레임(표 형태)으로 변환
                df = pd.DataFrame(daily_list)

                # 문자열로 들어온 숫자 컬럼들을 수치형 데이터로 변환 (정렬 및 그래프 계산용)
                numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
                for col in numeric_cols:
                    df[col] = (
                        pd.to_numeric(df[col], errors="coerce")
                        .fillna(0)
                        .astype(int)
                    )

                # 순위 기준 오름차순 정렬
                df = df.sort_values("rank").reset_index(drop=True)

                # --- [1] 1위 영화 지표 카드 3장 ---
                st.subheader("🏆 어제 1위 영화")
                top_1 = df.iloc[0]

                col1, col2, col3 = st.columns(3)
                col1.metric("영화명", str(top_1["movieNm"]))
                col2.metric("어제 관객수", f"{top_1['audiCnt']:,} 명")
                col3.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")

                st.divider()

                # --- [2] 관객수 상위 5편 막대그래프 ---
                st.subheader("📊 관객수 TOP 5")
                top_5_df = df.head(5)[["movieNm", "audiCnt"]].copy()
                top_5_df.columns = ["영화명", "관객수"]
                top_5_df = top_5_df.set_index("영화명")
                st.bar_chart(top_5_df)

                st.divider()

                # --- [3] 전체 박스오피스 순위 표 ---
                st.subheader("📋 전체 순위 목록")

                # 필요한 칼럼만 선택하고 컬럼명을 한글로 변경
                table_df = df[
                    [
                        "rank",
                        "movieNm",
                        "openDt",
                        "audiCnt",
                        "audiAcc",
                        "scrnCnt",
                    ]
                ].copy()
                table_df.columns = [
                    "순위",
                    "영화명",
                    "개봉일",
                    "관객수",
                    "누적관객",
                    "스크린수",
                ]

                # 표 출력 (숫자 세 자리마다 천 단위 쉼표 표기)
                st.dataframe(
                    table_df.style.format(
                        {
                            "관객수": "{:,}",
                            "누적관객": "{:,}",
                            "스크린수": "{:,}",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

    # HTTP 통신 예외 처리
    except requests.exceptions.RequestException as e:
        st.error("⚠️ 네트워크 통신 중 오류가 발생했습니다.")
        st.caption(f"상세 에러 내용: {e}")
        st.markdown(
            """
        **확인해야 할 사항:**
        - Streamlit Cloud의 외부 인터넷 연결 상태를 확인해 보세요.
        - KOBIS API 서버가 정상적으로 응답하는지 점검해 보세요.
        """
        )
    # 기타 예외 처리
    except Exception as e:
        st.error("⚠️ 데이터를 처리하는 도중 예상치 못한 오류가 발생했습니다.")
        st.caption(f"상세 에러 내용: {e}")
        st.markdown(
            """
        **확인해야 할 사항:**
        - 입력 데이터의 포맷 변환 과정에 문제가 발생했을 수 있습니다.
        """
        )
