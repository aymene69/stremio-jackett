from fastapi.exceptions import HTTPException

from debrid.alldebrid import AllDebrid
from debrid.premiumize import Premiumize
from debrid.realdebrid import RealDebrid
from debrid.torbox import TorBox


def get_debrid_service(config):
    service_name = config['service']
    if service_name == "realdebrid":
        debrid_service = RealDebrid(config)
    elif service_name == "alldebrid":
        debrid_service = AllDebrid(config)
    elif service_name == "premiumize":
        debrid_service = Premiumize(config)
    elif service_name == "torbox":
        debrid_service = TorBox(config)
    else:
        raise HTTPException(status_code=500, detail="Invalid service configuration.")

    return debrid_service