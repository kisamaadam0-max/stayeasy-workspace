#!/usr/bin/env python3
"""Issue #8 only: SerpApi Google Hotels lists + two optional own-hotel details.

Depends on price_parity.py/shared ledger from PR #7. Hard 30 issue attempts,
200/month shared cap (also retain ledger's 20/property guard). No API retries.
No personal/contact data; private sanitized resume cache stays outside Git.
Demand-calendar build is a separate offline script and never calls this API.
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
PREFIX='2026-10-29'
SOURCE='serpapi_google_hotels'
OWN_TOKEN='ChkI-tGC66yYwJwzGg0vZy8xMW5iNXFqcTlyEAE'
ORIGIN=(31.615070,-7.977506)
STAYS=[('2026-11-12',2),('2026-11-26',2),('2026-12-10',2),('2026-12-30',3),('2027-01-14',2),('2027-02-11',2),('2027-02-14',2),('2027-03-26',2),('2027-04-08',2),('2027-04-22',2)]
CANDIDATE_FIELDS='property_token name latitude longitude distance_km_from_riad_thais type hotel_class overall_rating reviews amenities_includes_breakfast first_observed_checkin source collected_at'.split()
PRICE_FIELDS='property_token name checkin checkout nights adults rate_per_night_lowest total_rate_lowest currency taxes_basis rate_per_night_before_taxes rate_per_night_after_taxes total_rate_before_taxes total_rate_after_taxes price_source listed_on_this_date observation_level room_type refundability breakfast_included search_id source collected_at'.split()
SAFE=set('properties property_token name type hotel_class extracted_hotel_class overall_rating reviews gps_coordinates latitude longitude amenities excluded_amenities rate_per_night total_rate lowest extracted_lowest display_price extracted_display_price before_taxes_fees extracted_before_taxes_fees after_taxes_fees extracted_after_taxes_fees prices price_source source official num_guests free_cancellation free_cancellation_until_date free_cancellation_until_time rooms benefits serpapi_pagination next_page_token search_metadata id status created_at processed_at'.split())


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',value).casefold() if c.isalnum())


def excluded(hotel):
    name=normalized(hotel.get('name',''))
    return 'riadsaba' in name or 'riadalaya' in name


def distance(lat,lon):
    a,b=map(math.radians,ORIGIN);c,d=map(math.radians,(float(lat),float(lon)))
    h=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(h)))


def candidate(hotel):
    if excluded(hotel) or hotel.get('property_token')==OWN_TOKEN:
        return False
    text=(hotel.get('name','')+' '+hotel.get('type','')).casefold().replace('_',' ')
    if not re.search(r'\briad\b|\bguest\s*house\b|\bboutique\b',text):
        return False
    gps=hotel.get('gps_coordinates',{})
    try:
        lat,lon=float(gps['latitude']),float(gps['longitude'])
        if not(-90<=lat<=90 and -180<=lon<=180):return False
        return bool(hotel.get('property_token')) and distance(lat,lon)<=1.5
    except (KeyError,ValueError,TypeError):return False


def clean(value,key=''):
    if isinstance(value,dict):
        if 'property_token' in value and excluded(value):return None
        return {k:clean(v,k) for k,v in value.items() if k in SAFE and not(k=='reviews' and not isinstance(v,(int,float)))}
    if isinstance(value,list):return [x for v in value if (x:=clean(v)) is not None]
    return value


def write_csv(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)


def breakfast(hotel):
    if any('breakfast' in str(x).casefold() for x in hotel.get('amenities',[])):return 'yes'
    if any('breakfast' in str(x).casefold() for x in hotel.get('excluded_amenities',[])):return 'no'
    return 'not_returned'


def base_params(day,nights):
    return dict(engine='google_hotels',q='riad Medina Marrakech',gl='ma',hl='en',currency='MAD',adults=2,children=0,
                check_in_date=day,check_out_date=(dt.date.fromisoformat(day)+dt.timedelta(days=nights)).isoformat())


def export(cache):
    pools={};candidates={};metadata={}
    for call in cache:
        p=call['parameters'];data=call['data']
        if 'property_token' in p:continue
        day=p['check_in_date'];pools.setdefault(day,{})
        metadata[day]=call['ledger']
        for h in data.get('properties',[]):
            if not h or excluded(h):continue
            token=h.get('property_token')
            if not token:continue
            pools[day].setdefault(token,(h,call['ledger']))
            if candidate(h) and token not in candidates:
                gps=h['gps_coordinates']
                candidates[token]=dict(property_token=token,name=h['name'],latitude=gps['latitude'],longitude=gps['longitude'],distance_km_from_riad_thais=round(distance(gps['latitude'],gps['longitude']),6),
                    type=h.get('type','not_returned'),hotel_class=h.get('hotel_class','not_returned'),overall_rating=h.get('overall_rating','not_returned'),reviews=h.get('reviews','not_returned'),
                    amenities_includes_breakfast=breakfast(h),first_observed_checkin=day,source=SOURCE,collected_at=call['ledger']['collected_at'])
    prices=[]
    for day,nights in STAYS:
        if day not in pools:continue  # Not a successful collected list => no absence inference.
        checkout=base_params(day,nights)['check_out_date']
        for token in sorted(set(candidates)|{OWN_TOKEN}):
            found=pools[day].get(token);h,row=found if found else ({},metadata[day])
            nr=h.get('rate_per_night',{});total=h.get('total_rate',{})
            identity=candidates.get(token,{'name':'Riad Thaïs Marrakech'})
            after=bool(nr.get('after_taxes_fees') or total.get('after_taxes_fees'))
            before=bool(nr.get('before_taxes_fees') or total.get('before_taxes_fees'))
            prices.append(dict(property_token=token,name=h.get('name',identity['name']),checkin=day,checkout=checkout,nights=nights,adults=2,
                rate_per_night_lowest=nr.get('extracted_lowest','not_returned'),total_rate_lowest=total.get('extracted_lowest','not_returned'),currency='MAD',
                taxes_basis='before_and_after_returned_lowest_basis_unverified' if before and after else 'after_taxes' if after and nr.get('extracted_lowest')==nr.get('extracted_after_taxes_fees') else 'before_taxes' if before and nr.get('extracted_lowest')==nr.get('extracted_before_taxes_fees') else 'not_returned',
                rate_per_night_before_taxes=nr.get('before_taxes_fees','not_returned'),rate_per_night_after_taxes=nr.get('after_taxes_fees','not_returned'),total_rate_before_taxes=total.get('before_taxes_fees','not_returned'),total_rate_after_taxes=total.get('after_taxes_fees','not_returned'),
                price_source=h.get('price_source',h.get('source','not_returned')),listed_on_this_date='yes' if found else 'not_in_results',observation_level='list_aggregate',room_type='not_returned',refundability='not_returned',breakfast_included='not_returned',search_id=row.get('search_id','not_returned'),source=SOURCE,collected_at=row['collected_at']))
    # Optional site detail observations stay distinct from the list aggregates.
    for call in cache:
        p=call['parameters'];h=call['data'];r=call['ledger']
        if p.get('property_token')!=OWN_TOKEN or h.get('property_token')!=OWN_TOKEN:continue
        nights=(dt.date.fromisoformat(p['check_out_date'])-dt.date.fromisoformat(p['check_in_date'])).days
        for offer in h.get('prices',[]):
            nr,total=offer.get('rate_per_night',{}),offer.get('total_rate',{})
            row=dict.fromkeys(PRICE_FIELDS,'not_returned');row.update(property_token=OWN_TOKEN,name=h.get('name','Riad Thaïs Marrakech'),checkin=p['check_in_date'],checkout=p['check_out_date'],nights=nights,adults=2,currency='MAD',
                rate_per_night_lowest=nr.get('extracted_lowest','not_returned'),total_rate_lowest=total.get('extracted_lowest','not_returned'),price_source=offer.get('source','not_returned'),listed_on_this_date='yes',observation_level='own_hotel_detail',
                refundability=json.dumps({k:v for k,v in offer.items() if k.startswith('free_cancellation')},ensure_ascii=False) if 'free_cancellation' in offer else 'not_returned',
                search_id=r.get('search_id','not_returned'),source=SOURCE,collected_at=r['collected_at'])
            row.update(rate_per_night_before_taxes=nr.get('before_taxes_fees','not_returned'), rate_per_night_after_taxes=nr.get('after_taxes_fees','not_returned'), total_rate_before_taxes=total.get('before_taxes_fees','not_returned'), total_rate_after_taxes=total.get('after_taxes_fees','not_returned'))
            room_names=[room['name'] for room in offer.get('rooms',[]) if room.get('name')]
            if room_names:row['room_type']=json.dumps(room_names,ensure_ascii=False)
            benefits=offer.get('benefits')
            if benefits and 'breakfast' in str(benefits).casefold():row['breakfast_included']=json.dumps(benefits,ensure_ascii=False)
            prices.append(row)
    write_csv(ROOT/'research/data'/f'{PREFIX}-riad-thais-compset-candidates.csv',list(candidates.values()),CANDIDATE_FIELDS)
    write_csv(ROOT/'research/data'/f'{PREFIX}-riad-thais-compset-prices.csv',prices,PRICE_FIELDS)
    print('Export:',len(candidates),'deduplicated candidates;',len(prices),'price/status rows')


def run(args):
    # Lazy import lets offline geo/export checks work before dependency PR #7 merges.
    from price_parity import Ledger,api_call,lock_for
    if not args.ledger.exists():raise SystemExit('Shared ledger missing: merge/reconcile PR #7 first; no calls sent')
    key=os.environ.get('SERPAPI_API_KEY')
    if not key:raise SystemExit('SERPAPI_API_KEY unavailable; no calls sent')
    cache_path=Path(args.cache)
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else []
    ledger=Ledger(args.ledger)
    with lock_for(args.ledger.parent/'issue-8-global') as lock:
        import fcntl
        fcntl.flock(lock,fcntl.LOCK_EX)
        cache=json.loads(cache_path.read_text()) if cache_path.exists() else []
        def fetch(parameters):
            for saved in cache:
                if saved['parameters']==parameters:return saved
            import price_parity as shared
            rows=shared.read_csv(args.ledger)
            prior=[r for r in rows if r['run_id']=='issue-8']
            if any(json.loads(r['parameters'])==parameters for r in prior):
                raise SystemExit('Parameters reserved but no cached response: no identical retry allowed')
            if len(prior)>=30:raise SystemExit('Issue #8 hard 30-attempt cap reached')
            month=shared.utc()[:7];used=sum(r['month']==month for r in rows)
            if used+(30-len(prior))>200:
                raise SystemExit('Remaining issue allowance would exceed 200/month; stop and comment on issue')
            if prior:
                time.sleep(2)
            # List discovery is market-wide, not an own-hotel weekly date check.
            prop='issue8_marrakech_medina_lists' if 'property_token' not in parameters else 'riad_thais'
            data,row=api_call(ledger,prop,parameters,'issue-8')
            if data is None:raise SystemExit('API failure recorded; no retry. Stop and report exact status from ledger')
            safe=clean(data)
            if key in json.dumps(safe):raise SystemExit('Secret in response; output suppressed')
            saved=dict(parameters=parameters,data=safe,ledger=row);cache.append(saved)
            cache_path.parent.mkdir(parents=True,exist_ok=True)
            temp=cache_path.with_suffix('.tmp');temp.write_text(json.dumps(cache,ensure_ascii=False));os.chmod(temp,0o600);os.replace(temp,cache_path)
            print('Issue calls:',len(prior)+1,'of 30;',parameters['check_in_date'],'cached:',row['cached'],flush=True)
            return saved
        for day,nights in STAYS:
            parameters=base_params(day,nights)
            import price_parity as shared
            failed=[r for r in shared.read_csv(args.ledger) if r['run_id']=='issue-8' and r['status']=='http_error' and json.loads(r['parameters'])==parameters]
            if failed:
                print('Previously failed date left uncollected:',day,flush=True)
                continue
            first=fetch(parameters)
            nearby=sum(candidate(h) for h in first['data'].get('properties',[]))
            next_token=first['data'].get('serpapi_pagination',{}).get('next_page_token')
            if nearby<20 and next_token:fetch(dict(parameters,next_page_token=next_token))
            export(cache)
        if args.details:
            for day,nights in [('2026-12-30',3),('2027-03-26',2)]:
                params=base_params(day,nights);params.pop('q');params['property_token']=OWN_TOKEN
                fetch(params)
            export(cache)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ledger',type=Path,default=ROOT/'research/data/parity/serpapi_ledger.csv')
    p.add_argument('--cache',type=Path,default=Path(tempfile.gettempdir())/'stayeasy-issue8/sanitized-responses.json')
    p.add_argument('--details',action='store_true',help='Two optional own-property site breakdowns, after list collection')
    p.add_argument('--export-only',action='store_true')
    args=p.parse_args()
    if args.export_only:export(json.loads(args.cache.read_text()))
    else:run(args)


if __name__=='__main__':main()
