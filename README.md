# Sally lightfoot


Collection of web crawlers (crabs) based on Scrapy framework. Each crab
focuses on very specific type of web sites or social networks.


## NOTES

  * Relies heavily on Google web services a Google account is required
  * Source data files are read in batches of 1000
  * One spreadsheet should be created by batch and one sheet for each
    1000
  * lightfoot does not crawl deeper than one level of links found in
    each given url
  * From each web page only `div`, `p`, `span`, `a` and `li` elements
    are searched for data extraction


## Crabs

### lightfoot

Very basic crab to extract general information from web sites.

  * Source: Google spreadsheet, 1000 rows max, only column **A** from
    first sheet

### hermit

Facebook pages crab, fetches contact info, location and likes

  * Source: Google spreadsheet, 1000 rows max, only column **A** from first
    sheet


## Requirements

  * Python 3.6 or greater.
  * MongoDB 3.6 or greater.


## Setup

  1. Create or select a project in the [Google developers console](https://console.developers.google.com/)
  2. Turn on Google Sheets and Google Drive APIs
  3. Create **OAuth client ID** in **Credentials**
  4. Download JSON for Client ID and save it as `client_secret.json` in
     the root directory of sally
  5. Create an app at [facebook for ddevelopers](https://developers.facebook.com/)
  N. TODO ...authorize app from command line


    git clone git@github.com:ecelis/sally.git
    cd sally
    python3 -m venv ENV
    ./ENV/bin/pip3 install --upgrade pip
    . .ENV/bin/activate
    pip install -r requirements.txt


## Database


    docker-compose -up d


## Crab settings and data sources

In Google drive you must create a folder hierarchy like the following:


    sally
    ├── done
    ├── results
    └── uploads


Crabs read configuration settings from a google spreadsheet... TODO
describe spreadsheet format and columns

Set SALLY_SETTINGS_ID environment variable in `variables.env`.


Crabs eat URLs from Google spreadsheets placed in a `uploads` folder in
Google drive.

Set DRIVE_UPLOADS environment variables in `variables.env`.


Crabs place cralw results in Google spreadsheets in a `results` folder
in Google drive.

Set DRIVE_RESULTS environment variable in `variables.env`.


When done source spreadsheets are moved to a `done` folder in Google
drive.

Set DRIVE_DONE environment variable in `variables.env`.


MongoDB is use to store almost raw crawling results, you can either
setup a MongoDB intance or use Mongo Atlas cloud service.

Set MONGO_ATLAS_URI to enable Atlas, it overrides any other MongoDB
settings for the crabs.

Set MONGO_HOST, MONGO_PORT, MONGO_DBNAME, MONGO_REPLICA_SET, MONGO_USER,
and MONGO_PASSWORD environment variables in `variables.env`.


For hermit you must set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET
environment variables in `variables.env`.


## Manual execution

TODO ... update it

In order to run any crab you do like the following command


  ./run.sh <spider name> [file.csv]


Pure python


    . .ENV/bin/activate
    scrapy crawl lightfoot -a csvfile=</path/to/csv>


## Scheduled execution

TODO ...


## Query data

Download [Robo 3T](https://robomongo.org/)


    docker-compose exec mongodb mongo sally
    db.<YYYYMMDD_hhmmss>.find()


### Find by base url


    db.lightfoot.find({ base_url: 'somesite.com'})


### Find emails by base_url


    db.lightfoot.find({ base_url: 'somesite.com'}, {email: 1})


## Reference

  * [Scrapy docs](https://scrapy.readthedocs.org)
  * [Google Developers](https://developers.google.com/)
  * [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
  * [MongoDB Docs](https://docs.mongodb.com/)
  * [Neo4j docker image](https://hub.docker.com/_/neo4j/)
