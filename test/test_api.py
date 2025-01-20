import src.api
import json

def test_validate_request_data():
    data = """{
    "map":"helloworld",
    "zone":0
}
"""
    jsondata = json.loads(data)
    assert src.api.validate_request_data(jsondata) == False

    data = """{
    "map":"surf_helloworld",
    "zone":0,
    "teams": [
        {
            "name": "Omnific oneshotters!",
            "players": [888645636, 62128582]
        },
        {
            "name": "1337 destroyers <<",
            "players": [219496353, 298786834]
        } 
    ]
}
"""
    jsondata = json.loads(data)
    assert src.api.validate_request_data(jsondata) == True