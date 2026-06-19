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

# Railway asigna un puerto dinámico vía la variable de entorno $PORT.
# Si la aplicación escucha en un puerto fijo (como 3000) en vez de
# leer $PORT, Railway no puede enrutar el tráfico hacia el contenedor
# y responde "Application failed to respond" aunque el contenedor esté
# corriendo correctamente por dentro.
EXPOSE 3000
CMD sh -c "serve -s build -l ${PORT:-3000}"
