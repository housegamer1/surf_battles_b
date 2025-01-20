curl -i -H "Content-Type: application/json" -X POST -d '{
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
}' http://127.0.0.1:5000/addmatch
