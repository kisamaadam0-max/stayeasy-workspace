#!/usr/bin/env python3
"""Read-only SerpApi Google Hotels weekly own-site price observations.

Key: SERPAPI_API_KEY only. Terms/limits: https://serpapi.com/legal ; use rights
remain subject to those terms (no claim of unrestricted redistribution).
Shared locked ledger counts every reserved attempt, including errors/cache hits.
"""
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://serpapi.com/search.json'
SOURCE = 'serpapi_google_hotels'
PROPERTY_CAP = 20
TOTAL_CAP = 200
LEDGER_FIELDS = 'month attempt property date endpoint cached status run_id parameters http_status elapsed_seconds search_id response_created_at source collected_at'.split()
TOKEN_FIELDS = 'property_slug property_name serpapi_query gl hl currency property_token source collected_at'.split()
FIELDS = 'property_name property_token type hotel_class overall_rating reviews address latitude longitude stay_check_in stay_check_out adults room_count children price_source is_official_site rate_per_night total_rate currency taxes_included before_taxes_per_night after_taxes_per_night before_taxes_total after_taxes_total breakfast_included benefits num_guests status request_attempt source collected_at run_id'.split()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def read_csv(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        writer = csv.DictWriter(f, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def lock_for(path):
    # Never replace/unlink this lock during a run; its stable inode protects writers.
    digest = hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()
    return open(Path(tempfile.gettempdir()) / ('stayeasy-parity-' + digest + '.lock'), 'a')


class BudgetError(RuntimeError):
    pass


class Ledger:
    def __init__(self, path, clock=utc):
        self.path, self.clock = Path(path), clock

    def budget(self, prop, month):
        rows = [r for r in read_csv(self.path) if r['month'] == month]
        return PROPERTY_CAP - sum(r['property'] == prop for r in rows), TOTAL_CAP - len(rows)

    def reserve(self, prop, stay, parameters, run_id):
        with lock_for(self.path) as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            collected = self.clock()
            month = collected[:7]  # UTC billing month, not requested stay month.
            remaining, total = self.budget(prop, month)
            if remaining <= 0 or total <= 0:
                raise BudgetError('Monthly cap reached; no request sent')
            rows = read_csv(self.path)
            row = dict.fromkeys(LEDGER_FIELDS, '')
            row.update(month=month, attempt=max([int(r['attempt']) for r in rows] or [0])+1,
                       property=prop, date=stay, endpoint=ENDPOINT, cached='unknown',
                       status='reserved', run_id=run_id, parameters=json.dumps(parameters, ensure_ascii=False, sort_keys=True),
                       source=SOURCE, collected_at=collected)
            rows.append(row)
            write_csv(self.path, rows, LEDGER_FIELDS)
            return row

    def finish(self, reserved, **updates):
        with lock_for(self.path) as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            rows = read_csv(self.path)
            found = [r for r in rows if str(r['attempt']) == str(reserved['attempt'])]
            if len(found) != 1:
                raise ValueError('Ledger reservation missing or duplicated')
            found[0].update(updates)
            write_csv(self.path, rows, LEDGER_FIELDS)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def transport(parameters, key):
    # Never return or log URLs/HTTP exception strings containing this query.
    url = ENDPOINT + '?' + urllib.parse.urlencode(dict(parameters, api_key=key))
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(url, timeout=90) as response:
        return response.status, json.load(response)


def api_call(ledger, prop, parameters, run_id, send=transport, key=None):
    if parameters.get('engine') != 'google_hotels' or 'api_key' in parameters:
        raise ValueError('Only key-free google_hotels request parameters allowed')
    key = key or os.environ.get('SERPAPI_API_KEY')
    if not key:
        raise ValueError('SERPAPI_API_KEY unavailable; no request sent')
    row = ledger.reserve(prop, parameters['check_in_date'], parameters, run_id)
    started = time.monotonic()
    status, http, data = 'reserved', '', None
    updates = {}
    try:
        http, data = send(parameters, key)
        meta = data.get('search_metadata', {})
        status = 'api_error' if data.get('error') else meta.get('status', 'not_returned')
        echoed = data.get('search_parameters', {})
        if any(k in echoed and str(echoed[k]) != str(v) for k,v in parameters.items()):
            status = 'request_context_mismatch'
        flag = meta.get('cached', data.get('cached'))
        cached = ('yes' if flag else 'no') if isinstance(flag, bool) else 'yes' if status == 'Cached' else 'unknown'
        updates.update(cached=cached, search_id=meta.get('id', ''), response_created_at=meta.get('created_at', ''))
    except urllib.error.HTTPError as exc:
        http, status = exc.code, 'http_error'
    except Exception as exc:
        status = 'error_' + type(exc).__name__  # Never exception text or error body.
    finally:
        if key in json.dumps(updates) or key in str(status):
            updates = {}
            status = 'secret_in_metadata_suppressed'
        updates.update(status=status, http_status=http, elapsed_seconds=round(time.monotonic()-started, 3))
        ledger.finish(row, **updates)
    row.update(updates)
    if status not in ('Success', 'Cached'):
        return None, row
    return data, row


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value).lower() if c.isalnum())


def config(path):
    rows = read_csv(path)
    active = [r for r in rows if r['active'].lower() == 'yes']
    if len({r['property_slug'] for r in rows}) != len(rows):
        raise ValueError('Duplicate property slug')
    for r in active:
        if not re.fullmatch(r'[a-z0-9_]+', r['property_slug']):
            raise ValueError('Unsafe property slug')
        if not all(r.get(k) for k in ('property_name', 'serpapi_query', 'gl', 'hl', 'currency')):
            raise ValueError('Incomplete property config')
    return active


def token_for(prop, path):
    matches = [r for r in read_csv(path) if all(r.get(k) == prop[k] for k in ('property_slug','property_name','serpapi_query','gl','hl','currency'))]
    if len(matches) > 1:
        raise ValueError('Ambiguous saved property token')
    return matches[0]['property_token'] if matches else None


def save_token(prop, token, path, collected):
    with lock_for(path) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rows = [r for r in read_csv(path) if r['property_slug'] != prop['property_slug']]
        rows.append(dict((k, prop[k]) for k in ('property_slug','property_name','serpapi_query','gl','hl','currency')) | dict(property_token=token, source=SOURCE, collected_at=collected))
        write_csv(path, rows, TOKEN_FIELDS)


def request_params(prop, day, token=None):
    p = dict(engine='google_hotels', gl=prop['gl'], hl=prop['hl'], currency=prop['currency'],
             check_in_date=day.isoformat(), check_out_date=(day+dt.timedelta(days=2)).isoformat(), adults=2, children=0)
    p.update({'property_token':token} if token else {'q':prop['serpapi_query']})
    return p


def match_property(data, prop, token=None):
    items = data.get('properties', [data] if data.get('name') else [])
    if token:
        matches = [p for p in items if p.get('property_token') == token]
    else:
        matches = [p for p in items if normalize(p.get('name','')) == normalize(prop['property_name'])]
    return matches[0] if len(matches) == 1 else None


def observations(prop, hotel, parameters, row, run_id, status=None):
    hotel = hotel or {}
    gps = hotel.get('gps_coordinates', {})
    base = dict.fromkeys(FIELDS, 'not_returned')
    base.update(property_name=hotel.get('name', prop['property_name']), property_token=hotel.get('property_token', parameters.get('property_token','not_returned')),
                type=hotel.get('type','not_returned'), hotel_class=hotel.get('hotel_class','not_returned'),
                overall_rating=hotel.get('overall_rating','not_returned'), reviews=hotel.get('reviews','not_returned') if isinstance(hotel.get('reviews'),(int,float)) else 'not_returned',
                address=hotel.get('address','not_returned'), latitude=gps.get('latitude','not_returned'), longitude=gps.get('longitude','not_returned'),
                stay_check_in=parameters['check_in_date'], stay_check_out=parameters['check_out_date'],
                adults=2, room_count=1, children=0, currency=parameters['currency'], request_attempt=row['attempt'],
                source=SOURCE, collected_at=row['collected_at'], run_id=run_id)
    if status or not hotel.get('prices'):
        return [dict(base, status=status or 'no_site_prices_returned',
                     rate_per_night=json.dumps(hotel.get('rate_per_night',{}),ensure_ascii=False),
                     total_rate=json.dumps(hotel.get('total_rate',{}),ensure_ascii=False))]
    result = []
    # Persist price objects only, never URLs, review bodies, personal/contact data.
    allowed = {'display_price','extracted_display_price','lowest','extracted_lowest','before_taxes_fees','extracted_before_taxes_fees','after_taxes_fees','extracted_after_taxes_fees'}
    for price in hotel['prices']:
        night = {k:v for k,v in price.get('rate_per_night',{}).items() if k in allowed}
        total = {k:v for k,v in price.get('total_rate',{}).items() if k in allowed}
        result.append(dict(base, price_source=price.get('source','not_returned'),
            is_official_site=str(price['official']).lower() if isinstance(price.get('official'),bool) else 'not_returned',
            rate_per_night=json.dumps(night,ensure_ascii=False), total_rate=json.dumps(total,ensure_ascii=False),
            before_taxes_per_night=night.get('before_taxes_fees','not_returned'), after_taxes_per_night=night.get('after_taxes_fees','not_returned'),
            before_taxes_total=total.get('before_taxes_fees','not_returned'), after_taxes_total=total.get('after_taxes_fees','not_returned'),
            num_guests=price.get('num_guests','not_returned'), status='site_price_returned'))
    return result


def run(args):
    props = config(args.config)
    if args.property:
        props = [p for p in props if p['property_slug'] == args.property]
        if not props:
            raise ValueError('No active configured property matches')
    today = dt.date.fromisoformat(args.run_date) if args.run_date else dt.datetime.now(ZoneInfo('Africa/Casablanca')).date()
    dates = [dt.date.fromisoformat(d) for d in args.dates.split(',')] if args.dates else [today+dt.timedelta(days=n) for n in (7,21,45,90)]
    if not dates or len(set(dates)) != len(dates) or any(d < today for d in dates):
        raise ValueError('Dates must be unique and not before run date')
    ledger = Ledger(args.ledger)
    month = utc()[:7]
    run_id = args.run_id or (utc().replace(':','') + '-' + uuid.uuid4().hex[:8])
    plans = []
    for prop in props:
        token = token_for(prop,args.tokens)
        remaining, total = ledger.budget(prop['property_slug'],month)
        print(prop['property_slug'], 'remaining this month:', remaining, 'property /',total,'account')
        for i,d in enumerate(dates):
            mode = 'detail' if token else 'discovery + optional detail' if i == 0 else 'detail if identity resolved; otherwise discovery'
            print('PLAN',d.isoformat(),'2 nights / 2 adults / 1 room',mode)
        plans.append((prop, token))
    if args.dry_run:
        print('DRY RUN: 0 API calls; no files changed')
        return 0
    if not os.environ.get('SERPAPI_API_KEY'):
        raise ValueError('SERPAPI_API_KEY unavailable; no request sent')
    used = 0
    # Serialize entire runs on the same output date; ledger itself also locks globally.
    with lock_for(Path(args.output_dir) / ('run-'+today.isoformat())) as run_lock:
        fcntl.flock(run_lock,fcntl.LOCK_EX)
        for prop, token in plans:
            output = Path(args.output_dir)/(today.isoformat()+'-'+prop['property_slug']+'.csv')
            if output.exists():
                raise ValueError('Output exists; refusing to overwrite/repeat this daily run')
            result = []
            for day in dates:
                if used >= args.max_requests:
                    print('Run request cap reached; remaining dates not collected')
                    return used
                p = request_params(prop,day,token)
                try:
                    if used:
                        time.sleep(2)
                    data, row = api_call(ledger,prop['property_slug'],p,run_id)
                except BudgetError:
                    print('Monthly budget cap reached; stopped before network')
                    return used
                used += 1
                hotel = match_property(data,prop,token) if data else None
                if not token and hotel and hotel.get('property_token'):
                    token = hotel['property_token']
                    save_token(prop,token,args.tokens,row['collected_at'])
                    if not hotel.get('prices') and used < args.max_requests:
                        time.sleep(2)
                        p = request_params(prop,day,token)
                        try:
                            data, row = api_call(ledger,prop['property_slug'],p,run_id)
                        except BudgetError:
                            result.extend(observations(prop,hotel,p,row,run_id,'discovery_only_budget_exhausted'))
                            write_csv(output,result,FIELDS)
                            return used
                        used += 1
                        hotel = match_property(data,prop,token) if data else None
                result.extend(observations(prop,hotel,p,row,run_id,'request_failed' if not data else 'property_not_matched' if not hotel else None))
                secret = os.environ['SERPAPI_API_KEY']
                if secret in json.dumps(result,ensure_ascii=False):
                    raise ValueError('Secret detected; output suppressed')
                write_csv(output,result,FIELDS)
                print('Saved',output.name,'attempt',row['attempt'],'status',row['status'],'cached',row['cached'])
                if data is None:
                    print('Request failed; stopped without retries')
                    return used
            remaining,total=ledger.budget(prop['property_slug'],utc()[:7])
            print('Remaining:',remaining,'property /',total,'account')
    print('Requests this run:',used)
    return used


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=ROOT/'research/config/properties.csv')
    p.add_argument('--tokens',type=Path,default=ROOT/'research/config/property_tokens.csv')
    p.add_argument('--ledger',type=Path,default=ROOT/'research/data/parity/serpapi_ledger.csv')
    p.add_argument('--output-dir',type=Path,default=ROOT/'research/data/parity')
    p.add_argument('--property')
    p.add_argument('--run-date',help='Local calendar date YYYY-MM-DD (default Africa/Casablanca today)')
    p.add_argument('--dates',help='Comma-separated check-in dates; 2-night checkout computed')
    p.add_argument('--run-id')
    p.add_argument('--max-requests',type=int,default=200,help='Additional per-run cap; use 1 for issue #6 smoke test')
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args()
    if not 0 <= args.max_requests <= 200:
        p.error('--max-requests must be 0..200')
    try:
        used = run(args)
        print('Completed run attempts:', used)
        ledger = Ledger(args.ledger)
        for prop in config(args.config):
            if not args.property or prop['property_slug'] == args.property:
                remaining, total = ledger.budget(prop['property_slug'], utc()[:7])
                print(prop['property_slug'], 'remaining:', remaining, 'property /', total, 'account')
    except (ValueError,KeyError,OSError) as exc:
        # Own validation messages are safe; OS exception paths may not be.
        print('Stopped:',str(exc) if isinstance(exc,ValueError) else type(exc).__name__)
        raise SystemExit(1)


if __name__=='__main__':
    main()
