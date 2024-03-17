import asyncio
import base64
import json
import logging
import os
import re
import shutil
import zipfile

import requests
import starlette.status as status
from aiocron import crontab
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from constants import NO_RESULTS
from debrid.alldebrid import get_stream_link_ad
from debrid.premiumize import get_stream_link_pm
from debrid.realdebrid import get_stream_link_rd
from utils.filter_results import filter_items
from utils.get_availability import availability
from utils.get_cached import search_cache
from utils.get_cached import get_cached_results
from utils.get_cached import process_cached_results
from utils.get_content import get_name
from utils.jackett import search
from utils.logger import setup_logger
from utils.process_results import process_results
from utils.direct_torrent import get_torrent_stream

load_dotenv()

root_path = os.environ.get("ROOT_PATH", None)
if root_path and not root_path.startswith("/"):
    root_path = "/" + root_path
app = FastAPI(root_path=root_path)

VERSION = "3.0.13"
isDev = True


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
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                              '%m-%d %H:%M:%S')
logger.info("Started Jackett Addon")


@app.get("/")
async def root():
    return RedirectResponse(url="/configure")


@app.get("/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{config}/configure")
async def configure(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
        }
    }

@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    stream_id = stream_id.replace(".json", "")
    
    logger.info("Getting config")
    config = json.loads(base64.b64decode(config).decode('utf-8'))
    logger.info("Got config")

    logger.info(stream_type + " request")
    logger.info("Getting name and properties")
    name = get_name(stream_id, stream_type, config['tmdbApi'], config['language'])
    logger.info("Got name and properties: " + str(name['title']))
    
    # Cache part
    filtered_cached_results = []
    if config['cache']:
        filtered_cached_results = get_cached_results(name, stream_type, config)
        cached_result_count = len(filtered_cached_results)
        
        if cached_result_count >= int(config['maxResults']):
            return process_cached_results(filtered_cached_results, stream_type, name, config)
        elif cached_result_count > 0:
            logger.info("Not enough cached results found (results: " + str(cached_result_count) + ")")
        else:
            logger.info('No cached result found')
    
    # Jackett search part
    logger.info("Searching for results on Jackett")
    search_results = search(name, config) 
    logger.info("Got " + str(len(search_results)) + " results from Jackett")
    
    logger.info("Filtering results")
    filtered_results = filter_items(search_results, stream_type, config)
    logger.info("Filtered results")
    
    logger.info("Checking availability")

    #TODO: Direct torrenting should be a option that MAY be used, if a given torrent is not already in debrid
    
    #Direct torrent route
    if config['directTorrent']:
        streams = []
        for result in filtered_results:
            torrent_stream = get_torrent_stream(result)
            if torrent_stream:
                streams.append(torrent_stream)
        return {
            "streams": streams
        }
    
    #Debrid route
    results = availability(filtered_results, config=config) + filtered_cached_results
    logger.info("Checked availability (results: " + str(len(results)) + ")")
    logger.info("Processing results")
    stream_list = process_results(results[:int(config['maxResults'])], False, stream_type,
                                  name['season'] if stream_type == "series" else None,
                                  name['episode'] if stream_type == "series" else None, config=config)
    
    logger.info("Processed results (results: " + str(len(stream_list)) + ")")
    if len(stream_list) == 0:
        logger.info("No results found")
        return NO_RESULTS
    return {"streams": stream_list}


@app.get("/playback/{config}/{query}/{title}")
async def get_playback(config: str, query: str, title: str, request: Request):
    try:
        if not query or not title:
            raise HTTPException(status_code=400, detail="Query and title are required.")
        config = json.loads(base64.b64decode(config).decode('utf-8'))
        logger.info("Decoding query")
        query = base64.b64decode(query).decode('utf-8')
        logger.info(query)
        logger.info("Decoded query")

        service = config['service']
        if service == "realdebrid":
            logger.info("Getting Real-Debrid link")
            source_ip = request.client.host
            link = get_stream_link_rd(query, source_ip, config=config)
        elif service == "alldebrid":
            logger.info("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        elif service == "premiumize":
            logger.info("Getting Premiumize link")
            link = get_stream_link_pm(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        logger.info("Got link: " + link)
        return RedirectResponse(url=link, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    except Exception as e:
        logger.error('An error occured %s', 'division', exc_info=e)
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")


async def update_app():
    try:
        if not isDev:
            current_version = "v" + VERSION
            url = "https://api.github.com/repos/aymene69/stremio-jackett/releases/latest"
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


@crontab("* * * * *", start=not isDev)
async def schedule_task():
    await update_app()


async def main():
    await asyncio.gather(
        schedule_task()
    )


if __name__ == "__main__":
    asyncio.run(main())
