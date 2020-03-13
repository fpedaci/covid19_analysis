import csv
import re
import numpy as np
import matplotlib.pyplot as plt


# path to local /COVID-19 repository:
path0 = '/home/francesco/scripts/repositories/COVID-19/'

class Covid_analysis():

    def __init__(self):
        path = path0 + 'csse_covid_19_data/csse_covid_19_time_series/'
        self.file_confirmed = path + 'time_series_19-covid-Confirmed.csv'
        self.file_deaths = path + 'time_series_19-covid-Deaths.csv' 
        self.d_confirmed = self.make_dict(self.file_confirmed)
        self.d_deaths = self.make_dict(self.file_deaths)


    def make_dict(self, filename):
        ''' open file and make main dict output '''
        f = open(filename, newline='') 
        f_reader = csv.DictReader(f) 
        k = 0 
        d = {} 
        for i in f_reader: 
            d[k] = dict(i) 
            k += 1 
        return d


    def find_country(self, d, country):
        ''' find keys for country in dict d'''
        keys_country = [i for i in d.keys() if d[i]['Country/Region']==country]
        print(f'Covid_analysis.find_country(): {country} found in {len(keys_country)} keys')
        
        for j,k in enumerate(keys_country):
            cases = np.array([int(d[k][i]) for i in d[k].keys() if re.match('(.|..)/(.|..)/(.|..)', i)])
            dates = np.array([i for i in d[k].keys() if re.match('(.|..)/(.|..)/(.|..)', i)])
            if j == 0:
                cases_matrix = np.zeros(len(cases))
            cases_matrix = np.vstack((cases_matrix, cases))
        cases_matrix = cases_matrix[1:]
        cases_sum = np.sum(cases_matrix, axis=0)
        return cases_sum, dates


    def plots_countries(self, countries=[], fitpts=5, fitpts_ext=5):
        ''' plot data for every country in list, with lin fit to log of last fitpts of data'''
        fig = plt.figure('find_country', clear=True)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=ax1)

        for country in countries:
            cases_conf, dates = self.find_country(self.d_confirmed, country)
            deaths, dates = self.find_country(self.d_deaths, country)
            
            xfit0 = np.arange(len(cases_conf)-fitpts, len(cases_conf))
            logfit = np.polyfit(xfit0, np.log10(cases_conf[-fitpts:]), 1) 
            
            p, = ax1.semilogy(cases_conf, '-o', alpha=0.5, label=country)
            xfit1 = np.arange(xfit0[0], xfit0[-1]+fitpts_ext)
            ax1.plot(xfit1, 10**np.poly1d(logfit)(xfit1), '--', color=p.get_color())
            ax2.semilogy(np.diff(cases_conf), '-o', alpha=0.5, label=country)
        
        ax1.legend()
        ax2.legend()
        ax1.set_title(f'day0={dates[0]}, last:{dates[-1]}')
        ax1.set_xlabel('Days')
        ax2.set_xlabel('Days')
        ax1.set_ylabel('Cases')
        ax2.set_ylabel('Cases/day')
            

        



