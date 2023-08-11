#Frontend.Dockerfile
#Builds and runs the frontend. This is done using Svelte's Node server
#(see the adapter used in svelte.config.js)
FROM node:buster
WORKDIR /app
COPY . .
#Install all the dependencies using yarn
RUN yarn install
#Set the origin URL for all requests
ENV ORIGIN="https://album-of-the-day.albins.website"
RUN yarn build
#Run the server
EXPOSE 3000
ENTRYPOINT ["yarn", "node", "server"]