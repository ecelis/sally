# Sally lightfoot


Collection of web crawlers (crabs) based on Scrapy framework. Each crab
focuses on very specific type of web sites or social networks.

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

### MongoDB


    docker run --name mongodb -p 2017:27017 -v $HOME/mongodb:/data/db mongo


### Neo4J


    docker run --neo4j -p 7474:7474 -p 7687:7687 \
      -v $HOME/neo4j/data:/data neo4j



## Crabs run

In order to run any crab youdo like the following command


    scrapy crawl lightfoot


## Query data


    docker exec -it mongodb mongo sally
    db.lightfoot.find()


### Find by base url


    db.lightfoot.find({ base_url: 'somesite.com'})


### Find emails by base_url


    db.lightfoot.find({ base_url: 'somesite.com'}, {email: 1})


## Reference

* [Neo4j docker image](https://hub.docker.com/_/neo4j/)
