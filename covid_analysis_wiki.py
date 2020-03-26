import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import wget, os, sys
import dateutil


# some valid names: 
# Mainland_China, Italy, France, United_States, United_Kingdom, Spain, Germany, 

#TODO
# Mainland_China error: seems that the data format changed from | to ; 


class Covid_analysis_wiki():
    

    def __init__(self, countries=['Italy','France'], download=False, fitpts=5, fitpts_ext=10, procapite=True, verbose=False):
        ''' 
        plot covid data of countries from their wikipedia pages.
        fit the log of the last 'fitpts' points, extend the plot to +- 'fitpts_ext' points

        ex. usage: 
            covid_analysis_wiki.Covid_analysis_wiki(download=True, countries=['Italy','France','United_States'], procapite=True)
        '''
        self.wiki_page = 'https://en.wikipedia.org/w/index.php?title=Template:2019%E2%80%9320_coronavirus_pandemic_data/'
        self.d_data = {}
        self.verbose = verbose
        
        for country in countries:
            if download:
                self.download(country)
            self.read_file(country)
        self.plot_data(fitpts=fitpts, fitpts_ext=fitpts_ext, procapite=procapite)



    def population(self,country):
        if country == 'Italy':          pop =    60486199
        if country == 'United_States':  pop =   327200000
        if country == 'Mainland_China': pop =  1386000000
        if country == 'Spain':          pop =    46660000
        if country == 'France':         pop =    66990000
        if country == 'United_Kingdom': pop =    66440000
        if country == 'Netherlands':    pop =    17180000
        if country == 'Germany':        pop =    82790000
        if country == 'South_Korea':    pop =    51470000
        return pop



    def download(self, country):
        print(f'covid_analysis_wiki.download(): downloading {country}')
        filename = f'wiki_{country}.txt'
        if filename in os.listdir():
            os.rename(filename, filename+'.old')
        address = self.wiki_page+country+'_medical_cases_chart&action=edit'
        if self.verbose: 
            print(f'covid_analysis_wiki.download(): {address}')
        sys.stdout = open(os.devnull, "w")
        wget.download(address, filename)
        sys.stdout = sys.__stdout__


    
    def read_file(self, country):
        # read country file:
        with open(f'wiki_{country}.txt', 'r') as f:
            lines = f.readlines()
        # get data:
        found_lines = [line for line in lines if re.match('{{Medical cases chart/Row\|202', line)]
        
        if country == 'Mainland_China':
            data_matrix = [f.replace('|||','|').split(sep='|')[1:5] for f in found_lines]
        else:
            data_matrix = [f.split(sep='|')[1:5] for f in found_lines]

        for i,d in enumerate(data_matrix):
            for j,dd in enumerate(d[1:]):
                try:
                    int(dd)
                except:
                    data_matrix[i][j+1] = ''
        
        if self.verbose: 
            print(data_matrix) 
        
        # avoid empty data:
        death_dates = [i[0] for i in data_matrix if i[1]!='' and not i[1].startswith('(')]
        recov_dates = [i[0] for i in data_matrix if i[2]!='' and not i[2].startswith('(')]
        cases_dates = [i[0] for i in data_matrix if i[3]!='' and not i[3].startswith('(')]
        death = np.array([int(i[1]) for i in data_matrix if i[1]!='' and not i[1].startswith('(')])
        recov = np.array([int(i[2]) for i in data_matrix if i[2]!='' and not i[2].startswith('(')])
        cases = np.array([int(i[3]) for i in data_matrix if i[3]!='' and not i[3].startswith('(')])
        # store:
        self.d_data[country] = {}
        self.d_data[country]['death_dates'] = death_dates
        self.d_data[country]['recov_dates'] = recov_dates
        self.d_data[country]['cases_dates'] = cases_dates
        self.d_data[country]['death'] = death
        self.d_data[country]['recov'] = recov
        self.d_data[country]['cases'] = cases
        return data_matrix

   
    def plot_data(self, fitpts=5, fitpts_ext=10, procapite=True):
        d = self.d_data
        fig1 = plt.figure('cumulative', clear=True, figsize=(5,8))
        ax11 = fig1.add_subplot(311)
        ax12 = fig1.add_subplot(312, sharex=ax11)
        ax13 = fig1.add_subplot(313, sharex=ax11)
        fig2 = plt.figure('per day', clear=True, figsize=(5,8))
        ax21 = fig2.add_subplot(311, sharex=ax11)
        ax22 = fig2.add_subplot(312, sharex=ax11)
        ax23 = fig2.add_subplot(313, sharex=ax11)

        for country in d:
            if procapite:
                pop = self.population(country)
            else:
                pop = 1

            death_dates = d[country]['death_dates']
            recov_dates = d[country]['recov_dates']
            cases_dates = d[country]['cases_dates']
            death_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in death_dates])
            recov_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in recov_dates])
            cases_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in cases_dates])

            death = d[country]['death']/pop
            recov = d[country]['recov']/pop
            cases = d[country]['cases']/pop

            # plots:
            cc, = ax11.semilogy(cases_dates_float, cases, '-o', mfc='none', mew=1, alpha=0.7)
            cd, = ax12.semilogy(death_dates_float, death, '-o', mfc='none', mew=1, alpha=0.7)
            cr, = ax13.semilogy(recov_dates_float, recov, '-o', mfc='none', mew=1, alpha=0.7)
            ax21.semilogy(cases_dates_float[1:], np.diff(cases), '-o', alpha=0.6, label=country)
            ax22.semilogy(death_dates_float[1:], np.diff(death), '-o', alpha=0.6, label=country)
            ax23.semilogy(recov_dates_float[1:], np.diff(recov), '-o', alpha=0.6, label=country)
            
            # fit ot log:
            dt = 86400 # = np.diff(cases_dates_float)[-1]
            try:
                logfit_cases = np.polyfit(cases_dates_float[-fitpts:], np.log10(cases[-fitpts:]), 1)
                xfit_cases = np.linspace(cases_dates_float[-fitpts] - fitpts_ext*dt, cases_dates_float[-1] + fitpts_ext*dt, 10)
                ax11.plot(xfit_cases, 10**np.poly1d(logfit_cases)(xfit_cases), '--', lw=2, alpha=0.6, color=cc.get_color())
            except:
                print('plot_data(): error logfit cases')

            try:
                logfit_death = np.polyfit(death_dates_float[-fitpts:], np.log10(death[-fitpts:]), 1)
                xfit_death = np.linspace(death_dates_float[-fitpts] - fitpts_ext*dt, death_dates_float[-1] + fitpts_ext*dt, 10)
                ax12.plot(xfit_death, 10**np.poly1d(logfit_death)(xfit_death), '--', lw=2, alpha=0.6, color=cd.get_color())
            except:
                print('plot_data(): error logfit death')

            try:
                logfit_recov = np.polyfit(recov_dates_float[-fitpts:], np.log10(recov[-fitpts:]), 1)
                xfit_recov = np.linspace(recov_dates_float[-fitpts] - fitpts_ext*dt, recov_dates_float[-1] + fitpts_ext*dt, 10)
                ax13.plot(xfit_recov, 10**np.poly1d(logfit_recov)(xfit_recov), '--', lw=2, alpha=0.6, color=cr.get_color())
            except:
                print(f'plot_data(): {country} error logfit recovery')

            ax11.semilogy(cases_dates_float[-fitpts:], cases[-fitpts:], 'o', color=cc.get_color(), alpha=0.6, label=country)
            ax12.semilogy(death_dates_float[-fitpts:], death[-fitpts:], 'o', color=cd.get_color(), alpha=0.6, label=country)
            ax13.semilogy(recov_dates_float[-fitpts:], recov[-fitpts:], 'o', color=cr.get_color(), alpha=0.6, label=country)

        proc = ' per capita' if procapite else ''
        ax11.set_ylabel('Cumul. cases'+proc)
        ax12.set_ylabel('Cumul. deaths'+proc)
        ax13.set_ylabel('Cumul. recoveries'+proc)
        ax11.set_xlabel('Days')
        ax12.set_xlabel('Days')
        ax13.set_xlabel('Days')
        ax11.legend(fontsize=8,labelspacing=0)
        ax12.legend(fontsize=8,labelspacing=0)
        ax13.legend(fontsize=8,labelspacing=0)
        ax21.set_ylabel('Daily cases'+proc)
        ax22.set_ylabel('Daily deaths'+proc)
        ax23.set_ylabel('Daily recoveries'+proc)
        ax21.set_xlabel('Days')
        ax22.set_xlabel('Days')
        ax23.set_xlabel('Days')
        ax21.legend(fontsize=8,labelspacing=0)
        ax22.legend(fontsize=8,labelspacing=0)
        ax23.legend(fontsize=8,labelspacing=0)
        fig1.tight_layout()
        fig2.tight_layout()
        
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime.fromtimestamp(x_val).date()).lstrip('2020'))
        ax11.xaxis.set_major_formatter(formatter)
        ax12.xaxis.set_major_formatter(formatter)
        ax13.xaxis.set_major_formatter(formatter)
        ax21.xaxis.set_major_formatter(formatter)
        ax22.xaxis.set_major_formatter(formatter)
        ax23.xaxis.set_major_formatter(formatter)


