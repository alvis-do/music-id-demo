import streamlit as st
import streamlit.components.v1 as components
import numpy as n
import codecs
from glob import glob
import os
import json
import logging
import pandas as pd
from mutagen.mp3 import MP3

EXTENSION = 'mp3'

root_path = os.path.dirname(os.path.abspath(__file__))
config = {}

log_file = root_path + '/.logs/default.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)
# logging.info('hello')
def main():
    global config
    # Load config
    with open(root_path + "/config.json", 'r') as f:
        config = json.load(f)

    # Init side bar
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
    selected_audio = st.sidebar.selectbox(
        'Search an audio', 
        [f"{i + 1}. {r}" for i, r in enumerate(query_summary.get('names'))], 
        0)
    selected_audio = selected_audio.split(' ', 1)[-1]
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
[Source Code](https://github.com/kudos-cmd/music-id-demo)
    """)

def get_audio_summary():
    asset_names = [os.path.basename(p) for p in list(glob(root_path + "/assets/*")) if os.path.basename(p) != 'XXXXXXXXXX']
    return {
        "names": asset_names
    }


def render_statistic():
    # TODO
    a = st.markdown("# Statistic")



def display_matched_result(audio_container_name, has_pex_result=False):
    st.title(f"Matched Result For:")
    st.markdown(f'https://www.youtube.com/watch?v={audio_container_name}')

    query_audio_path = list(glob(root_path + f"/assets/{audio_container_name}/query/*.{EXTENSION}"))[0]
    query_audio_name = os.path.basename(query_audio_path)
    asset_audio_container_paths = glob(root_path + f"/assets/{audio_container_name}/assets/*")

    # Show summary
    # dataframe = pd.DataFrame(
    #     np.array(get_result_dataframe(audio_container_name)),
    #     columns=['Video ID', 'Matching Segments On Clip', 'Matching Segment on Asset', 'Asset Filename'])
    # st.table(dataframe)

    # Show detail

    content_server_name = config.get('content_server_name', "")

    if has_pex_result:
        st.header('PEX Result:')
        components.iframe(
            f"{content_server_name}/index_origin", 
            height=300)
        st.header('DeepHub Result:')


    # logging.info(query_audio_name)

    components.iframe(
        f"{content_server_name}/query_predict?query_audio_container_name={audio_container_name}&query_audio_name={query_audio_name}", 
        height=250)

    st.header(f'Asset Segments ({len(asset_audio_container_paths)}):')
    match_duration = 0
    for asset_audio_container_path in asset_audio_container_paths:
        # get duration
        annot_path = os.path.join(asset_audio_container_path, 'annotation.json')
        with open(annot_path, 'r') as annot_f:
            annot_data = json.load(annot_f)
            for data in annot_data:
                start = float(data['start'])
                end = float(data['end'])
                match_duration += end - start

        # show asset audio
        asset_audio_name = os.path.basename(asset_audio_container_path)
        components.iframe(
            f"{content_server_name}/asset_predict?query_audio_container_name={audio_container_name}&asset_audio_name={asset_audio_name}", 
            height=250)

    display_summary(query_audio_path, len(asset_audio_container_paths), match_duration)


def display_summary(q_path, num_match, match_duration):
    audio = MP3(q_path)
    length_in_secs = int(audio.info.length)
    hours, mins, seconds = convert(length_in_secs)

    st.title('Summary:')
    
    dataframe = pd.DataFrame([
        ['Query audio duration', f'{str(hours).zfill(2)}:{str(mins).zfill(2)}:{str(seconds).zfill(2)}', '(hh:mm:ss)'],
        ['Number of matches', num_match, '(match)'],
        ['Rate (match duration/query duration)', f'{match_duration * 100/length_in_secs:.2f}', '(%)']], 
        columns=['Metric', 'Value', 'Unit'])
    st.table(dataframe)

    del audio

def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

if __name__ == "__main__":
    main()