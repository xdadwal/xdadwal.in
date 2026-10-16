# Server deployment

The portfolio runs as `portfolio.service`, using a private virtual environment
and loopback port 8010. Host Nginx proxies `https://xdadwal.in` to that port.
Ohara's existing dashboard is at `https://ohara.xdadwal.in`.

Install the distribution's `python3-venv`, then from the checkout:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/tailwindcss -i static/css/input.css -o static/css/output.css --minify
sudo install -m 644 deploy/portfolio.service /etc/systemd/system/portfolio.service
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio.service
```

The unit contains this machine's user and checkout path. Update those before
deploying elsewhere. On code updates, install changed requirements, rebuild CSS,
and run `sudo systemctl restart portfolio.service`. Check `/`, `/projects`, `/blog`
and `/static/css/output.css` through HTTPS. Logs: `journalctl -u portfolio.service`.
The service has read-only filesystem access, preserves forwarded HTTPS from
Nginx, restarts on failure, and starts at boot. Public TLS and DNS are managed by
the Ohara deployment; do not bind Uvicorn to a public interface.
