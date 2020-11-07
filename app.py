import streamlit as st
import streamlit.components.v1 as components
import numpy as n
import codecs
from glob import glob
import os
import sys
import json
import logging
import pandas as pd
from mutagen.mp3 import MP3
import youtube_dl
import uuid
import subprocess
from pathlib import Path
import shutil
import traceback

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'audfprint'))

from audfprint.audfprint import get_args_default, setup_analyzer, setup_matcher, setup_reporter
from audfprint import audfprint_analyze
from audfprint import audfprint_match, hash_table
from tools.adfprint_output import get_result_from_output_lines

EXTENSION = 'mp3'

root_path = os.path.dirname(os.path.abspath(__file__))
config = {}

log_file = root_path + '/.logs/default.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO)
TMP_DIR = Path(root_path) / '.tmp'
if not TMP_DIR.exists():
    TMP_DIR.mkdir(exist_ok=True)
# logging.info('hello')

def main():
    global config
    # Load config
    with open(root_path + "/config.json", 'r') as f:
        config = json.load(f)

    # Init side bar
    st.sidebar.header("Main")
    query_summary = get_audio_summary()
    option = st.sidebar.radio("Go to", ("Live Demo", "See Result", "See Statistic"))
    if option == 'Live Demo':
        create_live_demo()
    elif option == "See Result":
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

-----------
Version 0.2
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


def create_live_demo():
    st.title('Live Demo')

    ## STEP 1
    st.write('**Step 1: Setup Query Audio**')
    st.set_option('deprecation.showfileUploaderEncoding', False)

    option = st.radio('Select options:', ('Input a Youtube video link', 'Input a video file'))

    query_file_name = None
    step1_valid = False
    if option == 'Input a Youtube video link':
        yt_link = st.text_input('Paste a youtube link into below text box:')

        if yt_link:
            st.video(yt_link)

            def step_1():
                base_ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        },
                        {'key': 'FFmpegMetadata'},
                    ],
                    'outtmpl': str(TMP_DIR / 'live-%(id)s.%(ext)s')
                }
                with youtube_dl.YoutubeDL(base_ydl_opts) as ydl:
                    ydl.download([yt_link])
                    # info = ydl.extract_info(str(yt_link), download=True)
                    query_file_name = str(TMP_DIR / ('live-' + (yt_link.split('?v=')[1] + ".mp3")))

                return query_file_name

            step1_valid = True
            

    else:
        file_upload = st.file_uploader('Choose a video file from your device (Max size: 200MB, Type: video/mp4)', 'mp4')

        if file_upload is not None:
            video_bytes = file_upload.read()
            st.video(video_bytes)

            def step_1():
                id = 'live-' + uuid.uuid4().__str__()[-11:]
                query_file_name_without_ext = str(TMP_DIR / id)
                query_file_name = query_file_name_without_ext + '.mp4'
                with open(query_file_name, 'wb') as f:
                    f.write(video_bytes)
                
                subprocess.run(f"ffmpeg -i {query_file_name} -ac 2 -f mp3 {query_file_name_without_ext + '.mp3'}", shell=True)

                os.remove(query_file_name)
                query_file_name = query_file_name_without_ext + '.mp3'

                return query_file_name

            step1_valid = True

    if step1_valid:
        st.success('Success. Go to next step, please!')

    ## STEP 2:
    st.write('**Step 2: Setup Asset Audio**')

    step2_valid = False
    file_upload_2 = st.file_uploader('Choose a asset audio from your device (Max size: 200MB, Type: audio/mp3, audio/wav)', ['mp3', 'wav'])

    asset_file_name = None
    if file_upload_2 is not None:
        audio_bytes = file_upload_2.read()
        st.audio(audio_bytes)

        def step_2():
            id = uuid.uuid4().__str__()[-11:]
            audio_fn = str(TMP_DIR / id)
            with open(audio_fn, 'wb') as f:
                f.write(audio_bytes)
            
            subprocess.run(f"ffmpeg -i {audio_fn} -ac 2 -f wav {audio_fn + '.mp3'}", shell=True)

            os.remove(audio_fn)
            asset_file_name = audio_fn + '.mp3'

            return asset_file_name

        step2_valid = True

    if step2_valid:
        st.success('Success. Go to next step, please!')


    ## STEP 3:
    st.write('**Step 3: Find the matches**')
    if st.button('Run'):
        if not step1_valid or not step2_valid:
            st.error('Please complete Step 1 and Step 2 before!')
        else:
            
            query_file_name = step_1()
            asset_file_name = step_2()

            args = get_args_default()
            args['match'] = True
            args['--density'] = "70"
            args['--fanout'] = "5"
            args['--max-matches'] = '-1'
            args['--min-count'] = '10'
            args['--exact-count'] = True
            args['--find-time-range'] = True


            hash_tab = hash_table.HashTable(
                            hashbits=int(args['--hashbits']),
                            depth=int(args['--bucketsize']),
                            maxtime=(1 << int(args['--maxtimebits'])))
            analyzer = setup_analyzer(args)
            matcher = setup_matcher(args)

            hashes = analyzer.wavfile2hashes(filename=query_file_name)
            asset_hashes = analyzer.wavfile2hashes(filename=asset_file_name)
            hash_tab.store(query_file_name, hashes)
                
            msgs, _ = matcher.file_match_to_msgs(analyzer, hash_tab, asset_file_name, asset_hashes)

            result = get_result_from_output_lines(
                source_files=[asset_file_name],
                output_lines=msgs,
                min_matched_sec=5
            )

            st.write("Result:")
            st.write(result)


            # Save the result to assets follow the asset structure
            mk_asset_structure(
                query_name=query_file_name,
                asset_name=asset_file_name, 
                matched_result=result
            )

            # Show Matched Result Screen
            container_name = Path(query_file_name).stem
            display_matched_result(audio_container_name=container_name)

    if st.button("Clear"):
        shutil.rmtree(str(TMP_DIR), ignore_errors=True)
        live_dirs = glob(str(Path(root_path) / 'assets' / 'live-*'))
        for d in live_dirs:
            shutil.rmtree(d, ignore_errors=True)
        st.success('Remove temporary file completed!')
                

    # st.balloons()


def mk_asset_structure(query_name, asset_name, matched_result):
    container_name = Path(query_name).stem
    container_path = Path(root_path) / 'assets' / container_name
        
    c_query_path = container_path / 'query'
    c_query_path.mkdir(parents=True, exist_ok=True)
    Path(query_name).rename(str(c_query_path / os.path.basename(query_name)))

    annot_assets = matched_result[0].get('assets')
    if len(annot_assets) <= 0:
        return

    asset_container_name = Path(asset_name).stem
    c_asset_path = container_path / 'assets'
    asset_1 = c_asset_path / asset_container_name
    asset_1.mkdir(parents=True, exist_ok=True)
    Path(asset_name).rename(str(asset_1 / os.path.basename(asset_name)))

    # make annotation file
    annot_asset = annot_assets[0]
    query_segments = annot_asset.get('query_segments')
    asset_segments = annot_asset.get('asset_segments')

    annot_query_list = []
    annot_asset_list = []
    for i in range(len(query_segments)):
        annot_query_list.append({
            "start": query_segments[i][0],
            "end": query_segments[i][1],
            "data": {
                "note": f"song name : {asset_name}"
            }
        })
        annot_asset_list.append({
            "start": asset_segments[i][0],
            "end": asset_segments[i][1],
            "data": {
                "note": ""
            }
        })

    with open(str(c_query_path / 'annotation.json'), 'w') as f:
        json.dump(annot_query_list, f)
    with open(str(asset_1 / 'annotation.json'), 'w') as f:
        json.dump(annot_asset_list, f)



def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

if __name__ == "__main__":
    main()