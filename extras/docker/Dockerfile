FROM python:3.11-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc g++ libicu-dev pkgconf git

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# Install node dependencies in /node_modules
FROM base AS node-deps

RUN apt-get update && apt-get install -y --no-install-recommends \
  npm nodejs
COPY package.json .
COPY package-lock.json .
RUN npm install

# Build minimal runtime image
FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
RUN apt-get update && apt-get install -y --no-install-recommends \
  npm nodejs git

# Create and switch to a new user
RUN useradd --create-home w4af
WORKDIR /home/w4af
USER w4af

# Install application into container
COPY --chown=w4af . .
COPY --from=node-deps /node_modules node_modules

# Run the application
ENTRYPOINT [ "python", "-u" ]
CMD [ "w4af_console" ]
