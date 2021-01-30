# MongoDB schema creation guide

1. Verify if mongodb service is running.
    - Windows:
      1. `Ctrl` + `Alt` + `Esc` to open the task manager.
      2. Headover to `Services` tab and find `MongoDB` service.
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
