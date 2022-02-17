sudo apt-get remove -y certbot
sudo apt-get install -y python3-venv
sudo rm -rf /usr/local/bin/certbot
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -sf /opt/certbot/bin/certbot /usr/bin/certbot
sudo /usr/bin/certbot --version
sudo /opt/certbot/bin/pip list
