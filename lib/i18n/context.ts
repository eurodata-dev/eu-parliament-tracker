import type { Locale } from "./config";

type Procedure = { name: string; what: string; next: string };
type Context = {
  title: string;
  type: string;
  next: string;
  passes: string;
  passesText: string;
  amendment: string;
  amendmentText: string;
  file: string;
  method: string;
  unknown: string;
  procedures: Record<string, Procedure>;
};

// plain-language explanations of EU procedures, written by hand (no AI)
const CONTEXT: Record<Locale, Context> = {
  en: {
    title: "What kind of vote is this?",
    type: "Procedure",
    next: "What happens next",
    passes: "How a vote passes",
    passesText:
      "Most votes pass with a simple majority: more votes for than against. Abstentions don't count either way. Some decisions, for example certain budget votes, need a larger majority.",
    amendment: "A vote on an amendment",
    amendmentText:
      "An amendment is a proposed change to part of a text. This vote decided on that change only, not on the text as a whole.",
    file: "Follow the file on the Parliament's Legislative Observatory",
    method: "How the data and summaries work",
    unknown:
      "Every vote is part of a file that follows a set procedure. The Parliament's Legislative Observatory shows where this file stands.",
    procedures: {
      COD: {
        name: "Ordinary legislative procedure",
        what: "This is EU law in the making. The Parliament and the Council, where the governments of the member states sit, decide together on a proposal from the European Commission. Both have to agree on exactly the same text.",
        next: "If this was the Parliament's first position, negotiations with the Council usually follow. If the text had already been agreed with the Council, it becomes law once the Council confirms it and it is published in the Official Journal of the EU.",
      },
      CNS: {
        name: "Consultation procedure",
        what: "The Parliament gives its opinion, but the Council decides on its own, often by unanimity.",
        next: "The Council takes the final decision. It has to consult the Parliament but does not have to follow its opinion.",
      },
      APP: {
        name: "Consent procedure",
        what: "The Parliament can only approve or reject the text as a whole. It cannot change it. Without its consent, the text cannot be adopted.",
        next: "If the Parliament gave its consent, the Council can adopt the decision. If it refused, the text cannot go ahead in this form.",
      },
      NLE: {
        name: "Non-legislative procedure",
        what: "A decision that is not a law, for example on an international agreement or an appointment. Depending on the case, the Parliament gives its consent or only its opinion.",
        next: "The final decision is usually taken by the Council, taking the Parliament's vote into account.",
      },
      INI: {
        name: "Own-initiative report",
        what: "The Parliament sets out its own view on a subject. It is not binding: nobody is legally required to act on it.",
        next: "The report is sent to the Commission and the national governments. It can influence future proposals, but it does not change the law by itself.",
      },
      INL: {
        name: "Request for a legislative proposal",
        what: "The Parliament asks the European Commission to propose a new law. Only the Commission can formally propose EU laws.",
        next: "The Commission has committed to reply within three months and to explain its reasons if it does not follow up.",
      },
      RSP: {
        name: "Resolution on a topical subject",
        what: "A political statement on a current issue, often a crisis, a human rights situation or an upcoming international meeting. It is not binding.",
        next: "The resolution is sent to the institutions and governments concerned. It expresses the Parliament's position but creates no legal obligation.",
      },
      BUD: {
        name: "Budgetary procedure",
        what: "The annual EU budget, which the Parliament and the Council decide together.",
        next: "Both have to agree on the same figures. If they cannot agree, the Commission has to present a new draft budget.",
      },
      DEC: {
        name: "Budget discharge",
        what: "The Parliament checks how the EU budget of a past year was spent and decides whether to approve the accounts (\"grant discharge\") or to postpone that decision.",
        next: "If discharge is postponed, the institution concerned has to answer the Parliament's questions before a new vote.",
      },
      RPS: {
        name: "Objection to an implementing measure",
        what: "The Commission adopts many technical rules itself. Here, the Parliament can object to one of them within a deadline.",
        next: "If no majority objects, the measure can enter into force.",
      },
      DEA: {
        name: "Objection to a delegated act",
        what: "The Commission can adopt detailed rules under powers delegated by a law. The Parliament can object to them within a set deadline.",
        next: "If no majority objects in time, the act can enter into force.",
      },
      IMM: {
        name: "Parliamentary immunity",
        what: "A decision on whether to waive or defend an MEP's parliamentary immunity, usually at the request of national authorities. It is not a judgement on whether the MEP did anything wrong.",
        next: "If immunity is waived, national proceedings can continue. If it is defended, they cannot go ahead for now.",
      },
      REG: {
        name: "Rules of Procedure",
        what: "A change to the Parliament's own internal rules.",
        next: "The new rules apply from the date set in the decision.",
      },
    },
  },
  fr: {
    title: "De quel type de vote s'agit-il ?",
    type: "Procédure",
    next: "Et ensuite ?",
    passes: "Comment un vote est adopté",
    passesText:
      "La plupart des votes sont adoptés à la majorité simple : plus de voix pour que de voix contre. Les abstentions ne comptent ni pour ni contre. Certaines décisions, par exemple certains votes budgétaires, exigent une majorité plus large.",
    amendment: "Un vote sur un amendement",
    amendmentText:
      "Un amendement est une proposition de modification d'une partie d'un texte. Ce vote portait uniquement sur cette modification, pas sur le texte dans son ensemble.",
    file: "Suivre le dossier sur l'Observatoire législatif du Parlement",
    method: "Comment fonctionnent les données et les résumés",
    unknown:
      "Chaque vote fait partie d'un dossier qui suit une procédure précise. L'Observatoire législatif du Parlement indique où en est ce dossier.",
    procedures: {
      COD: {
        name: "Procédure législative ordinaire",
        what: "C'est une loi européenne en préparation. Le Parlement et le Conseil, où siègent les gouvernements des États membres, décident ensemble sur une proposition de la Commission européenne. Les deux doivent s'accorder sur exactement le même texte.",
        next: "S'il s'agissait de la première position du Parlement, des négociations avec le Conseil suivent en général. Si le texte avait déjà été négocié avec le Conseil, il devient loi une fois confirmé par le Conseil et publié au Journal officiel de l'UE.",
      },
      CNS: {
        name: "Procédure de consultation",
        what: "Le Parlement donne son avis, mais le Conseil décide seul, souvent à l'unanimité.",
        next: "Le Conseil prend la décision finale. Il doit consulter le Parlement mais n'est pas obligé de suivre son avis.",
      },
      APP: {
        name: "Procédure d'approbation",
        what: "Le Parlement peut seulement approuver ou rejeter le texte dans son ensemble, sans le modifier. Sans son approbation, le texte ne peut pas être adopté.",
        next: "Si le Parlement a donné son approbation, le Conseil peut adopter la décision. S'il l'a refusée, le texte ne peut pas aboutir sous cette forme.",
      },
      NLE: {
        name: "Procédure non législative",
        what: "Une décision qui n'est pas une loi, par exemple sur un accord international ou une nomination. Selon le cas, le Parlement donne son approbation ou seulement son avis.",
        next: "La décision finale est en général prise par le Conseil, en tenant compte du vote du Parlement.",
      },
      INI: {
        name: "Rapport d'initiative",
        what: "Le Parlement exprime sa propre position sur un sujet. Ce n'est pas contraignant : personne n'est légalement tenu d'y donner suite.",
        next: "Le rapport est transmis à la Commission et aux gouvernements nationaux. Il peut influencer de futures propositions, mais ne change pas la loi à lui seul.",
      },
      INL: {
        name: "Demande de proposition législative",
        what: "Le Parlement demande à la Commission européenne de proposer une nouvelle loi. Seule la Commission peut formellement proposer des lois européennes.",
        next: "La Commission s'est engagée à répondre dans les trois mois et à expliquer ses raisons si elle n'y donne pas suite.",
      },
      RSP: {
        name: "Résolution sur un sujet d'actualité",
        what: "Une déclaration politique sur une question d'actualité, souvent une crise, une situation de droits humains ou une rencontre internationale à venir. Elle n'est pas contraignante.",
        next: "La résolution est transmise aux institutions et gouvernements concernés. Elle exprime la position du Parlement mais ne crée aucune obligation juridique.",
      },
      BUD: {
        name: "Procédure budgétaire",
        what: "Le budget annuel de l'UE, que le Parlement et le Conseil décident ensemble.",
        next: "Les deux doivent s'accorder sur les mêmes montants. S'ils n'y parviennent pas, la Commission doit présenter un nouveau projet de budget.",
      },
      DEC: {
        name: "Décharge budgétaire",
        what: "Le Parlement vérifie comment le budget de l'UE d'une année passée a été dépensé et décide d'approuver les comptes (« donner décharge ») ou de reporter cette décision.",
        next: "Si la décharge est reportée, l'institution concernée doit répondre aux questions du Parlement avant un nouveau vote.",
      },
      RPS: {
        name: "Objection à une mesure d'exécution",
        what: "La Commission adopte elle-même de nombreuses règles techniques. Ici, le Parlement peut s'opposer à l'une d'elles dans un certain délai.",
        next: "Si aucune majorité ne s'y oppose, la mesure peut entrer en vigueur.",
      },
      DEA: {
        name: "Objection à un acte délégué",
        what: "La Commission peut adopter des règles détaillées grâce à des pouvoirs délégués par une loi. Le Parlement peut s'y opposer dans un délai fixé.",
        next: "Si aucune majorité ne s'y oppose à temps, l'acte peut entrer en vigueur.",
      },
      IMM: {
        name: "Immunité parlementaire",
        what: "Une décision sur la levée ou la défense de l'immunité d'un député, en général à la demande des autorités nationales. Ce n'est pas un jugement sur ce que le député aurait fait.",
        next: "Si l'immunité est levée, la procédure nationale peut se poursuivre. Si elle est défendue, elle ne peut pas avancer pour l'instant.",
      },
      REG: {
        name: "Règlement intérieur",
        what: "Une modification des règles internes du Parlement.",
        next: "Les nouvelles règles s'appliquent à partir de la date fixée dans la décision.",
      },
    },
  },
  de: {
    title: "Was für eine Abstimmung ist das?",
    type: "Verfahren",
    next: "Wie es weitergeht",
    passes: "Wann ein Text angenommen ist",
    passesText:
      "Die meisten Abstimmungen werden mit einfacher Mehrheit entschieden: mehr Ja- als Nein-Stimmen. Enthaltungen zählen in keine Richtung. Manche Entscheidungen, etwa bestimmte Haushaltsabstimmungen, brauchen eine größere Mehrheit.",
    amendment: "Abstimmung über einen Änderungsantrag",
    amendmentText:
      "Ein Änderungsantrag schlägt vor, einen Teil eines Textes zu ändern. Hier wurde nur über diese Änderung abgestimmt, nicht über den Text als Ganzes.",
    file: "Das Dossier in der Legislativen Beobachtungsstelle des Parlaments verfolgen",
    method: "Wie Daten und Zusammenfassungen entstehen",
    unknown:
      "Jede Abstimmung gehört zu einem Dossier mit einem festgelegten Verfahren. Die Legislative Beobachtungsstelle des Parlaments zeigt, wo dieses Dossier steht.",
    procedures: {
      COD: {
        name: "Ordentliches Gesetzgebungsverfahren",
        what: "Hier entsteht EU-Recht. Das Parlament und der Rat, in dem die Regierungen der Mitgliedstaaten sitzen, entscheiden gemeinsam über einen Vorschlag der Europäischen Kommission. Beide müssen sich auf genau denselben Text einigen.",
        next: "War dies die erste Position des Parlaments, folgen meist Verhandlungen mit dem Rat. War der Text bereits mit dem Rat ausgehandelt, wird er zum Gesetz, sobald der Rat ihn bestätigt und er im Amtsblatt der EU veröffentlicht ist.",
      },
      CNS: {
        name: "Anhörungsverfahren",
        what: "Das Parlament gibt eine Stellungnahme ab, entscheiden tut aber der Rat allein, oft einstimmig.",
        next: "Der Rat trifft die endgültige Entscheidung. Er muss das Parlament anhören, ist an seine Stellungnahme aber nicht gebunden.",
      },
      APP: {
        name: "Zustimmungsverfahren",
        what: "Das Parlament kann den Text nur als Ganzes annehmen oder ablehnen, ihn aber nicht ändern. Ohne seine Zustimmung kann der Text nicht angenommen werden.",
        next: "Hat das Parlament zugestimmt, kann der Rat den Beschluss fassen. Hat es abgelehnt, kann der Text in dieser Form nicht weiterverfolgt werden.",
      },
      NLE: {
        name: "Nichtlegislatives Verfahren",
        what: "Eine Entscheidung, die kein Gesetz ist, etwa über ein internationales Abkommen oder eine Ernennung. Je nach Fall gibt das Parlament seine Zustimmung oder nur eine Stellungnahme.",
        next: "Die endgültige Entscheidung trifft meist der Rat, unter Berücksichtigung der Abstimmung im Parlament.",
      },
      INI: {
        name: "Initiativbericht",
        what: "Das Parlament legt seine eigene Sicht auf ein Thema dar. Das ist nicht bindend: Niemand ist rechtlich verpflichtet, darauf zu reagieren.",
        next: "Der Bericht geht an die Kommission und die nationalen Regierungen. Er kann künftige Vorschläge beeinflussen, ändert aber für sich genommen kein Recht.",
      },
      INL: {
        name: "Aufforderung zu einem Gesetzesvorschlag",
        what: "Das Parlament fordert die Europäische Kommission auf, ein neues Gesetz vorzuschlagen. Nur die Kommission kann EU-Gesetze formell vorschlagen.",
        next: "Die Kommission hat sich verpflichtet, innerhalb von drei Monaten zu antworten und zu begründen, wenn sie nicht tätig wird.",
      },
      RSP: {
        name: "Entschließung zu einem aktuellen Thema",
        what: "Eine politische Erklärung zu einer aktuellen Frage, oft zu einer Krise, einer Menschenrechtslage oder einem bevorstehenden internationalen Treffen. Sie ist nicht bindend.",
        next: "Die Entschließung geht an die betroffenen Institutionen und Regierungen. Sie drückt die Position des Parlaments aus, schafft aber keine rechtliche Verpflichtung.",
      },
      BUD: {
        name: "Haushaltsverfahren",
        what: "Der jährliche EU-Haushalt, über den Parlament und Rat gemeinsam entscheiden.",
        next: "Beide müssen sich auf dieselben Zahlen einigen. Gelingt das nicht, muss die Kommission einen neuen Entwurf vorlegen.",
      },
      DEC: {
        name: "Haushaltsentlastung",
        what: "Das Parlament prüft, wie der EU-Haushalt eines vergangenen Jahres ausgegeben wurde, und entscheidet, ob es die Rechnung billigt („Entlastung erteilt“) oder die Entscheidung vertagt.",
        next: "Wird die Entlastung vertagt, muss die betroffene Institution vor einer neuen Abstimmung die Fragen des Parlaments beantworten.",
      },
      RPS: {
        name: "Einwand gegen eine Durchführungsmaßnahme",
        what: "Die Kommission erlässt viele technische Regeln selbst. Hier kann das Parlament innerhalb einer Frist Einwände gegen eine davon erheben.",
        next: "Erhebt keine Mehrheit Einwände, kann die Maßnahme in Kraft treten.",
      },
      DEA: {
        name: "Einwand gegen einen delegierten Rechtsakt",
        what: "Die Kommission kann aufgrund von Befugnissen, die ihr ein Gesetz überträgt, detaillierte Regeln erlassen. Das Parlament kann innerhalb einer Frist Einwände erheben.",
        next: "Erhebt keine Mehrheit rechtzeitig Einwände, kann der Rechtsakt in Kraft treten.",
      },
      IMM: {
        name: "Parlamentarische Immunität",
        what: "Eine Entscheidung darüber, ob die Immunität einer oder eines Abgeordneten aufgehoben oder geschützt wird, meist auf Antrag nationaler Behörden. Es ist kein Urteil darüber, ob die Person etwas falsch gemacht hat.",
        next: "Wird die Immunität aufgehoben, kann das nationale Verfahren weitergehen. Wird sie geschützt, kann es vorerst nicht fortgesetzt werden.",
      },
      REG: {
        name: "Geschäftsordnung",
        what: "Eine Änderung der internen Regeln des Parlaments.",
        next: "Die neuen Regeln gelten ab dem im Beschluss festgelegten Datum.",
      },
    },
  },
  nl: {
    title: "Wat voor stemming is dit?",
    type: "Procedure",
    next: "Wat er nu gebeurt",
    passes: "Wanneer een tekst is aangenomen",
    passesText:
      "De meeste stemmingen worden beslist met een gewone meerderheid: meer stemmen voor dan tegen. Onthoudingen tellen in geen enkele richting mee. Sommige beslissingen, zoals bepaalde begrotingsstemmingen, vragen een grotere meerderheid.",
    amendment: "Een stemming over een amendement",
    amendmentText:
      "Een amendement is een voorstel om een deel van een tekst te wijzigen. Deze stemming ging alleen over die wijziging, niet over de tekst als geheel.",
    file: "Volg het dossier in het Wetgevend Observatorium van het Parlement",
    method: "Hoe de gegevens en samenvattingen werken",
    unknown:
      "Elke stemming hoort bij een dossier dat een vaste procedure volgt. Het Wetgevend Observatorium van het Parlement toont hoe ver dit dossier staat.",
    procedures: {
      COD: {
        name: "Gewone wetgevingsprocedure",
        what: "Dit is Europese wetgeving in de maak. Het Parlement en de Raad, waarin de regeringen van de lidstaten zitten, beslissen samen over een voorstel van de Europese Commissie. Beide moeten het eens worden over precies dezelfde tekst.",
        next: "Was dit het eerste standpunt van het Parlement, dan volgen meestal onderhandelingen met de Raad. Was de tekst al met de Raad overeengekomen, dan wordt hij wet zodra de Raad hem bevestigt en hij in het Publicatieblad van de EU verschijnt.",
      },
      CNS: {
        name: "Raadplegingsprocedure",
        what: "Het Parlement geeft zijn advies, maar de Raad beslist alleen, vaak met eenparigheid van stemmen.",
        next: "De Raad neemt de eindbeslissing. Hij moet het Parlement raadplegen, maar hoeft zijn advies niet te volgen.",
      },
      APP: {
        name: "Goedkeuringsprocedure",
        what: "Het Parlement kan de tekst alleen in zijn geheel goedkeuren of verwerpen, niet wijzigen. Zonder zijn goedkeuring kan de tekst niet worden aangenomen.",
        next: "Heeft het Parlement zijn goedkeuring gegeven, dan kan de Raad het besluit aannemen. Heeft het geweigerd, dan kan de tekst in deze vorm niet doorgaan.",
      },
      NLE: {
        name: "Niet-wetgevingsprocedure",
        what: "Een beslissing die geen wet is, bijvoorbeeld over een internationaal akkoord of een benoeming. Afhankelijk van het geval geeft het Parlement zijn goedkeuring of alleen een advies.",
        next: "De eindbeslissing ligt meestal bij de Raad, die rekening houdt met de stemming in het Parlement.",
      },
      INI: {
        name: "Initiatiefverslag",
        what: "Het Parlement geeft zijn eigen standpunt over een onderwerp. Dat is niet bindend: niemand is wettelijk verplicht er gevolg aan te geven.",
        next: "Het verslag gaat naar de Commissie en de nationale regeringen. Het kan toekomstige voorstellen beïnvloeden, maar verandert op zich de wet niet.",
      },
      INL: {
        name: "Verzoek om een wetgevingsvoorstel",
        what: "Het Parlement vraagt de Europese Commissie een nieuwe wet voor te stellen. Alleen de Commissie kan formeel Europese wetten voorstellen.",
        next: "De Commissie heeft beloofd binnen drie maanden te antwoorden en uit te leggen waarom als ze er geen gevolg aan geeft.",
      },
      RSP: {
        name: "Resolutie over een actueel onderwerp",
        what: "Een politieke verklaring over een actuele kwestie, vaak een crisis, een mensenrechtensituatie of een komende internationale bijeenkomst. Ze is niet bindend.",
        next: "De resolutie gaat naar de betrokken instellingen en regeringen. Ze geeft het standpunt van het Parlement weer, maar schept geen wettelijke verplichting.",
      },
      BUD: {
        name: "Begrotingsprocedure",
        what: "De jaarlijkse EU-begroting, waarover het Parlement en de Raad samen beslissen.",
        next: "Beide moeten het eens worden over dezelfde bedragen. Lukt dat niet, dan moet de Commissie een nieuwe ontwerpbegroting voorleggen.",
      },
      DEC: {
        name: "Kwijting",
        what: "Het Parlement controleert hoe de EU-begroting van een vorig jaar werd besteed en beslist of het de rekeningen goedkeurt (\"kwijting verleent\") of die beslissing uitstelt.",
        next: "Wordt de kwijting uitgesteld, dan moet de betrokken instelling eerst de vragen van het Parlement beantwoorden voor er opnieuw wordt gestemd.",
      },
      RPS: {
        name: "Bezwaar tegen een uitvoeringsmaatregel",
        what: "De Commissie stelt veel technische regels zelf vast. Hier kan het Parlement binnen een termijn bezwaar maken tegen een van die regels.",
        next: "Maakt geen meerderheid bezwaar, dan kan de maatregel in werking treden.",
      },
      DEA: {
        name: "Bezwaar tegen een gedelegeerde handeling",
        what: "De Commissie kan gedetailleerde regels vaststellen op basis van bevoegdheden die een wet haar geeft. Het Parlement kan daar binnen een vaste termijn bezwaar tegen maken.",
        next: "Maakt geen meerderheid op tijd bezwaar, dan kan de handeling in werking treden.",
      },
      IMM: {
        name: "Parlementaire immuniteit",
        what: "Een beslissing over het opheffen of verdedigen van de immuniteit van een lid, meestal op verzoek van nationale autoriteiten. Het is geen oordeel over de vraag of het lid iets verkeerd heeft gedaan.",
        next: "Wordt de immuniteit opgeheven, dan kan de nationale procedure verdergaan. Wordt ze verdedigd, dan kan die voorlopig niet doorgaan.",
      },
      REG: {
        name: "Reglement",
        what: "Een wijziging van de interne regels van het Parlement.",
        next: "De nieuwe regels gelden vanaf de datum die in het besluit is vastgelegd.",
      },
    },
  },
  es: {
    title: "¿Qué tipo de votación es esta?",
    type: "Procedimiento",
    next: "Qué pasa después",
    passes: "Cuándo se aprueba un texto",
    passesText:
      "La mayoría de las votaciones se deciden por mayoría simple: más votos a favor que en contra. Las abstenciones no cuentan en ningún sentido. Algunas decisiones, como ciertas votaciones presupuestarias, requieren una mayoría más amplia.",
    amendment: "Una votación sobre una enmienda",
    amendmentText:
      "Una enmienda es una propuesta para cambiar una parte de un texto. Esta votación decidió solo sobre ese cambio, no sobre el texto en su conjunto.",
    file: "Seguir el expediente en el Observatorio Legislativo del Parlamento",
    method: "Cómo funcionan los datos y los resúmenes",
    unknown:
      "Cada votación forma parte de un expediente que sigue un procedimiento fijo. El Observatorio Legislativo del Parlamento muestra en qué punto está.",
    procedures: {
      COD: {
        name: "Procedimiento legislativo ordinario",
        what: "Es una ley europea en preparación. El Parlamento y el Consejo, donde se sientan los gobiernos de los Estados miembros, deciden juntos sobre una propuesta de la Comisión Europea. Ambos deben ponerse de acuerdo sobre exactamente el mismo texto.",
        next: "Si era la primera posición del Parlamento, suelen seguir negociaciones con el Consejo. Si el texto ya se había acordado con el Consejo, se convierte en ley cuando el Consejo lo confirma y se publica en el Diario Oficial de la UE.",
      },
      CNS: {
        name: "Procedimiento de consulta",
        what: "El Parlamento da su opinión, pero el Consejo decide solo, a menudo por unanimidad.",
        next: "El Consejo toma la decisión final. Debe consultar al Parlamento, pero no está obligado a seguir su opinión.",
      },
      APP: {
        name: "Procedimiento de aprobación",
        what: "El Parlamento solo puede aprobar o rechazar el texto en su conjunto, sin modificarlo. Sin su aprobación, el texto no puede adoptarse.",
        next: "Si el Parlamento dio su aprobación, el Consejo puede adoptar la decisión. Si la denegó, el texto no puede seguir adelante en esta forma.",
      },
      NLE: {
        name: "Procedimiento no legislativo",
        what: "Una decisión que no es una ley, por ejemplo sobre un acuerdo internacional o un nombramiento. Según el caso, el Parlamento da su aprobación o solo su opinión.",
        next: "La decisión final suele tomarla el Consejo, teniendo en cuenta la votación del Parlamento.",
      },
      INI: {
        name: "Informe de propia iniciativa",
        what: "El Parlamento expone su propia posición sobre un tema. No es vinculante: nadie está legalmente obligado a darle curso.",
        next: "El informe se envía a la Comisión y a los gobiernos nacionales. Puede influir en futuras propuestas, pero no cambia la ley por sí solo.",
      },
      INL: {
        name: "Petición de propuesta legislativa",
        what: "El Parlamento pide a la Comisión Europea que proponga una nueva ley. Solo la Comisión puede proponer formalmente leyes europeas.",
        next: "La Comisión se ha comprometido a responder en un plazo de tres meses y a explicar sus motivos si no le da curso.",
      },
      RSP: {
        name: "Resolución sobre un tema de actualidad",
        what: "Una declaración política sobre una cuestión de actualidad, a menudo una crisis, una situación de derechos humanos o una próxima reunión internacional. No es vinculante.",
        next: "La resolución se envía a las instituciones y gobiernos afectados. Expresa la posición del Parlamento, pero no crea obligaciones jurídicas.",
      },
      BUD: {
        name: "Procedimiento presupuestario",
        what: "El presupuesto anual de la UE, que el Parlamento y el Consejo deciden juntos.",
        next: "Ambos deben acordar las mismas cifras. Si no lo consiguen, la Comisión debe presentar un nuevo proyecto de presupuesto.",
      },
      DEC: {
        name: "Aprobación de la gestión presupuestaria",
        what: "El Parlamento comprueba cómo se gastó el presupuesto de la UE de un año anterior y decide si aprueba las cuentas (\"aprueba la gestión\") o aplaza esa decisión.",
        next: "Si se aplaza, la institución afectada debe responder a las preguntas del Parlamento antes de una nueva votación.",
      },
      RPS: {
        name: "Objeción a una medida de ejecución",
        what: "La Comisión adopta por sí misma muchas normas técnicas. Aquí, el Parlamento puede oponerse a una de ellas dentro de un plazo.",
        next: "Si ninguna mayoría se opone, la medida puede entrar en vigor.",
      },
      DEA: {
        name: "Objeción a un acto delegado",
        what: "La Comisión puede adoptar normas detalladas gracias a poderes delegados por una ley. El Parlamento puede oponerse a ellas dentro de un plazo fijado.",
        next: "Si ninguna mayoría se opone a tiempo, el acto puede entrar en vigor.",
      },
      IMM: {
        name: "Inmunidad parlamentaria",
        what: "Una decisión sobre si se suspende o se defiende la inmunidad de un eurodiputado, normalmente a petición de las autoridades nacionales. No es un juicio sobre si el eurodiputado hizo algo mal.",
        next: "Si se suspende la inmunidad, el procedimiento nacional puede continuar. Si se defiende, no puede avanzar por ahora.",
      },
      REG: {
        name: "Reglamento interno",
        what: "Un cambio en las normas internas del Parlamento.",
        next: "Las nuevas normas se aplican desde la fecha fijada en la decisión.",
      },
    },
  },
  it: {
    title: "Che tipo di votazione è?",
    type: "Procedura",
    next: "Cosa succede dopo",
    passes: "Quando un testo è approvato",
    passesText:
      "La maggior parte delle votazioni si decide a maggioranza semplice: più voti favorevoli che contrari. Le astensioni non contano in nessun senso. Alcune decisioni, come certe votazioni sul bilancio, richiedono una maggioranza più ampia.",
    amendment: "Una votazione su un emendamento",
    amendmentText:
      "Un emendamento è una proposta di modifica di una parte di un testo. Questa votazione ha deciso solo su quella modifica, non sul testo nel suo insieme.",
    file: "Seguire il fascicolo sull'Osservatorio legislativo del Parlamento",
    method: "Come funzionano i dati e i riassunti",
    unknown:
      "Ogni votazione fa parte di un fascicolo che segue una procedura precisa. L'Osservatorio legislativo del Parlamento mostra a che punto è.",
    procedures: {
      COD: {
        name: "Procedura legislativa ordinaria",
        what: "È una legge europea in preparazione. Il Parlamento e il Consiglio, dove siedono i governi degli Stati membri, decidono insieme su una proposta della Commissione europea. Entrambi devono accordarsi esattamente sullo stesso testo.",
        next: "Se era la prima posizione del Parlamento, di solito seguono negoziati con il Consiglio. Se il testo era già stato concordato con il Consiglio, diventa legge quando il Consiglio lo conferma e viene pubblicato nella Gazzetta ufficiale dell'UE.",
      },
      CNS: {
        name: "Procedura di consultazione",
        what: "Il Parlamento esprime un parere, ma decide da solo il Consiglio, spesso all'unanimità.",
        next: "Il Consiglio prende la decisione finale. Deve consultare il Parlamento ma non è obbligato a seguirne il parere.",
      },
      APP: {
        name: "Procedura di approvazione",
        what: "Il Parlamento può solo approvare o respingere il testo nel suo insieme, senza modificarlo. Senza la sua approvazione, il testo non può essere adottato.",
        next: "Se il Parlamento ha dato la sua approvazione, il Consiglio può adottare la decisione. Se l'ha negata, il testo non può andare avanti in questa forma.",
      },
      NLE: {
        name: "Procedura non legislativa",
        what: "Una decisione che non è una legge, per esempio su un accordo internazionale o una nomina. A seconda dei casi, il Parlamento dà la sua approvazione o solo un parere.",
        next: "La decisione finale spetta di solito al Consiglio, tenendo conto del voto del Parlamento.",
      },
      INI: {
        name: "Relazione d'iniziativa",
        what: "Il Parlamento esprime la propria posizione su un tema. Non è vincolante: nessuno è legalmente obbligato a darle seguito.",
        next: "La relazione viene inviata alla Commissione e ai governi nazionali. Può influenzare proposte future, ma da sola non cambia la legge.",
      },
      INL: {
        name: "Richiesta di proposta legislativa",
        what: "Il Parlamento chiede alla Commissione europea di proporre una nuova legge. Solo la Commissione può proporre formalmente leggi europee.",
        next: "La Commissione si è impegnata a rispondere entro tre mesi e a spiegare i motivi se non dà seguito.",
      },
      RSP: {
        name: "Risoluzione su un tema d'attualità",
        what: "Una dichiarazione politica su una questione d'attualità, spesso una crisi, una situazione dei diritti umani o un prossimo incontro internazionale. Non è vincolante.",
        next: "La risoluzione viene inviata alle istituzioni e ai governi interessati. Esprime la posizione del Parlamento ma non crea obblighi giuridici.",
      },
      BUD: {
        name: "Procedura di bilancio",
        what: "Il bilancio annuale dell'UE, che Parlamento e Consiglio decidono insieme.",
        next: "Entrambi devono accordarsi sulle stesse cifre. Se non ci riescono, la Commissione deve presentare un nuovo progetto di bilancio.",
      },
      DEC: {
        name: "Discarico di bilancio",
        what: "Il Parlamento verifica come è stato speso il bilancio dell'UE di un anno passato e decide se approvare i conti (\"concedere il discarico\") o rinviare la decisione.",
        next: "Se il discarico è rinviato, l'istituzione interessata deve rispondere alle domande del Parlamento prima di un nuovo voto.",
      },
      RPS: {
        name: "Obiezione a una misura di esecuzione",
        what: "La Commissione adotta da sola molte norme tecniche. Qui il Parlamento può opporsi a una di esse entro un termine.",
        next: "Se nessuna maggioranza si oppone, la misura può entrare in vigore.",
      },
      DEA: {
        name: "Obiezione a un atto delegato",
        what: "La Commissione può adottare norme dettagliate grazie a poteri delegati da una legge. Il Parlamento può opporsi entro un termine fissato.",
        next: "Se nessuna maggioranza si oppone in tempo, l'atto può entrare in vigore.",
      },
      IMM: {
        name: "Immunità parlamentare",
        what: "Una decisione sulla revoca o sulla difesa dell'immunità di un eurodeputato, di solito su richiesta delle autorità nazionali. Non è un giudizio sul fatto che l'eurodeputato abbia fatto qualcosa di sbagliato.",
        next: "Se l'immunità è revocata, il procedimento nazionale può proseguire. Se è difesa, per ora non può andare avanti.",
      },
      REG: {
        name: "Regolamento interno",
        what: "Una modifica delle regole interne del Parlamento.",
        next: "Le nuove regole si applicano dalla data fissata nella decisione.",
      },
    },
  },
};

export function contextText(locale: Locale) {
  return CONTEXT[locale] ?? CONTEXT.en;
}

// "2023/0123(COD)" -> "COD"
export function procedureCode(reference?: string | null, type?: string | null) {
  const fromRef = reference?.match(/\(([A-Z]{3})\)/)?.[1];
  if (fromRef) return fromRef;
  const t = type?.toUpperCase().trim();
  return t && /^[A-Z]{3}$/.test(t) ? t : null;
}
