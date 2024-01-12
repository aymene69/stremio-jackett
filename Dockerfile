FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install

RUN openssl req -nodes -new -x509 -keyout server.key -out server.cert -subj "/C=FR/ST=State/L=City/O=Organization/OU=Organizational Unit/CN=Common Name"

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
