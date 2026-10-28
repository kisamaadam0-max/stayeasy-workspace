"""Synthetic fixtures only. All transports mocked; no network or API key needed."""
import argparse
import contextlib
import csv
import datetime as dt
from decimal import Decimal
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import price_parity as p
import parity_summary as s


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'ledger.csv'
        self.ledger=p.Ledger(self.path,clock=lambda:'2026-10-26T12:00:00Z')
        self.params={'engine':'google_hotels','check_in_date':'2026-12-10'}

    def reserve(self,name='a'):
        return self.ledger.reserve(name,'2026-12-10',self.params,'test')

    def test_property_21st_rejected(self):
        for i in range(20):self.reserve()
        with self.assertRaises(p.BudgetError):self.reserve()
        self.assertEqual(len(p.read_csv(self.path)),20)
        self.assertEqual(self.ledger.budget('a','2026-10'),(0,180))

    def test_account_201st_rejected(self):
        for i in range(200):self.reserve('p'+str(i//20))
        with self.assertRaises(p.BudgetError):self.reserve('new')
        self.assertEqual(len(p.read_csv(self.path)),200)

    def test_other_month_does_not_count(self):
        for i in range(20):self.reserve()
        other=p.Ledger(self.path,clock=lambda:'2026-11-01T00:00:00Z')
        other.reserve('a','2026-12-10',self.params,'nov')
        self.assertEqual(other.budget('a','2026-11'),(19,199))

    def test_concurrent_reservations_cannot_overspend(self):
        for i in range(19):self.reserve()
        def attempt(_):
            try:self.reserve();return True
            except p.BudgetError:return False
        with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(attempt,range(4)))
        self.assertEqual(sum(result),1)
        self.assertEqual(len(p.read_csv(self.path)),20)

    def test_errors_cached_and_crashes_count_and_no_secret(self):
        def failed(*args):raise RuntimeError('SECRET in a request URL')
        data,row=p.api_call(self.ledger,'a',self.params,'run',send=failed,key='SECRET')
        self.assertIsNone(data);self.assertEqual(row['status'],'error_RuntimeError')
        data,row=p.api_call(self.ledger,'a',self.params,'run',send=lambda *_:(200,{'search_metadata':{'status':'Cached'}}),key='SECRET')
        self.assertEqual(row['cached'],'yes')
        self.reserve()  # interrupted reservation
        self.assertEqual(self.ledger.budget('a','2026-10'),(17,197))
        self.assertNotIn('SECRET',self.path.read_text())

    def test_reservation_is_written_before_network_and_cap_blocks_transport(self):
        def sender(*_):
            self.assertEqual(p.read_csv(self.path)[-1]['status'],'reserved')
            return 200,{'search_metadata':{'status':'Success'}}
        p.api_call(self.ledger,'a',self.params,'run',send=sender,key='SECRET')
        for i in range(19):self.reserve()
        with self.assertRaises(p.BudgetError):
            p.api_call(self.ledger,'a',self.params,'run',send=lambda *_:self.fail('network after cap'),key='SECRET')

    def test_mismatched_response_context_and_secret_metadata_fail_closed(self):
        for response in [
            {'search_metadata':{'status':'Success'},'search_parameters':{'currency':'USD'}},
            {'search_metadata':{'status':'Success','id':'SECRET'}},
        ]:
            data,row=p.api_call(self.ledger,'a',dict(self.params,currency='MAD'),'run',send=lambda *_,r=response:(200,r),key='SECRET')
            self.assertIsNone(data)
        self.assertNotIn('SECRET',self.path.read_text())

    def test_other_engine_no_key_or_reservation(self):
        with self.assertRaises(ValueError):p.api_call(self.ledger,'a',dict(self.params,engine='google'), 'r',key='SECRET')
        self.assertFalse(self.path.exists())


class SummaryTests(unittest.TestCase):
    def row(self,site,price,official='not_returned',**extra):
        row=dict(property_name='Synthetic Hotel',property_token='fixture-token',run_id='fixture-run',
            stay_check_in='2026-12-10',stay_check_out='2026-12-12',currency='MAD',adults='2',children='0',room_count='1',
            price_source=site,is_official_site=official,status='site_price_returned',num_guests='2',
            total_rate=json.dumps({'extracted_display_price':price}),rate_per_night='{}',collected_at='2026-10-26T00:00:00Z')
        row.update(extra);return row

    def test_fixture_gap_ties_and_official(self):
        rows=[self.row('OTA A',100),self.row('Direct',125,'true'),self.row('OTA B',100)]
        result,_=s.summarize(rows);r=result[0]
        self.assertEqual(r['gap'],Decimal(25));self.assertEqual(r['lowest_sites'],['OTA A','OTA B'])
        self.assertTrue(r['official']);self.assertIn('25.00',s.markdown(rows))

    def test_zero_denominator_and_missing_official(self):
        rows=[self.row('A',0),self.row('B',50)]
        result,_=s.summarize(rows);self.assertIsNone(result[0]['gap'])
        self.assertIn('missing (no confirmed offer)',s.markdown(rows))

    def test_bases_currency_occupancy_are_separate(self):
        rows=[self.row('A',100),self.row('B',999,currency='USD'),self.row('C',125,adults='3',num_guests='3'),
              self.row('D',150,total_rate=json.dumps({'extracted_after_taxes_fees':150}))]
        result,_=s.summarize(rows);self.assertEqual(len(result),4)
        self.assertTrue(all(r['gap']==0 for r in result))

    def test_mixed_properties_runs_rejected(self):
        for extra in [dict(property_token='other'),dict(property_name='other'),dict(run_id='other')]:
            with self.assertRaises(ValueError):s.summarize([self.row('A',100),self.row('B',110,**extra)])

    def test_absent_invalid_or_different_guest_prices_not_comparable(self):
        rows=[self.row('A','NaN'),self.row('B',110,num_guests='1'),self.row('C',100,status='no_site_prices_returned')]
        result,_=s.summarize(rows);self.assertEqual(result,[])
        self.assertIn('No comparable site prices',s.markdown(rows))


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.prop=dict(property_slug='test_hotel',property_name='Synthetic Hotel',serpapi_query='Synthetic Hotel',gl='ma',hl='en',currency='MAD',active='yes')
        p.write_csv(self.root/'properties.csv',[self.prop],list(self.prop))
        p.save_token(self.prop,'fixture-token',self.root/'tokens.csv','2026-10-26T00:00:00Z')
        self.args=argparse.Namespace(config=self.root/'properties.csv',tokens=self.root/'tokens.csv',ledger=self.root/'ledger.csv',output_dir=self.root/'out',property='test_hotel',run_date='2026-10-26',dates=None,run_id='test',max_requests=1,dry_run=True)

    def test_dry_run_four_dates_no_key_network_or_writes(self):
        before={str(f):f.read_bytes() for f in self.root.rglob('*.csv')}
        out=io.StringIO()
        with patch.dict(p.os.environ,{},clear=True),patch.object(p,'transport',side_effect=AssertionError('network')),contextlib.redirect_stdout(out):p.run(self.args)
        self.assertEqual(out.getvalue().count('PLAN'),4)
        for date in ('2026-11-02','2026-11-16','2026-12-10','2027-01-24'):self.assertIn(date,out.getvalue())
        self.assertEqual(before,{str(f):f.read_bytes() for f in self.root.rglob('*.csv')})

    def test_mocked_end_to_end_one_call_and_output_protection(self):
        self.args.dry_run=False;self.args.dates='2026-12-10'
        def sender(*_):return 200,{'search_metadata':{'status':'Success'},'name':'Synthetic Hotel','property_token':'fixture-token','prices':[{'source':'OTA','num_guests':2,'rate_per_night':{'extracted_display_price':100},'total_rate':{'extracted_display_price':200}}]}
        def call(ledger,prop,parameters,run_id):return p.api_call(ledger,prop,parameters,run_id,send=sender,key='SECRET')
        actual=p.api_call
        def wrapped(ledger,prop,parameters,run_id):return actual(ledger,prop,parameters,run_id,send=sender,key='SECRET')
        with patch.dict(p.os.environ,{'SERPAPI_API_KEY':'SECRET'}),patch.object(p,'api_call',side_effect=wrapped),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(p.run(self.args),1)
            with self.assertRaises(ValueError):p.run(self.args)
        rows=p.read_csv(self.root/'out/2026-10-26-test_hotel.csv')
        self.assertEqual(rows[0]['price_source'],'OTA');self.assertIn('200',s.markdown(rows))
        self.assertEqual(len(p.read_csv(self.args.ledger)),1)
        self.assertNotIn('SECRET',''.join(f.read_text() for f in self.root.rglob('*.csv')))


if __name__=='__main__':unittest.main()
