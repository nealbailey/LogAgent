# LogAgent
Tiny log reader. This agent provides remote access to pre-determined log files on the host. Its designed and optimized to require no external dependencies and be as small and quick as possible.

## Installation

1. Clone the repository and change into the project directory:

	```bash
	git clone <repository-url>
	cd LogAgent
	```

2. Configure the log files in `logagent.json`. Add or remove entries as needed; each key becomes a log endpoint and each value must be the path to a readable log file:

	```json
	{
	  "logs": {
		 "nordvpn": "/var/log/nordvpn.sh.log",
		 "killswitch": "/var/log/killswitch.sh.log"
	  }
	}
	```

	Ensure the user running LogAgent has permission to read the configured files.

3. Start the agent:

	```bash
	python3 logagent.py
	```

	The agent listens on port `8010`. Request `/` to list configured logs or `/<log-name>` to read a log, for example:

	```text
	http://localhost:8010/nordvpn
	```

## Run as an Ubuntu daemon

On Ubuntu 22.04 or newer, create a dedicated `systemd` service so LogAgent can
be managed with `systemctl`.

1. From the project directory, configure `logagent.json`, then install the
   application files under `/opt/logagent`:

	```bash
	sudo mkdir -p /opt/logagent
	sudo cp logagent.py logreader.py logagent.json /opt/logagent/
	```

2. Create a service account and grant it access to standard system logs:

	```bash
	sudo useradd --system --no-create-home --shell /usr/sbin/nologin logagent
	sudo usermod --append --groups adm logagent
	sudo chown -R root:root /opt/logagent
	```

	If the paths in `logagent.json` are not readable by the `adm` group, update
	the file permissions or group ownership so the `logagent` user can read them.

3. Create `/etc/systemd/system/logagent.service` with the following contents:

	```ini
	[Unit]
	Description=LogAgent log reader
	After=network.target

	[Service]
	Type=simple
	User=logagent
	Group=logagent
	WorkingDirectory=/opt/logagent
	ExecStart=/usr/bin/python3 /opt/logagent/logagent.py
	Restart=on-failure

	[Install]
	WantedBy=multi-user.target
	```

4. Reload `systemd`, enable the service at boot, and start it:

	```bash
	sudo systemctl daemon-reload
	sudo systemctl enable --now logagent.service
	sudo systemctl status logagent.service
	```

5. Use the standard `systemctl` commands to control the daemon:

	```bash
	sudo systemctl start logagent.service
	sudo systemctl stop logagent.service
	sudo systemctl restart logagent.service
	sudo systemctl disable logagent.service
	```

	View service output with:

	```bash
	sudo journalctl --unit logagent.service --follow
	```

## Usage

LogAgent provides two HTTP GET endpoints.

### List available logs

Request `/` to return the hostname, port, and configured log names:

```bash
curl -l http://localhost:8010/
```

```json
{
	"hostname": "popos-desktop",
	"port": 8010,
	"build_version": "1.4.0",
	"logs": [
		"nordvpn",
		"killswitch"
	]
}
```

### Read a log

Request `/<log-name>` to return the contents of a configured log:

```bash
curl -l http://localhost:8010/killswitch
```

```text
2024-02-09T10:32 Started executing script tasks.
2024-02-09T10:32 There is no vpn tunnel established to secure (iface tun0).
```

Add the optional `search` parameter to return only lines containing the
specified string. The search is case-insensitive and URL-encoded by `curl`:

```bash
curl -G --data-urlencode 'search=vpn tunnel' http://localhost:8010/killswitch/
```

If no lines match, the response is:

```text
No matches found in log.
```
