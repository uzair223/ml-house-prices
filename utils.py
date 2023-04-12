import requests
from werkzeug.exceptions import BadRequest

# Utility function to format big numbers
# 128,956 => 129k, 1,245,234 => 1.25M
def formatNumber(n, precision):
    ranges = ((1e6, "M"), (1e3, "k"))
    for r in ranges:
        if (n >= r[0]):
            return f"{n/r[0]:.{precision}g}{r[1]}"
    return n

# findthatpostcode api
def findthatpostcode(postcode):
    response = requests.get(f"https://findthatpostcode.uk/postcodes/{postcode}.json")
    if(response.status_code != 200): raise BadRequest(f"Invalid postcode: {postcode}")
    extract = ["location","laua_name","ward_name","oac11","imd","pcd"]
    data = {k:response.json()["data"]["attributes"][k] for k in extract}
    data["location"]["lng"] = data["location"].pop("lon")
    return data