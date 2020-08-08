import streamlit as st
import streamlit.components.v1 as components
import numpy as n
import codecs
from glob import glob
import os

root_path = os.path.dirname(os.path.abspath(__file__))

def main():
    st.sidebar.header("Main")
    query_summary = get_audio_summary()
    option = st.sidebar.radio("Go to", ("See Result", "See Statistic"))
    if option == "See Result":
        create_select_audio_sidebar(query_summary)
    else:
        create_statistic_sidebar()
    create_footer_sidebar()

def create_select_audio_sidebar(query_summary):
    st.sidebar.subheader("Select audio")
    selected_audio = st.sidebar.selectbox('Search an audio', query_summary.get('names'), 0)
    display_matched_result(selected_audio)

def create_statistic_sidebar():
    st.sidebar.subheader("Statistic")

    if st.sidebar.button('Run'):
        render_statistic()

def create_footer_sidebar():
    st.sidebar.header("Authors")
    st.sidebar.info("""
- Vu Do \n
- Hai Ngo \n
DeepHub team ♥️
    """)

def get_audio_summary():
    asset_names = [os.path.basename(p) for p in list(glob(root_path + "/assets/*"))]
    return {
        "names": asset_names
    }


def render_statistic():
    # TODO
    a = st.markdown("# Statistic")


def display_matched_result(audio_container_name, has_pex_result=False):
    st.title(f"Result for {audio_container_name}")

    if has_pex_result:
        st.header('PEX Result:')
        components.iframe("http://localhost:8601/index_origin", height=300)
    
    st.header('DeepHub Result:')
    query_audio_name = os.path.basename(list(glob(root_path + f"/assets/{audio_container_name}/query/*.mp3"))[0])
    components.iframe(f"http://localhost:8601/query_predict?query_audio_container_name={audio_container_name}&query_audio_name={query_audio_name}", height=250)

    asset_audio_container_paths = glob(root_path + f"/assets/{audio_container_name}/assets/*")
    st.header(f'Asset Segments ({len(asset_audio_container_paths)}):')
    for asset_audio_container_path in asset_audio_container_paths:
        asset_audio_name = os.path.basename(asset_audio_container_path)
        components.iframe(f"http://localhost:8601/asset_predict?query_audio_container_name={audio_container_name}&asset_audio_name={asset_audio_name}", height=250)


if __name__ == "__main__":
    main()