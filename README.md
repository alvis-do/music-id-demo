# Dependences
- python3.6
- streamlit
- flask

# How to run
1. Create virtual environment and install requirement.txt:

2. Run the content-server:
```
# python content-server/server.py -p 8602
-------------
...
* Running on http://localhost:8602/ (Press CTRL+C to quit)
```

3. Setup the config:

    Duplicate `config.json.example` file and rename to `config.json`.

    If you run at local machine, change the value of `content_server_name` option by the value from step 2.

    If you run at server, repace that with `http://<domain_name>:<public_port>`. Remember that, you need to setup a proxy pass to localhost from step 2.

4. Run the streamlit app:
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

# How to deploy to server
1. Install NGINX
2. Run streamlit app (Refer to [How to run](#how-to-run) section)
3. Config NGINX:

- Edit the NGINX config file at `/etc/nginx/sites-available/default`:

```
server {
    listen 8601;
    listen [::]:8601;

    server_name your_domain.com;
    proxy_read_timeout 86400;

    location / {
        proxy_pass http://localhost:8602/;
    }
}
server {
    listen 80;
    listen [::]:80;

    server_name your_domain.com;
    keepalive_timeout 5;

    location / {
        proxy_pass http://localhost:8501/;
    }
    location ^~ /static {
        proxy_pass http://localhost:8501/static/;
    }
    location ^~ /healthz {
        proxy_pass http://localhost:8501/healthz;
    }

    location ^~ /vendor {
        proxy_pass http://localhost:8501/vendor;
    }
    location /stream { # most important config
        proxy_pass http://localhost:8501/stream;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
 }
```

- Restart the NGINX service after changed
- Visit http://example.com on any browser.

    Note: Replace `example.com` with your domain

Recommend: Follow tutorial and using Gunicorn to deploy, [here](https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a)

# Thank you

Author: Vu Do - DeepHub Team ♥️
