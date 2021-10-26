import requests, json, pandas as pd

df=pd.read_csv('country-codes.csv')
ip=input('Enter the country name:').title()

#print(df.head())

index=df.index
try:
    condition=df['countries']==ip
    code_index=index[condition].tolist()
    ci=code_index[0]
    country_code=df['Alpha-2 code'].iloc[ci]

#print(ci)
#print(df['Alpha-2 code'].iloc[ci])
#print(country_code)


    url = "https://www.travel-advisory.info/api"

    #querystring = {'countrycode':'IND'}
    querystring=dict()
    querystring['countrycode']=country_code

    response = requests.request("GET", url, params=querystring)

    #print(response.text)

    r=json.loads(response.text)
    r2=r['data'][country_code]['advisory']

    print(r2['message'])
    print(r2['source'])

except:
    print('Enter the correct country name')