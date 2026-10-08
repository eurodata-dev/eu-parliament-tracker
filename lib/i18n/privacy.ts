import type { Locale } from "./config";

type Privacy = { title: string; updated: string; sections: { h: string; p: string }[] };

// {email} is replaced with CONTACT_EMAIL
const PRIVACY: Record<Locale, Privacy> = {
  en: {
    title: "Privacy",
    updated: "Last updated: October 2026",
    sections: [
      { h: "Who is responsible", p: "EU Parliament Tracker is a personal, non-commercial project run by Burhan Elmas (Belgium). For any question about your data, write to {email}." },
      { h: "What is collected", p: "Newsletter: your email address and the language you chose. Contact form: your name, email address and message, which are forwarded to my mailbox. Nothing else: no account, no tracking cookies, no advertising." },
      { h: "Cookies and statistics", p: "A single cookie, lang, remembers your language. Visits are counted with Vercel Web Analytics, which uses no cookies and keeps no personal data." },
      { h: "Why", p: "To send you the weekly email you asked for (based on your consent) and to answer your messages. Your data is never sold or shared for marketing." },
      { h: "Who processes it", p: "Supabase (database, servers in Ireland), Resend (email delivery) and Vercel (hosting). Questions typed on the Ask page and summary requests are sent to Groq to write the answer, so please don't type personal information there." },
      { h: "How long", p: "Your email stays on the list until you unsubscribe, with the link at the bottom of every email. Contact messages are deleted once the conversation is over." },
      { h: "Your rights", p: "You can ask to see, correct or delete your data at any time by writing to {email}. You can also file a complaint with the Belgian Data Protection Authority (dataprotectionauthority.be)." },
    ],
  },
  fr: {
    title: "Confidentialité",
    updated: "Dernière mise à jour : octobre 2026",
    sections: [
      { h: "Responsable", p: "EU Parliament Tracker est un projet personnel et non commercial géré par Burhan Elmas (Belgique). Pour toute question sur vos données, écrivez à {email}." },
      { h: "Données collectées", p: "Newsletter : votre adresse e-mail et la langue choisie. Formulaire de contact : votre nom, votre adresse e-mail et votre message, transmis à ma boîte mail. Rien d'autre : pas de compte, pas de cookies de suivi, pas de publicité." },
      { h: "Cookies et statistiques", p: "Un seul cookie, lang, retient votre langue. Les visites sont comptées avec Vercel Web Analytics, qui n'utilise pas de cookies et ne garde aucune donnée personnelle." },
      { h: "Pourquoi", p: "Pour vous envoyer l'e-mail hebdomadaire que vous avez demandé (sur la base de votre consentement) et pour répondre à vos messages. Vos données ne sont jamais vendues ni utilisées à des fins de marketing." },
      { h: "Qui les traite", p: "Supabase (base de données, serveurs en Irlande), Resend (envoi des e-mails) et Vercel (hébergement). Les questions posées sur la page Questions et les demandes de résumé sont envoyées à Groq pour rédiger la réponse : n'y écrivez donc pas d'informations personnelles." },
      { h: "Durée de conservation", p: "Votre adresse reste sur la liste jusqu'à votre désinscription, avec le lien présent en bas de chaque e-mail. Les messages de contact sont supprimés une fois l'échange terminé." },
      { h: "Vos droits", p: "Vous pouvez à tout moment demander à consulter, corriger ou supprimer vos données en écrivant à {email}. Vous pouvez aussi introduire une plainte auprès de l'Autorité de protection des données (autoriteprotectiondonnees.be)." },
    ],
  },
  de: {
    title: "Datenschutz",
    updated: "Zuletzt aktualisiert: Oktober 2026",
    sections: [
      { h: "Verantwortlich", p: "EU Parliament Tracker ist ein privates, nicht kommerzielles Projekt von Burhan Elmas (Belgien). Bei Fragen zu Ihren Daten schreiben Sie an {email}." },
      { h: "Welche Daten", p: "Newsletter: Ihre E-Mail-Adresse und die gewählte Sprache. Kontaktformular: Ihr Name, Ihre E-Mail-Adresse und Ihre Nachricht, die an mein Postfach weitergeleitet werden. Sonst nichts: kein Konto, keine Tracking-Cookies, keine Werbung." },
      { h: "Cookies und Statistik", p: "Ein einziges Cookie, lang, merkt sich Ihre Sprache. Besuche werden mit Vercel Web Analytics gezählt, das keine Cookies verwendet und keine personenbezogenen Daten speichert." },
      { h: "Zweck", p: "Um Ihnen die gewünschte wöchentliche E-Mail zu senden (auf Grundlage Ihrer Einwilligung) und Ihre Nachrichten zu beantworten. Ihre Daten werden nie verkauft oder für Werbung weitergegeben." },
      { h: "Auftragsverarbeiter", p: "Supabase (Datenbank, Server in Irland), Resend (E-Mail-Versand) und Vercel (Hosting). Fragen auf der Seite Fragen und Anfragen nach Zusammenfassungen werden an Groq gesendet, um die Antwort zu schreiben. Geben Sie dort bitte keine persönlichen Daten ein." },
      { h: "Speicherdauer", p: "Ihre Adresse bleibt auf der Liste, bis Sie sich über den Link am Ende jeder E-Mail abmelden. Kontaktnachrichten werden gelöscht, sobald der Austausch beendet ist." },
      { h: "Ihre Rechte", p: "Sie können jederzeit Auskunft, Berichtigung oder Löschung Ihrer Daten verlangen, indem Sie an {email} schreiben. Sie können auch Beschwerde bei der belgischen Datenschutzbehörde einlegen (dataprotectionauthority.be)." },
    ],
  },
  nl: {
    title: "Privacy",
    updated: "Laatst bijgewerkt: oktober 2026",
    sections: [
      { h: "Verantwoordelijke", p: "EU Parliament Tracker is een persoonlijk, niet-commercieel project van Burhan Elmas (België). Voor vragen over je gegevens kun je schrijven naar {email}." },
      { h: "Welke gegevens", p: "Nieuwsbrief: je e-mailadres en de taal die je koos. Contactformulier: je naam, e-mailadres en bericht, die naar mijn mailbox worden doorgestuurd. Verder niets: geen account, geen trackingcookies, geen reclame." },
      { h: "Cookies en statistieken", p: "Eén cookie, lang, onthoudt je taal. Bezoeken worden geteld met Vercel Web Analytics, dat geen cookies gebruikt en geen persoonsgegevens bewaart." },
      { h: "Waarom", p: "Om je de wekelijkse e-mail te sturen waarom je vroeg (op basis van je toestemming) en om je berichten te beantwoorden. Je gegevens worden nooit verkocht of gedeeld voor marketing." },
      { h: "Wie verwerkt ze", p: "Supabase (database, servers in Ierland), Resend (verzending van e-mails) en Vercel (hosting). Vragen op de pagina Vragen en aanvragen voor samenvattingen worden naar Groq gestuurd om het antwoord te schrijven, typ daar dus geen persoonlijke gegevens." },
      { h: "Hoe lang", p: "Je adres blijft op de lijst tot je je uitschrijft via de link onderaan elke e-mail. Contactberichten worden verwijderd zodra het gesprek afgerond is." },
      { h: "Je rechten", p: "Je kunt op elk moment vragen om je gegevens in te zien, te verbeteren of te wissen door te schrijven naar {email}. Je kunt ook een klacht indienen bij de Gegevensbeschermingsautoriteit (gegevensbeschermingsautoriteit.be)." },
    ],
  },
  es: {
    title: "Privacidad",
    updated: "Última actualización: octubre de 2026",
    sections: [
      { h: "Responsable", p: "EU Parliament Tracker es un proyecto personal y sin ánimo de lucro de Burhan Elmas (Bélgica). Para cualquier pregunta sobre tus datos, escribe a {email}." },
      { h: "Qué se recoge", p: "Boletín: tu dirección de correo y el idioma elegido. Formulario de contacto: tu nombre, tu correo y tu mensaje, que se reenvían a mi buzón. Nada más: sin cuenta, sin cookies de seguimiento, sin publicidad." },
      { h: "Cookies y estadísticas", p: "Una sola cookie, lang, recuerda tu idioma. Las visitas se cuentan con Vercel Web Analytics, que no usa cookies ni guarda datos personales." },
      { h: "Para qué", p: "Para enviarte el correo semanal que pediste (con tu consentimiento) y responder a tus mensajes. Tus datos nunca se venden ni se comparten con fines de marketing." },
      { h: "Quién los trata", p: "Supabase (base de datos, servidores en Irlanda), Resend (envío de correos) y Vercel (alojamiento). Las preguntas de la página Preguntar y las solicitudes de resumen se envían a Groq para redactar la respuesta, así que no escribas datos personales ahí." },
      { h: "Cuánto tiempo", p: "Tu dirección permanece en la lista hasta que te des de baja con el enlace al final de cada correo. Los mensajes de contacto se borran cuando termina la conversación." },
      { h: "Tus derechos", p: "Puedes pedir en cualquier momento ver, corregir o borrar tus datos escribiendo a {email}. También puedes presentar una reclamación ante la autoridad belga de protección de datos (dataprotectionauthority.be)." },
    ],
  },
  it: {
    title: "Privacy",
    updated: "Ultimo aggiornamento: ottobre 2026",
    sections: [
      { h: "Titolare", p: "EU Parliament Tracker è un progetto personale e non commerciale di Burhan Elmas (Belgio). Per qualsiasi domanda sui tuoi dati, scrivi a {email}." },
      { h: "Cosa viene raccolto", p: "Newsletter: il tuo indirizzo email e la lingua scelta. Modulo di contatto: nome, email e messaggio, inoltrati alla mia casella di posta. Nient'altro: nessun account, nessun cookie di tracciamento, nessuna pubblicità." },
      { h: "Cookie e statistiche", p: "Un solo cookie, lang, ricorda la tua lingua. Le visite sono contate con Vercel Web Analytics, che non usa cookie e non conserva dati personali." },
      { h: "Perché", p: "Per inviarti l'email settimanale che hai richiesto (sulla base del tuo consenso) e per rispondere ai tuoi messaggi. I tuoi dati non vengono mai venduti né condivisi per marketing." },
      { h: "Chi li tratta", p: "Supabase (database, server in Irlanda), Resend (invio delle email) e Vercel (hosting). Le domande scritte nella pagina Chiedi e le richieste di riassunto vengono inviate a Groq per scrivere la risposta, quindi non inserire lì dati personali." },
      { h: "Per quanto tempo", p: "Il tuo indirizzo resta nella lista finché non ti disiscrivi con il link in fondo a ogni email. I messaggi di contatto vengono cancellati a conversazione conclusa." },
      { h: "I tuoi diritti", p: "Puoi chiedere in qualsiasi momento di vedere, correggere o cancellare i tuoi dati scrivendo a {email}. Puoi anche presentare un reclamo all'autorità belga per la protezione dei dati (dataprotectionauthority.be)." },
    ],
  },
};

export function privacyText(locale: Locale) {
  return PRIVACY[locale] ?? PRIVACY.en;
}
