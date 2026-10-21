"""Generate complete French and Spanish pages from the English site.

Run after editing dist/index.html. Missing translations fail explicitly so that
new English copy cannot silently appear untranslated in the other languages.
Paper titles and institutional names retain their original names.
"""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://edgar-jimenez-bedolla.github.io'

# English text: (French, Spanish)
COPY = {
'Edgar Jimenez Bedolla — Political Economy': ('Edgar Jimenez Bedolla — Économie politique', 'Edgar Jimenez Bedolla — Economía política'),
'Skip to content': ('Aller au contenu', 'Ir al contenido'),
'Research': ('Recherche', 'Investigación'),
'Teaching': ('Enseignement', 'Docencia'),
'Seminar': ('Séminaire', 'Seminario'),
'Contact': ('Contact', 'Contacto'),
'PhD candidate': ('Doctorant', 'Doctorante'),
'Explore my research': ('Découvrir mes recherches', 'Explorar mi investigación'),
'Download CV': ('Télécharger le CV (anglais)', 'Descargar CV (inglés)'),
'Governance & Regulation Chair': ('Chaire Gouvernance & Régulation', 'Cátedra de Gobernanza y Regulación'),
'DRM · Management & Regulation': ('DRM · Management & Régulation', 'DRM · Gestión y Regulación'),
'Institutional profile': ('Profil institutionnel', 'Perfil institucional'),
'01 / About': ('01 / Présentation', '01 / Presentación'),
'Information.': ('Information.', 'Información.'),
'Influence.': ('Influence.', 'Influencia.'),
'Institutions.': ('Institutions.', 'Instituciones.'),
'I am a PhD candidate at Université Paris-Dauphine–PSL, affiliated with the Governance & Regulation Chair and Dauphine Recherches en Management (DRM). My thesis is supervised by Éric Brousseau.': (
'Je suis doctorant à l’Université Paris-Dauphine–PSL, rattaché à la Chaire Gouvernance & Régulation et à Dauphine Recherches en Management (DRM). Ma thèse est dirigée par Éric Brousseau.',
'Soy doctorante en Université Paris-Dauphine–PSL, adscrito a la Cátedra de Gobernanza y Regulación y a Dauphine Recherches en Management (DRM). Mi tesis está dirigida por Éric Brousseau.'),
'My research focuses on lobbying in the European Union, particularly the role of stakeholder participation and the information exchange during the European Commission public consultations. I use computational text analysis to study how stakeholders’ arguments relate to legislative proposals.': (
'Mes recherches portent sur le lobbying dans l’Union européenne, en particulier sur le rôle de la participation des parties prenantes et des échanges d’informations au cours des consultations publiques de la Commission européenne. J’utilise l’analyse computationnelle de textes pour étudier les liens entre les arguments des participants et les propositions législatives.',
'Mi investigación se centra en el lobbying en la Unión Europea, en particular en el papel de la participación de los actores y el intercambio de información durante las consultas públicas de la Comisión Europea. Utilizo el análisis computacional de textos para estudiar la relación entre sus argumentos y las propuestas legislativas.'),
'My methods combine econometric analysis with natural language processing, structural topic modelling, embeddings, and web scraping in Python and R.': (
'Mes méthodes associent l’analyse économétrique au traitement automatique du langage, aux modèles thématiques structurels, aux embeddings et à la collecte automatisée de données avec Python et R.',
'Mis métodos combinan el análisis econométrico con el procesamiento del lenguaje natural, los modelos estructurales de temas, los embeddings y la extracción automatizada de datos con Python y R.'),
'I hold a Master’s degree in Public Policy from Université Paris 1 Panthéon-Sorbonne. Alongside my research and teaching, I co-organise the': (
'Je suis titulaire d’un master en politiques publiques de l’Université Paris 1 Panthéon-Sorbonne. Parallèlement à mes activités de recherche et d’enseignement, je coorganise le',
'Soy titular de una maestría en Políticas Públicas de Université Paris 1 Panthéon-Sorbonne. Además de mis actividades de investigación y docencia, coorganizo el'),
'Political Economy + AI seminar': ('séminaire Political Economy + AI', 'seminario Political Economy + AI'),
'Policymaking': ('Élaboration des politiques publiques', 'Elaboración de políticas públicas'),
'EU lobbying': ('Lobbying dans l’UE', 'Lobbying en la UE'),
'Public consultations': ('Consultations publiques', 'Consultas públicas'),
'Text as data': ('Textes comme données', 'Textos como datos'),
'02 / Research': ('02 / Recherche', '02 / Investigación'),
'Research & work in progress': ('Recherches & travaux en cours', 'Investigación y trabajos en curso'),
'How do stakeholders make': ('Comment les parties prenantes', '¿Cómo logran los actores'),
'their voices heard?': ('font-elles entendre leur voix ?', 'hacer oír su voz?'),
'Working paper': ('Document de travail', 'Documento de trabajo'),
'With Isac Olave-Cruz and José Carlos Romero Moreno': ('Avec Isac Olave-Cruz et José Carlos Romero Moreno', 'Con Isac Olave-Cruz y José Carlos Romero Moreno'),
'How does the way stakeholders frame their arguments relate to policy outcomes? We analyse position papers submitted to European Commission public consultations and measure their semantic alignment with final legislative proposals.': (
'Quel lien existe-t-il entre le framing utilisé par les parties prenantes et les décisions publiques ? Nous analysons les contributions écrites soumises aux consultations publiques de la Commission européenne et mesurons leur alignement sémantique avec les propositions législatives finales.',
'¿Qué relación existe entre el framing empleado por los actores y las decisiones públicas? Analizamos las contribuciones escritas a las consultas públicas de la Comisión Europea y medimos su alineación semántica con las propuestas legislativas finales.'),
'Request paper': ('Demander le texte', 'Solicitar el artículo'),
'Read abstract': ('Lire le résumé', 'Leer el resumen'),
'This paper examines the relationship between stakeholders’ framing strategies and preference–policy alignment in European Commission policymaking. Using a dataset of position papers submitted during policy drafting, we develop a computational approach to measuring semantic alignment with the Commission’s legislative proposals. Technical regulatory arguments are associated with greater alignment than arguments centred on ethical or broad global concerns. Drawing on the logic of access, we examine how this pattern relates to the Commission’s demand for specialised information and expertise.': (
'Cet article examine les liens entre les stratégies de framing des parties prenantes et l’alignement entre leurs préférences et les propositions de la Commission européenne. À partir d’un corpus de contributions écrites soumises pendant l’élaboration des politiques, nous développons une approche computationnelle pour mesurer l’alignement sémantique avec les propositions législatives. Les arguments techniques et réglementaires sont associés à un alignement plus élevé que ceux centrés sur des préoccupations éthiques ou globales. En nous appuyant sur la logique de l’accès, nous examinons les liens entre ce résultat et la demande d’informations spécialisées et d’expertise de la Commission.',
'Este artículo examina la relación entre las estrategias de framing de los actores y la alineación entre sus preferencias y las propuestas de la Comisión Europea. A partir de un conjunto de contribuciones escritas presentadas durante la elaboración de políticas, desarrollamos un enfoque computacional para medir su alineación semántica con las propuestas legislativas. Los argumentos técnicos y regulatorios se asocian con una mayor alineación que los centrados en preocupaciones éticas o globales. Desde la lógica del acceso, examinamos cómo este patrón se relaciona con la demanda de información especializada y conocimientos técnicos de la Comisión.'),
'Work in progress': ('Travail en cours', 'Trabajo en curso'),
'With Rami Benabdelkrim and Gabriel Benevides': ('Avec Rami Benabdelkrim et Gabriel Benevides', 'Con Rami Benabdelkrim y Gabriel Benevides'),
'This paper examines how stakeholder input relates to the drafting of specifications for Producer Responsibility Organizations (PROs) in France, focusing on CiFREP and open public consultations.': (
'Cet article examine les liens entre les contributions des parties prenantes et l’élaboration des cahiers des charges des éco-organismes en France, à travers la CiFREP et les consultations publiques ouvertes.',
'Este artículo examina la relación entre las aportaciones de los actores y la elaboración de los pliegos de condiciones de las organizaciones de responsabilidad del productor (PRO) en Francia, centrándose en la CiFREP y las consultas públicas abiertas.'),
'Project description': ('Présentation du projet', 'Descripción del proyecto'),
'This paper examines how stakeholder input relates to the drafting of specifications for Producer Responsibility Organizations (PROs) in France. It focuses on two consultation channels: the CiFREP stakeholder advisory commission and open public consultations. Drawing on informational lobbying, we are developing an approach that combines comparisons of draft and final regulatory texts with LLM-assisted analysis of consultation comments. The aim is to identify comments that address provisions revised during the regulatory process and examine the correspondence between stakeholder arguments and textual changes. The project seeks to inform the study of stakeholder participation in environmental regulation.': (
'Cet article examine les liens entre les contributions des parties prenantes et l’élaboration des cahiers des charges des éco-organismes en France. Il porte sur deux canaux de consultation : la commission consultative CiFREP, qui réunit différentes catégories de parties prenantes, et les consultations publiques ouvertes. En nous appuyant sur les travaux sur le lobbying informationnel, nous développons une approche associant la comparaison des projets et des textes réglementaires finaux à l’analyse des commentaires assistée par de grands modèles de langage (LLM). L’objectif est de repérer les commentaires portant sur les dispositions modifiées et d’examiner les correspondances entre les arguments des participants et les révisions des textes. Ce projet vise à éclairer l’étude de la participation des parties prenantes à la réglementation environnementale.',
'Este artículo examina la relación entre las aportaciones de los actores y la elaboración de los pliegos de condiciones de las organizaciones de responsabilidad del productor (PRO) en Francia. Se centra en dos canales de consulta: la comisión consultiva CiFREP, que reúne a distintas categorías de actores, y las consultas públicas abiertas. A partir de la literatura sobre lobbying informacional, estamos desarrollando un enfoque que combina la comparación de borradores y textos regulatorios finales con el análisis de comentarios asistido por grandes modelos de lenguaje (LLM). El objetivo es identificar comentarios que abordan disposiciones modificadas durante el proceso regulatorio y examinar las correspondencias entre los argumentos de los participantes y las revisiones de los textos. El proyecto busca contribuir al estudio de la participación de los actores en la regulación ambiental.'),
'Public participation': ('Participation du public', 'Participación pública'),
'Decision making': ('Prise de décision', 'Toma de decisiones'),
'France': ('France', 'Francia'),
'Early-stage research': ('Projet à un stade préliminaire', 'Proyecto en fase inicial'),
'This early-stage project examines repeated stakeholder participation in European Commission public consultations, focusing on engagement across policy-drafting and adoption-feedback stages.': (
'Ce projet, à un stade préliminaire, porte sur la participation répétée des parties prenantes aux consultations publiques de la Commission européenne, entre l’élaboration des politiques et les retours recueillis après l’adoption par la Commission.',
'Este proyecto, en fase inicial, estudia la participación recurrente de los actores en las consultas públicas de la Comisión Europea, desde la elaboración de políticas hasta los comentarios posteriores a su adopción por la Comisión.'),
'Stakeholder participation': ('Participation des parties prenantes', 'Participación de los actores'),
'European Union': ('Union européenne', 'Unión Europea'),
'03 / Teaching': ('03 / Enseignement', '03 / Docencia'),
'In the classroom': ('Enseignement', 'Docencia'),
'My teaching spans economics and strategy, with courses taught in English and French.': ('Mes enseignements portent sur l’économie et la stratégie, avec des cours dispensés en anglais et en français.', 'Imparto cursos de economía y estrategia, en inglés y francés.'),
'Microeconomics 1': ('Microéconomie 1', 'Microeconomía 1'),
'First-year undergraduate · Paris School of AI · English': ('Licence 1 · Paris School of AI · Anglais', 'Primer año de grado · Paris School of AI · Inglés'),
'Macroeconomics 1': ('Macroéconomie 1', 'Macroeconomía 1'),
'Fundamentals of Strategy': ('Fondamentaux de la stratégie', 'Fundamentos de estrategia'),
'Third-year undergraduate · Université Paris-Dauphine–PSL · English': ('Licence 3 · Université Paris-Dauphine–PSL · Anglais', 'Tercer año de grado · Université Paris-Dauphine–PSL · Inglés'),
'Introduction to Economics': ('Introduction à l’économie', 'Introducción a la economía'),
'First-year undergraduate · Sciences Po · English': ('Licence 1 · Sciences Po · Anglais', 'Primer año de grado · Sciences Po · Inglés'),
'National Accounting': ('Comptabilité nationale', 'Contabilidad nacional'),
'First-year undergraduate · Université Paris 1 Panthéon-Sorbonne · French': ('Licence 1 · Université Paris 1 Panthéon-Sorbonne · Français', 'Primer año de grado · Université Paris 1 Panthéon-Sorbonne · Francés'),
'04 / Academic community': ('04 / Vie scientifique', '04 / Comunidad académica'),
'Co-organised with Vladimir Avetian': ('Coorganisé avec Vladimir Avetian', 'Coorganizado con Vladimir Avetian'),
'An online seminar bringing together researchers working at the intersection of political economy, AI, and computational methods.': ('Un séminaire en ligne réunissant des chercheurs à l’interface de l’économie politique, de l’intelligence artificielle et des méthodes computationnelles.', 'Un seminario en línea que reúne a investigadores en la intersección de la economía política, la inteligencia artificial y los métodos computacionales.'),
'Jointly organised by King’s College London and Université Paris-Dauphine–PSL, the series welcomes research in progress and talks on methods, tools, and research practices.': ('Organisé conjointement par King’s College London et l’Université Paris-Dauphine–PSL, le séminaire accueille des travaux en cours ainsi que des présentations sur les méthodes, les outils et les pratiques de recherche.', 'Organizado conjuntamente por King’s College London y Université Paris-Dauphine–PSL, el seminario acoge trabajos en curso y presentaciones sobre métodos, herramientas y prácticas de investigación.'),
'Selected Mondays · Online': ('Certains lundis · En ligne', 'Lunes seleccionados · En línea'),
'17:30–18:30 Paris / 16:30–17:30 London': ('17h30–18h30 Paris / 16h30–17h30 Londres', '17:30–18:30 París / 16:30–17:30 Londres'),
'Visit the seminar website': ('Consulter le site du séminaire', 'Visitar el sitio del seminario'),
'05 / Contact': ('05 / Contact', '05 / Contacto'),
'Get in touch': ('Me contacter', 'Contacto'),
'For research discussions, seminar invitations, or questions about my work, please contact me by email.': ('Pour échanger sur mes recherches, m’inviter à un séminaire ou me poser une question sur mes travaux, vous pouvez me contacter par courriel.', 'Para conversar sobre mi investigación, invitarme a un seminario o plantear preguntas sobre mi trabajo, puede contactarme por correo electrónico.'),
'Copy email address': ('Copier l’adresse courriel', 'Copiar correo electrónico'),
'Paris, France': ('Paris, France', 'París, Francia'),
'Governance & Regulation profile': ('Profil à la Chaire Gouvernance & Régulation', 'Perfil en la Cátedra de Gobernanza y Regulación'),
'Back to top': ('Retour en haut', 'Volver arriba'),
'Main navigation': ('Navigation principale', 'Navegación principal'),
'Language': ('Langue', 'Idioma'),
'Profile and affiliation': ('Profil et affiliation', 'Perfil y afiliación'),
'Research interests': ('Thèmes de recherche', 'Temas de investigación'),
'Portrait of Edgar Jimenez Bedolla': ('Portrait d’Edgar Jimenez Bedolla', 'Retrato de Edgar Jimenez Bedolla'),
'Edgar Jimenez Bedolla, home': ('Edgar Jimenez Bedolla, accueil', 'Edgar Jimenez Bedolla, inicio'),
'Edgar Jimenez Bedolla is a PhD candidate at Université Paris-Dauphine–PSL. Research on lobbying, framing, and participation in European policymaking.': ('Edgar Jimenez Bedolla est doctorant à l’Université Paris-Dauphine–PSL. Recherches sur le lobbying, le framing et la participation à l’élaboration des politiques européennes.', 'Edgar Jimenez Bedolla es doctorante en Université Paris-Dauphine–PSL. Investigación sobre lobbying, framing y participación en la elaboración de políticas europeas.'),
'Research on lobbying, information, and participation in European policymaking. Université Paris-Dauphine–PSL.': ('Recherches sur le lobbying, l’information et la participation à l’élaboration des politiques européennes. Université Paris-Dauphine–PSL.', 'Investigación sobre lobbying, información y participación en la elaboración de políticas europeas. Université Paris-Dauphine–PSL.'),
}

UNCHANGED = {
'LinkedIn', 'EJB', '.', '↗', '↓', '↑', '+', '/', '⧉', 'PDF', 'EN', 'FR', 'ES', 'English', 'Français', 'Español',
'Edgar Jimenez', 'Bedolla', 'Université Paris-Dauphine–PSL',
'01', '02', '03', '2026', '2022', 'Political Economy', '+ AI',
'edgar.jimenez-bedolla@dauphine.eu', '© 2026 Edgar Jimenez Bedolla',
'Hear me out: Lobbying Frames and Policy Outcomes in the European Union',
'Open vs. Closed Consultation Impact on Decision Making: Evidence from PROs in France',
'I Will Lobby Again: Repeated Stakeholder Participation During European Public Consultations',
}

def translated(text, lang):
    if lang == 'en':
        return text
    key = text.strip()
    if not key:
        return text
    if key in COPY:
        result = COPY[key][0 if lang == 'fr' else 1]
        return text[:len(text)-len(text.lstrip())] + result + text[len(text.rstrip()):]
    if key in UNCHANGED:
        return text
    raise ValueError(f'Missing {lang} translation: {key!r}')

class Localize(HTMLParser):
    def __init__(self, lang):
        super().__init__(convert_charrefs=True)
        self.lang = lang
        self.out = []
    def handle_decl(self, decl):
        self.out.append(f'<!{decl}>')
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            attrs['lang'] = self.lang
        for key in ('aria-label', 'alt'):
            if key in attrs:
                attrs[key] = translated(attrs[key], self.lang)
        if tag == 'meta' and (attrs.get('name') == 'description' or attrs.get('property') in ('og:title','og:description')):
            attrs['content'] = translated(attrs['content'], self.lang)
        if tag == 'meta' and attrs.get('property') == 'og:url':
            attrs['content'] = ORIGIN + ('/' if self.lang == 'en' else f'/{self.lang}/')
        if self.lang != 'en':
            for key in ('src','href'):
                if attrs.get(key) in ('favicon.svg','styles.css','script.js','portrait.jpg','cv/edgar-jimenez-bedolla-cv.pdf'):
                    attrs[key] = '../' + attrs[key]
            if tag == 'h3':
                # Paper titles remain in their original bibliographic language.
                attrs['lang'] = 'en' if 'paper' in self.current_context else self.lang
        if tag == 'article':
            self.current_context = 'paper'
        if tag == 'a' and 'data-language' in attrs:
            if attrs['data-language'] == self.lang:
                attrs['aria-current'] = 'page'
            else:
                attrs.pop('aria-current', None)
        rendered = ''.join(f' {k}' if v is None else f' {k}="{escape(v, quote=True)}"' for k,v in attrs.items())
        self.out.append(f'<{tag}{rendered}>')
    current_context = ''
    def handle_endtag(self, tag):
        self.out.append(f'</{tag}>')
        if tag == 'article':
            self.current_context = ''
    def handle_data(self, data):
        self.out.append(escape(translated(data, self.lang), quote=False))
    def handle_comment(self, data):
        self.out.append(f'<!--{data}-->')

def main():
    page = (ROOT/'index.html').read_text()
    # Replace generated header links, allowing this script to run repeatedly.
    page = re.sub(r'\s*<div class="language-switch".*?</div>', '', page, flags=re.S)
    switcher = '<div class="language-switch" role="group" aria-label="Language"><a href="/" data-language="en" lang="en" hreflang="en" aria-label="English">EN</a><a href="/fr/" data-language="fr" lang="fr" hreflang="fr" aria-label="Français">FR</a><a href="/es/" data-language="es" lang="es" hreflang="es" aria-label="Español">ES</a></div>'
    page = page.replace('</nav>', '</nav>\n      '+switcher, 1)
    page = re.sub(r'\s*<link rel="alternate"[^>]*>', '', page)
    alternates = '\n'.join(f'  <link rel="alternate" hreflang="{lang}" href="{ORIGIN}{path}">' for lang,path in [('en','/'),('fr','/fr/'),('es','/es/'),('x-default','/')])
    page = page.replace('</head>', alternates+'\n</head>')
    # Write only after all three versions have passed translation coverage.
    pages = {}
    for lang in ('en','fr','es'):
        parser = Localize(lang)
        parser.feed(page)
        pages[lang] = ''.join(parser.out)
    for lang, text in pages.items():
        dest = ROOT/('index.html' if lang == 'en' else f'{lang}/index.html')
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    print('Generated English, French, and Spanish pages with complete translation coverage.')

if __name__ == '__main__':
    main()
