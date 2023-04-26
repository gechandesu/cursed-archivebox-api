# Cursed API for ArchiveBox

ArchiveBox [doesn't have a web API](https://github.com/ArchiveBox/ArchiveBox/issues/496) yet. This is shitty single-endpoint API to automate page archiving. It uses subprocess to run archivebox CLI. archivebox CLI runs in new thread to avoid blocking main thread.

# Deployment

You must deploy API to server which ArchieveBox runs.

Make working directory, create virtualenv and install dependencies:

```
apt install -y git python3-venv
mkdir -p /opt/cursed_archievebox_api && cd /opt/cursed_archievebox_api
python -m venv env
source env/bin/activate
pip install bottle gunicorn
git clone https://git.nxhs.cloud/ge/cursed-archivebox-api.git .
```

Start API. Set actual path to docker-compose.yml:

```
ARCHIVEBOX_BIN="docker compose -f /opt/archievebox/docker-compose.yml run archivebox" python cursed_archivebox_api.py
```

See also [cursed-archivebox-api.service](cursed-archivebox-api.service).

Install service:

```
cp cursed-archivebox-api.service /etc/systemd/system
systemctl enable --now cursed-archivebox-api.service
```

See logs:

```
journalctl -u cursed-archivebox-api.service -f
```

# Environment

| Variable          | Default               |
| ----------------- | --------------------- |
| `ARCHIVEBOX_BIN`  | `/usr/bin/archivebox` (default for non-Docker installations) |
| `CURSED_PORT`     | `9998`                |
| `CURSED_HOST`     | `0.0.0.0`             |
| `CURSED_SERVER`   | `gunicorn` See [server backends](https://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend) |

# GET /add

Query parameters:

* `url`. Resource URL
* `depth`. Archive depth. Default: 0 (current page)
* `tag`. List of comma separated tags e.g. `my_tag`, `my_tag,another_one`.

Example request:

```
curl -i 'http://localhost:9998/add?url=https://example.com&depth=0&tag=api,example'
```
