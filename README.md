# automate-ig-reel-dm

Automating instagram is easier with instagrapi.

## Prequisite

In Amazon EC2 Linux Instance,

```sh
pip install Pillow
pip install instagrapi
```

To use runtime IG credentials on EC2 instance:

- Configure your IG credentials on AWS Secrets Manager.
- Associate the secret with a policy.
- Create a role and attach the policy.
- Assign the role to your EC2 instance.

## Configure systemd timer in EC2

AWS is [deprecating](https://docs.aws.amazon.com/linux/al2023/ug/deprecated-al2023.html) cron jobs and transitioning to systemd timers.

Create a service:

```sh
vim /etc/systemd/system/mycronjob.service
```

```sh
[Unit]
Description=Execute automate.py

[Service]
ExecStart=/usr/bin/python3 /home/ec2-user/your-proj/automate.py
```

Create a timer:

```sh
vim /etc/systemd/system/mycronjob.timer
```

```sh
[Unit]
Description=send reel to your selected person at the assigned time

[Timer]
OnCalendar=*-*-* 00:00:00 Australia/Melbourne
Persistent=true

[Install]
WantedBy=multi-user.target
```

Restart timer and service:

```sh
sudo systemctl daemon-reload
sudo systemctl restart mycronjob.timer
```

List timer:

```sh
sudo systemctl list-timers --all
```

Logging:

```sh
journalctl -u mycronjob.service
```
