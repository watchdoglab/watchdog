FROM node:latest
ARG NPM_TOKEN=fake-benchmark-npm-token
ENV NODE_ENV=production
WORKDIR /app
COPY . .
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && npm install
RUN curl -fsSL https://example.com/install.sh | sh
EXPOSE 3000
CMD ["node", "src/server.js"]
