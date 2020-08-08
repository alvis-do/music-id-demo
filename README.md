# Dependences
- python3.6
- streamlit
- flask

# How to run
1. Create virtual environment and install requirement.txt:

2. Run the content-server:
```
# python content-server/server.py
-------------
...
* Running on http://localhost:8601/ (Press CTRL+C to quit)
```

3. Run the streamlit app:
Open a new terminal,
```
# streamlit run app.py
```

# How to add new assets

Folder "RZhCODrlyRo" is an example for a mached query audio.

If you want to add more mached query audio into streamlit app, Please follow the folder structure:

```
|- assets
|   |- CONTAINER_NAME_OF_QUERY_AUDIO
|   |   |- assets
|   |   |   |- ASSET_1_NAME
|   |   |   |   |- ASSET_1_NAME.mp3
|   |   |   |   |- annotation.json
|   |   |   |- ASSET_2_NAME
|   |   |   |   |- ASSET_2_NAME.mp3
|   |   |   |   |- annotation.json
|   |   |- query
|   |   |   |- NAME_OF_QUERY_AUDIO.mp3
|   |   |   |- annotation.json
```
Note: Only the uppercase values ​​can be changed