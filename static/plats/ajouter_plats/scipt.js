/**********************************
 * 1. DONNÉES D'ENTRÉE
 **********************************/

const profil = $json.profil_analyse ?? {};

const platsDB =
  $('Pré‑Filtrage Nutritionnel1').item.json["plats_filtrés"] ?? [];
const menus =
  $('Pré‑Filtrage Nutritionnel1').item.json["menus_filtrés"] ?? [];


/**********************************
 * 2. MODE AUTOMATIQUE SELON IMC
 **********************************/

function detectMode(profil) {
  const imc = profil.imc ?? 0;
  if (imc >= 35) return 'cut';
  if (imc >= 27) return 'recomp';
  if (imc >= 22) return 'maintenance';
  return 'bulk';
}

const mode = detectMode(profil);


/**********************************
 * 3. UTILITAIRES
 **********************************/

function ratio(val, cible) {
  if (!cible || cible === 0) return 0;
  return val / cible;
}

function clamp(v) {
  return Math.max(0, Math.min(100, v));
}

function parseIds(str) {
  return str
    ? str.split(',').map(x => parseInt(x.trim(), 10)).filter(Boolean)
    : [];
}

function aggregateNutrition(plats) {
  return plats.reduce(
    (acc, p) => ({
      proteine: acc.proteine + (p.proteine ?? 0),
      glucides: acc.glucides + (p.glucides ?? 0),
      lipides: acc.lipides + (p.lipides ?? 0),
      fibres: acc.fibres + (p.fibres ?? 0),
      calorie: acc.calorie + (p.calorie ?? 0)
    }),
    { proteine: 0, glucides: 0, lipides: 0, fibres: 0, calorie: 0 }
  );
}


/**********************************
 * 4. PROFIL PAR REPAS
 **********************************/

const repasParJour = 3;

const profilParRepas = {
  calories_cibles: (profil.calories_cibles ?? 0) / repasParJour,
  proteine_cibles: (profil.proteine_cibles ?? 0) / repasParJour,
  glucides_cibles: (profil.glucides_cibles ?? 0) / repasParJour,
  lipides_cibles: (profil.lipides_cibles ?? 0) / repasParJour,
  fibres_cibles: (profil.fibres_cibles ?? 0) / repasParJour
};


/**********************************
 * 5. INTERPRÉTATION AMÉLIORÉE – PLATS
 **********************************/

function platInterpretation({ calorieRatio, proteinRatio, fibreRatio, mode }) {
  const positives = [];
  const negatives = [];

  // Calories
  if (mode === 'cut') {
    if (calorieRatio < 0.25) negatives.push("plat trop léger, peu rassasiant");
    else if (calorieRatio <= 0.6) positives.push("calories bien maîtrisées");
    else negatives.push("trop calorique pour la perte de poids");
  }

  if (mode === 'bulk') {
    if (calorieRatio < 0.4) negatives.push("apport calorique insuffisant");
    else if (calorieRatio <= 1.1) positives.push("bon apport énergétique");
    else negatives.push("trop calorique, risque de prise de gras");
  }

  if (mode === 'recomp') {
    if (calorieRatio <= 0.7) positives.push("calories adaptées à la recomposition");
    else negatives.push("trop calorique pour une recomposition");
  }

  // Protéines
  if (proteinRatio >= 0.6)
    positives.push("bon apport en protéines");
  else
    negatives.push("apport en protéines insuffisant");

  // Fibres
  if (fibreRatio >= 0.5)
    positives.push("riche en fibres, favorise la satiété");
  else
    negatives.push("fibres insuffisantes");

  let conclusion = "Plat correct";
  if (positives.length >= 3 && negatives.length === 0)
    conclusion = "Excellent choix nutritionnel";
  if (negatives.length >= 2)
    conclusion = "Plat peu adapté à votre objectif";

  return {
    conclusion,
    points_positifs: positives,
    points_a_ameliorer: negatives
  };
}


/**********************************
 * 6. INTERPRÉTATION AMÉLIORÉE – MENUS
 **********************************/

function menuInterpretation({ calorieRatio, proteinRatio, fibreRatio, mode }) {
  const positives = [];
  const negatives = [];

  if (mode === 'cut') {
    if (calorieRatio < 0.7) negatives.push("menu trop léger, risque de faim");
    else if (calorieRatio <= 1) positives.push("calories adaptées à la perte de poids");
    else negatives.push("menu trop calorique pour la perte de poids");
  }

  if (mode === 'bulk') {
    if (calorieRatio < 1) negatives.push("apport calorique insuffisant");
    else if (calorieRatio <= 1.2) positives.push("bon surplus calorique");
    else negatives.push("surplus excessif, prise de gras probable");
  }

  if (mode === 'recomp') {
    if (calorieRatio <= 1) positives.push("bon équilibre énergétique");
    else negatives.push("menu trop calorique pour une recomposition");
  }

  if (proteinRatio >= 0.8)
    positives.push("excellent apport en protéines");
  else
    negatives.push("protéines insuffisantes pour l'objectif");

  if (fibreRatio >= 0.7)
    positives.push("apport élevé en fibres");
  else
    negatives.push("fibres à améliorer");

  let conclusion = "Menu correct";
  if (positives.length >= 3 && negatives.length === 0)
    conclusion = "Menu très bien équilibré";
  if (negatives.length >= 2)
    conclusion = "Menu peu adapté à votre objectif";

  return {
    conclusion,
    points_positifs: positives,
    points_a_ameliorer: negatives
  };
}


/**********************************
 * 7. SCORING PLATS (INCHANGÉ)
 **********************************/

function scorePlat(n, cible) {
  const calorieRatio = ratio(n.calorie, cible.calories_cibles);
  const carbRatio = ratio(n.glucides, cible.glucides_cibles);
  const fatRatio = ratio(n.lipides, cible.lipides_cibles);

  let penalty = 0;

  if (mode === 'cut') {
    if (calorieRatio > 0.5) penalty += (calorieRatio - 0.5) * 120;
    if (calorieRatio > 0.8) penalty += 40;
  }

  if (mode === 'bulk') {
    if (calorieRatio > 1.2) penalty += (calorieRatio - 1.2) * 100;
  }

  if (mode === 'recomp' && calorieRatio > 0.7) {
    penalty += (calorieRatio - 0.7) * 80;
  }

  if (carbRatio > 1.2) penalty += (carbRatio - 1.2) * 30;
  if (fatRatio > 1.2) penalty += (fatRatio - 1.2) * 30;

  const base =
    (
      Math.min(ratio(n.proteine, cible.proteine_cibles), 1) * 3 +
      Math.min(ratio(n.fibres, cible.fibres_cibles), 1) * 1.6 +
      Math.min(calorieRatio, 1) * 1.2 +
      Math.min(carbRatio, 1) +
      Math.min(fatRatio, 1)
    ) / 7.8 * 100;

  return {
    score: Math.round(clamp(base - penalty)),
    score_details: {
      calories_pct: Math.round(calorieRatio * 100),
      proteines_pct: Math.round(ratio(n.proteine, cible.proteine_cibles) * 100),
      fibres_pct: Math.round(ratio(n.fibres, cible.fibres_cibles) * 100),
      penalty: Math.round(penalty),
      interpretation: platInterpretation({
        calorieRatio,
        proteinRatio: ratio(n.proteine, cible.proteine_cibles),
        fibreRatio: ratio(n.fibres, cible.fibres_cibles),
        mode
      })
    }
  };
}


/**********************************
 * 8. SCORING MENUS (INCHANGÉ)
 **********************************/

function scoreMenu(n, profil) {
  const calorieRatio = ratio(n.calorie, profil.calories_cibles);
  let penalty = 0;

  if (mode === 'cut' && calorieRatio > 1) penalty += (calorieRatio - 1) * 120;
  if (mode === 'bulk' && calorieRatio > 1.25) penalty += (calorieRatio - 1.25) * 120;
  if (mode === 'recomp' && calorieRatio > 1.05) penalty += (calorieRatio - 1.05) * 80;

  const base =
    (
      Math.min(ratio(n.proteine, profil.proteine_cibles), 1) * 2.5 +
      Math.min(ratio(n.fibres, profil.fibres_cibles), 1) * 1.6 +
      Math.min(calorieRatio, 1) * 1.4 +
      Math.min(ratio(n.glucides, profil.glucides_cibles), 1) +
      Math.min(ratio(n.lipides, profil.lipides_cibles), 1)
    ) / 7.5 * 100;

  return {
    score: Math.round(clamp(base - penalty)),
    score_details: {
      calories_pct: Math.round(calorieRatio * 100),
      proteines_pct: Math.round(ratio(n.proteine, profil.proteine_cibles) * 100),
      fibres_pct: Math.round(ratio(n.fibres, profil.fibres_cibles) * 100),
      penalty: Math.round(penalty),
      interpretation: menuInterpretation({
        calorieRatio,
        proteinRatio: ratio(n.proteine, profil.proteine_cibles),
        fibreRatio: ratio(n.fibres, profil.fibres_cibles),
        mode
      })
    }
  };
}


/**********************************
 * 9. CALCUL FINAL
 **********************************/

const platsById = Object.fromEntries(platsDB.map(p => [p.id, p]));
const platsScorés = platsDB.map(p => ({
  ...p,
  ...scorePlat(p, profilParRepas)
}));

const menusScorés = menus.map(m => {
  const ids = parseIds(m.plats);
  const plats = ids.map(id => platsById[id]).filter(Boolean);
  const nutrition = aggregateNutrition(plats);

  return {
    menu_id: m.id,
    nom: m.nom,
    description: m.description,
    plats_ids: ids,
    nutrition,
    ...scoreMenu(nutrition, profil)
  };
});


/**********************************
 * 10. SORTIE N8N
 **********************************/

return {
  json: {
    mode,
    profil,
    profil_par_repas: profilParRepas,
    top_plats: platsScorés.sort((a, b) => b.score - a.score).slice(0, 6),
    top_menus: menusScorés.sort((a, b) => b.score - a.score).slice(0, 3)
  }
};