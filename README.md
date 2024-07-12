# Onyx Bot

Onyx Bot est un bot Discord conçu pour aider les utilisateurs à gérer et analyser leurs rêves, avec un focus particulier sur les rêves lucides.

## Fonctionnalités

- **Journal de Rêves**: Ajoutez, listez, visualisez et supprimez vos rêves.
- **Statistiques de Rêves**: Obtenez des statistiques détaillées sur vos rêves et ceux de la communauté.
- **Calendrier des Rêves**: Visualisez vos rêves sur un calendrier mensuel.
- **Profil Onirique**: Gérez votre profil de rêveur, incluant le nombre de rêves lucides.
- **Alarme WBTB**: Programmez des alarmes pour la technique Wake Back To Bed.
- **Statistiques d'Activité**: Suivez votre activité sur le serveur.
- **Système d'Idées**: Soumettez et consultez des idées pour améliorer le bot.

## Commandes Principales

- `o!interactivedream`: Interface interactive pour gérer vos rêves.
- `o!dreamcalendar`: Affiche un calendrier de vos rêves.
- `o!dstats [@membre]`: Affiche les statistiques de rêves d'un utilisateur.
- `o!gstats`: Affiche les statistiques globales des rêves sur le serveur.
- `o!profile [@membre]`: Affiche le profil onirique d'un utilisateur.
- `o!wbtb <heure>`: Programme une alarme WBTB.
- `o!mystats`: Affiche vos statistiques d'activité sur le serveur.
- `o!submitidea <idée>`: Soumet une idée pour améliorer le bot.

## Structure du Projet

```
onyx-bot/
│
├── bot.py
├── config.py
├── requirements.txt
│
├── cogs/
│   ├── dreamjournal.py
│   ├── profile.py
│   ├── statistics.py
│   ├── utilities.py
│   ├── admin.py
│   ├── fun.py
│   └── help.py
│
├── utils/
│   ├── json_manager.py
│   └── time_utils.py
│
└── data/
    ├── dreams.json
    ├── user_data.json
    └── stats.json
```

## Installation

1. Clonez ce repository
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez votre token Discord dans un fichier `.env`
4. Lancez le bot : `python bot.py`

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

This project is licensed under the MIT License.

```