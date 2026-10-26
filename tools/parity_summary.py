#!/usr/bin/env python3
"""Compute descriptive site-price extrema; no pricing recommendations.

Never combine different properties, runs, currencies, occupancy, stay lengths or
explicit tax bases. Unknown tax/room equivalence is disclosed, not inferred.
"""
import argparse
from collections import defaultdict
import datetime as dt
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from price_parity import read_csv


def amount(row):
    # Compare entire-stay values first; keep nightly-only quotes separate.
    for field,basis in [('total_rate','stay'),('rate_per_night','night')]:
        values=json.loads(row.get(field,'{}'))
        for name,tax in [('extracted_after_taxes_fees','after_taxes'),('extracted_before_taxes_fees','before_taxes'),('extracted_display_price','tax_unknown'),('extracted_lowest','tax_unknown')]:
            if values.get(name) is None:
                continue
            try:value=Decimal(str(values[name]))
            except InvalidOperation:continue
            if value.is_finite() and value >= 0:
                return value,basis,tax
    return None


def summarize(rows):
    if not rows:
        raise ValueError('CSV has no observations')
    if len({r['property_token'] for r in rows}) != 1 or len({r['property_name'] for r in rows}) != 1:
        raise ValueError('Never combine properties in one summary')
    if len({r['run_id'] for r in rows}) != 1:
        raise ValueError('Never combine separate runs')
    groups=defaultdict(list)
    dates=defaultdict(list)
    for r in rows:
        dates[(r['stay_check_in'],r['stay_check_out'])].append(r)
        if r['status']!='site_price_returned' or r['price_source']=='not_returned':
            continue
        value=amount(r)
        if not value:
            continue
        if r.get('num_guests','not_returned') not in ('not_returned','',r['adults']):
            continue  # Offer capacity conflicts with requested occupancy.
        price,basis,tax=value
        key=(r['stay_check_in'],r['stay_check_out'],r['currency'],r['adults'],r['room_count'],r['children'],basis,tax)
        groups[key].append((price,r))
    result=[]
    for key,offers in sorted(groups.items()):
        low=min(v for v,r in offers);high=max(v for v,r in offers)
        gap=(high-low)/low*Decimal(100) if low else None
        result.append(dict(check_in=key[0],check_out=key[1],currency=key[2],adults=key[3],rooms=key[4],children=key[5],basis=key[6],tax=key[7],
            lowest=low,highest=high,lowest_sites=sorted({r['price_source'] for v,r in offers if v==low}),
            highest_sites=sorted({r['price_source'] for v,r in offers if v==high}),gap=gap,
            official=any(r['is_official_site']=='true' for v,r in offers),count=len(offers)))
    return result,dates


def escape(text):
    return str(text).replace('|','\\|').replace('\n',' ')


def markdown(rows):
    result,dates=summarize(rows)
    out=['# Site-price summary — '+escape(rows[0]['property_name']), '',
         'Run: '+escape(rows[0]['run_id']), '',
         '| Stay | Currency / basis / tax | Guests / rooms | Lowest site(s) | Lowest | Highest site(s) | Highest | Gap % | >5% | Official offer |',
         '| --- | --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |']
    for r in result:
        gap='not_computable' if r['gap'] is None else str(r['gap'].quantize(Decimal('0.01')))
        out.append('| '+' | '.join(map(escape,[r['check_in']+' → '+r['check_out'],r['currency']+' / '+r['basis']+' / '+r['tax'],r['adults']+' adults + '+r['children']+' children / '+r['rooms'],', '.join(r['lowest_sites']),r['lowest'],', '.join(r['highest_sites']),r['highest'],gap,'yes' if r['gap'] is not None and r['gap']>5 else 'no' if r['gap'] is not None else 'unknown','present' if r['official'] else 'missing (no confirmed offer)']))+' |')
    measured={(r['check_in'],r['check_out']) for r in result}
    for day,items in sorted(dates.items()):
        if day not in measured:
            out.extend(['','No comparable site prices for '+day[0]+' → '+day[1]+': '+', '.join(sorted({r['status'] for r in items}))+'.'])
    out.extend(['','Gap = (highest − lowest) / lowest × 100, calculated with Decimal; zero denominator is not computable. Ties are listed. A single offer gives a zero observed gap, not evidence of parity.',
                '', 'Source: serpapi_google_hotels. Collected: '+', '.join(sorted({r['collected_at'] for r in rows}))+'.',
                '', 'Unknown tax treatment is not tax-inclusive evidence. Tax bases, stay lengths, currencies and occupancy are kept separate. Room, meal and cancellation equivalence may be unknown; these are observed extrema, not a like-for-like parity conclusion. An absent official flag is not proof that no direct rate exists.'])
    return '\n'.join(out)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',type=Path);args=p.parse_args()
    try:print(markdown(read_csv(args.csv)),end='')
    except (ValueError,KeyError,TypeError) as exc:p.exit(1,'Cannot summarize: '+str(exc)+'\n')


if __name__=='__main__':main()
