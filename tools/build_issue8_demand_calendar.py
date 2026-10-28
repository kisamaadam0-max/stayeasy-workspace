#!/usr/bin/env python3
"""Rebuild manually verified official-page calendar observations (no network/API).

Snapshot read 2026-10-28 for issue #8. Dates are inclusive; school resumption
boundaries are normalized explicitly. Scope clipped to 2026-11-01..2027-10-31.
No demand-level inference. Unknown Gregorian dates remain not_returned.
"""
import csv
import datetime as dt
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/data/2026-10-29-marrakech-demand-calendar-2026-27.csv'
COLLECTED='2026-10-28'
START,END=dt.date(2026,11,1),dt.date(2027,10,31)
FIELDS='date_from date_to event market region type status source collected_at notes'.split()
rows=[]


def add(start,end,event,market,region,source,kind='school holiday',status='confirmed',notes=''):
    if start!='not_returned' and end!='not_returned':
        a,b=dt.date.fromisoformat(start),dt.date.fromisoformat(end)
        if b<START or a>END:return
        if a<START or b>END:notes+='; clipped to issue window; published '+start+'..'+end
        start,end=max(a,START).isoformat(),min(b,END).isoformat()
        assert start<=end
    rows.append(dict(zip(FIELDS,[start,end,event,market,region,kind,status,source,COLLECTED,notes.strip('; ')])))


# France: Service Public explicitly states resumption in the morning.
FR='https://www.service-public.gouv.fr/particuliers/vosdroits/F31952?lang=fr'
for zone,winter,spring in [('A',('2027-02-13','2027-02-28'),('2027-04-10','2027-04-25')),('B',('2027-02-20','2027-03-07'),('2027-04-17','2027-05-02')),('C',('2027-02-06','2027-02-21'),('2027-04-03','2027-04-18'))]:
    for name,a,b in [('Autumn','2026-10-17','2026-11-01'),('Christmas','2026-12-19','2027-01-03'),('Winter',*winter),('Spring',*spring),('Summer','2027-07-03','2027-09-01'),('Autumn 2027','2027-10-23','2027-11-07')]:
        add(a,b,name+' school break','France','Zone '+zone,FR,notes='Inclusive end = day before published resumption; start after classes on published start date; summer resumption 2027-09-02')
    add('2027-05-07','2027-05-07','Ascension school closure','France','Zone '+zone,FR)

# England is not one national school calendar. This council's dates are labelled.
UK='https://www.hertfordshire.gov.uk/services/schools-and-education/at-school/school-term-dates/school-term-dates.aspx'
for a,b,name in [('2026-12-21','2027-01-01','Christmas'),('2027-02-15','2027-02-19','February half-term'),('2027-03-26','2027-04-09','Easter'),('2027-05-31','2027-06-04','May half-term'),('2027-07-23','2027-08-31','Summer'),('2027-10-25','2027-10-29','October half-term')]:
    add(a,b,name+' school break','UK (England)','Hertfordshire council framework only',UK,notes='Published holiday boundaries; other councils/academies/individual schools may differ; weekends not added')
UKBH='https://www.gov.uk/bank-holidays'
for day,name in [('2026-12-25','Christmas Day'),('2026-12-28','Boxing Day substitute'),('2027-01-01','New Year'),('2027-03-26','Good Friday'),('2027-03-29','Easter Monday'),('2027-05-03','Early May bank holiday'),('2027-05-31','Spring bank holiday'),('2027-08-30','Summer bank holiday')]:
    add(day,day,name,'UK (England)','England and Wales',UKBH,'public holiday')

# Madrid: use legal text, not conflicting press release extensions.
ES='https://gestiona.comunidad.madrid/wleg_pub/html/ficheroTemporal_8488.html'
for a,b,name in [('2026-12-23','2027-01-06','Christmas vacation'),('2027-03-20','2027-03-28','Easter vacation'),('2026-11-02','2026-11-02','School public-holiday closure'),('2026-12-07','2026-12-08','School public-holiday closure')]:
    add(a,b,name,'Spain','Madrid publicly funded schools',ES,notes='Legal calendar; press release instead describes broader nonteaching Christmas/Easter intervals; no national generalization')
# Summer end is not dated in the source; do not supply a guessed return date.
add('2027-07-01','not_returned','Summer vacation; end not yet extracted','Spain','Madrid; exclusions for infant schools',ES,notes='Legal text starts vacation July 1; end is day before 2027/28 school starts, no exact return date recorded')

# German regional sample from KMK published table: inclusive first/last days.
DE='https://www.kmk.org/service/ferienregelung/ferienkalender.html'
regions={
'Baden-Wuerttemberg':[('2026-12-23','2027-01-09','Christmas'),('2027-03-25','2027-03-25','Easter closure'),('2027-03-30','2027-04-03','Easter'),('2027-05-18','2027-05-29','Pentecost'),('2027-07-29','2027-09-11','Summer')],
'Bavaria':[('2026-11-02','2026-11-06','Autumn'),('2026-12-24','2027-01-08','Christmas'),('2027-02-08','2027-02-12','Spring'),('2027-03-22','2027-04-02','Easter'),('2027-05-18','2027-05-28','Pentecost'),('2027-08-02','2027-09-13','Summer')],
'Berlin':[('2026-12-23','2027-01-02','Christmas'),('2027-02-01','2027-02-06','Winter'),('2027-03-22','2027-04-02','Easter'),('2027-05-07','2027-05-07','Ascension closure'),('2027-05-18','2027-05-19','Pentecost'),('2027-07-01','2027-08-14','Summer')],
'North Rhine-Westphalia':[('2026-12-23','2027-01-06','Christmas'),('2027-03-22','2027-04-03','Easter'),('2027-05-18','2027-05-18','Pentecost'),('2027-07-19','2027-08-31','Summer')]}
for region,periods in regions.items():
    for a,b,name in periods:add(a,b,name+' school break','Germany',region,DE,notes='KMK inclusive dates; selected 4 states only; other states and autumn 2027 not yet collected')

# Italy: Veneto publishes concrete dated Easter/Carnival periods.
IT='https://www.regione.veneto.it/article-detail?articleGroupId=3059728&articleId=3061491'
for a,b,name in [('2026-12-07','2026-12-07','Immaculate Conception bridge'),('2026-12-24','2027-01-05','Christmas vacation'),('2027-02-08','2027-02-10','Carnival closure'),('2027-03-25','2027-03-30','Easter vacation'),('2027-04-29','2027-04-30','Labour Day bridge')]:
    add(a,b,name,'Italy','Veneto primary/secondary',IT,notes='Regional school suspension, not national travel demand')
for day,name in [('2026-11-01','All Saints'),('2026-12-08','Immaculate Conception'),('2026-12-25','Christmas'),('2026-12-26','St Stephen'),('2027-01-01','New Year'),('2027-01-06','Epiphany'),('2027-04-25','Liberation Day'),('2027-05-01','Labour Day'),('2027-06-02','Republic Day')]:
    add(day,day,name,'Italy','National mandatory holidays listed by Veneto',IT,'public holiday')

NL='https://www.rijksoverheid.nl/themas/onderwijs/schoolvakanties/overzicht-schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2026-2027'
for region,sp,summer in [('North',('2027-02-20','2027-02-28'),('2027-07-10','2027-08-22')),('Central',('2027-02-20','2027-02-28'),('2027-07-17','2027-08-29')),('South',('2027-02-13','2027-02-21'),('2027-07-24','2027-09-05'))]:
    for name,a,b,notes in [('Christmas','2026-12-19','2027-01-03','Mandatory school-calendar dates'),('Spring',*sp,'Official advisory dates; schools may differ'),('May','2027-04-24','2027-05-02','Mandatory week; optional extensions not assumed'),('Summer',*summer,'Mandatory regional school dates')]:
        add(a,b,name+' school break','Netherlands',region,NL,notes=notes)
NL2='https://www.rijksoverheid.nl/themas/onderwijs/schoolvakanties/overzicht-schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2027-2028'
for region,a,b in [('North','2027-10-16','2027-10-24'),('Central','2027-10-16','2027-10-24'),('South','2027-10-23','2027-10-31')]:
    add(a,b,'Autumn school break','Netherlands',region,NL2,notes='Official advisory dates; schools may differ')

BE='https://www.vlaanderen.be/onderwijs-en-vorming/wat-mag-en-moet-op-school/schoolvakanties-vrije-dagen-en-afwezigheden/schoolvakanties'
for a,b,name in [('2026-11-02','2026-11-08','Autumn'),('2026-12-21','2027-01-03','Christmas'),('2027-02-08','2027-02-14','Carnival'),('2027-03-29','2027-04-11','Easter'),('2027-05-06','2027-05-07','Ascension closure'),('2027-07-01','2027-08-31','Summer')]:
    add(a,b,name+' school break','Belgium','Flemish Community',BE)
FWB='https://glatigny.cfwb.be/home/communiques-de-presse/presses/calendrier-des-vacances-pour-l-annee-scolaire-2026-2027.html'
for a,b,name in [('2026-12-21','2027-01-01','Christmas'),('2027-02-22','2027-03-05','Carnival'),('2027-04-26','2027-05-07','Spring')]:
    add(a,b,name+' school break','Belgium','French Community primary/secondary',FWB,status='provisional',notes='Government first-reading announcement; final decree identified but access blocked, not verified here; weekends not added')
for day,name in [('2026-11-02','All Souls school closure'),('2026-11-11','Armistice school closure'),('2027-02-09','Mardi Gras school closure'),('2027-03-29','Easter Monday school closure'),('2027-05-06','Ascension school closure'),('2027-05-17','Pentecost school closure')]:
    add(day,day,name,'Belgium','French Community primary/secondary',FWB,status='provisional',notes='First-reading announcement only; final text not verified')

MA='https://maroc.ma/fr/le-maroc/fetes-nationales-et-religieuses'
for event,hijri in [('Eid al-Fitr 2027','1 Shawwal'),('Eid al-Adha 2027','10 Dhu al-Hijjah')]:
    add('not_returned','not_returned',event,'Morocco (context only)','National',MA,'religious','provisional',notes='Official portal gives '+hijri+' only; 2027 Gregorian date not published in inspected source; moon-sighting dependent; no conversion estimated')
add('not_returned','not_returned','Ramadan 2027','Morocco (context only)','National','https://www.habous.gov.ma/آخر-المقالات','religious','provisional',notes='No 2027 Gregorian start/end located in official ministry announcements; do not extrapolate lunar dates')

for a,b,event,kind,url in [('2026-11-20','2026-11-28','Marrakech International Film Festival','festival','https://marrakech-festival.com/en/home/'),('2027-01-29','2027-01-30','Marrakech Marathon village','sport','https://www.marathonmarrakech.ma/'),('2027-01-31','2027-01-31','Marrakech International Marathon','sport','https://www.marathonmarrakech.ma/'),('2027-04-26','2027-04-28','GITEX Africa','trade fair','https://gitexafrica.com/who-attends')]:
    add(a,b,event,'International / Morocco','Marrakech',url,kind,notes='Published organizer dates only; no attendance or demand impact inferred')

FRBH='https://www.service-public.gouv.fr/particuliers/vosdroits/F2405'
for day,name in [('2027-01-01','New Year'),('2027-03-29','Easter Monday'),('2027-05-01','Labour Day'),('2027-05-06','Ascension'),('2027-05-08','Victory Day'),('2027-05-17','Whit Monday'),('2027-07-14','National Day'),('2027-08-15','Assumption')]:
    add(day,day,name,'France','Metropolitan general case',FRBH,'public holiday')



# Scope amendment on issue #8: public official sources only; no national inference.
CA='https://www.ontario.ca/page/school-year-calendars'
add('2027-03-15','2027-03-19','March break','Canada','Ontario ministry framework',CA)
add('2026-12-21','2027-01-01','Christmas school break','Canada','Ontario ministry framework',CA)
BC='https://westvancouverschools.ca/annual-school-calendars/'
add('2027-03-15','2027-03-29','March break (including Easter)','Canada','British Columbia: West Vancouver district only',BC,notes='District calendar, not province-wide')
add('2027-03-15','2027-03-29','March break range','Canada','Ontario + BC West Vancouver sample',CA+' | '+BC,notes='range: earliest start/latest end across inspected calendars; not a complete provincial census or continuous nationwide closure')
BR='https://www.ribeiraopreto.sp.gov.br/portal/noticia/educacao-municipal-divulga-calendario-escolar-2027'
add('2027-01-04','2027-02-02','Summer school holidays','Brazil','Ribeirao Preto municipal network, Sao Paulo',BR,notes='Municipal scope only; not national summer dates')
add('2027-02-10','2027-02-10','Ash Wednesday school closure','Brazil','Ribeirao Preto municipal network, Sao Paulo',BR)
US='https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/'
for day,name in [('2026-11-26','Thanksgiving'),('2026-12-25','Christmas'),('2027-01-01','New Year')]:
    add(day,day,name,'USA','Federal employees',US,'public holiday',notes='Federal holiday only; does not establish school vacation or a full Thanksgiving week')
LE='https://www.leicester.gov.uk/schools-and-education/term-dates'
for a,b,name in [('2026-12-21','2027-01-01','Christmas'),('2027-02-15','2027-02-19','February half-term'),('2027-03-22','2027-04-02','Easter'),('2027-05-31','2027-06-04','May half-term')]:
    add(a,b,name+' school break','UK (England)','Leicester City maintained/voluntary-controlled schools',LE)
# Summary ranges only for comparable named periods with dated components.
# They describe the sampled regions, never nationwide closures.
for market in ['UK (England)','Germany','Netherlands','Belgium']:
    periods={}
    for r in list(rows):
        if r['market']==market and r['type']=='school holiday' and 'school break' in r['event'] and r['date_from']!='not_returned' and r['date_to']!='not_returned':
            periods.setdefault(r['event'],[]).append(r)
    for event,parts in periods.items():
        if len({r['region'] for r in parts})<2:continue
        add(min(r['date_from'] for r in parts),max(r['date_to'] for r in parts),event+' range',market,'Sample: '+'; '.join(r['region'] for r in parts),' | '.join(sorted({r['source'] for r in parts})),status='provisional' if any(r['status']=='provisional' for r in parts) else 'confirmed',notes='range: earliest start/latest end across listed regions only; intervening dates are not necessarily holidays everywhere; not a complete national census')


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,FIELDS,lineterminator='\n');w.writeheader();w.writerows(sorted(rows,key=lambda r:(r['date_from'],r['market'],r['region'],r['event'])))
    print('Wrote',len(rows),'official-source calendar rows; 0 API calls')


if __name__=='__main__':main()
