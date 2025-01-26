import streamlit as st

hide_anchor_css = """
<style>
.st-emotion-cache-gi0tri svg {
    display: none;
}
</style>
"""

st.set_page_config(
    page_title="BTPs",
    page_icon=":money_with_wings:",
    layout="wide"
)

st.markdown(hide_anchor_css, unsafe_allow_html=True)

st.title("BTPs")
