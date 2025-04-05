# 🤖 Crypto Smart Bot — USDC v2 (filtrage + 10 USDC)

## ✅ Fonctionnalités :
- Trading en USDC
- Budget par trade : 10 USDC
- Filtres :
  - Ignore les marchés fermés
  - Ignore les paires dont le minimum d'achat est trop élevé
- Achat si +5%, vente si +10% ou -5%
- Cooldown 10 minutes
- Variable `BOT_ACTIVE` pour pause rapide

## 🌐 Variables à ajouter sur Railway :
- BINANCE_API_KEY
- BINANCE_SECRET_KEY
- BOT_ACTIVE = true / false
