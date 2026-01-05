#!/bin/sh
# Startup script for nginx that handles PORT environment variable from Railway

PORT=${PORT:-3000}

# Replace PORT in nginx config template
sed "s/listen 3000/listen $PORT/g" /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx
exec nginx -g "daemon off;"

