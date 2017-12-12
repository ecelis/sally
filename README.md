# Sally lightfoot


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



## Reference

* [Neo4j docker image](https://hub.docker.com/_/neo4j/)
