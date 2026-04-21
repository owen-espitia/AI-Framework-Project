FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
#nginx has been implemented as a workaround to serve the static files,
#I ran into a bunch of issues with StaticFiles from FastAPI

# Copy static files
COPY static/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]