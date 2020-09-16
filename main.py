import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

class minerStat():
    def __init__(self):
        self.baseUrl = 'https://minerstat.com/'
        pass

    def getGpus(self, currency, electricityCost, isMultiPool):
        url = self.baseUrl + 'hardware/gpus'
        data = {'algorithms': 'All', 'currency': currency, 'electricityCosts': electricityCost, 'multipools': int(isMultiPool)}
        response = requests.post(url, data=data).content
        soup = BeautifulSoup(response, 'html.parser')
        gpuList = soup.find_all('div', {'class': 'tr'})

        # Placeholder
        gpuName, coin1PnL, coin1Name, coin2PnL, coin2Name, coin3PnL, coin3Name = [[] for i in range(7)]

        # Loop through each GPU
        for gpu in gpuList:
            gpuRow = gpu.find('div', {'class': 'flexHardware td'})
            if gpuRow is None:
                continue
            gpuName.append(gpuRow.find('a').text.strip())
            pnlList = gpu.find_all('div', {'class': 'profits'})

            # Loop through each Estimated Daily Profit
            for pnl in pnlList:
                pnlCols = pnl.find_all('div', {'class': 'text'})
                if len(pnlCols) != 3:
                    coin1PnL.append(np.nan)
                    coin2Name.append(np.nan)
                    coin2PnL.append(np.nan)
                    coin2Name.append(np.nan)
                    coin3PnL.append(np.nan)
                    coin3Name.append(np.nan)
                    continue

                # Estimated Daily Profit for each GPU in each column
                pnlCol1 = pnlCols[0].text.strip().split('\n')
                pnlCol2 = pnlCols[1].text.strip().split('\n')
                pnlCol3 = pnlCols[2].text.strip().split('\n')

                # Append cleaned data into lists
                coin1PnL.append(pnlCol1[0].strip(currency))
                coin1Name.append(pnlCol1[1])
                coin2PnL.append(pnlCol2[0].strip(currency))
                coin2Name.append(pnlCol2[1])
                coin3PnL.append(pnlCol3[0].strip(currency))
                coin3Name.append(pnlCol3[1])

        df = pd.DataFrame(zip(gpuName, coin1Name, coin1PnL, coin2Name, coin2PnL, coin3Name, coin3PnL), columns=['GPU Name', 'Algo 1 Name', 'Algo 1 PnL', 'Algo 2 Name', 'Algo 2 PnL', 'Algo 3 Name', 'Algo 3 PnL'])
        return df

    def pcPart(self, deviceName):
        # GPU Name: [Price, TDP]
        dvc = {'Radeon VII': [1328, 300], 'RTX 2080 Ti': [1800, 280], 'RTX 2070 Super': [549, 215], 'RTX 2080 Super': [780, 250],
               'RTX 2080': [800, 215], 'P102-100': [360, 250], 'GTX 1080 Ti': [1100, 250], 'RTX 2070': [420, 175], 'RX 5700': [377, 300],
               'Tesla P100-PCIE-16GB': [3250, 250], 'P104-100': [300, 180], 'GTX 1070 Ti': [429, 180], 'GTX 1080': [860, 180], 'RX 5700 XT': [400, 225],
               'RTX 2060': [370, 180], 'RX Vega 56': [600, 210], 'RX 5600 XT': [300, 150], 'GTX 1660 Ti': [270, 120], 'GTX 1660 Super': [250, 120],
               'RTX 2060 Super': [435, 175], 'GTX 1070': [625, 150], 'RX Vega 64': [620, 295], 'GTX 1660': [220, 120], 'RX 580': [180, 185],
               'R9 390': [350, 275], 'RX 470': [240, 120], 'RX 480': [400, 150], 'GTX 1060': [180, 120]}
        try:
            return dvc[deviceName]
        except KeyError:
            return [np.nan, np.nan]
    def run(self, currency, electricityCost, isMultiPool):
        df = self.getGpus(currency=currency, electricityCost=electricityCost, isMultiPool=isMultiPool)
        devicePrice, deviceTDP = [], []
        for gpu in df['GPU Name'].tolist():
            gpu = " ".join(gpu.split(' ')[1:]).replace('Ti', ' Ti')
            gpuInfo = self.pcPart(gpu)
            devicePrice.append(gpuInfo[0])
            deviceTDP.append(gpuInfo[1])
        df.insert(1, column='Product Price', value=devicePrice)
        df.insert(2, column='Product TDP', value=deviceTDP)
        df.insert(3, column='PnL per Watt', value=df['Algo 1 PnL'].astype(float) / df['Product TDP'])
        df.insert(4, column='PnL per GPU Price', value=df['Algo 1 PnL'].astype(float) / df['Product Price'])
        df = df.sort_values('PnL per Watt', ascending=False)
        print(df)

if __name__ == '__main__':
    ms = minerStat()
    # ms.getGpus(currency='USD', electricityCost=0.15, isMultiPool=True)
    ms.run(currency='USD', electricityCost=0.15, isMultiPool=True)