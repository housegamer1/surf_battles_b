curl -i -H "Content-Type: application/json" -X POST -d '{
    "map":"surf_outside",
    "zone":1,
    "duration":1,
    "teams": [
        {
            "name": "Not edible objects",
            "players": ["37964988", "64839667"]
        },
        {
            "name": "Edible objects",
            "players": ["145718694", "396780543"]
        },
        {
            "name": "Deadly objects",
            "players": ["921269561", "209170634"]
        }
    ]
}' http://127.0.0.1:5000/addmatch
