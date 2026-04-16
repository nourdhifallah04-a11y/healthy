#!/bin/bash
# 🚀 Script de Démarrage Rapide - Navbar Améliorée
# Fresh & Green - Bootstrap 5 Enhancement

echo "🌿 ============================================== 🌿"
echo "   NAVBAR AMÉLIORÉE - DÉMARRAGE RAPIDE"
echo "🌿 ============================================== 🌿"
echo ""

# Vérification de l'installation
echo "📋 Vérification de l'installation..."
python verify_navbar.py 2>&1 | head -20
echo ""

# Demander à l'utilisateur
echo "Que voulez-vous faire?"
echo ""
echo "1) Démarrer l'application (python manage.py runserver)"
echo "2) Consulter la documentation (NAVBAR_GUIDE.html)"
echo "3) Vérifier complètement l'installation"
echo "4) Quitter"
echo ""
read -p "Sélectionnez une option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Démarrage de l'application..."
        echo "Ouvrez: http://localhost:8000"
        echo ""
        python manage.py runserver
        ;;
    2)
        echo ""
        echo "📖 Ouverture du guide..."
        if command -v open &> /dev/null; then
            open NAVBAR_GUIDE.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open NAVBAR_GUIDE.html
        elif command -v start &> /dev/null; then
            start NAVBAR_GUIDE.html
        else
            echo "Fichier: NAVBAR_GUIDE.html"
            echo "Veuillez l'ouvrir manuellement dans votre navigateur"
        fi
        ;;
    3)
        echo ""
        echo "🔍 Vérification complète..."
        python verify_navbar.py
        ;;
    4)
        echo "Au revoir! 🌿"
        exit 0
        ;;
    *)
        echo "Option invalide!"
        exit 1
        ;;
esac
