import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="Chamber Explorer", page_icon="🔬", layout="wide")

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem;}
        div[data-testid="stMetric"] {
            background: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 14px 18px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(path: str = "machine_chambers.csv") -> pd.DataFrame:
    return pd.read_csv(path)


df = load_data()
machine_names = sorted(df["Machine_Name"].unique())

# Consistent color per chamber type across every chart
chamber_types = sorted(df["Chamber_Type"].unique())
palette = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
color_map = {t: palette[i % len(palette)] for i, t in enumerate(chamber_types)}

# ---------- Header ----------
st.title("🔬 Chamber Explorer")
st.caption("Search for a machine to see its chambers and their types.")

# ---------- Sidebar: search + run ----------
with st.sidebar:
    st.header("Search")
    # selectbox is searchable: typing filters the list like an autocomplete
    selected = st.selectbox(
        "Machine name",
        options=machine_names,
        index=None,
        placeholder="Start typing a machine name...",
    )
    run = st.button("Run", type="primary", use_container_width=True, disabled=selected is None)
    st.divider()
    st.metric("Machines in dataset", len(machine_names))
    st.metric("Total chambers", len(df))

# Remember the last run so results stay visible when the page reruns
if run and selected:
    st.session_state["active_machine"] = selected

active = st.session_state.get("active_machine")

# ---------- Results ----------
if not active:
    st.info("👈 Pick a machine in the sidebar and press **Run** to see its chambers.")
else:
    result = (
        df.loc[df["Machine_Name"] == active, ["Chamber_ID", "Chamber_Type"]]
        .reset_index(drop=True)
    )
    counts = (
        result["Chamber_Type"].value_counts().rename_axis("Chamber_Type")
        .reset_index(name="Count")
    )

    st.subheader(f"Machine: {active}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total chambers", len(result))
    c2.metric("Distinct chamber types", result["Chamber_Type"].nunique())
    c3.metric("Most common type", counts.iloc[0]["Chamber_Type"])

    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.markdown("##### Chamber details")
        st.dataframe(result, use_container_width=True, hide_index=True, height=min(38 * (len(result) + 1), 420))
        st.download_button(
            "⬇️ Download as CSV",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name=f"{active}_chambers.csv",
            mime="text/csv",
        )

    with right:
        st.markdown("##### Chamber type breakdown")
        fig = px.bar(
            counts,
            x="Chamber_Type",
            y="Count",
            color="Chamber_Type",
            color_discrete_map=color_map,
            text="Count",
        )
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Chambers",
                          margin=dict(t=10, b=10), yaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)
