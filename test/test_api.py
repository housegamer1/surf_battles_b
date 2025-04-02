import src.api
import json

def test_validate_add_request():
    data = """{
    "map":"helloworld",
    "zone":0
}
"""
    jsondata = json.loads(data)
    assert src.api.validate_add_request(jsondata) == False

    data = """{
    "map":"surf_helloworld",
    "zone":0,
    "duration":1,
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
    assert src.api.validate_add_request(jsondata) == True


def test_validate_add_request_no_name():
    data = """{
    "map":"surf_helloworld",
    "zone":0,
    "duration":1,
    "teams": [
        {
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
    assert src.api.validate_add_request(jsondata) == False