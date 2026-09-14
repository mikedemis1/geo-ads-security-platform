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


# Pinned by digest as well as tag. The tag is what a human reads; the digest is
# what makes the build reproducible. Both matter, and the reason is on the wall
# here: this image used to pin 1.27-alpine, a line whose last rebuild was June
# 2025. Fifteen months later it carried 2 critical and 32 high findings with
# fixes available upstream, purely from sitting still. The Trivy gate in CI is
# what says when this line needs bumping.
FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:adf5042a17f4ecdd200c595fa9ffd1be37efb18f89a830bd1a00e4ab4d59d42c AS runtime

COPY --from=build /src/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
  CMD wget -q --spider http://127.0.0.1:3000/ || exit 1
