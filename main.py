import json
import uuid

import quart
import quart_cors
from quart import request, send_from_directory

# components used for generating charts.
from pyecharts.charts.base import Base

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# create chart with options
@app.post("/charts")
async def create_chart():
    options = await quart.request.get_json(force=True)
    chart = Base()
    chart.options = options

    suffix = uuid.uuid4()
    file_name = suffix
    if 'title' in options:
        if 'text' in options['title']:
            file_name = f"{options['title']['text']}_{file_name}"

    html_path = f"output/{file_name}.html"
    img_path = f"output/{file_name}.png"
    chart.render(html_path)

    response_dict = {}
    response_dict['htmlPath'] = f"{request.host}/{html_path}"
    response_dict['imgPath'] = f"{request.host}/{img_path}"

    return quart.Response(response=json.dumps(response_dict), status=200)

# reading locally stored static resources.
@app.route('/output/<path:path>')
async def serve_file(path):
    return await send_from_directory('./output', path)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
