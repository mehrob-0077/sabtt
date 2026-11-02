# Ҷойгиркунӣ дар сервери Ubuntu

Ин дастур барои VPS бо Ubuntu, Python, PostgreSQL, Gunicorn ва Nginx аст. Фармонҳо дар сервер иҷро мешаванд.

## 1. Код ва муҳит

Лоиҳаро ба `/opt/sabt` нусха кунед. Баъд:

```bash
cd /opt/sabt
sudo apt update
sudo apt install -y python3-venv python3-pip libpq-dev postgresql nginx
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 2. PostgreSQL ва танзимот

Дар PostgreSQL барои барнома база ва корбар созед, баъд танзимоти `.env.example`-ро бо қиматҳои худ ба `/etc/sabt.env` гузоред. Қиматҳои воқеии махфиро ба Git ворид накунед. Файли env бояд танҳо барои root ва корбари хидмат дастрас бошад.

```bash
sudo install -m 640 -o root -g www-data .env.example /etc/sabt.env
sudo nano /etc/sabt.env
```

`SECRET_KEY`, пароли база, суроғаҳои домен ва SMTP-ро ҳатман иваз кунед. Барои корбари Gmail аз App Password-и нав истифода кунед.

## 3. Омодасозии Django

```bash
cd /opt/sabt
. .venv/bin/activate
set -a
. /etc/sabt.env
set +a
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check --deploy
```

Агар `check --deploy` огоҳӣ нишон диҳад, пеш аз кушодани сайт танзимоти дахлдорро ҳал кунед.

## 4. Gunicorn бо systemd

Файли `/etc/systemd/system/sabt.service` созед:

```ini
[Unit]
Description=Sabt Django application
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/sabt
EnvironmentFile=/etc/sabt.env
ExecStart=/opt/sabt/.venv/bin/gunicorn server.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=on-failure
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /opt/sabt
sudo systemctl daemon-reload
sudo systemctl enable --now sabt
sudo systemctl status sabt
```

## 5. Nginx ва HTTPS

Барои домени худ дар Nginx `server_name` гузошта, `/static/`-ро ба `/opt/sabt/staticfiles/`, `/media/`-ро ба `/opt/sabt/media/`, ва дигар дархостҳоро ба `http://127.0.0.1:8000` равона кунед. Ба proxy header-ҳои `Host`, `X-Forwarded-For` ва `X-Forwarded-Proto` фиристед. Баъд сертификати HTTPS гиред ва `SECURE_SSL_REDIRECT=True`-ро фаъол нигоҳ доред. Барои upload-ҳо директорияи `media/` бояд барои `www-data` навишташаванда ва дар backup бошад.

Файлҳои `.env`, база, upload-ҳо ва `staticfiles/`-ро ба Git commit накунед. SQLite барои санҷиши маҳаллӣ мемонад; дар сервер аз PostgreSQL истифода кунед. Backup-и база ва `media/`-ро мунтазам гиред.

Навсозии код:

```bash
cd /opt/sabt
sudo -u www-data .venv/bin/python manage.py migrate
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart sabt
```

## Render: нигоҳдории тасвир ва фиристодани email

Дар нақшаи ройгони Render файлҳои маҳаллӣ нигоҳ дошта намешаванд ва SMTP дар портҳои маъмул баста аст. Барои истифодаи тасвирҳо ва тасдиқи почта ин хидматҳои ройгонро пайваст кардан мумкин аст:

1. Дар Cloudinary ҳисоби ройгон кушоед. Аз Dashboard қимати `CLOUDINARY_URL`-ро гирифта, дар Render → Web Service → Environment ҳамчун тағйирёбанда илова кунед. Танзимоти лоиҳа пас аз ин тасвирҳои нави `ImageField`-ро ба Cloudinary мефиристад. Ҳадди ройгони Cloudinary бо кредитҳои истифода ҳисоб мешавад; истифодаи онро дар панели онҳо назорат кунед.
2. Дар Resend ҳисоби ройгон кушоед ва API key созед. Дар Render тағйирёбандаи `RESEND_API_KEY` илова кунед. Қимати `DEFAULT_FROM_EMAIL` бояд аз домени тасдиқшудаи Resend бошад. Барои тасдиқи домен сабтҳои DNS-и нишон додаи Resend-ро дар панели домен ворид кунед.
3. Пас аз иловаи ҳар ду тағйирёбанда, Render-ро redeploy кунед.

Дар `.env.example` шакли ин тағйирёбандаҳо ҳаст. `CLOUDINARY_URL` ва `RESEND_API_KEY`-ро ба GitHub нафиристед. Тасвирҳои кӯҳнаи `media/` худкор ба Cloudinary намегузаранд; ин пайвастшавӣ upload-ҳои навро нигоҳ медорад. Render Postgres-и ройгон маҳдудияти муҳлат дорад, бинобар ин маълумоти воқеиро пеш аз муҳлати база содир (export) ва нусхаи эҳтиётӣ гиред.
