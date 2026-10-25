#!/usr/bin/env python3
"""One-shot, unauthenticated TourMind v1.0.8 Marrakech research pilot.

Only the five owner-approved read-only endpoints are callable. Serial calls,
2-second pause, no conversions, no update checks, no booking operations.
Outputs exclude contacts, access links/tickets, images and rate codes.
Run: python3 tools/tourmind_rates.py --output-dir /tmp/tourmind-pilot
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

BASE = 'https://api.tourmind.com/skill/toc/'
ALLOWED = frozenset({'search_location', 'search_hotels', 'get_hotel_detail',
                     'query_room_rates', 'batch_query_room_rates'})
DATES = ('2026-12-10', '2026-12-31', '2027-02-14', '2027-04-08')
STEM = '2026-10-26-tourmind-marrakech-pilot'
MEALS = {1: 'room only', 2: 'breakfast included for booked guests',
         3: '1 breakfast', 4: '2 breakfasts', 5: '3 breakfasts',
         6: '4 breakfasts', 7: '5 breakfasts', 8: '6 breakfasts',
         9: '7 breakfasts', 10: '8 breakfasts', 11: 'lunch only',
         12: 'dinner only', 13: 'lunch and dinner', 14: 'half board',
         15: 'full board', 16: 'all inclusive', 17: 'buffet (meal time unspecified)',
         18: 'breakfast and lunch', 19: 'breakfast and dinner'}
# Allowlist persistence avoids collecting contact/person/account data or tickets.
SAFE = set('hotel ok data error reason regions hotels place region_id region_name name name_cn full_name full_name_cn country region_type hotel_count latitude longitude recommended_radius_km search_scope hotel_id hotel_name hotel_name_cn address address_cn star_rating total room_types products rate currency currency_code total_price per_night_price is_on_request max_occupancy maxOccupancy max_children maxChildren meal_type meal_count cancellation_policy type free_cancel_deadline effective_non_refundable results summary matched empty failed room_id taxes_included tax_included fees mandatory'.split())


def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if k in SAFE}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fields, extrasaction='raise')
        w.writeheader()
        w.writerows(rows)


class Client:
    def __init__(self, output):
        self.output = output
        self.calls = []
        self.saved = []
        path = output / (STEM + '-requests.csv')
        if path.exists():
            self.saved = list(csv.DictReader(path.open(encoding='utf-8')))

    def call(self, endpoint, payload):
        if endpoint not in ALLOWED:
            raise ValueError('Endpoint is not approved for research')
        if 'user_key' in json.dumps(payload):
            raise ValueError('Authentication is forbidden')
        if len(self.calls) < len(self.saved):
            row = self.saved[len(self.calls)]
            if row['endpoint'] != endpoint or json.loads(row['request']) != payload:
                raise ValueError('Resume request differs from saved collection')
            self.calls.append(row)
            return json.loads(row['response']), row['collected_at']
        if self.calls:
            time.sleep(2)
        timestamp = utc()
        start = time.monotonic()
        status = ''
        try:
            req = urllib.request.Request(BASE + endpoint,
                data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=90) as response:
                status = response.status
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            status = exc.code
            result = {'ok': False, 'error': 'HTTP ' + str(exc.code)}
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            result = {'ok': False, 'error': str(exc)}
        row = {'endpoint': endpoint, 'request': json.dumps(payload, sort_keys=True),
               'http_status': status, 'seconds': round(time.monotonic()-start, 3),
               'response': json.dumps(clean(result), ensure_ascii=False),
               'source': 'tourmind_api', 'collected_at': timestamp}
        self.calls.append(row)
        write_csv(self.output / (STEM + '-requests.csv'), self.calls, list(row))
        print(endpoint, status, row['seconds'], 'ok=' + str(result.get('ok')), flush=True)
        return result, timestamp


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--resume', action='store_true', help='Reuse saved responses after interruption; never requery saved calls')
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Never accidentally overwrite a previous collection or repeat its requests.
    if not args.resume and any(args.output_dir.glob(STEM + '*.csv')):
        p.error('Output already contains a collection; choose a new directory')
    client = Client(args.output_dir)
    location, _ = client.call('search_location', {'keyword': 'Medina Marrakech Morocco'})
    regions = location.get('data', {}).get('regions', [])
    matches = [r for r in regions if r.get('name') == 'Medina'
               and r.get('country') == 'Morocco'
               and 'Marrakech' in r.get('full_name', '')
               and r.get('region_type') == 'Neighborhood']
    if len(matches) != 1:
        raise SystemExit('No unambiguous Medina region; stop without guessing')
    region = matches[0]
    rows = []
    fields = 'hotel_id hotel_name area_district address star_rating stay_check_in stay_check_out adults room_count children room_name meal meal_type meal_count cancellation is_on_request price_per_night total_price currency taxes_included tax_basis max_adults occupancy_status status endpoint source collected_at'.split()
    for check_in in DATES:
        check_out = (dt.date.fromisoformat(check_in)+dt.timedelta(days=2)).isoformat()
        stay = dict(check_in_date=check_in, check_out_date=check_out,
                    adults=2, room_count=1, children=0, children_ages=[])
        search, _ = client.call('search_hotels', dict(stay,
            region_id=str(region['region_id']), location_name=region['full_name']))
        hotels = search.get('data', {}).get('hotels', [])[:20]
        if not hotels:
            continue
        ids = list(dict.fromkeys(str(h['hotel_id']) for h in hotels))
        endpoint = 'batch_query_room_rates' if len(ids) > 1 else 'query_room_rates'
        response, collected = client.call(endpoint, dict(stay,
            **({'hotel_ids': ids} if len(ids) > 1 else {'hotel_id': ids[0]})))
        items = response.get('data', {}).get('results', []) if len(ids) > 1 else [dict(response, hotel_id=ids[0])]
        by_id = {str(item.get('hotel_id')): item for item in items}
        for hotel in hotels:
            hid = str(hotel['hotel_id'])
            item = by_id.get(hid, {'ok': False, 'reason': response.get('error', 'missing_batch_item')})
            data = item.get('data', {})
            base = dict.fromkeys(fields, '')
            base.update(hotel_id=hid, hotel_name=hotel.get('hotel_name', hotel.get('name', '')),
                area_district=hotel.get('region_name', ''), address=hotel.get('address', ''), star_rating=hotel.get('star_rating', ''),
                stay_check_in=check_in, stay_check_out=check_out, adults=2, room_count=1,
                children=0, endpoint=endpoint, source='tourmind_api', collected_at=collected)
            count = 0
            for room in data.get('room_types', []):
                for product in room.get('products', []):
                    rate = product.get('rate', {})
                    capacity = product.get('max_occupancy', product.get('maxOccupancy'))
                    row = dict(base, room_name=room.get('name', room.get('name_cn', '')),
                        meal=MEALS.get(int(product.get('meal_type') or 0), 'not returned'),
                        meal_type=product.get('meal_type', ''), meal_count=product.get('meal_count', ''),
                        cancellation=json.dumps(product.get('cancellation_policy', {}), ensure_ascii=False),
                        is_on_request=str(rate.get('is_on_request', '')).lower(),
                        price_per_night=rate.get('per_night_price', ''), total_price=rate.get('total_price', ''),
                        currency=rate.get('currency', ''), max_adults=capacity if capacity is not None else '',
                        occupancy_status='matches' if capacity is not None and float(capacity) >= 2 else 'unverified' if capacity is None else 'insufficient',
                        taxes_included=rate.get('taxes_included', product.get('taxes_included', 'not_returned')),
                        tax_basis='API field if returned; otherwise unknown (docs claim tax included)', status='rate_returned')
                    rows.append(row)
                    count += 1
            if not count:
                rows.append(dict(base, status=item.get('reason', data.get('reason', 'empty' if item.get('ok') else 'error')),
                                 cancellation=item.get('error', '')))
        write_csv(args.output_dir / (STEM + '.csv'), rows, fields)
    # Exact-name lookup examples test catalogue visibility only, not extra rate shops.
    for keyword in ('Riad Yasmine Marrakech', 'Riad BE Marrakech', 'Riad Kniza Marrakech'):
        client.call('search_hotels', {'keyword': keyword})
    for hid in sorted({r['hotel_id'] for r in rows}):
        client.call('get_hotel_detail', {'hotel_id': hid})


if __name__ == '__main__':
    main()
