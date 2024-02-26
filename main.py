import base64
import json
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import starlette.status as status

from constants import NO_RESULTS
from utils.get_content import get_name
from utils.get_cached import search_cache
from utils.jackett import search
from utils.filter_results import filter_items
from utils.get_availability import availability
from utils.logger import setup_logger
from utils.process_results import process_results

from debrid.realdebrid import get_stream_link_rd
from debrid.alldebrid import get_stream_link_ad

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/{params}/manifest.json")
async def get_manifest():
    return {
        "id": "community.aymene69.jackett",
        "icon": "https://i.imgur.com/tVjqEJP.png",
        "version": "3.0.10",
        "catalogs": [],
        "resources": ["stream"],
        "types": ["movie", "series"],
        "name": "Jackett",
        "description": "Stremio Jackett Addon",
        "behaviorHints": {
            "configurable": True,
        }
    }

formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')

@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    stream_id = stream_id.replace(".json", "")
    config = json.loads(base64.b64decode(config).decode('utf-8'))
    if stream_type == "movie":
        logger.info("Movie request")
        logger.info("Getting name and properties")
        name = get_name(stream_id, stream_type, config=config)
        logger.info("Got name and properties: " + str(name['title']))
        logger.info("Getting config")
        logger.info("Got config")
        logger.info("Getting cached results")
        cached_results = search_cache(name)
        logger.info("Got " + str(len(cached_results)) + " cached results")
        logger.info("Filtering cached results")
        filtered_cached_results = filter_items(cached_results, "movie", config=config, cached=True)
        logger.info("Filtered cached results")
        if len(filtered_cached_results) >= int(config['maxResults']):
            logger.info("Cached results found")
            logger.info("Processing cached results")
            stream_list = process_results(filtered_cached_results[:int(config['maxResults'])], True, "movie", config=config)
            logger.info("Processed cached results")
            if len(stream_list) == 0:
                logger.info("No results found")
                return NO_RESULTS
            return {"streams": stream_list}
        else:
            logger.info("No cached results found")
            logger.info("Searching for results on Jackett")
            search_results = search({"type": name['type'], "title": name['title'], "year": name['year']}, config=config)
            logger.info("Got " + str(len(search_results)) + " results from Jackett")
            logger.info("Filtering results")
            filtered_results = filter_items(search_results, config=config)
            logger.info("Filtered results")
            logger.info("Checking availability")
            results = availability(filtered_results, config=config) + filtered_cached_results
            logger.info("Checked availability (results: " + str(len(results)) + ")")
            logger.info("Processing results")
            stream_list = process_results(results[:int(config['maxResults'])], False, "movie", config=config)
            logger.info("Processed results (results: " + str(len(stream_list)) + ")")
            if len(stream_list) == 0:
                logger.info("No results found")
                return NO_RESULTS
            return {"streams": stream_list}
    if stream_type == "series":
        logger.info("Series request")
        logger.info("Getting name and properties")
        name = get_name(stream_id, stream_type, config=config)
        logger.info("Got name and properties: " + str(name['title']))
        logger.info("Getting config")
        logger.info("Got config")
        logger.info("Getting cached results")
        cached_results = search_cache(name)
        logger.info("Got " + str(len(cached_results)) + " cached results")
        logger.info("Filtering cached results")
        filtered_cached_results = filter_items(cached_results, "series", config=config, cached=True, season=name['season'], episode=name['episode'])
        logger.info("Filtered cached results")
        if len(filtered_cached_results) >= int(config['maxResults']):
            logger.info("Cached results found")
            if len(filtered_cached_results) == 1:
                logger.info("Processing cached results")
                stream_list = process_results(filtered_cached_results, True, "series", name['season'], name['episode'], config=config)
                logger.info("Processed cached results")
                if len(stream_list) == 0:
                    logger.info("No results found")
                    return NO_RESULTS
                return {"streams": stream_list}
            else:
                logger.info("Processing cached results")
                stream_list = process_results(filtered_cached_results[:int(config['maxResults'])], True, "series",
                                              name['season'], name['episode'], config=config)
                logger.info("Processed cached results")
                if len(stream_list) == 0:
                    logger.info("No results found")
                    return NO_RESULTS
                return {"streams": stream_list}
        else:
            logger.info("No cached results found")
            logger.info("Searching for results on Jackett")
            search_results = search(
                {"type": name['type'], "title": name['title'], "season": name['season'], "episode": name['episode']}, config=config)
            logger.info("Got " + str(len(search_results)) + " results from Jackett")
            logger.info("Filtering results")
            filtered_results = filter_items(search_results, stream_type, config=config)
            logger.info("Filtered results")
            logger.info("Checking availability")
            results = availability(filtered_results, config=config) + filtered_cached_results
            logger.info("Checked availability (results: " + str(len(results)) + ")")
            logger.info("Processing results")
            stream_list = process_results(results[:int(config['maxResults'])], False, "series",
                                          name['season'], name['episode'], config=config)
            logger.info("Processed results (results: " + str(len(stream_list)) + ")")
            if len(stream_list) == 0:
                logger.info("No results found")
                return NO_RESULTS
            return {"streams": stream_list}


@app.get("/playback/{config}/{query}/{title}")
async def get_playback(config: str, query: str, title: str):
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
            link = get_stream_link_rd(query, config=config)
        elif service == "alldebrid":
            logger.info("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        logger.info("Got link: " + link)
        return RedirectResponse(url=link, status_code=status.HTTP_302_FOUND)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

@app.head("/playback/{config}/{query}/{title}")
async def get_playback(config: str, query: str, title: str):
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
            link = get_stream_link_rd(query, config=config)
        elif service == "alldebrid":
            logger.info("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        logger.info("Got link: " + link)
        return RedirectResponse(url=link, status_code=status.HTTP_302_FOUND)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")