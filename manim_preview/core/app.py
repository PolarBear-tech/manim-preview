from importlib.resources import files
from mimetypes import guess_type
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from manim_preview import config

from .process import get_status

app = FastAPI(title="Manim Preview")

pkg = files("manim_preview.static")


@app.get("/")
def index():
    html_res = pkg.joinpath("index.html").read_bytes()
    return Response(content=html_res, media_type="text/html")


@app.get("/status")
def status():
    return get_status()


@app.get("/static/{file_name:path}")
def static(file_name: str):
    static_res = pkg.joinpath(file_name).read_bytes()
    mime, _ = guess_type(file_name)
    return Response(static_res, media_type=mime)


@app.get("/output/{file_name:path}")
def video(file_name: str):
    path = Path("./output") / file_name
    mime, _ = guess_type(file_name)
    if path.exists():
        return FileResponse(path=path, media_type=mime)

    raise HTTPException(404)


def start_server(port: int):
    import uvicorn

    level = config["log"]["web_level"]
    uvicorn.run(app, host="127.0.0.1", port=port, log_level=level)
