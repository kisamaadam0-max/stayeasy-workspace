#!/usr/bin/env python3
"""Issue #3: Riad Thais only (owner's scope amendment).

Only SerpApi google_hotels; key from SERPAPI_API_KEY. Never print exceptions
containing request URLs. Persistent pre-request ledger, hard 20-attempt cap,
serial calls, no redirects/retries, and sanitized allowlist response evidence.
Run `lists`, inspect evidence, then `detail --token TOKEN` for Dec 10 if needed.
"""
import argparse
import csv
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STEM = '2026-10-26-serpapi-google-hotels-pilot'
DATA = ROOT / 'research/data'
LOG = DATA / (STEM + '-requests.csv')
EVIDENCE = DATA / (STEM + '-evidence.csv')
LIMIT = 20
ENDPOINT = 'https://serpapi.com/search.json'
SOURCE = 'serpapi_google_hotels'
DATES = ('2026-12-10', '2026-12-31', '2027-02-14', '2027-04-08')
LOG_FIELDS = 'attempt endpoint parameters cached cache_evidence quota_cost quota_cost_basis http_status elapsed_seconds status search_id response_created_at collected_at source'.split()
EVIDENCE_FIELDS = 'attempt parameters response source collected_at'.split()
# Deliberately exclude reviews, reviewer names, contacts, photos and all URLs.
SAFE = set('search_metadata id status created_at processed_at total_time_taken cached search_parameters engine q gl hl currency adults children check_in_date check_out_date property_token search_information hotels_results_state properties type name address gps_coordinates latitude longitude hotel_class extracted_hotel_class overall_rating reviews prices source official num_guests rate_per_night total_rate lowest extracted_lowest display_price extracted_display_price before_taxes_fees extracted_before_taxes_fees after_taxes_fees extracted_after_taxes_fees benefits free_cancellation free_cancellation_until_date free_cancellation_until_time'.split())
PRICE_FIELDS = 'property_name property_token type hotel_class overall_rating reviews address latitude longitude stay_check_in stay_check_out adults price_source is_official_site rate_per_night total_rate currency taxes_included before_taxes_per_night after_taxes_per_night before_taxes_total after_taxes_total breakfast_included benefits num_guests status request_attempt source collected_at'.split()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value).lower() if c.isalnum())


def target(prop):
    return 'riadthais' in normalized(prop.get('name', ''))


def clean(value, key=''):
    if isinstance(value, dict):
        return {k: clean(v, k) for k, v in value.items()
                if k in SAFE and not (k == 'reviews' and isinstance(v, (dict, list)))}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def sanitize_response(value):
    result = clean(value)
    # Never persist other properties, including excluded hotels accidentally returned.
    if 'properties' in result:
        result['properties'] = [p for p in result['properties'] if target(p)]
    if 'name' in result and not target(result):
        result = {k: v for k, v in result.items() if k.startswith('search_')}
    return result


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        w = csv.DictWriter(f, fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward the credential to a different destination.


def params(check_in, token=None):
    result = dict(engine='google_hotels', gl='ma', hl='en', currency='MAD',
                  adults=2, children=0, check_in_date=check_in,
                  check_out_date=(dt.date.fromisoformat(check_in)+dt.timedelta(days=2)).isoformat())
    if token:
        result['property_token'] = token
    else:
        result['q'] = 'Riad Thaïs Marrakech'
    return result


def call(parameters):
    allowed = set(params(DATES[0])) | {'property_token'}
    if parameters.get('engine') != 'google_hotels' or set(parameters)-allowed:
        raise ValueError('Only approved Google Hotels parameters allowed')
    key = os.environ.get('SERPAPI_API_KEY')
    if not key:
        raise SystemExit('SERPAPI_API_KEY unavailable; no request made')
    DATA.mkdir(parents=True, exist_ok=True)
    # One fixed issue ledger across all invocations; lock covers reservation and call.
    with (DATA / (STEM + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        log = read_csv(LOG)
        encoded = json.dumps(parameters, ensure_ascii=False, sort_keys=True)
        previous = [r for r in log if r['parameters'] == encoded]
        if previous:
            print('Saved request already exists; no duplicate call:', previous[-1]['attempt'])
            return
        if len(log) >= LIMIT:
            raise SystemExit('Hard cap of 20 attempts reached; no request made')
        if log:
            time.sleep(2)
        row = dict.fromkeys(LOG_FIELDS, '')
        row.update(attempt=len(log)+1, endpoint=ENDPOINT, parameters=encoded,
                   cached='unknown', quota_cost='unknown', quota_cost_basis='not yet observed',
                   status='reserved', collected_at=now(), source=SOURCE)
        log.append(row)
        write_csv(LOG, log, LOG_FIELDS)  # Crash/timeout still consumes an attempt.
        started = time.monotonic()
        response = None
        try:
            url = ENDPOINT + '?' + urllib.parse.urlencode(dict(parameters, api_key=key))
            opener = urllib.request.build_opener(NoRedirect)
            with opener.open(url, timeout=90) as res:
                row['http_status'] = res.status
                response = json.load(res)
            meta = response.get('search_metadata', {})
            row.update(status=meta.get('status', 'not_returned'), search_id=meta.get('id', ''),
                       response_created_at=meta.get('created_at', ''))
            cached = meta.get('cached', response.get('cached'))
            if isinstance(cached, bool):
                row['cached'] = 'yes' if cached else 'no'
                row['cache_evidence'] = 'explicit cached boolean'
            elif str(meta.get('status', '')).lower() == 'cached':
                row['cached'] = 'yes'
                row['cache_evidence'] = 'search_metadata.status=Cached'
            else:
                row['cache_evidence'] = 'cache flag absent; Success alone not assumed to prove fresh billing'
            if row['cached'] == 'yes':
                row.update(quota_cost=0, quota_cost_basis='documented cached searches are free')
            elif row['cached'] == 'no' and row['status'] == 'Success':
                row.update(quota_cost=1, quota_cost_basis='explicit non-cached successful search')
            else:
                row['quota_cost_basis'] = 'not verified; reserve one unit conservatively'
            safe = sanitize_response(response)
            text = json.dumps(safe, ensure_ascii=False)
            if key in text:
                raise ValueError('Secret detected in sanitized response')
            evidence = read_csv(EVIDENCE)
            evidence.append(dict(attempt=row['attempt'], parameters=encoded,
                                 response=text, source=SOURCE, collected_at=row['collected_at']))
            write_csv(EVIDENCE, evidence, EVIDENCE_FIELDS)
        except urllib.error.HTTPError as exc:
            row.update(http_status=exc.code, status='http_error')
        except Exception as exc:
            # Exception messages can contain the key-bearing URL: persist class only.
            row['status'] = 'error_' + type(exc).__name__
        finally:
            row['elapsed_seconds'] = round(time.monotonic()-started, 3)
            write_csv(LOG, log, LOG_FIELDS)
        print('Attempt', row['attempt'], 'HTTP', row['http_status'],
              'status', row['status'], 'cached', row['cached'], flush=True)
        if row['status'] not in ('Success', 'Cached'):
            raise SystemExit('Call not successful; stopped without automatic retries')


def export():
    rows = []
    evidence = read_csv(EVIDENCE)
    detailed = set()
    for record in evidence:
        data = json.loads(record['response'])
        p = json.loads(record['parameters'])
        if data.get('prices') and target(data):
            detailed.add((data.get('property_token'), p['check_in_date']))
    for record in evidence:
        p = json.loads(record['parameters'])
        data = json.loads(record['response'])
        properties = data.get('properties', [data] if data.get('name') else [])
        for prop in properties:
            if not target(prop):
                continue
            if not prop.get('prices') and (prop.get('property_token'), p['check_in_date']) in detailed:
                continue
            base = dict.fromkeys(PRICE_FIELDS, 'not_returned')
            gps = prop.get('gps_coordinates', {})
            base.update(property_name=prop['name'], property_token=prop.get('property_token', 'not_returned'),
                type=prop.get('type', 'not_returned'), hotel_class=prop.get('hotel_class', 'not_returned'),
                overall_rating=prop.get('overall_rating', 'not_returned'), reviews=prop.get('reviews', 'not_returned'),
                address=prop.get('address', 'not_returned'), latitude=gps.get('latitude', 'not_returned'),
                longitude=gps.get('longitude', 'not_returned'), stay_check_in=p['check_in_date'],
                stay_check_out=p['check_out_date'], adults=p['adults'], currency=p['currency'],
                source=SOURCE, collected_at=record['collected_at'], request_attempt=record['attempt'])
            for price in prop.get('prices', []):
                night, total = price.get('rate_per_night', {}), price.get('total_rate', {})
                row = dict(base, price_source=price.get('source', 'not_returned'),
                    is_official_site=str(price['official']).lower() if 'official' in price else 'not_returned',
                    rate_per_night=json.dumps(night, ensure_ascii=False), total_rate=json.dumps(total, ensure_ascii=False),
                    before_taxes_per_night=night.get('before_taxes_fees', 'not_returned'),
                    after_taxes_per_night=night.get('after_taxes_fees', 'not_returned'),
                    before_taxes_total=total.get('before_taxes_fees', 'not_returned'),
                    after_taxes_total=total.get('after_taxes_fees', 'not_returned'),
                    benefits=price.get('benefits', 'not_returned'), num_guests=price.get('num_guests', 'not_returned'),
                    status='site_price_returned')
                rows.append(row)
            if not prop.get('prices'):
                rows.append(dict(base, rate_per_night=json.dumps(prop.get('rate_per_night', {}), ensure_ascii=False),
                                 total_rate=json.dumps(prop.get('total_rate', {}), ensure_ascii=False),
                                 status='aggregate_only_no_site_attribution' if prop.get('rate_per_night') else 'no_price_returned'))
    write_csv(DATA / (STEM + '.csv'), rows, PRICE_FIELDS)
    print('Exported', len(rows), 'rows from', len(read_csv(LOG)), 'attempts')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['lists', 'detail', 'export'])
    parser.add_argument('--token')
    args = parser.parse_args()
    if args.step == 'lists':
        for day in DATES:
            call(params(day))
    elif args.step == 'detail':
        if not args.token:
            parser.error('--token required')
        # Only a token actually returned for Riad Thais is accepted.
        known = set()
        for r in read_csv(EVIDENCE):
            d = json.loads(r['response'])
            for p in d.get('properties', [d] if d.get('name') else []):
                if target(p):
                    known.add(p.get('property_token'))
        if args.token not in known:
            parser.error('Token is not a saved Riad Thais result')
        call(params(DATES[0], args.token))
    export()


if __name__ == '__main__':
    main()
