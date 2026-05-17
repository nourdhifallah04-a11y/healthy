/**************************************************
 * 1. INPUT
 **************************************************/
const profil = $json.profil_analyse ?? {};

const platsDB =
  $('Pré‑Filtrage Nutritionnel1').item.json["plats_filtrés"] ?? [];
const menusDB =
  $('Pré‑Filtrage Nutritionnel1').item.json["menus_filtrés"] ?? [];

const consent =  $('Pré‑Filtrage Nutritionnel1').item.json["consentements"];
const prescription = $json.prescription ?? null;

/**************************************************
 * 2. MODE & CONTEXTE
 **************************************************/
function detectMode(p) {
  const imc = p.imc ?? 0;
  if (imc >= 40) return "cut_clinique";
  if (imc >= 35) return "cut";
  if (imc >= 27) return "recomp";
  if (imc >= 22) return "maintenance";
  return "bulk";
}

const mode = detectMode(profil);
const lifestyle = profil.lifestyle ?? "sedentaire";
const pathology = profil.pathologie ?? "none";
const abVariant = profil.ab_variant ?? "A";
const clinicalObesity = profil.imc >= 40;

/**************************************************
 * 3. RGPD – BLOQUANT
 **************************************************/
if (!consent.donnees_sante_sensibles) {
  return { json: { error: "Consentement santé requis" } };
}

/**************************************************
 * 4. CONFIGURATION
 **************************************************/
const modifiers = {
  sedentaire: { protein: 1, fibre: 1, calorie: 1 },
  sportif: { protein: 1.15, fibre: 1.1, calorie: 1.1 }
};

const thresholdsBase = {
  A: { protein: 0.7, fibre: 0.5 },
  B: { protein: 0.8, fibre: 0.65 }
};

const mod = modifiers[lifestyle];
let thresholds = thresholdsBase[abVariant];

/**************************************************
 * 5. UTILITAIRES
 **************************************************/
const clamp = v => Math.max(0, Math.min(100, v));
const ratio = (v, c) => (c ? v / c : 0);

function aggregateNutrition(list) {
  return list.reduce(
    (a, p) => ({
      calorie: a.calorie + (p.calorie ?? 0),
      proteine: a.proteine + (p.proteine ?? 0),
      glucides: a.glucides + (p.glucides ?? 0),
      lipides: a.lipides + (p.lipides ?? 0),
      fibres: a.fibres + (p.fibres ?? 0),
      sodium: a.sodium + (p.sodium ?? 0)
    }),
    { calorie: 0, proteine: 0, glucides: 0, lipides: 0, fibres: 0, sodium: 0 }
  );
}

/**************************************************
 * 6. PATHOLOGIES
 **************************************************/
function pathologyCheck(n) {
  const alerts = [];

  if (pathology === "diabete") {
    if (n.glucides > 120)
      alerts.push({ code: "GLUC_HIGH", severity: "high" });
    if (n.fibres < 30)
      alerts.push({ code: "FIB_LOW", severity: "medium" });
  }

  if (pathology === "hta") {
    if (n.sodium > 1800)
      alerts.push({ code: "SODIUM_HIGH", severity: "high" });
  }

  return alerts;
}

/**************************************************
 * 7. PENALITES
 **************************************************/
const penalties = {
  GLUC_HIGH: 25,
  FIB_LOW: 15,
  SODIUM_HIGH: 30
};

function applyPenalties(score, alerts) {
  let s = score;
  alerts.forEach(a => (s -= penalties[a.code] ?? 0));
  return clamp(s);
}

/**************************************************
 * 8. SCORING PLAT
 **************************************************/
function scorePlat(p) {
  const calorieRatio = ratio(p.calorie, (profil.calories_cibles / 3) * mod.calorie);
  const proteinRatio = ratio(p.proteine, (profil.proteine_cibles / 3) * mod.protein);
  const fibreRatio = ratio(p.fibres, (profil.fibres_cibles / 3) * mod.fibre);

  let base =
    (
      Math.min(calorieRatio, 1) * 1.3 +
      Math.min(proteinRatio, 1) * 2.8 +
      Math.min(fibreRatio, 1) * 1.9
    ) / 6 * 100;

  const alerts = pathologyCheck(p);
  const finalScore = applyPenalties(base, alerts);

  return {
    score: Math.round(finalScore),
    badge:
      finalScore >= 80 ? "💪" :
      finalScore >= 65 ? "✅" :
      "⚠️",
    interpretation:
      finalScore >= 80
        ? "Très bon plat adapté à votre objectif"
        : finalScore >= 65
        ? "Plat correct mais améliorable"
        : "Plat peu adapté",
    alerts
  };
}

/**************************************************
 * 9. SCORING MENU
 **************************************************/
function scoreMenu(n) {
  const calorieTolerance = clinicalObesity ? 0.9 : 1;

  const calorieRatio = ratio(n.calorie, profil.calories_cibles * calorieTolerance);
  const proteinRatio = ratio(n.proteine, profil.proteine_cibles * mod.protein);
  const fibreRatio = ratio(n.fibres, profil.fibres_cibles * mod.fibre);

  let base =
    (
      Math.min(calorieRatio, 1) * 1.2 +
      Math.min(proteinRatio, 1) * 3 +
      Math.min(fibreRatio, 1) * 2
    ) / 6.2 * 100;

  const alerts = pathologyCheck(n);
  const finalScore = applyPenalties(base, alerts);

  return {
    score: Math.round(finalScore),
    badge:
      finalScore >= 80 ? "✅" :
      finalScore >= 65 ? "⚠️" :
      "❌",
    interpretation:
      finalScore >= 80
        ? "Menu très bien équilibré"
        : finalScore >= 65
        ? "Menu correct mais perfectible"
        : "Menu peu adapté",
    alerts
  };
}

/**************************************************
 * 10. CALCUL PLATS & TOP PLATS ✅
 **************************************************/
const platsScored = platsDB.map(p => ({
  ...p,
  ...scorePlat(p)
}));

const topPlats = platsScored
  .sort((a, b) => b.score - a.score)
  .slice(0, 12);

/**************************************************
 * 11. CALCUL MENUS
 **************************************************/
const platsById = Object.fromEntries(platsScored.map(p => [p.id, p]));

const menusScored = menusDB.map(m => {
  const ids = m.plats.split(',').map(x => parseInt(x.trim(), 10));
  const plats = ids.map(id => platsById[id]).filter(Boolean);
  const nutrition = aggregateNutrition(plats);

  return {
    menu_id: m.id,
    nom: m.nom,
    description: m.description,
    plats_ids: ids,
    nutrition,
    ...scoreMenu(nutrition)
  };
});

const topMenus = menusScored
  .sort((a, b) => b.score - a.score)
  .slice(0, 6);

/**************************************************
 * 12. SORTIE FINALE N8N
 **************************************************/
return {
  json: {
    mode,
    clinical_obesity: clinicalObesity,
    top_plats: topPlats,
    top_menus: topMenus,
    analytics: {
      avg_plat_score: Math.round(
        platsScored.reduce((a, p) => a + p.score, 0) / platsScored.length
      ),
      avg_menu_score: Math.round(
        menusScored.reduce((a, m) => a + m.score, 0) / menusScored.length
      )
    }
  }
};