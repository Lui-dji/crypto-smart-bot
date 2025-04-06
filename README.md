# 🤖 SmartBot++ (USDC)

## ✅ Fonctionnalités :
- Multi-positions simultanées (budget dynamique)
- Détection intelligente des tendances
- Recyclage automatique des résidus invendables (optionnel)
- Variables simples à modifier
- Optimisé pour railway (1 clic de déploiement)

## ⚙️ Variables à définir dans Railway :
- `BINANCE_API_KEY`
- `BINANCE_SECRET_KEY`
- `BUDGET_TOTAL` (ex : 150)
- `POSITION_BUDGET` (ex : 10)
- `MAX_POSITIONS` (auto = budget_total // position_budget)
- `RECYCLE_DUST` = true / false
- `RISK_LEVEL` = low / medium / high (non utilisé encore)

## 💻 Start command :
python main.py
