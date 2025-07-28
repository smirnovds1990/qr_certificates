FROM python:3.12.11-slim-bookworm
WORKDIR /src

COPY pyproject.toml uv.lock ./
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl ca-certificates \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv sync --frozen

COPY src/ .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
