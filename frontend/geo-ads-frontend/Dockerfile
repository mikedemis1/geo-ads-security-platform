# Frontend image. Builds the React app, then serves the static output from
# nginx. The build toolchain does not ship: node and node_modules stay in the
# first stage, and the runtime layer is nginx plus a few hundred KB of assets.
FROM node:20-alpine AS build

WORKDIR /src

# npm ci needs the lockfile and installs exactly what it pins, which is the
# point of using it here instead of npm install.
COPY package.json package-lock.json* ./
RUN npm ci --silent

COPY . .
RUN npm run build


FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

COPY --from=build /src/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
  CMD wget -q --spider http://127.0.0.1:3000/ || exit 1
