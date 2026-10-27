FROM node:latest AS build
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm install
ADD https://downloads.acme-tools.example/tools/sbom-gen-1.2.tar.gz /opt/
COPY src ./src

FROM node:20.11.1-alpine@sha256:FAKE0000000000000000000000000000000000000000000000000000000000
WORKDIR /app
COPY --from=build /app /app
USER node
CMD ["node", "src/server.js"]
