FROM node:18

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

EXPOSE 5000
CMD ["node", "server.js"]
