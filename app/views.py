import log
from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint

from app import settings
from app.api import images, templates
from app.api.images import get_sample_images
from app.helpers import display_images

app = Sanic(name="memegen")

app.config.SERVER_NAME = settings.SERVER_NAME
app.config.API_SCHEMES = settings.API_SCHEMES
app.config.API_VERSION = "0.0"
app.config.API_TITLE = "Memes API"


app.blueprint(images.blueprint)
app.blueprint(images.blueprint_legacy)
app.blueprint(templates.blueprint)
app.blueprint(swagger_blueprint)


@app.get("/")
@doc.exclude(True)
def index(request):
    if "debug" in request.args and settings.DEBUG:
        return response.file(f"app/tests/images/index.html")
    urls = get_sample_images(request)
    text = display_images(urls)
    return response.html(text)


@app.get("/test")
@doc.exclude(True)
def test(request):
    if settings.DEBUG:
        return response.file(f"app/tests/images/index.html")
    return response.redirect("/")


@app.get("/api/")
@doc.exclude(True)
async def api(request):
    return response.json(
        {
            "templates": request.app.url_for("templates.index", _external=True),
            "images": request.app.url_for("images.index", _external=True),
        }
    )


@app.get("/templates/<filename:path>")
@doc.exclude(True)
async def image(request, filename):
    return await response.file(f"templates/{filename}")


if __name__ == "__main__":
    log.silence("asyncio", "datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
    )
