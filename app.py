import streamlit as st
import duckdb
import pandas as pd
import altair as alt

# ページの設定
st.set_page_config(
    page_title="JEPX エリアプライス価格",
    layout="wide"
)

# DuckDBへの接続
@st.cache_resource
def get_duckdb_connection():
    conn = duckdb.connect("jepx_dbt/dev.duckdb", read_only=True)
    return conn

try:
    conn = get_duckdb_connection()
except Exception as e:
    st.error(f"データベースへの接続に失敗しました: {e}")
    st.stop()

# 1. エリア一覧の取得
@st.cache_data
def load_areas(_conn):
    query = "SELECT DISTINCT エリア FROM marts.spot_summary_long ORDER BY エリア"
    return _conn.execute(query).df()["エリア"].tolist()

areas = load_areas(conn)

if not areas:
    st.warning("エリアデータが見つかりませんでした。")
    st.stop()

# 2. 利用可能な年度一覧の取得
@st.cache_data
def load_years(_conn):
    query = "SELECT DISTINCT 年度 FROM marts.spot_summary_long ORDER BY 年度 DESC"
    return _conn.execute(query).df()["年度"].tolist()

years = load_years(conn)

# --- 💡 サイドバーにフィルターを集約 ---
st.sidebar.header("🔍 絞り込み条件")

default_area = "東京" if "東京" in areas else areas[0]
selected_area = st.sidebar.selectbox(
    "比較するエリアを選択", 
    areas, 
    index=areas.index(default_area) if default_area in areas else 0
)

# デフォルトで全年度（または最新の数年）を選択状態にする
default_selected_years = years[:3] if len(years) >= 3 else years
selected_years = st.sidebar.multiselect(
    "比較する年度を選択（複数選択可）",
    options=years,
    default=default_selected_years
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 ヒント: グラフはマウスで拡大・縮小したり、ツールチップで詳細を確認できます。")

if not selected_years:
    st.warning("サイドバーから比較する年度を1つ以上選択してください。")
    st.stop()

# --- メイン画面：タイトル ---
st.title("⚡ JEPX 月別平均エリアプライス")
st.markdown("marts層のテーブル (`spot_summary_long`) を使用して、年度ごとの月別平均価格を比較します。")
st.markdown("") # 空間の調整

# --- 3. データの集計・取得（選択された年度で絞り込み） ---
@st.cache_data
def load_aggregated_data(_conn, area_name, target_years):
    # IN句用のプレースホルダーを作成（例: (?, ?, ?)）
    placeholders = ", ".join(["?"] * len(target_years))
    query = f"""
        SELECT 
            年度,
            月,
            AVG(CAST(エリアプライス AS DOUBLE)) AS 平均価格
        FROM marts.spot_summary_long
        WHERE エリア = ? AND 年度 IN ({placeholders})
        GROUP BY 年度, 月
        ORDER BY 月, 年度
    """
    # パラメータとして [エリア名, 年度1, 年度2, ...] を渡す
    params = [area_name] + target_years
    return _conn.execute(query, params).df()

df = load_aggregated_data(conn, selected_area, selected_years)

# --- 4. メイン画面：可視化 ---
st.subheader(f"📈 【{selected_area}エリア】月別平均エリアプライス推移（年度比較）")

if df.empty:
    st.warning("指定された条件に一致するデータがありません。")
else:
    # 月をX軸、平均価格をY軸、年度を色(Color)にして折れ線グラフを描画
    df["月_str"] = df["月"].astype(str)
    
    # Altairを使った折れ線グラフ
    chart = alt.Chart(df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X(
            "月_str:N", 
            title="月", 
            sort=["4", "5", "6", "7", "8", "9", "10", "11", "12", "1", "2", "3"],
            axis=alt.Axis(labelAngle=0)  # ラベルを水平（0度）にする
        ),
        y=alt.Y("平均価格:Q", title="平均エリアプライス (円/kWh)"),
        color=alt.Color("年度:N", title="年度", sort=selected_years),
        tooltip=["年度", "月", alt.Tooltip("平均価格:Q", format=".2f")]
    ).properties(
        width="container",
        height=450
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # --- 5. データテーブルの表示 ---
    with st.expander("📊 集計データ詳細を確認する（ピボット表示）"):
        pivot_df = df.pivot(index="月_str", columns="年度", values="平均価格")
        st.dataframe(pivot_df.style.format("{:.2f} 円/kWh"), use_container_width=True)