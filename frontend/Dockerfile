FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

FROM base AS development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]