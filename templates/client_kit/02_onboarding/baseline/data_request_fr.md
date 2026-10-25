# Données à nous transmettre – {{PROPERTY_NAME}}

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

Si nous avons accès au channel manager ou au PMS, nous extrayons ces fichiers nous-mêmes. Sinon, merci de les exporter en **CSV ou Excel** (pas en PDF si possible).

| # | Fichier | Période | Colonnes souhaitées |
|---|---|---|---|
| 1 | Liste des réservations (y compris annulées) | 12 à 24 derniers mois + toutes les réservations futures | n° réservation, date de réservation, date d'arrivée, date de départ, chambre/type, canal, statut (confirmée/annulée), date d'annulation, montant total, commission, nombre de personnes |
| 2 | Grille tarifaire actuelle | 12 prochains mois | type de chambre, période, prix, plan tarifaire (remboursable / non remboursable / petit-déjeuner), séjour minimum, restrictions |
| 3 | Promotions actives par OTA | actuelles | canal, nom, remise, dates de séjour, dates de réservation |
| 4 | Conditions de vente | actuelles | annulation, acompte, enfants, taxe de séjour |
| 5 | Factures ou relevés de commission OTA | 3 derniers mois | canal, mois, montant |
| 6 | Périodes de fermeture ou travaux prévus | 12 prochains mois | dates, chambres concernées |
| 7 | Liste des concurrents déjà suivis | si elle existe | nom, lien |
| 8 | Ventes hors chambres (day pass, événements, restaurant) | 12 derniers mois | date, produit, nombre, montant |

Aucune donnée personnelle client (nom, email, téléphone) n'est nécessaire : vous pouvez supprimer ces colonnes avant l'envoi.

---
*Internal:* save each file unchanged in `03_source_data/<system>/` as `YYYY-MM-DD_<source>_<content>_<period>.csv` and add a line to `03_source_data/exports_log.csv`.
