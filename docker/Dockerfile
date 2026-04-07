FROM nginx:stable

# Use repository nginx config for production container.
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Serve prebuilt Hugo output without host bind mounts.
COPY public/ /usr/share/nginx/html/

# Normalize file permissions so static assets such as PDFs are always readable.
RUN find /usr/share/nginx/html -type d -exec chmod 755 {} + \
    && find /usr/share/nginx/html -type f -exec chmod 644 {} +
