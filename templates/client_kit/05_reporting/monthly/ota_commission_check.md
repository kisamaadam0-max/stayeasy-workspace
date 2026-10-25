# Contrôle des commissions OTA – {{PROPERTY_NAME}} – {{MONTH}}

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

Vérifie chaque mois que ce que l'OTA facture correspond aux séjours réellement consommés. C'est la base du revenu net et de l'ADR net du rapport mensuel.

| OTA | Séjours consommés (channel manager) | Nuitées | Revenu brut | Commission facturée (facture OTA) | Taux effectif | Taux du contrat | Annulations / no-shows facturés | Écart | Explication |
|---|---|---|---|---|---|---|---|---|---|
| Booking.com | | | | | | | | | |
| Airbnb | | | | | | | | | |
| Expedia | | | | | | | | | |
| Autre | | | | | | | | | |

Sources : export réservations du ____ (`03_source_data/channel_manager/`), factures OTA du ____ (`03_source_data/ota/`).

Règles :
- Taux effectif = commission facturée ÷ revenu brut des séjours consommés, calculé en Python.
- Le taux du contrat vient du contrat ou de l'extranet, jamais d'une moyenne du marché.
- Un écart entre taux effectif et taux du contrat est signalé au propriétaire avec la ligne de facture concernée. StayEasy ne conteste rien auprès de l'OTA sans son accord.
