# Récupération des images des sites utilisant yoolib

* installer les requirements python : `pip3 install -r requirements.txt`

## Récupération des vignettes

* paramètrer le récupérateur de vignettes:
    * URL: la première URL des résultats à récupérer
    * DATA_DIR: le dossier vers lequel sont télécharger les vignettes
    * WIDTH et HEIGHT: les tailles des vignettes en pixel sur le disque
    * TRANSLATE_TABLE: table de traduction des méta données de l'image
    
* lancer le programme: `scrapy runspider thumbnails_spider.py`

## Affichage des méta données de l'image

Les différentes informations relatives à l'image sont stockées dans les méta données dans la colonne UserComment.
Vous pouvez les afficher de la façon suivante avec ImageMagick:

```bash
identify -verbose /home/jean-baptiste/mht_files/Yacht\ auxiliaire\ \[de\ 10\,5\ mètres\]..jpeg | grep "exif:"
```

## Téléchargement de l'image en haute définition

* l'url de l'image est stockée dans le champs scrapper_url
* renseigner les urls à télécharger dans le récupérateur d'image HD (paramètre tableaux URLS)
* lancer le programme de récupération d'images hautes définitions: `scrapy runspider picture_spider.py`
