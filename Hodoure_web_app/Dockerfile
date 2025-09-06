FROM odoo:17.0

USER root

# Met à jour pip à une version moderne
RUN pip3 install --upgrade pip

# Copie le fichier de dépendances
COPY requirements.txt /tmp/requirements.txt

# Installe les dépendances globalement
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
