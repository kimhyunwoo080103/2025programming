import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="군 장병 개인 정보 현황", page_icon="🪖", layout="wide")


def decompose_hangul(char: str) -> tuple[int, int, int]:
    """한글 문자를 초성, 중성, 종성으로 분해"""
    if not ('가' <= char <= '힣'):
        # 한글이 아니면 유니코드 값으로 정렬
        return (999, ord(char), 0)
    
    code = ord(char) - ord('가')
    # 초성: 19개 (ㄱ, ㄲ, ㄴ, ㄷ, ㄸ, ㄹ, ㅁ, ㅂ, ㅃ, ㅅ, ㅆ, ㅇ, ㅈ, ㅉ, ㅊ, ㅋ, ㅌ, ㅍ, ㅎ)
    cho = code // (21 * 28)
    # 중성: 21개 (ㅏ, ㅐ, ㅑ, ㅒ, ㅓ, ㅔ, ㅕ, ㅖ, ㅗ, ㅘ, ㅙ, ㅚ, ㅛ, ㅜ, ㅝ, ㅞ, ㅟ, ㅠ, ㅡ, ㅢ, ㅣ)
    jung = (code // 28) % 21
    # 종성: 28개
    jong = code % 28
    
    return (cho, jung, jong)


def hangul_sort_key(name: str) -> tuple:
    """이름을 한글 정렬 기준으로 변환"""
    result = []
    for char in name:
        result.append(decompose_hangul(char))
    return tuple(result)

SIZE_OPTIONS = ["S", "M", "L", "XL", "XXL", "XXXL"]
ALLERGY_OPTIONS = [
    "유제품: 우유",
    "난류: 달걀",
    "견과류: 땅콩",
    "견과류: 호두",
    "견과류: 밤",
    "곡류: 밀",
    "곡류: 메밀",
    "콩류: 대두(콩)",
    "해산물: 생선(고등어 등)",
    "해산물: 조개",
    "해산물: 갑각류(새우, 게)",
    "육류: 닭고기",
    "과일 및 채소: 복숭아",
    "과일 및 채소: 토마토",
]


def init_session_state():
    if "records" not in st.session_state:
        st.session_state.records = [
            {
                "이름": "김민수",
                "모자 사이즈": "M",
                "옷 사이즈": "L",
                "식품 알레르기": "난류: 달걀, 해산물: 갑각류(새우, 게)",
            },
            {
                "이름": "이영희",
                "모자 사이즈": "S",
                "옷 사이즈": "M",
                "식품 알레르기": "견과류: 땅콩, 견과류: 호두",
            },
            {
                "이름": "박철수",
                "모자 사이즈": "XL",
                "옷 사이즈": "XL",
                "식품 알레르기": "해산물: 생선(고등어 등)",
            },
        ]


def add_record(name: str, hat_size: str, cloth_size: str, allergies: list[str]) -> None:
    if not name:
        st.warning("이름을 입력해주세요.")
        return

    allergy_text = ", ".join(allergies) if allergies else "없음"
    st.session_state.records.append(
        {
            "이름": name,
            "모자 사이즈": hat_size,
            "옷 사이즈": cloth_size,
            "식품 알레르기": allergy_text,
        }
    )
    st.success(f"{name} 정보를 추가했습니다.")


def delete_record(index: int) -> None:
    if 0 <= index < len(st.session_state.records):
        deleted_name = st.session_state.records[index]["이름"]
        st.session_state.records.pop(index)
        st.success(f"{deleted_name} 정보를 삭제했습니다.")
        st.rerun()


def create_charts(records: list[dict]) -> None:
    """원형 그래프 생성"""
    if not records:
        return
    
    # 모자 사이즈별 인원 수
    hat_size_counts = {}
    for record in records:
        size = record["모자 사이즈"]
        hat_size_counts[size] = hat_size_counts.get(size, 0) + 1
    
    # 옷 사이즈별 인원 수
    cloth_size_counts = {}
    for record in records:
        size = record["옷 사이즈"]
        cloth_size_counts[size] = cloth_size_counts.get(size, 0) + 1
    
    # 알레르기별 인원 수
    allergy_counts = {}
    for record in records:
        allergies = record["식품 알레르기"]
        if allergies and allergies != "없음":
            # 알레르기가 여러 개일 수 있으므로 쉼표로 분리
            allergy_list = [a.strip() for a in allergies.split(",")]
            for allergy in allergy_list:
                allergy_counts[allergy] = allergy_counts.get(allergy, 0) + 1
    
    # 그래프 생성
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 모자 사이즈 그래프
        if hat_size_counts:
            hat_df = pd.DataFrame({
                "사이즈": list(hat_size_counts.keys()),
                "인원 수": list(hat_size_counts.values())
            })
            # 사이즈 순서대로 정렬
            size_order = ["S", "M", "L", "XL", "XXL", "XXXL"]
            hat_df["사이즈"] = pd.Categorical(hat_df["사이즈"], categories=size_order, ordered=True)
            hat_df = hat_df.sort_values("사이즈")
            
            fig_hat = px.pie(
                hat_df, 
                values="인원 수",
                names="사이즈",
                title="모자 사이즈별 인원 수",
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_hat.update_traces(textposition='inside', textinfo='percent+label')
            fig_hat.update_layout(height=350)
            st.plotly_chart(fig_hat, use_container_width=True)
        else:
            st.info("모자 사이즈 데이터가 없습니다.")
        
        # 옷 사이즈 그래프
        if cloth_size_counts:
            cloth_df = pd.DataFrame({
                "사이즈": list(cloth_size_counts.keys()),
                "인원 수": list(cloth_size_counts.values())
            })
            # 사이즈 순서대로 정렬
            cloth_df["사이즈"] = pd.Categorical(cloth_df["사이즈"], categories=size_order, ordered=True)
            cloth_df = cloth_df.sort_values("사이즈")
            
            fig_cloth = px.pie(
                cloth_df, 
                values="인원 수",
                names="사이즈",
                title="옷 사이즈별 인원 수",
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig_cloth.update_traces(textposition='inside', textinfo='percent+label')
            fig_cloth.update_layout(height=350)
            st.plotly_chart(fig_cloth, use_container_width=True)
        else:
            st.info("옷 사이즈 데이터가 없습니다.")
    
    with col2:
        # 알레르기 그래프
        if allergy_counts:
            allergy_df = pd.DataFrame({
                "알레르기": list(allergy_counts.keys()),
                "인원 수": list(allergy_counts.values())
            })
            # 인원 수 기준으로 내림차순 정렬
            allergy_df = allergy_df.sort_values("인원 수", ascending=False)
            
            fig_allergy = px.pie(
                allergy_df, 
                values="인원 수",
                names="알레르기",
                title="알레르기별 인원 수",
                color_discrete_sequence=px.colors.sequential.Reds
            )
            fig_allergy.update_traces(textposition='inside', textinfo='percent+label')
            fig_allergy.update_layout(height=700)
            st.plotly_chart(fig_allergy, use_container_width=True)
        else:
            st.info("알레르기 정보가 없습니다.")


def main():
    init_session_state()

    st.title("군 장병 개인별 사이즈 및 알레르기 현황")
    st.markdown(
        "이름과 모자/옷 사이즈, 식품 알레르기를 선택하여 아래 표에 정보를 추가하세요."
    )

    with st.form("personal_info_form", clear_on_submit=True):
        name = st.text_input("이름", placeholder="예: 홍길동")
        col1, col2 = st.columns(2)
        with col1:
            hat_size = st.selectbox("모자 사이즈", SIZE_OPTIONS, index=1)
        with col2:
            cloth_size = st.selectbox("옷 사이즈", SIZE_OPTIONS, index=2)

        allergies = st.multiselect("식품 알레르기", ALLERGY_OPTIONS)
        submitted = st.form_submit_button("정보 추가")

    if submitted:
        add_record(name, hat_size, cloth_size, allergies)

    st.markdown("---")
    st.subheader("등록된 정보 목록")
    
    if not st.session_state.records:
        st.info("등록된 정보가 없습니다.")
    else:
        # 이름 기준으로 한글 정렬 (자음/모음 순서)
        sorted_records = sorted(st.session_state.records, key=lambda x: hangul_sort_key(x["이름"]))
        
        # 각 행에 삭제 버튼 추가
        for idx, record in enumerate(sorted_records):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 3, 1])
                with col1:
                    st.write(f"**{record['이름']}**")
                with col2:
                    st.write(f"모자: {record['모자 사이즈']}")
                with col3:
                    st.write(f"옷: {record['옷 사이즈']}")
                with col4:
                    st.write(f"알레르기: {record['식품 알레르기']}")
                with col5:
                    delete_key = f"delete_{record['이름']}_{idx}"
                    if st.button("🗑️ 삭제", key=delete_key, type="secondary"):
                        # 확인 다이얼로그 표시
                        if st.session_state.get(f"show_confirm_{record['이름']}", False):
                            st.session_state[f"show_confirm_{record['이름']}"] = False
                        else:
                            st.session_state[f"show_confirm_{record['이름']}"] = True
                        st.rerun()
                
                # 확인 다이얼로그 표시
                if st.session_state.get(f"show_confirm_{record['이름']}", False):
                    with st.container():
                        st.warning(f"**{record['이름']}**의 정보를 정말 삭제할까요?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅ 예", key=f"confirm_yes_{record['이름']}_{idx}", type="primary"):
                                # 이름으로 원본 records에서 찾아서 삭제
                                for i, r in enumerate(st.session_state.records):
                                    if r["이름"] == record["이름"]:
                                        delete_record(i)
                                        break
                                if f"show_confirm_{record['이름']}" in st.session_state:
                                    del st.session_state[f"show_confirm_{record['이름']}"]
                        with col_no:
                            if st.button("❌ 아니요", key=f"confirm_no_{record['이름']}_{idx}"):
                                st.session_state[f"show_confirm_{record['이름']}"] = False
                                st.rerun()
                
                st.markdown("---")
        
        # 그래프 표시
        st.markdown("---")
        st.subheader("통계 그래프")
        create_charts(st.session_state.records)


if __name__ == "__main__":
    main()

