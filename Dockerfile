FROM node:latest

WORKDIR /app

ENV NODE_ENV production

COPY package*.json ./

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
