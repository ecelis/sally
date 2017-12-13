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


    docker run \
      --publish=7474:7474 --publish=7687:7687 \
      --volume=$HOME/neo4j/data:/data \
      neo4j



## Crabs run

In order to run any crab youdo like the following command


    scrapy crawl lightfoot -o <output_item_feed>.csv




## Reference

* [Neo4j docker image](https://hub.docker.com/_/neo4j/)
