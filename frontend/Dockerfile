# Etapa 1: construir la aplicación React
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Las variables REACT_APP_* deben existir en tiempo de BUILD, no de
# ejecución, porque Create React App las incrusta directamente en
# el JavaScript compilado. Railway las inyecta como build args.
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Etapa 2: servir los archivos estáticos compilados con un servidor liviano
FROM node:20-alpine

WORKDIR /app
RUN npm install -g serve

COPY --from=build /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
