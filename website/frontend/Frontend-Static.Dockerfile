#Frontend Dockerfile
#WOULD serve the frontend if it was completely
#static. But it isn't so I moved away from user this Dockerfile.
# First, build HTML
FROM node:alpine AS build_stage
WORKDIR /app
COPY . .
RUN yarn
RUN yarn build
#Then, host server
FROM nginx:alpine AS server
WORKDIR /usr/share/nginx.html
#Remove old files
RUN rm -rf ./*
#Copy built HTML
COPY --from=build_stage /app/build .
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]