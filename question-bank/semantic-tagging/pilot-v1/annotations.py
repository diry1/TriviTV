# Human-readable, manually classified pilot annotations. Not a bulk classifier.
# Short keys: t topic, s subject, f form, y style, a audience, u UK risk,
# e entity kind, l location mention, d decade.
ROWS = []
def a(n,tags,why,entities=(),issues=(),proposals=(),era=()):
    ROWS.append(dict(number=n,tags=tags,rationale=why,entities=list(entities),issues=list(issues),proposals=list(proposals),eraRoles=list(era)))
def ent(surface,role,kind,regions=()):
    return dict(surface=surface,role=role,kind=kind,regions=list(regions))
a(1,'t=animals,plants;s=animal-behaviour;f=identification',
  'Catnip response tests animal behaviour and plant interaction; no specialist audience tag just because the mechanism is biological.',
  issues=['Source explanation is not fact-verified; tagging does not endorse the biological claim.'])
a(2,'t=animals;f=comparison;u=scientific-terminology',
  'Most venomous insect comparison; linked choices contain specialized ant common names.',
  issues=['Check species names and the unqualified most-venomous assertion separately.'])
a(3,'t=philosophy,language;f=missing-word,quote-identification;u=quote-localization;e=historical-figure-name;l=asia',
  'Completing a quotation attributed to Confucius; Chinese is an explicit geographic adjective.',
  [ent('Confucius','prompt','historical-figure-name'),ent('Chinese','prompt','location',['asia'])],
  ['Attribution is source-claimed, not independently verified.'])
a(4,'t=religion;s=mythology;f=identification;u=proper-name-localization',
  'Norse gods and named mythological realms; preserve Arts & Humanities source category.',
  issues=['UK renders Norse as Norwegian; cultural terminology needs review.'],
  proposals=[{'family':'location-mention','value':'europe','reason':'Norse cultural adjective, rather than a direct place reference.'},{'family':'location-mention','value':'europe','reason':'Olympia distractor may be mythological rather than real Greek place.'}])
a(5,'t=language;f=missing-word;u=proverb-localization,idiom',
  'Squeaking-wheel proverb completion depends on an established expression; source-based localization risk.',
  issues=['No linked Ukrainian draft; UK risk inferred from English only.'])
a(6,'t=animals;f=riddle',
  'Birds remaining after gunfire is a situational riddle, not ordinary subtraction.',
  issues=['Assumes surviving birds fly away; preserve existing human Keep decision.'])
a(7,'t=movies,music;s=celebrity-biography;f=identification;e=movie-title;u=title-localization;d=2000s',
  'Identify a 2009 biographical film; do not classify all musical works in distractors as film titles.',
  [ent('Notorious','choice:0','movie-title')],era=[{'value':'2000s','role':'work-release','evidence':'2009 movie'}])
a(8,'t=music;s=song-lyrics;f=missing-word;u=quote-localization,answer-distinction;e=song-title',
  'Missing English lyric is tested while answer words are translated into Ukrainian; check grammatical and semantic correspondence.',
  [ent('I Dont Want To Miss A Thing','prompt','song-title')])
a(9,'t=movies,actors;s=screen-characters;f=identification;e=movie-title;u=title-localization,character-name;d=1980s',
  'Cast-to-character mapping for explicitly dated 1980 film.',
  [ent('Popeye','prompt','movie-title')],era=[{'value':'1980s','role':'work-release','evidence':'1980 movie'}])
a(10,'t=comics;f=biography-detail;u=character-name;a=specialist-knowledge',
  'Requires a particular FoxTrot family detail, consistent with saved obscure/niche Exclude feedback.',
  issues=['Comic-title entity kind is a vocabulary proposal; do not misuse book-title.'],
  proposals=[{'family':'entity-kind','value':'comic-title','reason':'FoxTrot is explicitly a comic.'}])
a(11,'t=religion;s=mythology;f=identification',
  'Identify the nymph in a Zeus/Hera myth, despite General Knowledge source category.',
  issues=['No Ukrainian draft; character-name localization would be source-only risk if translated.'])
a(12,'t=language;f=definition;u=english-spelling,answer-distinction',
  'Options are near-identical English spellings of addressable; translated definition does not remove English-spelling dependence.')
a(13,'t=geography;s=us-states;f=identification;a=us-specific;l=usa,north-america;u=proper-name-localization',
  'Detailed US valley/range-to-state knowledge, not merely a US mention.',
  [ent('Big Smoky Valley','prompt','location',['usa','north-america']),ent('Toiyabe Range','prompt','location',['usa','north-america']),ent('Toquima Range','prompt','location',['usa','north-america'])]+[ent(x,'choice:'+str(i),'location',['usa','north-america']) for i,x in enumerate(['Nevada','Minnesota','Indiana','Oregon'])])
a(14,'t=geography;f=comparison;l=usa,north-america,oceania,africa;u=proper-name-localization',
  'Worldwide mountain-height comparison; US distractor/correct-option mention is not US-specific audience knowledge.',
  [ent('Mount McKinley','choice:0','location',['usa','north-america']),ent('Puncak Jaya','choice:1','location',['oceania']),ent('Mount Kilimanjaro','choice:3','location',['africa'])],
  issues=['Do not treat historical McKinley/Denali naming as an answer correction during tagging.'],
  proposals=[{'family':'location-mention','value':'europe','reason':'Mount Elbrus needs explicit Europe/Asia boundary convention.'},{'family':'location-mention','value':'asia','reason':'Mount Elbrus boundary convention unresolved.'}])
a(15,'t=history,religion;s=warfare;f=identification;e=historical-figure-name;u=proper-name-localization',
  'Identify a rebellion from a named leader and religious claim; no inferred decade or region from unstated external history.',
  [ent('Hong Xiuquan','prompt','historical-figure-name')],
  proposals=[{'family':'location-mention','value':'asia','reason':'Taiping/Opium conflicts require external referent resolution; not explicit place strings.'},{'family':'location-mention','value':'europe','reason':'Turko-Russian War distractor has transregional historical scope.'}])
a(16,'t=history,science;s=space;f=event-detail',
  'Identify fatal space mission from narrative; no explicit event year.',
  issues=['Prompt calls a Soyuz choice a space station; possible source terminology/factual issue, not a UK-only error.'],
  proposals=[{'family':'era','value':'1970s','reason':'Requires externally checking mission date; do not infer from category.'}])
a(17,'t=food,geography;s=countries;f=identification;l=asia,europe',
  'Food-origin question with explicit countries in all choices; American in a dish name alone is not a USA-audience tag.',
  [ent('Thailand','choice:0','location',['asia']),ent('China','choice:1','location',['asia']),ent('Italy','choice:2','location',['europe']),ent('France','choice:3','location',['europe'])],
  proposals=[{'family':'location-mention','value':'usa','reason':'American fried rice is a dish name; country referent not asserted by the name alone.'}])
a(18,'t=food,plants;f=identification;l=asia',
  'Identify a spice from culinary and plant properties; 1000 years is a duration, not a dated era.',
  [ent('Asia','prompt','location',['asia'])])
a(19,'t=books;f=event-detail;e=book-title;u=title-localization,character-name;a=specialist-knowledge',
  'Detailed plot transaction in The Wind in the Willows; no factual animal topic from fictional Toad.',
  [ent('The Wind in the Willows','prompt','book-title')],
  ['Check title and character-name consistency, plus dated ethnic wording in source and UK.'])
a(20,'t=books;f=identification;e=book-title;u=title-localization,character-name,answer-distinction',
  'Named fictional mouse with deliberately similar distractor names; title and character spellings need localization attention.',
  [ent('Prince Caspian','prompt','book-title')])
a(21,'t=books;f=identification;e=book-title;u=title-localization,character-name',
  'Stephen King work identification; the category says literature but the correct Silver Bullet work type needs verification.',
  [ent('The Stand','choice:1','book-title'),ent('Bag of Bones','choice:2','book-title'),ent('Night Shift','choice:3','book-title')],
  ['Silver Bullet may be an adaptation title rather than the story title; verify source before changing anything.'],
  proposals=[{'family':'entity-kind','value':'movie-title','reason':'Silver Bullet work type needs reference check.'},{'family':'entity-kind','value':'book-title','reason':'Silver Bullet source calls it a story, but relation is unresolved.'}])
a(22,'t=books;f=identification;e=book-title;u=title-localization,character-name',
  'Character detail in explicitly named novel; Ukrainian title looks semantically suspicious and needs reference checking.',
  [ent('The Amber Spyglass','prompt','book-title')],
  ['UK title Янтарний шпигун and John Parry→Джон Гаррі require title/name checking; no replacement invented.'])
a(23,'t=movies;f=identification;e=movie-title;u=title-localization;d=1990s,2000s;l=europe,usa,north-america',
  'Explicit 1997 original/2008 remake eras. Austrian refers to Europe; Louisiana occurs only within a distractor title, not required US knowledge.',
  [ent(x,'choice:'+str(i),'movie-title') for i,x in enumerate(['Funny Games','Ambrose, Louisiana','The Omen','The Echo'])]+[ent('Austrian','prompt','location',['europe']),ent('Louisiana','choice:1','location-in-title',['usa','north-america'])],
  era=[{'value':'1990s','role':'work-release','evidence':'1997 Austrian film'},{'value':'2000s','role':'work-release','evidence':'2008 movie'}])
a(24,'t=movies,actors;s=screen-characters;f=identification;e=movie-title;u=title-localization,character-name;a=specialist-knowledge',
  'Actor cross-credit detail across two works; source calls both movie but The Tommyknockers work type needs review.',
  [ent('12 Angry Men','prompt','movie-title')],
  ['The Tommyknockers could refer to a television adaptation; entity type not confirmed.'],
  proposals=[{'family':'entity-kind','value':'television-title','reason':'The Tommyknockers adaptation type needs verification.'}])
a(25,'t=music;f=identification;a=specialist-knowledge;u=proper-name-localization',
  'Band membership and festival-performance detail; America is a band option, not a location mention.',
  proposals=[{'family':'era','value':'1960s','reason':'Festival era requires reference, not explicitly dated.'},{'family':'location-mention','value':'usa','reason':'Monterey Pop Festival contains a place name, referent not independently resolved in this pilot.'}])
a(26,'t=music;s=celebrity-biography;f=biography-detail;e=song-title;d=1970s',
  'Explicit musical icon from the 70s; identifies performer using spouse and hit song.',
  [ent('Youre So Vain','prompt','song-title')],era=[{'value':'1970s','role':'subject-active-period','evidence':'musical icon from the 70s'}])
a(27,'t=history,geography;f=identification;e=historical-figure-name;l=europe,south-america,asia;u=proper-name-localization',
  'Exploration history with explicit South America, Asia and European/Italian origin; no invented decade.',
  [ent(x,'choice:'+str(i),'historical-figure-name') for i,x in enumerate(['Amerigo Vespucci','Marco Polo','Christopher Columbus','Ferdinand Magellan'])]+[ent('South America','prompt','location',['south-america']),ent('Asia','prompt','location',['asia']),ent('Italian','prompt','location',['europe']),ent('European','prompt','location',['europe'])])
a(28,'t=history;f=biography-detail;e=historical-figure-name;u=proper-name-localization;a=specialist-knowledge',
  'Political historical figure and ethnic affiliation detail; ethnicity does not itself assert residence or place.',
  [ent('Idi Amin','prompt','historical-figure-name')],proposals=[{'family':'subject','value':'ethnic-groups','reason':'Potential reusable subject, needs broader examples.'}])
a(29,'t=religion;f=biography-detail;u=proper-name-localization',
  'Relationship between religious figures; religion kept in full master despite excluded regional pools.',
  issues=['Do not treat scriptural figures as independently verified historical persons; entity-kind withheld.'])
a(30,'t=religion,geography;s=cities;f=identification;l=asia,europe;u=proper-name-localization',
  'Religious city identification with real cities in all choices, not an audience-specific label.',
  [ent('Jerusalem','choice:0','location',['asia']),ent('Constantinople','choice:1','location',['europe']),ent('Medina','choice:2','location',['asia']),ent('Mecca','choice:3','location',['asia'])],
  issues=['Constantinople tagged for historic city core; do not silently extend to both banks of modern Istanbul. No political status claim.'])
a(31,'t=science;s=chemistry;f=comparison;u=scientific-terminology',
  'Relative lightness of metal elements; basic chemistry does not automatically mean specialist knowledge.')
a(32,'t=science;s=anatomy;f=number-recall;u=missing-context',
  'Exact tooth count is asked without adult/child or wisdom-teeth qualification in either language.',
  issues=['Missing adult/dentition scope is a source-context issue as well as a localization risk.'])
a(33,'t=sport;s=us-sports-leagues;f=negative-question;a=us-specific;e=brand-name;l=usa,north-america;u=proper-name-localization',
  'Historical New York Mets roster detail requires US-league familiarity.',
  [ent('New York Mets','prompt','brand-name'),ent('New York','prompt','location-in-team-name',['usa','north-america'])])
a(34,'t=sport,geography;s=countries;f=event-detail;l=europe,usa,north-america;u=proper-name-localization',
  'Figure-skating first achievement; explicit United States is merely a distractor, not US-specific knowledge.',
  [ent('Sweden','choice:0','location',['europe']),ent('United States','choice:1','location',['usa','north-america']),ent('Ukraine','choice:2','location',['europe'])],
  proposals=[{'family':'location-mention','value':'asia','reason':'Russia distractor is transcontinental; apply explicit multi-region convention before publishing.'}])
a(35,'t=television;s=screen-characters;f=biography-detail;e=television-title;u=title-localization,character-name',
  'Occupation of a fictional television character; no US-audience label solely because show originated there.',
  [ent('Two and a Half Men','prompt','television-title')],
  issues=['Pilot consistency pass uses screen-characters for both film and television.'])
a(36,'t=television,business;f=identification;e=television-title,brand-name;u=title-localization;a=specialist-knowledge',
  'Production-company credit for named show, a specialist credit detail.',
  [ent('St. Elsewhere','prompt','television-title'),ent('MTM','choice:0','brand-name'),ent('Miramar Productions','choice:2','brand-name')],
  issues=['Do not assert every company-like distractor is a real brand; Windevil and SKG identities unresolved.'])
a(37,'t=video-games;s=cities;f=identification;e=video-game-title;u=proper-name-localization;l=usa,north-america',
  'Game setting location; New York/Toronto distractors give location mentions without US-audience judgement.',
  [ent('Halo 3 ODST','prompt','video-game-title'),ent('Toronto','choice:2','location',['north-america']),ent('New York','choice:3','location',['usa','north-america'])],
  proposals=[{'family':'location-mention','value':'africa','reason':'New Mombasa is fictional; Voi real/fictional referent needs checking in game context.'}])
a(38,'t=video-games,business;f=negative-question;e=video-game-title,brand-name',
  'Publisher identification with explicitly named Nintendo and four game works.',
  [ent('Nintendo','prompt','brand-name')]+[ent(x,'choice:'+str(i),'video-game-title') for i,x in enumerate(['Assassins Creed','Warioware','Mario Galaxy','Star Fox'])])
a(39,'t=history,geography;f=date-recall;l=europe;d=1920s',
  'Year of state establishment; only canonical answer 1929 supplies the answer-era, not distractor decades.',
  [ent('Vatican City','prompt','location',['europe'])],era=[{'value':'1920s','role':'event-year','evidence':'correct choice 1929'}])
a(40,'t=customs,language;f=quote-identification;u=quote-localization,idiom;l=europe',
  'Regional Halloween phrase rather than religion; quoted wording and rhyming alternatives need localization review.',
  [ent('Scotland','prompt','location',['europe'])],
  ['Source says trick-or-threat; UK phrase changes meaning strongly. Source phrase correctness and translated rhyme require separate review.'])
a(41,'t=language,food;f=wordplay;y=humor;u=wordplay,answer-distinction;l=europe',
  'Wurst/worst pun, not ordinary German food knowledge; Ukrainian choices appear to blur distinct English wrong answers.',
  [ent('German','prompt','location',['europe'])],
  ['Source best/pits/worst alternatives and UK найкращі/найгірші/провал need answer-order semantic review; canonical index preserved.'])
a(42,'t=movies,history,sport;f=identification;e=movie-title,historical-figure-name;u=title-localization;l=africa;d=2000s',
  'Identify explicitly dated film about Mandela/rugby; African setting is explicit, not an inferred audience restriction.',
  [ent(x,'choice:'+str(i),'movie-title') for i,x in enumerate(['Invictus','The Objective','Scrum','A Serious Man'])]+[ent('Nelson Mandela','prompt','historical-figure-name'),ent('South African','prompt','location',['africa'])],
  era=[{'value':'2000s','role':'work-release','evidence':'2009 film'}])
a(43,'t=books,history,politics;s=us-presidents;f=negative-question;e=book-title,historical-figure-name;u=title-localization;l=usa,north-america;d=1980s;a=specialist-knowledge',
  'Novel-detail knowledge, not simply a US-presidents fact question. Release year and Civil War setting must remain separate.',
  [ent('Lincoln','prompt','book-title'),ent('Lincoln','prompt','historical-figure-name'),ent('American Civil War','choice:1','location-in-event',['usa','north-america'])],
  era=[{'value':'1980s','role':'work-release','evidence':'published in 1984'}])
a(44,'t=geography;s=landmarks,us-states;f=identification;a=us-specific;l=usa,north-america;u=proper-name-localization',
  'Detailed infrastructure between Michigan peninsulas, unlike a globally comparative geography question.',
  [ent('Michigan','prompt','location',['usa','north-america']),ent('The Mackinac Bridge','choice:0','location',['usa','north-america']),ent('The Ambassador Bridge','choice:1','location',['usa','north-america'])],
  issues=['Other two bridge/tunnel-like options not asserted as real named places.'])
a(45,'t=geography;s=countries;f=identification;l=africa;u=proper-name-localization',
  'Lake/river and explicit African countries across all four options.',
  [ent('Nile','prompt','location',['africa']),ent('Lake Victoria','prompt','location',['africa'])]+[ent(x,'choice:'+str(i),'location',['africa']) for i,group in enumerate([['Uganda','Kenya','Tanzania'],['Sudan','Ethiopia','Kenya'],['Zambia','Angola','Sudan'],['Egypt','Morocco','Zimbabwe']]) for x in group],
  issues=['No rivers/lakes subject in v2; retain geography and propose reusable subject.'],proposals=[{'family':'subject','value':'rivers-and-lakes','reason':'Explicit Nile/Lake Victoria; useful reusable geography facet.'}])
a(46,'t=sport;s=celebrity-biography;f=date-recall;a=us-specific;e=brand-name;u=proper-name-localization;d=1970s',
  'US promotion debut-year detail; US-specific aligns with saved user Exclude feedback. Only correct 1979 supplies era.',
  [ent('World Wrestling Federation','prompt','brand-name')],era=[{'value':'1970s','role':'event-year','evidence':'correct choice 1979'}])
a(47,'t=animals,hobbies;f=negative-question;e=brand-name;u=proper-name-localization;a=specialist-knowledge',
  'Knowledge of an attraction exhibit roster, not a general animal-habitat fact. Wild Arctic is an exhibit name, not proof of an actual Arctic location.',
  [ent('SeaWorld','prompt','brand-name')],
  proposals=[{'family':'location-mention','value':'usa','reason':'Attraction location unstated; do not infer just from brand.'}])
a(48,'t=movies,actors,history;s=film-awards,oscars;f=event-detail;e=historical-figure-name;u=proper-name-localization;d=1990s',
  'Award/character identification in explicit 1999 ceremony; do not assign Elizabethan era to the award question.',
  [ent('Queen Elizabeth I','choice:0','historical-figure-name'),ent('Joan of Arc','choice:1','historical-figure-name')],
  proposals=[{'family':'entity-kind','value':'historical-figure-name','reason':'Virginia Woolf literary/historical boundary requires consistent scope; religious Virgin Mary historicity not assumed.'}],
  era=[{'value':'1990s','role':'award-year','evidence':'Academy Awards in 1999'}])
a(49,'t=television,music;f=identification;e=television-title,song-title;u=title-localization,answer-distinction',
  'TV episode recreating a song; Georgia in song title is ambiguous without reference. UK fourth option differs in title from English.',
  [ent('The Devil Went Down to Georgia','prompt','song-title')]+[ent(x,'choice:'+str(i),'television-title') for i,x in enumerate(['The Muppets','The Simpsons','Arthur','Family Guy'])],
  ['UK Georgia is rendered Грузію; verify intended US-state/country referent. Family Guy→Американський тато is a potential distinct-show mismatch; no correction applied.'],
  proposals=[{'family':'location-mention','value':'usa','reason':'Georgia song-title referent needs checking, not guessed from translation.'},{'family':'location-mention','value':'asia','reason':'Country Georgia is an alternative possible referent, not a definite tag.'}])
a(50,'t=business,history;f=identification;e=brand-name;d=1940s',
  'Company split and brand identification with explicit 1948 event; no country mentioned and no automatic US audience tag.',
  [ent('Adidas','prompt','brand-name')]+[ent(x,'choice:'+str(i),'brand-name') for i,x in enumerate(['Puma','Kenvelo','Umbro','Reebok'])],
  era=[{'value':'1940s','role':'event-year','evidence':'In 1948'}])
