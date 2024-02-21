import base64
import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import starlette.status as status

from utils.get_content import get_name
from utils.get_cached import search_cache
from utils.jackett import search
from utils.filter_results import filter_items
from utils.get_availability import availability
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
        "version": "3.0.0",
        "catalogs": [],
        "resources": ["stream"],
        "types": ["movie", "series"],
        "name": "Jackett",
        "description": "Stremio Jackett Addon",
        "behaviorHints": {
            "configurable": True,
        }
    }


@app.get("/{config}/stream/{stream_type}/{stream_id}")
async def get_results(config: str, stream_type: str, stream_id: str):
    stream_id = stream_id.replace(".json", "")
    config = json.loads(base64.b64decode(config).decode('utf-8'))
    if stream_type == "movie":
        print("Movie request")
        print("Getting name and properties")
        name = get_name(stream_id, stream_type, config=config)
        print("Got name and properties: " + str(name['title']))
        print("Getting config")
        print("Got config")
        print("Getting cached results")
        cached = search_cache(name)
        print("Got cached results")
        if len(cached) >= int(config['maxResults']):
            print("Cached results found")
            print("Processing cached results")
            stream_list = process_results(cached[:int(config['maxResults'])], True, "movie", config=config)
            print("Processed cached results")
            if len(stream_list) == 0:
                print("No results found")
                return {"streams": [{"url": "#", "title": "No results found"}]}
            return {"streams": stream_list}
        else:
            print("No cached results found")
            print("Searching for results on Jackett")
            search_results = search({"type": name['type'], "title": name['title'], "year": name['year']}, config=config)
            print("Got results from Jackett")
            print("Filtering results")
            filtered_results = filter_items(search_results, config=config)
            print("Filtered results")
            print("Checking availability")
            results = availability(filtered_results, config=config) + cached
            print("Checked availability")
            print("Processing results")
            stream_list = process_results(results[:int(config['maxResults'])], False, "movie", config=config)
            print("Processed results")
            if len(stream_list) == 0:
                print("No results found")
                return {"streams": [{"url": "#", "title": "No results found"}]}
            return {"streams": stream_list}
    if stream_type == "series":
        print("Series request")
        print("Getting name and properties")
        name = get_name(stream_id, stream_type, config=config)
        print("Got name and properties: " + str(name['title']))
        print("Getting config")
        print("Got config")
        print("Getting cached results")
        cached = search_cache(name)
        print("Got cached results")
        if len(cached) >= int(config['maxResults']):
            print("Cached results found")
            if len(cached) == 1:
                print("Processing cached results")
                stream_list = process_results(cached, True, "series", name['season'], name['episode'], config=config)
                print("Processed cached results")
                if len(stream_list) == 0:
                    print("No results found")
                    return {"streams": [{"url": "#", "title": "No results found"}]}
                return {"streams": stream_list}
            else:
                print("Processing cached results")
                stream_list = process_results(cached[:int(config['maxResults'])], True, "series",
                                              name['season'], name['episode'], config=config)
                print("Processed cached results")
                if len(stream_list) == 0:
                    print("No results found")
                    return {"streams": [{"url": "#", "title": "No results found"}]}
                return {"streams": stream_list}
        else:
            print("No cached results found")
            print("Searching for results on Jackett")
            search_results = search(
                {"type": name['type'], "title": name['title'], "season": name['season'], "episode": name['episode']}, config=config)
            print("Got results from Jackett")
            print("Filtering results")
            filtered_results = filter_items(search_results, stream_type, config=config)
            print("Filtered results")
            print("Checking availability")
            results = availability(filtered_results, config=config) + cached
            print("Checked availability")
            print("Processing results")
            stream_list = process_results(results[:int(config['maxResults'])], False, "series",
                                          name['season'], name['episode'], config=config)
            print("Processed results")
            if len(stream_list) == 0:
                print("No results found")
                return {"streams": [{"url": "#", "title": "No results found"}]}
            return {"streams": stream_list}


@app.get("/{config}/playback/{query}/{title}")
async def get_playback(config: str, query: str, title: str):
    try:
        if not query or not title:
            raise HTTPException(status_code=400, detail="Query and title are required.")
        config = json.loads(base64.b64decode(config).decode('utf-8'))
        print("Decoding query")
        query = base64.b64decode(query).decode('utf-8')
        print(query)
        print("Decoded query")

        service = config['service']
        if service == "realdebrid":
            print("Getting Real-Debrid link")
            link = get_stream_link_rd(query, config=config)
        elif service == "alldebrid":
            print("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        print("Got link:", link)
        return RedirectResponse(url=link, status_code=status.HTTP_302_FOUND)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")


@app.head("/{config}/playback/{query}/{title}")
async def get_playback(config: str, query: str, title: str):
    try:
        if not query or not title:
            raise HTTPException(status_code=400, detail="Query and title are required.")
        config = json.loads(base64.b64decode(config).decode('utf-8'))
        print("Decoding query")
        query = base64.b64decode(query).decode('utf-8')
        print(query)
        print("Decoded query")

        service = config['service']
        if service == "realdebrid":
            print("Getting Real-Debrid link")
            link = get_stream_link_rd(query, config=config)
        elif service == "alldebrid":
            print("Getting All-Debrid link")
            link = get_stream_link_ad(query, config=config)
        else:
            raise HTTPException(status_code=500, detail="Invalid service configuration.")

        print("Got link:", link)
        return RedirectResponse(url=link, status_code=status.HTTP_302_FOUND)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

@app.get("/{config}/nocache")
async def get_nocache():
    return FileResponse("nocache.mp4", media_type="video/mp4")

@app.get("/nocache")
async def get_nocache():
    return FileResponse("nocache.mp4", media_type="video/mp4")