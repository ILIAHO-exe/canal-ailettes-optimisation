# Canal avec Ailettes - Optimisation

Étude paramétrique d'optimisation d'un échangeur de chaleur compact avec ailettes rectangulaires en régime laminaire.

## 📊 Contexte Scientifique

Cette étude s'inscrit dans la tradition de recherche établie par la thèse de **Frédéric Michel (CEA GRETh, 2003)** sur l'optimisation d'échangeurs thermiques compacts.

**Objectif** : Déterminer la géométrie optimale (hauteur et espacement des ailettes) qui maximise le critère de performance **PEC** (Performance Evaluation Criteria).

## 🎯 Paramètres de l'Étude

### Matrice Paramétrique
- **Hauteur ailettes (h_fin)** : 2, 4, 6, 8 mm (4 valeurs)
- **Espacement ailettes (s_fin)** : 2, 4, 6, 8, 10 mm (5 valeurs)
- **Total** : 20 cas paramétriques + 1 cas référence = **21 configurations**

### Géométrie Fixe
| Paramètre | Valeur |
|-----------|--------|
| Hauteur canal (H_ch) | 10 mm |
| Longueur canal (L_ch) | 100 mm |
| Épaisseur ailette (e_fin) | 1 mm |

## 🌡️ Conditions Physiques

### Propriétés du Fluide (Air à 300 K)
| Propriété | Symbole | Valeur | Unité |
|-----------|---------|--------|-------|
| Densité | ρ | 1.2 | kg/m³ |
| Viscosité dynamique | μ | 1.86×10⁻⁵ | Pa·s |
| Conductivité thermique | k | 0.0262 | W/(m·K) |
| Capacité thermique | cp | 1005 | J/(kg·K) |
| Nombre de Prandtl | Pr | 0.707 | - |

### Conditions de Simulation
| Condition | Valeur | Justification |
|-----------|--------|---------------|
| Régime | Laminaire | Re ≈ 645 < 2300 |
| Température entrée | 300 K | Ambiante (~27°C) |
| Température paroi | 330 K | Chauffée (~57°C) |
| Vitesse entrée | 0.5 m/s | Laminaire assuré |
| Temps simulation | 10 s | État stationnaire |

**Reynolds** : Re = ρVD_h/μ ≈ 645 → Régime laminaire confirmé

## 📐 Critère de Performance (PEC)

```
PEC = (Nu/Nu₀) / (f/f₀)^(1/3)
```

Où :
- **Nu** = Nombre de Nusselt (transfert thermique)
- **f** = Facteur de friction Darcy (perte de charge)
- **Indice 0** = Valeurs de référence (sans ailettes)

**Interprétation** :
- PEC > 1 : Amélioration globale vs cas sans ailettes
- PEC = 1.5 : +50% d'efficacité globale
- **Objectif** : Maximiser PEC

## 🏗️ Structure du Projet

```
canal-ailettes-optimisation/
├── README.md                          # Ce fichier
├── .gitignore                         # Fichiers à ignorer
├── config/
│   └── simulation_params.yaml         # Paramètres partagés
├── scripts/
│   ├── generate_cases.py              # Crée 21 cas
│   ├── generate_blockMeshDict.py      # Génère maillages paramétrés
│   ├── run_simulations.sh             # Lance les simulations
│   ├── extract_results.py             # Extrait Nu, f, ΔP
│   └── analyze_optimization.py        # Analyse et graphiques
├── template_constant/                 # Fichiers de configuration constants
│   ├── transportProperties
│   ├── thermophysicalProperties
│   └── g
├── template_system/                   # Fichiers système constants
│   ├── controlDict
│   ├── fvSchemes
│   ├── fvSolution
│   └── decomposeParDict
└── cases/                             # Répertoire des simulations
    ├── 00_Reference_NoFins/           # Cas référence (pas d'ailettes)
    ├── 01_h2_s2/
    ├── 02_h2_s4/
    ├── ...
    └── 20_h8_s10/                     # Dernier cas
```

## 🚀 Instructions d'Utilisation

### 1. Cloner le repository
```bash
git clone git@github.com:ILIAHO-exe/canal-ailettes-optimisation.git
cd canal-ailettes-optimisation
```

### 2. Générer les 21 cas
```bash
python3 scripts/generate_cases.py
```

### 3. Générer les maillages paramétrés
```bash
python3 scripts/generate_blockMeshDict.py
```

### 4. Lancer les simulations
```bash
chmod +x scripts/run_simulations.sh
./scripts/run_simulations.sh
```

### 5. Extraire les résultats
```bash
python3 scripts/extract_results.py
python3 scripts/analyze_optimization.py
```

## 📊 Résultats Attendus

Les scripts génèrent :
- `results_summary.csv` : Résumé des 21 cas
- `Nu_values.csv` : Nombres de Nusselt
- `f_values.csv` : Facteurs de friction
- `PEC_values.csv` : Critères de performance
- Graphiques PNG :
  - Heatmap PEC (h_fin vs s_fin)
  - Sensibilité Nu vs géométrie
  - Sensibilité ΔP vs géométrie
  - Courbes d'optimisation

## 🔧 Solveur Utilisé

**buoyantBoussinesqPimpleFoam** (OpenFOAM)

Résout simultanément :
- Continuité (incompressible)
- Momentum (Navier-Stokes)
- Énergie (convection-diffusion)

Approximation de Boussinesq adaptée pour ΔT modéré (30 K).

## 📚 Références Scientifiques

1. **Michel, F.** (2003). "Numerical simulations and experimental investigations of an offset strip fin compact heat exchanger." *Thèse, CEA GRETh.*

2. **OpenFOAM Documentation** : https://www.openfoam.com/documentation/

## 👤 Auteur

**Elhanily** - Stage M1 CORIA - Rouen Normandie

## 📝 Licence

MIT License

---

**Status** : 🔄 En cours de développement

**Dernière mise à jour** : 19 mai 2026
