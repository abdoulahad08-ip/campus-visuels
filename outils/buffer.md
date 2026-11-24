# Publication via Buffer (depuis le 22 nov 2026, remplace Metricool)

Organisation Buffer : « My Organization » — organizationId `6638d32f44a7f39c6aca3fc7` (forfait gratuit).
Fuseau du compte Buffer : Europe/Paris. Toujours écrire `dueAt` en UTC explicite (= heure de Dakar), ex. `2026-11-22T10:00:00+00:00`, et vérifier dans la réponse que `dueAt` correspond bien à cette heure UTC.

| Réseau | channelId | Compte |
|---|---|---|
| TikTok | `6b022cf8ece6dfde5f4d8545` | @campubourse |
| LinkedIn | `6b022cbaece6dfde5f4d7f8b` | page Campus Bourse |
| X | `6b022cd8ece6dfde5f4d845c` | @campusbourse |
Facebook : aucun (on ne publie plus sur Facebook). Ne jamais deviner un channelId : en cas d'erreur « channel », appeler list_channels.

## Paramètres create_post (testés le 21 nov 2026)
Toujours : `schedulingType: "automatic"`, `mode: "customScheduled"`, `dueAt` (futur), `text` = contenu EXACT du .txt.
- **TikTok (carrousel photo)** : `assets` = liste d'images `{"image":{"url":"<raw .jpg>?v=1","metadata":{"altText":"<texte court de la diapo>"}}}` dans l'ordre (**10 images max** : Buffer renvoie « TikTok posts cannot have more than 10 assets », constaté le 24 nov 2026) ; `metadata: {"tiktok":{"title":"<titre court>"}}`.
- **LinkedIn (carrousel PDF)** : assembler les fb_XX.png en un PDF (`python3 -c` avec PIL : `ims[0].save('carrousel.pdf', save_all=True, append_images=ims[1:], resolution=150)`), le pousser sur GitHub, puis `assets` = `[{"document":{"url":"<raw carrousel.pdf>?v=1","title":"<titre court>","thumbnailUrl":"<raw fb_01.png>?v=1"}}]`. Pas de `metadata.linkedin.firstComment` : le PREMIER COMMENTAIRE EST RÉSERVÉ AUX FORFAITS PAYANTS (erreur 400 sur le forfait gratuit). Le texte du premier commentaire est donc envoyé à l'utilisateur dans le rapport, à poster à la main juste après la publication.
- **X (post ou thread)** : post simple = `text` + 1 image `x.png` (générée par outils/visuel_x.py, jamais une diapo de carrousel) en `assets`. Thread = `text` identique au 1er élément ET `metadata: {"twitter":{"thread":[{"text":"…","assets":[…]},{"text":"…"}, …]}}` avec TOUS les éléments. Chaque élément ≤ 280 caractères (vérifié en Python). Si Buffer refuse la longueur, ne pas couper soi-même : signaler l'erreur.
- URLs des médias : `https://raw.githubusercontent.com/abdoulahad08-ip/campus-visuels/main/<chemin>?v=1` (vérifier HTTP 200 avant).

## Anti-doublon
`list_posts` (organizationId, `channelIds` du réseau, `status: ["scheduled","sending","sent"]`, `dueAt: {start: "<jour>T00:00:00+00:00", end: "<jour>T23:59:59+00:00"}`) : si un post Campus Bourse existe déjà au créneau, ne pas le recréer.

## Limites du forfait gratuit Buffer
- **10 posts programmés au maximum à la fois** (toutes chaînes). Chaque tâche ne programme que les posts du jour même. Si Buffer refuse pour limite atteinte : ne rien contourner, envoyer les textes et visuels à l'utilisateur avec l'erreur.
- 3 chaînes maximum (TikTok, LinkedIn, X).
- Pas de premier commentaire LinkedIn.
- Statistiques : `get_aggregated_post_metrics` et `list_posts` avec `includeMetrics` (31 derniers jours sur le forfait gratuit).

## Journal
campus-bourse/journal.csv : la colonne `uuid_metricool` contient désormais les **id de posts Buffer** (séparés par « | »).
