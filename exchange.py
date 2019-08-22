
# TODO
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

def daum_exchanges():
    
    # TODO
    url = 'https://finance.daum.net/exchanges'
    driver = webdriver.Chrome()
    driver.get(url)
    national0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[1]/a')
    unit0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[2]')
    unit_p0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[3]/span')
    rate_pre0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[4]/span')
    price_buy0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[5]/span')
    price_sell0 = driver.find_elements_by_xpath('//*[@id="boxContents"]/div[2]/div[2]/div/table/tbody/tr/td[6]/span')
    national = [it.text.split('(')[0].strip() for it in national0]
    unit = [it.text.strip() for it in unit0]
    unit_p = [it.text.strip() for it in unit_p0]
    rate_pre = [it.text[1:].strip() for it in rate_pre0]
    price_buy = [it.text.strip() for it in price_buy0]
    price_sell = [it.text.strip() for it in price_sell0]
    driver.quit()
    df0 = []
    for i in range(len(unit)):
        df0.append({'country':national[i],'currencyName':unit[i],'basePrice':unit_p[i],'changePrice':rate_pre[i],'cashBuyingPrice':price_buy[i],'cashSellingPrice':price_sell[i]})
    df = pd.DataFrame(df0)    
    
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
        self.basePrice = float(basePrice.replace(',',''))
        self.changePrice = changePrice
        self.cashBuyingPrice = float(cashBuyingPrice.replace(',',''))
        self.cashSellingPrice = float(cashSellingPrice.replace(',',''))

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
        records=[ExchangeDaum(a[1].country,a[1].currencyName,a[1].basePrice,a[1].changePrice,a[1].cashBuyingPrice,a[1].cashSellingPrice) for a in df.iterrows()]

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