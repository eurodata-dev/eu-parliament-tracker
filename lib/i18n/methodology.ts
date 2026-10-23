import type { Locale } from "./config";

type Section = { id: string; h: string; p: string[] };
type Methodology = { title: string; lede: string; updated: string; sections: Section[] };

const METHODOLOGY: Record<Locale, Methodology> = {
  en: {
    title: "Methodology",
    lede: "Where the data comes from, how often it is updated, how the numbers are calculated and how the AI summaries are written. And what all of this cannot tell you.",
    updated: "Last updated: October 2026",
    sections: [
      {
        id: "data",
        h: "Where the data comes from",
        p: [
          "Every vote on this site is a roll-call vote held in the plenary of the European Parliament, where the vote of each MEP is recorded by name. These records are published by the Parliament itself.",
          "They are collected and cleaned by HowTheyVote.eu, an independent open-source project that republishes them as open data (ODbL licence). MEP photos and press summaries come from the European Parliament (© European Union).",
        ],
      },
      {
        id: "coverage",
        h: "What is covered, and what is not",
        p: [
          "All plenary roll-call votes since July 2019, which covers the 9th and the current 10th parliamentary term.",
          "Not covered: votes by show of hands or electronic votes where names are not recorded, votes in committees, and the positions of national governments in the Council. A missing vote on this site does not mean that no decision was taken.",
        ],
      },
      {
        id: "updates",
        h: "How often it is updated",
        p: [
          "The site reads the data live. A new vote appears as soon as the Parliament has published the roll-call results and HowTheyVote.eu has processed them, usually the same day or the next.",
          "Lists are refreshed at least every 15 minutes. The result of a vote never changes once it has been published.",
        ],
      },
      {
        id: "numbers",
        h: "How the numbers are calculated",
        p: [
          "Result: the official outcome as recorded by the Parliament (adopted or rejected). Margin: votes for minus votes against. Turnout: the share of MEPs who cast a vote (for, against or abstention).",
          "Group unity: the share of a group's votes that went the same way as the group's most common choice. Attendance on MEP pages: the share of the last 100 plenary votes in which the MEP cast a vote.",
          "Recent political changes: the votes of the last 30 days compared with the 120 votes before. Polarisation is the average distance between each group's share of votes in favour and 50%: the higher it is, the more clearly groups take opposite sides.",
          "\"Absent\" only means that no vote was recorded. An MEP can be absent for many reasons, including official duties elsewhere.",
        ],
      },
      {
        id: "ai",
        h: "How the AI summaries are written",
        p: [
          "Summaries are written by a language model (GPT-OSS, an open-weight model run by Groq) and only when you ask for them. The model receives only the official record of the vote: its title, the type of procedure, the results by political group and, when available, the Parliament's press summary.",
          "It is instructed to explain in plain language, to stay strictly neutral, never to judge a person, party or group, and not to add facts that are not in the record. Questions asking for a judgement on someone are not sent to the model at all.",
          "Every AI text is labelled as such. The numbers, charts and lists on each page always come straight from the official data, never from the AI.",
        ],
      },
      {
        id: "limits",
        h: "Limits",
        p: [
          "A roll-call vote shows how MEPs voted, not why. Voting against a text can mean opposing it, or wanting it to go further.",
          "AI summaries can contain mistakes or simplify too much. Always check the numbers and the official documents linked on each vote page. Vote titles come from the Parliament and are often only available in English.",
        ],
      },
      {
        id: "independence",
        h: "Independence",
        p: [
          "EU Parliament Tracker is an independent, non-commercial project by Burhan Elmas. It is not affiliated with the European Parliament, any political party or any interest group, and it receives no funding.",
          "If you spot an error, please let me know through the contact page.",
        ],
      },
    ],
  },
  fr: {
    title: "Méthodologie",
    lede: "D'où viennent les données, à quelle fréquence elles sont mises à jour, comment les chiffres sont calculés et comment les résumés IA sont rédigés. Et ce que tout cela ne permet pas de dire.",
    updated: "Dernière mise à jour : octobre 2026",
    sections: [
      {
        id: "data",
        h: "D'où viennent les données",
        p: [
          "Chaque vote présenté ici est un vote par appel nominal en séance plénière du Parlement européen, où le vote de chaque député est enregistré nominativement. Ces registres sont publiés par le Parlement lui-même.",
          "Ils sont collectés et structurés par HowTheyVote.eu, un projet indépendant et open source qui les republie en données ouvertes (licence ODbL). Les photos des députés et les résumés de presse proviennent du Parlement européen (© Union européenne).",
        ],
      },
      {
        id: "coverage",
        h: "Ce qui est couvert, et ce qui ne l'est pas",
        p: [
          "Tous les votes par appel nominal en plénière depuis juillet 2019, soit la 9e législature et l'actuelle 10e législature.",
          "Ne sont pas couverts : les votes à main levée ou électroniques sans enregistrement des noms, les votes en commission et les positions des gouvernements nationaux au Conseil. Un vote absent du site ne signifie donc pas qu'aucune décision n'a été prise.",
        ],
      },
      {
        id: "updates",
        h: "Fréquence de mise à jour",
        p: [
          "Le site lit les données en direct. Un nouveau vote apparaît dès que le Parlement a publié les résultats nominaux et que HowTheyVote.eu les a traités, en général le jour même ou le lendemain.",
          "Les listes sont actualisées au moins toutes les 15 minutes. Le résultat d'un vote ne change plus une fois publié.",
        ],
      },
      {
        id: "numbers",
        h: "Comment les chiffres sont calculés",
        p: [
          "Résultat : l'issue officielle enregistrée par le Parlement (adopté ou rejeté). Écart : voix pour moins voix contre. Participation : la part des députés qui ont voté (pour, contre ou abstention).",
          "Unité d'un groupe : la part des voix du groupe qui vont dans le même sens que le choix le plus fréquent du groupe. Présence sur les pages des députés : la part des 100 derniers votes en plénière auxquels le député a pris part.",
          "Changements politiques récents : les votes des 30 derniers jours comparés aux 120 votes précédents. La polarisation est l'écart moyen entre la part de voix « pour » de chaque groupe et 50 % : plus elle est élevée, plus les groupes prennent des positions nettement opposées.",
          "« Absent » signifie seulement qu'aucun vote n'a été enregistré. Un député peut être absent pour de nombreuses raisons, y compris une mission officielle ailleurs.",
        ],
      },
      {
        id: "ai",
        h: "Comment les résumés IA sont rédigés",
        p: [
          "Les résumés sont rédigés par un modèle de langage (GPT-OSS, un modèle ouvert exécuté par Groq), et uniquement quand vous les demandez. Le modèle ne reçoit que le registre officiel du vote : son titre, le type de procédure, les résultats par groupe politique et, s'il existe, le résumé de presse du Parlement.",
          "Il a pour consigne d'expliquer simplement, de rester strictement neutre, de ne jamais juger une personne, un parti ou un groupe, et de ne rien ajouter qui ne figure pas dans le registre. Les questions qui demandent un jugement sur quelqu'un ne sont pas du tout envoyées au modèle.",
          "Chaque texte rédigé par l'IA est signalé comme tel. Les chiffres, graphiques et listes de chaque page proviennent toujours directement des données officielles, jamais de l'IA.",
        ],
      },
      {
        id: "limits",
        h: "Limites",
        p: [
          "Un vote par appel nominal montre comment les députés ont voté, pas pourquoi. Voter contre un texte peut vouloir dire s'y opposer, ou vouloir qu'il aille plus loin.",
          "Les résumés IA peuvent contenir des erreurs ou trop simplifier. Vérifiez toujours les chiffres et les documents officiels liés sur chaque page de vote. Les titres des votes viennent du Parlement et ne sont souvent disponibles qu'en anglais.",
        ],
      },
      {
        id: "independence",
        h: "Indépendance",
        p: [
          "EU Parliament Tracker est un projet indépendant et non commercial de Burhan Elmas. Il n'est lié ni au Parlement européen, ni à un parti politique, ni à un groupe d'intérêt, et ne reçoit aucun financement.",
          "Si vous repérez une erreur, n'hésitez pas à me le signaler via la page de contact.",
        ],
      },
    ],
  },
  de: {
    title: "Methodik",
    lede: "Woher die Daten stammen, wie oft sie aktualisiert werden, wie die Zahlen berechnet und wie die KI-Zusammenfassungen geschrieben werden. Und was all das nicht aussagen kann.",
    updated: "Zuletzt aktualisiert: Oktober 2026",
    sections: [
      {
        id: "data",
        h: "Woher die Daten stammen",
        p: [
          "Jede Abstimmung auf dieser Seite ist eine namentliche Abstimmung im Plenum des Europäischen Parlaments, bei der die Stimme jeder und jedes Abgeordneten mit Namen erfasst wird. Diese Protokolle veröffentlicht das Parlament selbst.",
          "Gesammelt und aufbereitet werden sie von HowTheyVote.eu, einem unabhängigen Open-Source-Projekt, das sie als offene Daten (ODbL-Lizenz) bereitstellt. Fotos der Abgeordneten und Pressezusammenfassungen stammen vom Europäischen Parlament (© Europäische Union).",
        ],
      },
      {
        id: "coverage",
        h: "Was abgedeckt ist und was nicht",
        p: [
          "Alle namentlichen Abstimmungen im Plenum seit Juli 2019, also die 9. und die laufende 10. Wahlperiode.",
          "Nicht abgedeckt sind Abstimmungen per Handzeichen oder elektronische Abstimmungen ohne Namenserfassung, Abstimmungen in den Ausschüssen und die Positionen der nationalen Regierungen im Rat. Fehlt eine Abstimmung hier, heißt das also nicht, dass keine Entscheidung gefallen ist.",
        ],
      },
      {
        id: "updates",
        h: "Wie oft aktualisiert wird",
        p: [
          "Die Seite liest die Daten live. Eine neue Abstimmung erscheint, sobald das Parlament die namentlichen Ergebnisse veröffentlicht und HowTheyVote.eu sie verarbeitet hat, meist noch am selben oder am nächsten Tag.",
          "Listen werden mindestens alle 15 Minuten aktualisiert. Das Ergebnis einer Abstimmung ändert sich nach der Veröffentlichung nicht mehr.",
        ],
      },
      {
        id: "numbers",
        h: "Wie die Zahlen berechnet werden",
        p: [
          "Ergebnis: das offizielle Ergebnis laut Parlament (angenommen oder abgelehnt). Abstand: Ja-Stimmen minus Nein-Stimmen. Beteiligung: der Anteil der Abgeordneten, die abgestimmt haben (dafür, dagegen oder Enthaltung).",
          "Geschlossenheit einer Fraktion: der Anteil ihrer Stimmen, der in dieselbe Richtung ging wie die häufigste Wahl der Fraktion. Anwesenheit auf den Abgeordnetenseiten: der Anteil der letzten 100 Plenarabstimmungen, an denen die Person teilgenommen hat.",
          "Politische Veränderungen: die Abstimmungen der letzten 30 Tage im Vergleich zu den 120 Abstimmungen davor. Die Polarisierung ist der durchschnittliche Abstand zwischen dem Ja-Anteil jeder Fraktion und 50 %: Je höher sie ist, desto deutlicher stehen sich die Fraktionen gegenüber.",
          "„Abwesend“ bedeutet nur, dass keine Stimme erfasst wurde. Abgeordnete können aus vielen Gründen fehlen, auch wegen offizieller Termine an anderer Stelle.",
        ],
      },
      {
        id: "ai",
        h: "Wie die KI-Zusammenfassungen entstehen",
        p: [
          "Die Zusammenfassungen schreibt ein Sprachmodell (GPT-OSS, ein offenes Modell, betrieben von Groq), und nur, wenn Sie sie anfordern. Das Modell erhält ausschließlich das offizielle Protokoll der Abstimmung: Titel, Art des Verfahrens, Ergebnisse nach Fraktion und, falls vorhanden, die Pressezusammenfassung des Parlaments.",
          "Es ist angewiesen, verständlich zu erklären, strikt neutral zu bleiben, niemals eine Person, Partei oder Fraktion zu bewerten und keine Fakten hinzuzufügen, die nicht im Protokoll stehen. Fragen, die eine Bewertung von jemandem verlangen, werden gar nicht an das Modell geschickt.",
          "Jeder KI-Text ist als solcher gekennzeichnet. Zahlen, Grafiken und Listen auf jeder Seite stammen immer direkt aus den offiziellen Daten, nie von der KI.",
        ],
      },
      {
        id: "limits",
        h: "Grenzen",
        p: [
          "Eine namentliche Abstimmung zeigt, wie Abgeordnete abgestimmt haben, nicht warum. Gegen einen Text zu stimmen kann Ablehnung bedeuten oder den Wunsch, dass er weiter geht.",
          "KI-Zusammenfassungen können Fehler enthalten oder zu stark vereinfachen. Prüfen Sie immer die Zahlen und die offiziellen Dokumente, die auf jeder Abstimmungsseite verlinkt sind. Die Titel stammen vom Parlament und liegen oft nur auf Englisch vor.",
        ],
      },
      {
        id: "independence",
        h: "Unabhängigkeit",
        p: [
          "EU Parliament Tracker ist ein unabhängiges, nicht kommerzielles Projekt von Burhan Elmas. Es ist weder mit dem Europäischen Parlament noch mit einer Partei oder Interessengruppe verbunden und erhält keine Finanzierung.",
          "Wenn Ihnen ein Fehler auffällt, schreiben Sie mir gerne über die Kontaktseite.",
        ],
      },
    ],
  },
  nl: {
    title: "Methodologie",
    lede: "Waar de gegevens vandaan komen, hoe vaak ze worden bijgewerkt, hoe de cijfers worden berekend en hoe de AI-samenvattingen worden geschreven. En wat dit allemaal niet kan vertellen.",
    updated: "Laatst bijgewerkt: oktober 2026",
    sections: [
      {
        id: "data",
        h: "Waar de gegevens vandaan komen",
        p: [
          "Elke stemming op deze site is een hoofdelijke stemming in de plenaire vergadering van het Europees Parlement, waarbij de stem van elk lid met naam wordt geregistreerd. Die registers worden door het Parlement zelf gepubliceerd.",
          "Ze worden verzameld en opgeschoond door HowTheyVote.eu, een onafhankelijk opensourceproject dat ze als open data publiceert (ODbL-licentie). Foto's van de leden en persberichten komen van het Europees Parlement (© Europese Unie).",
        ],
      },
      {
        id: "coverage",
        h: "Wat wel en niet aan bod komt",
        p: [
          "Alle hoofdelijke stemmingen in de plenaire vergadering sinds juli 2019, dus de 9e en de huidige 10e zittingsperiode.",
          "Niet opgenomen: stemmingen met handopsteking of elektronische stemmingen zonder namen, stemmingen in de commissies en de standpunten van de nationale regeringen in de Raad. Ontbreekt een stemming op deze site, dan betekent dat dus niet dat er geen beslissing is genomen.",
        ],
      },
      {
        id: "updates",
        h: "Hoe vaak de site wordt bijgewerkt",
        p: [
          "De site leest de gegevens live. Een nieuwe stemming verschijnt zodra het Parlement de hoofdelijke uitslagen heeft gepubliceerd en HowTheyVote.eu ze heeft verwerkt, meestal dezelfde dag of de dag erna.",
          "Lijsten worden minstens om de 15 minuten vernieuwd. De uitslag van een stemming verandert niet meer na publicatie.",
        ],
      },
      {
        id: "numbers",
        h: "Hoe de cijfers worden berekend",
        p: [
          "Uitslag: de officiële uitkomst zoals geregistreerd door het Parlement (aangenomen of verworpen). Verschil: stemmen voor min stemmen tegen. Opkomst: het aandeel leden dat een stem uitbracht (voor, tegen of onthouding).",
          "Eensgezindheid van een fractie: het aandeel van haar stemmen dat dezelfde kant op ging als de meest gekozen optie van de fractie. Aanwezigheid op de pagina's van de leden: het aandeel van de laatste 100 plenaire stemmingen waaraan het lid deelnam.",
          "Recente politieke veranderingen: de stemmingen van de laatste 30 dagen vergeleken met de 120 stemmingen daarvoor. Polarisatie is de gemiddelde afstand tussen het aandeel voorstemmen van elke fractie en 50%: hoe hoger, hoe duidelijker de fracties tegenover elkaar staan.",
          "\"Afwezig\" betekent alleen dat er geen stem werd geregistreerd. Een lid kan om veel redenen afwezig zijn, ook voor officiële taken elders.",
        ],
      },
      {
        id: "ai",
        h: "Hoe de AI-samenvattingen worden geschreven",
        p: [
          "De samenvattingen worden geschreven door een taalmodel (GPT-OSS, een open model dat door Groq wordt gedraaid), en alleen wanneer je erom vraagt. Het model krijgt enkel het officiële register van de stemming: de titel, het soort procedure, de uitslagen per fractie en, als die er is, de samenvatting uit het persbericht van het Parlement.",
          "Het krijgt de opdracht om in eenvoudige taal uit te leggen, strikt neutraal te blijven, nooit een persoon, partij of fractie te beoordelen en geen feiten toe te voegen die niet in het register staan. Vragen die een oordeel over iemand vragen, worden helemaal niet naar het model gestuurd.",
          "Elke AI-tekst is als zodanig aangeduid. De cijfers, grafieken en lijsten op elke pagina komen altijd rechtstreeks uit de officiële gegevens, nooit van de AI.",
        ],
      },
      {
        id: "limits",
        h: "Beperkingen",
        p: [
          "Een hoofdelijke stemming toont hoe leden stemden, niet waarom. Tegen een tekst stemmen kan betekenen dat je ertegen bent, of dat je wilt dat hij verder gaat.",
          "AI-samenvattingen kunnen fouten bevatten of te veel vereenvoudigen. Controleer altijd de cijfers en de officiële documenten die op elke stemmingspagina gelinkt zijn. De titels van de stemmingen komen van het Parlement en zijn vaak alleen in het Engels beschikbaar.",
        ],
      },
      {
        id: "independence",
        h: "Onafhankelijkheid",
        p: [
          "EU Parliament Tracker is een onafhankelijk, niet-commercieel project van Burhan Elmas. Het is niet verbonden aan het Europees Parlement, een politieke partij of een belangengroep en krijgt geen financiering.",
          "Zie je een fout? Laat het me weten via de contactpagina.",
        ],
      },
    ],
  },
  es: {
    title: "Metodología",
    lede: "De dónde vienen los datos, cada cuánto se actualizan, cómo se calculan las cifras y cómo se redactan los resúmenes con IA. Y lo que todo esto no puede decir.",
    updated: "Última actualización: octubre de 2026",
    sections: [
      {
        id: "data",
        h: "De dónde vienen los datos",
        p: [
          "Cada votación de este sitio es una votación nominal celebrada en el pleno del Parlamento Europeo, en la que el voto de cada eurodiputado queda registrado con su nombre. Estos registros los publica el propio Parlamento.",
          "Los recoge y organiza HowTheyVote.eu, un proyecto independiente y de código abierto que los publica como datos abiertos (licencia ODbL). Las fotos de los eurodiputados y los resúmenes de prensa proceden del Parlamento Europeo (© Unión Europea).",
        ],
      },
      {
        id: "coverage",
        h: "Qué se cubre y qué no",
        p: [
          "Todas las votaciones nominales en el pleno desde julio de 2019, es decir, la 9.ª legislatura y la actual 10.ª.",
          "No se cubren las votaciones a mano alzada o electrónicas sin registro de nombres, las votaciones en comisión ni las posiciones de los gobiernos nacionales en el Consejo. Que una votación no aparezca aquí no significa que no se haya tomado ninguna decisión.",
        ],
      },
      {
        id: "updates",
        h: "Cada cuánto se actualiza",
        p: [
          "El sitio lee los datos en directo. Una nueva votación aparece en cuanto el Parlamento publica los resultados nominales y HowTheyVote.eu los procesa, normalmente el mismo día o al día siguiente.",
          "Las listas se actualizan como mínimo cada 15 minutos. El resultado de una votación ya no cambia una vez publicado.",
        ],
      },
      {
        id: "numbers",
        h: "Cómo se calculan las cifras",
        p: [
          "Resultado: el resultado oficial registrado por el Parlamento (aprobado o rechazado). Margen: votos a favor menos votos en contra. Participación: la proporción de eurodiputados que votaron (a favor, en contra o abstención).",
          "Unidad de un grupo: la proporción de sus votos que fue en la misma dirección que la opción más frecuente del grupo. Asistencia en las páginas de los eurodiputados: la proporción de las últimas 100 votaciones del pleno en las que participó.",
          "Cambios políticos recientes: las votaciones de los últimos 30 días comparadas con las 120 anteriores. La polarización es la distancia media entre la proporción de votos a favor de cada grupo y el 50 %: cuanto más alta, más claramente se enfrentan los grupos.",
          "\"Ausente\" solo significa que no se registró ningún voto. Un eurodiputado puede faltar por muchas razones, incluidas obligaciones oficiales en otro lugar.",
        ],
      },
      {
        id: "ai",
        h: "Cómo se redactan los resúmenes con IA",
        p: [
          "Los resúmenes los redacta un modelo de lenguaje (GPT-OSS, un modelo abierto ejecutado por Groq), y solo cuando los pides. El modelo recibe únicamente el registro oficial de la votación: el título, el tipo de procedimiento, los resultados por grupo político y, si existe, el resumen de prensa del Parlamento.",
          "Tiene instrucciones de explicar con claridad, mantenerse estrictamente neutral, no juzgar nunca a una persona, partido o grupo y no añadir datos que no estén en el registro. Las preguntas que piden un juicio sobre alguien no se envían al modelo.",
          "Todo texto escrito por la IA se indica como tal. Las cifras, gráficos y listas de cada página proceden siempre directamente de los datos oficiales, nunca de la IA.",
        ],
      },
      {
        id: "limits",
        h: "Límites",
        p: [
          "Una votación nominal muestra cómo votaron los eurodiputados, no por qué. Votar en contra de un texto puede significar oponerse a él o querer que vaya más lejos.",
          "Los resúmenes con IA pueden contener errores o simplificar demasiado. Comprueba siempre las cifras y los documentos oficiales enlazados en cada página de votación. Los títulos proceden del Parlamento y a menudo solo están en inglés.",
        ],
      },
      {
        id: "independence",
        h: "Independencia",
        p: [
          "EU Parliament Tracker es un proyecto independiente y sin ánimo de lucro de Burhan Elmas. No está vinculado al Parlamento Europeo, a ningún partido político ni a ningún grupo de interés, y no recibe financiación.",
          "Si detectas un error, escríbeme a través de la página de contacto.",
        ],
      },
    ],
  },
  it: {
    title: "Metodologia",
    lede: "Da dove vengono i dati, ogni quanto vengono aggiornati, come si calcolano i numeri e come vengono scritti i riassunti con l'IA. E cosa tutto questo non può dire.",
    updated: "Ultimo aggiornamento: ottobre 2026",
    sections: [
      {
        id: "data",
        h: "Da dove vengono i dati",
        p: [
          "Ogni votazione su questo sito è una votazione per appello nominale in plenaria al Parlamento europeo, in cui il voto di ogni eurodeputato viene registrato con il suo nome. Questi registri sono pubblicati dal Parlamento stesso.",
          "Vengono raccolti e organizzati da HowTheyVote.eu, un progetto indipendente e open source che li ripubblica come dati aperti (licenza ODbL). Le foto degli eurodeputati e i riassunti stampa provengono dal Parlamento europeo (© Unione europea).",
        ],
      },
      {
        id: "coverage",
        h: "Cosa è incluso e cosa no",
        p: [
          "Tutte le votazioni per appello nominale in plenaria da luglio 2019, cioè la 9ª legislatura e l'attuale 10ª.",
          "Non sono incluse le votazioni per alzata di mano o elettroniche senza registrazione dei nomi, le votazioni in commissione e le posizioni dei governi nazionali in Consiglio. Se una votazione non compare qui, non significa che non sia stata presa alcuna decisione.",
        ],
      },
      {
        id: "updates",
        h: "Ogni quanto viene aggiornato",
        p: [
          "Il sito legge i dati in tempo reale. Una nuova votazione compare non appena il Parlamento ha pubblicato i risultati nominali e HowTheyVote.eu li ha elaborati, di solito lo stesso giorno o il giorno dopo.",
          "Gli elenchi vengono aggiornati almeno ogni 15 minuti. Il risultato di una votazione non cambia più dopo la pubblicazione.",
        ],
      },
      {
        id: "numbers",
        h: "Come si calcolano i numeri",
        p: [
          "Esito: il risultato ufficiale registrato dal Parlamento (approvato o respinto). Margine: voti favorevoli meno voti contrari. Partecipazione: la quota di eurodeputati che hanno votato (a favore, contro o astensione).",
          "Compattezza di un gruppo: la quota dei suoi voti andata nella stessa direzione della scelta più frequente del gruppo. Presenza nelle pagine degli eurodeputati: la quota delle ultime 100 votazioni in plenaria a cui ha partecipato.",
          "Cambiamenti politici recenti: le votazioni degli ultimi 30 giorni confrontate con le 120 precedenti. La polarizzazione è la distanza media tra la quota di voti favorevoli di ciascun gruppo e il 50%: più è alta, più i gruppi prendono posizioni nettamente opposte.",
          "\"Assente\" significa solo che non è stato registrato alcun voto. Un eurodeputato può essere assente per molte ragioni, compresi impegni ufficiali altrove.",
        ],
      },
      {
        id: "ai",
        h: "Come vengono scritti i riassunti con l'IA",
        p: [
          "I riassunti sono scritti da un modello linguistico (GPT-OSS, un modello aperto eseguito da Groq), e solo quando li chiedi. Il modello riceve soltanto il registro ufficiale della votazione: il titolo, il tipo di procedura, i risultati per gruppo politico e, se disponibile, il riassunto stampa del Parlamento.",
          "Ha l'istruzione di spiegare in modo semplice, restare rigorosamente neutrale, non giudicare mai una persona, un partito o un gruppo e non aggiungere fatti che non siano nel registro. Le domande che chiedono un giudizio su qualcuno non vengono inviate al modello.",
          "Ogni testo scritto dall'IA è indicato come tale. I numeri, i grafici e gli elenchi di ogni pagina provengono sempre direttamente dai dati ufficiali, mai dall'IA.",
        ],
      },
      {
        id: "limits",
        h: "Limiti",
        p: [
          "Una votazione per appello nominale mostra come hanno votato gli eurodeputati, non perché. Votare contro un testo può voler dire opporsi, oppure volere che vada più lontano.",
          "I riassunti con l'IA possono contenere errori o semplificare troppo. Controlla sempre i numeri e i documenti ufficiali collegati in ogni pagina di votazione. I titoli provengono dal Parlamento e spesso sono disponibili solo in inglese.",
        ],
      },
      {
        id: "independence",
        h: "Indipendenza",
        p: [
          "EU Parliament Tracker è un progetto indipendente e non commerciale di Burhan Elmas. Non è legato al Parlamento europeo, a partiti politici o a gruppi di interesse, e non riceve finanziamenti.",
          "Se trovi un errore, scrivimi tramite la pagina dei contatti.",
        ],
      },
    ],
  },
};

export function methodologyText(locale: Locale) {
  return METHODOLOGY[locale] ?? METHODOLOGY.en;
}
