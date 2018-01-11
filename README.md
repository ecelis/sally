# Sally lightfoot


Collection of web crawlers (crabs) based on Scrapy framework. Each crab
focuses on very specific type of web sites or social networks.


## NOTES

  * lightfoot does not crawal deeper then one level of links found in
    each given url


### Crabs

* lightfoot, very basic crab to extract general information from web
  sites


## Setup


    git clone TODO
    cd sally
    virtualenv -p python3 ENV
    ./ENV/bin/pip3 install --upgrade pip
    . .ENV/bin/activate
    pip install -r requirements.txt


## Database


    docker-compose -up d



## Crabs run

In order to run any crab you do like the following command


    . .ENV/bin/activate
    scrapy crawl lightfoot -a csvfile=</path/to/csv>


## Query data

Download [Robo 3T](https://robomongo.org/)


    docker-compose exec mongodb mongo sally
    db.<YYYYMMDD_hhmmss>.find()


### Find by base url


    db.lightfoot.find({ base_url: 'somesite.com'})


### Find emails by base_url


    db.lightfoot.find({ base_url: 'somesite.com'}, {email: 1})


## Reference

* [Neo4j docker image](https://hub.docker.com/_/neo4j/)
