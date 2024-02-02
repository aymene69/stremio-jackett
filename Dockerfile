FROM node:latest

WORKDIR /app

ENV NODE_ENV production

COPY package*.json ./

RUN npm install pm2 -g

RUN npm install parse-torrent

COPY . .

COPY .env.example .env

EXPOSE 3000

CMD ["pm2", "start", "--no-daemon", "ecosystem.config.cjs"]
