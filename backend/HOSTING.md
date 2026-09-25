# Hosting the Backend on Ubuntu Without Docker

This guide runs the FastAPI backend with SQLite and `systemd` for testing.

## 1. Create the application directory

```bash
sudo mkdir -p /opt/quo-aluminum/backend/data
sudo chown -R $USER:$USER /opt/quo-aluminum
```

Copy the local `backend` folder into:

```text
/opt/quo-aluminum/backend
```

## 2. Install Python

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

## 3. Create the virtual environment

```bash
cd /opt/quo-aluminum/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure SQLite

Create or edit `/opt/quo-aluminum/backend/.env`:

```env
SECRET_KEY=use-a-long-random-secret-key
DB_URI=sqlite:////opt/quo-aluminum/backend/data/aluminium_quotation.db

COMPANY_NAME="Quo Aluminum"
COMPANY_ADDRESS="123 Aluminum Street, City"
COMPANY_PHONE="+1 234 567 890"
COMPANY_WEBSITE="https://your-frontend-domain.com"
COMPANY_LOGO_URL="https://your-frontend-domain.com/logo.png"

ORIGIN=https://your-frontend-domain.com,http://your-frontend-domain.com
```

The four slashes in the SQLite URL are intentional. They specify an absolute Linux path.

## 5. Create the database and seed users

```bash
cd /opt/quo-aluminum/backend
source .venv/bin/activate
python -c "from database.connection import DatabaseManager; DatabaseManager.create_db_and_tables()"
python seed.py
```

The seed script creates these initial users:

```text
admin / admin123
worker / worker123
```

Change these passwords after logging in.

## 6. Test the backend manually

```bash
cd /opt/quo-aluminum/backend
source .venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test these URLs from a browser:

```text
http://YOUR_SERVER_IP:8000/
http://YOUR_SERVER_IP:8000/docs
```

Stop the test server with `Ctrl+C`.

## 7. Run the backend with systemd

Create the service file:

```bash
sudo nano /etc/systemd/system/quo-aluminum.service
```

Add the following content. Replace `ubuntu` with the Ubuntu username that owns the application files:

```ini
[Unit]
Description=Quo Aluminum FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/quo-aluminum/backend
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/quo-aluminum/backend/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable quo-aluminum
sudo systemctl start quo-aluminum
sudo systemctl status quo-aluminum
```

View backend logs:

```bash
sudo journalctl -u quo-aluminum -f
```

## 8. Open the testing port

```bash
sudo ufw allow 8000/tcp
sudo ufw enable
```

If the server provider has a separate cloud firewall, allow TCP port `8000` there as well.

## 9. Connect the separate frontend

On the frontend server, set the API URL before building:

```env
VITE_API_BASE_URL=http://YOUR_BACKEND_SERVER_IP:8000
```

Then rebuild and redeploy the frontend:

```bash
npm run build
```

The SQLite database is stored at:

```text
/opt/quo-aluminum/backend/data/aluminium_quotation.db
```

Back up this file regularly. This direct port setup is suitable for testing. For production, use Nginx and HTTPS in front of Uvicorn.
