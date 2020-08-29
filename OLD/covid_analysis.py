import csv
import re
import numpy as np
import matplotlib.pyplot as plt

#wget.download('https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-14_1.xls', './data.xls')


# path to local /COVID-19 repository:
path0 = '/home/francesco/scripts/repositories/COVID-19/'

class Covid_analysis():

    def __init__(self, countries=['Italy','France','United Kingdom','Germany','US','Spain'], fitpts=5, fitpts_ext=20):

        path = path0 + 'csse_covid_19_data/csse_covid_19_time_series/'
        self.file_confirmed = path + 'time_series_19-covid-Confirmed.csv'
        self.file_deaths = path + 'time_series_19-covid-Deaths.csv' 
        self.file_recovered = path + 'time_series_19-covid-Recovered.csv' 

        self.d_confirmed = self.make_dict(self.file_confirmed)
        self.d_deaths = self.make_dict(self.file_deaths)
        self.d_recovered = self.make_dict(self.file_recovered)

        self.plots_countries('cases', countries, fitpts=fitpts, fitpts_ext=fitpts_ext)
        self.plots_countries('deaths', countries, fitpts=fitpts, fitpts_ext=fitpts_ext)
        self.plots_countries('recovered', countries, fitpts=fitpts, fitpts_ext=fitpts_ext)



    def open_xls(self, countries=['Italy']):
        ''' '''
        book = xlrd.open_workbook('data.xls') 
        sheet = book.sheet_by_index(0)
        dates_float = sheet.col_values(0)
        countries_all = sheet.col_values(1)
        newconfcases = sheet.col_values(2)
        newdeaths = sheet.col_values(3)
        cases_all = np.array(list(zip(countries_all, dates_float, newconfcases)))[1:]
        deaths_all = np.array(list(zip(countries_all, dates_float, newdeaths)))[1:]
        
        for country in countries:
            cases_country  = [i for i in cases_all if i[0]==country]
            deaths_country = [i for i in deaths_all if i[0]==country] 

        return cases_country, deaths_country



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
        ''' find keys,cases,dates for country in dict d'''
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



    def plots_countries(self, which='cases', countries=[], fitpts=5, fitpts_ext=5):
        ''' plot data for every country in list, with fit of last fitpts of data
        which : 'cases', 'deaths'
        countries : list of string with valid names
        fitpts : last points to use in fit 
        fitpts_ext : extra points to plot fit
        '''   
        if which == 'cases':
            d = self.d_confirmed
        elif which == 'deaths':
            d = self.d_deaths
        elif which == 'recovered':
            d = self.d_recovered

        fig1 = plt.figure(which, clear=True)
        ax11 = fig1.add_subplot(211)
        ax12 = fig1.add_subplot(212, sharex=ax11)

        for country in countries:
            # get data:
            cases_conf, dates = self.find_country(d, country)
            # fit of last fitpts:            
            xfit0 = np.arange(len(cases_conf)-fitpts, len(cases_conf))
            logfit_cases = np.polyfit(xfit0, np.log10(cases_conf[-fitpts:]), 1) 
            # plots:
            c1, = ax11.semilogy(cases_conf, '-o', alpha=0.5, label=country)
            xfit1 = np.arange(xfit0[0], xfit0[-1]+fitpts_ext)
            ax11.plot(xfit1, 10**np.poly1d(logfit_cases)(xfit1), '--', color=c1.get_color())
            ax12.semilogy(np.diff(cases_conf), '-o', alpha=0.5, label=country)
            
        ax11.legend()
        ax12.legend()
        ax11.set_title(f'day0={dates[0]}, last:{dates[-1]}')
        ax11.set_xlabel('days', fontsize=14)
        ax12.set_xlabel('days', fontsize=14)
        ax11.set_ylabel(which, fontsize=14)
        ax12.set_ylabel(which+'/day', fontsize=14)
        plt.tight_layout()
            

        



