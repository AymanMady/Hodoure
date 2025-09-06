# hodoure
School Management System - Notifications

root : Ayman.22420813
github-token : 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

apt update && apt install -y docker.io
systemctl start docker
systemctl enable docker

apt install -y docker-compose


docker-compose up -d --build

 docker restart hodoure_odoo

nginx config file : /etc/nginx/nginx.conf
 /etc/nginx/sites-enabled/odoo

rechargement de nginx : 
sudo nginx -t && sudo systemctl reload nginx

verification de la date de validation du certificat let's encrypted https : 
sudo openssl x509 -in /etc/letsencrypt/live/team404.tech/fullchain.pem -noout -dates

s'il est expirer on peux le renouveller avec : 
sudo certbot --nginx -d team404.tech --force-renewal

sudo certbot --nginx -d team404.tech -d www.team404.tech

Vérifie si ton VPS écoute sur le port 443
sudo ss -tuln | grep 443

Vérifie si ton certificat SSL est bien généré
sudo certbot certificates

