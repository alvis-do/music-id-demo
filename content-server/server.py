from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
import click
import sys

app = Flask(__name__, 
            template_folder="templates", 
            static_folder=".")
            
cors = CORS(app)


@app.route('/base/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/', filename)

@app.route('/assets/<path:filename>')
def asset_static(filename):
    return send_from_directory(app.root_path + '/../assets/', filename)


@app.route('/index_origin', methods=['GET'])
def index_origin():
    return render_template("index_origin.html")


@app.route('/query_predict', methods=['GET'])
def query_predict():
    return render_template("query_predict.html", 
            query_audio_container_name=request.args.get("query_audio_container_name"),
            query_audio_name=request.args.get("query_audio_name"))

@app.route('/asset_predict', methods=['GET'])
def asset_predict():
    return render_template("asset_predict.html", 
            query_audio_container_name=request.args.get("query_audio_container_name"),
            asset_audio_name=request.args.get("asset_audio_name"))

@click.command()
@click.option("-p", "--port", default=8602, help="The server port")
def main(port):
    app.run(host='localhost', port=port)


if __name__ == '__main__':
    main()