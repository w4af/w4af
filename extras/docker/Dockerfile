FROM python:3.11-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# Install compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libicu-dev pkgconf git

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install node dependencies in /node_modules
FROM base AS node-deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    npm nodejs
COPY package.json .
COPY package-lock.json .
RUN npm install

# Build minimal runtime image
FROM base AS runtime

# Copy virtual env from base stage
COPY --from=base /usr/local /usr/local

# Install additional runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    npm nodejs git

# Create and switch to a new user
RUN useradd --create-home w4af
WORKDIR /home/w4af
USER w4af

# Copy application files and node modules
COPY --chown=w4af . .
COPY --from=node-deps /node_modules node_modules

# Run the application
ENTRYPOINT [ "python", "-u" ]
CMD [ "w4af_console" ]
