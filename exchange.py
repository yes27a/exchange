
# TODO
import requests
from fake_useragent import UserAgent
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

# TODO
def daum_exchanges():
    
    # TODO
    url = 'https://finance.daum.net/exchanges'
    url2 = 'https://finance.daum.net/api/exchanges/summaries'
    headers = {'User-Agent':UserAgent().Chrome,
              'referer':'https://finance.daum.net/exchanges'}
    req = requests.get(url2, headers=headers)
    jsondata=req.json()['data']
    df0 = [{'country':a['country'],'currencyName':a['currencyName'],'basePrice':a['basePrice'],'change':'+' if str(a['change'])=='RISE' else '-','changePrice':('+' if str(a['change'])=='RISE' else '-')+str(a['changePrice']),'cashBuyingPrice':a['cashBuyingPrice'],'cashSellingPrice':a['cashSellingPrice']} 
     for a in jsondata]
    
    df = pd.DataFrame(df0,columns=['country','currencyName','basePrice','changePrice','cashBuyingPrice','cashSellingPrice'])    
    
    return df

base = declarative_base()
class ExchangeDaum(base):
    __tablename__ = "daum"

    country = Column(String(50),primary_key=True)
    currencyName = Column(String(100), nullable=False)
    basePrice = Column(Float(10), nullable=False)
    changePrice = Column(String(10), nullable=False)
    cashBuyingPrice = Column(Float(10), nullable=False)
    cashSellingPrice = Column(Float(10), nullable=False)


    def __init__(self, country, currencyName,basePrice,changePrice,cashBuyingPrice,cashSellingPrice):
        self.country = country
        self.currencyName = currencyName
        self.basePrice = float(basePrice)
        self.changePrice = changePrice
        self.cashBuyingPrice = float(cashBuyingPrice)
        self.cashSellingPrice = float(cashSellingPrice)

    def __repr__(self):
        return "<ExchangeDaum>" 

class SaveDatabase:

    def __init__(self, base, df, ip="52.78.15.216", pw="1234", database="exchange"):
        # TODO
        self.mysql_client = create_engine("mysql://root:{}@{}/{}?charset=utf8".format(pw, ip, database))
        self.base = base
        self.df = df
        
    def mysql_save(self):
        # TODO
        records = []
        # make table
        self.base.metadata.create_all(self.mysql_client)
        
        # make session
        maker = sessionmaker(bind=self.mysql_client)
        session = maker()
        
        #data
        records=[ExchangeDaum(a[1].country,a[1].currencyName,a[1].basePrice,a[1].changePrice,a[1].cashBuyingPrice,a[1].cashSellingPrice) for a in self.df.iterrows()]

        # save datas
        session.add_all(records)
        session.commit()

        # close session
        session.close()

def run():
    # 데이터 베이스 저장 객체 생성
    sd = SaveDatabase(base, daum_exchanges())
    # 데이터 베이스에 저장
    sd.mysql_save()
    print('saved!')

run()