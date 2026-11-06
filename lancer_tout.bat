@echo off
chcp 65001 >nul
set PYTHONUTF8=1
echo Lancement du pipeline, sorties dans sorties.txt ...
(
python etape1_collecte.py && python etape2_nettoyage.py && python etape3_decoupage.py && python etape4_indexation.py && python etape5_recherche.py && python etape6_generation.py && python etape7_evaluation.py recherche && python etape7_evaluation.py generer
) > sorties.txt 2>&1
echo Termine. Ouvre sorties.txt puis remplis resultats.csv a la main.
pause
