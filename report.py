# encoding=utf8

import sys, os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath('functions'))
from functions import mongo_db, csv_file2, diff
import pandas as pd

def read_db(coll):
    try:
        days = int(sys.argv[1])
        pers = float(sys.argv[2])
    except:
        print 'days and persentage whether missing or having a wrong format'
        sys.exit(1)

    delta = timedelta(days=days)
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    data_today = coll.find({'timestamp': {'$regex': date_today}})
    date_hist = datetime.utcnow() - delta
    date_hist = date_hist.strftime("%Y-%m-%d")
    data_hist = coll.find({'timestamp': {'$regex': date_hist}})
    if data_hist.count() == 0:
        print '%s data is missing' % date_hist
        sys.exit(1)
    if data_today.count() == 0:
        print "today's data is missing, run the spiders"
        sys.exit(1)

    header = 'brand,cashback_today,cashback_historical,diff,offer,details,url,source\n'
    fh = csv_file2(header, date_today, date_hist)

    read_df(data_today, data_hist, fh, pers)

def read_df(data_t, data_h, fh, pers):
    df_t = pd.DataFrame(list(data_t)).drop(['_id', 'timestamp'], axis=1).drop_duplicates(subset=['brand', 'source', 'offer', 'details', 'url'])
    df_h = pd.DataFrame(list(data_h)).drop(['_id', 'timestamp'], axis=1).drop_duplicates(subset=['brand', 'source', 'offer', 'details', 'url'])
    print "today's data:", len(df_t)
    print "historical data:", len(df_h)
    df_n = pd.merge(df_t, df_h, how='inner', left_on=['brand', 'source', 'offer', 'details', 'url'], right_on=['brand', 'source', 'offer', 'details', 'url'])
    df_n = df_n[df_n['cashback_x']!=''].apply(lambda x: diff(x, pers), axis=1).dropna()
    print "report data:", len(df_n)
    for i, r in df_n.iterrows():
        line = '"%s","%s","%s","%s","%s","%s","%s","%s"\n' % (r['brand'], r['cashback_x'], r['cashback_y'], r['diff'], r['offer'], r['details'], r['url'], r['source'])
        fh.write(line.encode('utf8'))

    fh.close()
    
def main():
    client, coll = mongo_db()
    read_db(coll)
    client.close()

main()
