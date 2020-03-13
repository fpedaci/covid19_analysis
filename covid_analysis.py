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


    def plots_countries(self, countries=[]):
        fig = plt.figure('find_country', clear=True)
        ax = fig.add_subplot(111)

        for country in countries:
            cases_conf, dates = self.find_country(self.d_confirmed, country)
            deaths, dates = self.find_country(self.d_deaths, country)
        
            ax.semilogy(cases_conf, '-o', label=country)
        
        ax.legend()
        ax.set_title(f'day0={dates[0]}, last:{dates[-1]}')
        ax.set_xlabel('Days')
        ax.set_ylabel('')
            

        



