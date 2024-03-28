import asyncio
import logging
import os
import re
import shutil
import time
import zipfile

import requests
import starlette.status as status
from aiocron import crontab
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from constants import NO_RESULTS
from debrid.get_debrid_service import get_debrid_service
from jackett.jackett_service import JackettService
from torrent.torrent_service import TorrentService
from torrent.torrent_smart_container import TorrentSmartContainer
from utils.cache import search_cache
from utils.filter_results import filter_items
from utils.filter_results import sort_items
from utils.logger import setup_logger
from utils.parse_config import parse_config
from utils.process_results import process_results
from utils.string_encoding import decodeb64
from utils.tmdb import get_metadata
from utils.stremio_parser import parse_to_stremio_streams

load_dotenv()

root_path = os.environ.get("ROOT_PATH", None)
if root_path and not root_path.startswith("/"):
    root_path = "/" + root_path
app = FastAPI(root_path=root_path)

VERSION = "4.0.0"
isDev = os.getenv("NODE_ENV") == "development"


class LogFilterMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        path = request.url.path
        sensible_path = re.sub(r'/ey.*?/', '/<SENSITIVE_DATA>/', path)
        logger.info(f"{request.method} - {sensible_path}")
        return await self.app(scope, receive, send)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not isDev:
    app.add_middleware(LogFilterMiddleware)

templates = Jinja2Templates(directory=".")

logger = setup_logger(__name__)


@app.get("/")
async def root():
    return RedirectResponse(url="/configure")


@app.get("/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{config}/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/manifest.json")
@app.get("/{params}/manifest.json")
async def get_manifest():
    return {
        "id": "community.aymene69.jackett",
        "icon": "https://i.imgur.com/tVjqEJP.png",
        "version": VERSION,
        "catalogs": [],
        "resources": ["stream"],
        "types": ["movie", "series"],
        "name": "Jackett" + (" (Dev)" if isDev else ""),
        "description": "Elevate your Stremio experience with seamless access to Jackett torrent links, effortlessly "
                       "fetching torrents for your selected movies within the Stremio interface.",
        "behaviorHints": {
            "configurable": True,
            # "configurationRequired": True
        }
    }


formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                              '%m-%d %H:%M:%S')

logger.info("Started Jackett Addon")


@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    start = time.time()
    stream_id = stream_id.replace(".json", "")
    config = parse_config(config)
    logger.info(stream_type + " request")
    logger.info("Getting media from tmdb")
    media = get_metadata(stream_id, stream_type, config=config)
    logger.info("Got media and properties: " + media.title)
    debrid_service = get_debrid_service(config)
    logger.info("Getting cached results")
    if config['cache']:
        cached_results = search_cache(media)
    else:
        cached_results = []
    logger.info("Got " + str(len(cached_results)) + " cached results")
    filtered_cached_results = []
    if len(cached_results) > 0:
        logger.info("Filtering cached results")
        filtered_cached_results = filter_items(cached_results, media.type, config=config)

        logger.info("Filtered cached results")
    # TODO: if we have results per quality set, most of the time we will not have enough cached results AFTER filtering them
    # because we will have less results than the maxResults, so we will always have to search for new results
    if len(filtered_cached_results) >= int(config['maxResults']):
        logger.info("Cached results found")
        logger.info("Processing cached results")
        stream_list = process_results(filtered_cached_results[:int(config['maxResults'])], True, media.type,
                                      media.season if media.type == "series" else None,
                                      media.episode if media.type == "series" else None,
                                      debrid_service=debrid_service, config=config)
        logger.info("Processed cached results")
        logger.info("Total time: " + str(time.time() - start) + "s")
        if len(stream_list) == 0:
            logger.info("No results found")
            return NO_RESULTS
        return {"streams": stream_list}
    else:
        if len(filtered_cached_results) > 0:
            logger.info("Not enough cached results found (results: " + str(len(filtered_cached_results)) + ")")
        else:
            logger.info("No cached results found")
        logger.info("Searching for results on Jackett")
        jackett_service = JackettService(config)
        jackett_search_results = jackett_service.search(media)
        logger.info("Got " + str(len(jackett_search_results)) + " results from Jackett")
        logger.info("Converting results")
        logger.info("Converted results")
        logger.info("Filtering results")
        filtered_jackett_search_results = filter_items(jackett_search_results, media, config=config)
        logger.info("Filtered results")
        logger.debug("Converting result to TorrentItems (results: " + str(len(filtered_jackett_search_results)) + ")")
        torrent_service = TorrentService()
        torrent_results = torrent_service.convert_and_process(filtered_jackett_search_results)
        logger.debug("Converted result to TorrentItems (results: " + str(len(torrent_results)) + ")")
        torrent_smart_container = TorrentSmartContainer(torrent_results)
        logger.debug("Checking availability")
        hashes = torrent_smart_container.get_hashes()
        result = debrid_service.get_availability_bulk(hashes)
        torrent_smart_container.update_availability(result, type(debrid_service))
        logger.debug("Checked availability (results: " + str(len(result.items())) + ")")
        logger.debug("Getting best matching results")
        best_matching_results = torrent_smart_container.get_best_matching(media)
        best_matching_results = sort_items(best_matching_results, config)
        logger.debug("Got best matching results (results: " + str(len(best_matching_results)) + ")")
        logger.info("Processing results")

        stream_list = parse_to_stremio_streams(best_matching_results, config)
        logger.info("Processed results (results: " + str(len(stream_list)) + ")")
        logger.info("Total time: " + str(time.time() - start) + "s")
        return {"streams": stream_list}


@app.get("/playback/{config}/{query}")
async def get_playback(config: str, query: str):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query required.")
        config = parse_config(config)
        logger.info("Decoding query")
        query = decodeb64(query)
        logger.info(query)
        logger.info("Decoded query")

        debrid_service = get_debrid_service(config)
        link = debrid_service.get_stream_link(query)
        
        if link is None:
            logger.info("Caching in progress.")
             #This doesn't work for some reason?
            return RedirectResponse(url=f"{config["addonHost"]}/nocache", status_code=status.HTTP_301_MOVED_PERMANENTLY)

        logger.info("Got link: " + link)
        return RedirectResponse(url=link, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

async def update_app():
    try:
        current_version = "v" + VERSION
        url = "https://api.github.com/repos/itsvncl/stremio-jackett-hungary/releases/latest"
        response = requests.get(url)
        data = response.json()
        latest_version = data['tag_name']
        if latest_version != current_version:
            logger.info("New version available: " + latest_version)
            logger.info("Updating...")
            logger.info("Getting update zip...")
            update_zip = requests.get(data['zipball_url'])
            with open("update.zip", "wb") as file:
                file.write(update_zip.content)
            logger.info("Update zip downloaded")
            logger.info("Extracting update...")
            with zipfile.ZipFile("update.zip", 'r') as zip_ref:
                zip_ref.extractall("update")
            logger.info("Update extracted")

            extracted_folder = os.listdir("update")[0]
            extracted_folder_path = os.path.join("update", extracted_folder)
            for item in os.listdir(extracted_folder_path):
                s = os.path.join(extracted_folder_path, item)
                d = os.path.join(".", item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            logger.info("Files copied")

            logger.info("Cleaning up...")
            shutil.rmtree("update")
            os.remove("update.zip")
            logger.info("Cleaned up")
            logger.info("Updated !")
    except Exception as e:
        logger.error(f"Error during update: {e}")

@app.get("/nocache")
async def nocache_video_file():
    return FileResponse("videos/nocache.mp4")

@crontab("* * * * *", start=not isDev)
async def schedule_task():
    await update_app()


async def main():
    await asyncio.gather(
        schedule_task()
    )


if __name__ == "__main__":
    asyncio.run(main())
