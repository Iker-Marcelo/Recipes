0) To startup the three containers that make the app, i.e. todo-fastapi-microservice, express-auth-api microservice and fastapi-gateway
docker-compose up 

If you need to rebuild the containers execute the command: docker-compose up --build --force-recreate --no-deps

docker compose up -d --no-deps --build main-app

The following steps would be carried out in case you want to start the containers manually: 

1) Start the microservice of TODOs
cd todo-fastapi-microservice
pip install fastapi uvicorn httpx
uvicorn main:app --reload

2) Start the microservice of authentication

cd express-auth-api
npm install express bcryptjs jsonwebtoken swagger-ui-express yamljs
node server.js

3) Start the gateway
cd fastapi-gateway
pip install fastapi uvicorn httpx
uvicorn main:app --reload --port 8080


This step is not needed any longer since 3) already includes the HTML front-end. It is a good example on how to expose static content though. 
4) Load frontend
cd frontend
npm install http-server -g
http-server -o --cors