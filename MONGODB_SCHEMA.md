# MongoDB schema creation guide
[Click here to learn about API key placement](#api-placement)
1. Verify if mongodb service is running.
    - Windows:
        1. `Ctrl` + `Alt` + `Esc` to open the task manager.
        2. Head over to `Services` tab and find `MongoDB` service.
        3. Right click and `Start` if service is stopped.
    - Linux:
        1. `sudo systemctl status mongod`
        2. If service is stopped or disabled, run
            - `sudo systemctl start mongod`
            - `sudo systemctl enable mongod`

2. Open terminal or CMD and run `mongo` command to open mongoDB shell.
3. Create database -> `use stockticker`
4. Create Collections
    - `db.createCollection('globalsymbols')`
    - `db.createCollection('tickers')` 

<h2 id="api-placement"> API Token Placement</h2>

1. Verify that the JSON files have the structure `{"key": "<YOUR-TOKEN>"}` 
2. Rename files to `Telegram_token.json` and `alpha_vantage_api_key.json`
3. Place JSON files in `./config` and it's done