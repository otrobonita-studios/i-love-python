FROM python:3.12-slim

WORKDIR /app

# NiceGUI is the repo's one runtime dependency (pyproject.toml). Installed
# by name, not `pip install .` -- pyproject.toml declares no [build-system],
# so there's nothing for pip to build; the app runs straight from source.
RUN pip install --no-cache-dir "nicegui>=1.4.30"

COPY . .

EXPOSE 8321

CMD ["python", "app.py"]
