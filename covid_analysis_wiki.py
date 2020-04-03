import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import wget, os, sys
import dateutil


# some valid countries names: 
# Mainland_China, Italy, France, United_States, United_Kingdom, Spain, Germany, Netherlands, Sweden 



class Covid_analysis_wiki():
    

    def __init__(self, countries=['Italy','France'], download=False, fitpts=5, fitpts_ext=10, procapite=True, verbose=False):
        ''' 
        plot covid data of countries from their wikipedia pages.
        fit the log of the last 'fitpts' points, extend the plot to +- 'fitpts_ext' points

        ex. usage: 
            covid_analysis_wiki.Covid_analysis_wiki(download=True, countries=['Italy','France','United_States'], procapite=True)
        '''
        self.wiki_page = 'https://en.wikipedia.org/w/index.php?title=Template:2019%E2%80%9320_coronavirus_pandemic_data/'
        self.ntests_filename = 'full-list-total-tests-for-covid-19.csv'
        self.d_data = {}
        self.verbose = verbose
        
        for country in countries:
            if download:
                self.wiki_download(country)
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


    
    def ntests_download(self):
        ''' download tests .csv from blob:https://ourworldindata.org/e409dc8f-f005-4693-8874-7ecdd659df6b '''
        import webbot, time 
        print('covid_analysis_wiki.download_tests(): downloading n.tests using Chromium...')
        driver = webbot.Browser()                                                                                                                            
        driver.go_to('https://ourworldindata.org/covid-testing')
        driver.scrolly(4000)
        driver.click(text='DATA', number=1)
        driver.click(text=self.ntests_filename)                                                                                                    
        # wait until download is done:
        timeout = 10
        filesizes = 0
        t0 = time.time()
        while True:
            time.sleep(.5)
            try:
                filesize = os.path.getsize('/home/francesco/Downloads/' + self.ntests_filename)
            except:
                filesize = 0
            filesizes = np.append(filesizes, filesize)    
            if filesize>0 and len(filesizes)>3 and not np.any(np.diff(filesizes)[:-3]):
                break
            else:
                if time.time() - t0 > timeout:
                    raise TimeoutError('timeout in downlaoding.')
        driver.close_current_tab()
        os.replace('/home/francesco/Downloads/' + self.ntests_filename, '/home/francesco/scripts/repositories/covid19_analysis/' + self.ntests_filename)
        print('covid_analysis_wiki.download_tests(): done.')



    def ntests_make_dict_from_csv(self, filename):
        ''' open file and make main dict output '''
        import csv
        f = open(filename, newline='')
        f_reader = csv.DictReader(f) 
        k = 0 
        d = {} 
        for i in f_reader: 
            d[k] = dict(i) 
            k += 1 
        return d



    def ntests_make_country_data(self, country)
        ''' make ntests data for country '''
        d = self.ntests_make_dict_from_csv(self.ntests_filename)
        



    def wiki_download(self, country):
        ''' download from wikipedia page of country '''
        print(f'covid_analysis_wiki.wiki_download(): downloading {country}')
        filename_wiki = f'wiki_{country}.txt'
        if filename_wiki in os.listdir():
            os.rename(filename_wiki, filename_wiki+'.old')
        address_wiki = self.wiki_page+country+'_medical_cases_chart&action=edit'
        if self.verbose: 
            print(f'covid_analysis_wiki.wiki_download(): {address_wiki}')
        sys.stdout = open(os.devnull, "w")
        wget.download(address_wiki, filename_wiki)
        sys.stdout = sys.__stdout__


    
    def read_file(self, country):
        # read country file:
        with open(f'wiki_{country}.txt', 'r') as f:
            lines = f.readlines()
        # get data:
        # format until 200327:
        found_lines = [line for line in lines if re.match('{{Medical cases chart/Row\|202', line)]
        data_format = 'old'
        if self.verbose: print(f'covid_analysis_wiki.read_file(): found_lines: {found_lines}')
        # format from 200327:
        if found_lines == []:
            found_lines = [line for line in lines if re.match('202', line)]
            data_format = '200327'
        if self.verbose: print(f'covid_analysis_wiki.read_file(): found_lines: {found_lines}')
            
        if country == 'Mainland_China':
            found_lines = [f.replace(';;;',';') for f in found_lines]
        
        if data_format == 'old':
            data_matrix = [f.split(sep='|')[1:5] for f in found_lines]
        elif data_format == '200327':
            data_matrix = [f.split(sep=';')[:4] for f in found_lines]
#        for i,d in enumerate(data_matrix):
#            for j,dd in enumerate(d[1:]):
#                try:
#                    int(dd)
#                except:
#                    data_matrix[i][j+1] = ''      
        if self.verbose: 
            if self.verbose: print(f'covid_analysis_wiki.read_file(): data_matrix: {data_matrix}') 
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
        marker_size= 4
        fig1 = plt.figure('cumulative', clear=True, figsize=(5,8))
        ax11 = fig1.add_subplot(311)
        ax12 = fig1.add_subplot(312, sharex=ax11)
        ax13 = fig1.add_subplot(313, sharex=ax11)
        fig2 = plt.figure('per day', clear=True, figsize=(5,8))
        ax21 = fig2.add_subplot(311, sharex=ax11)
        ax22 = fig2.add_subplot(312, sharex=ax11)
        ax23 = fig2.add_subplot(313, sharex=ax11)
        fig3 = plt.figure('tests', clear=True, figsize=(5,8))
        ax31 = fig3.add_subplot(311)
        ax32 = fig3.add_subplot(312)
        ax33 = fig3.add_subplot(313)

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
            cc, = ax11.semilogy(cases_dates_float, cases, '-o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            cd, = ax12.semilogy(death_dates_float, death, '-o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            cr, = ax13.semilogy(recov_dates_float, recov, '-o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            ax21.semilogy(cases_dates_float[1:], np.diff(cases), '-o', alpha=0.6, label=country, ms=marker_size)
            ax22.semilogy(death_dates_float[1:], np.diff(death), '-o', alpha=0.6, label=country, ms=marker_size)
            ax23.semilogy(recov_dates_float[1:], np.diff(recov), '-o', alpha=0.6, label=country, ms=marker_size)
            ax31.plot(cases[1:], np.diff(cases), '-o', alpha=0.7, label=country, ms=marker_size)
            ax32.plot(death[1:], np.diff(death), '-o', alpha=0.7, label=country, ms=marker_size)
            ax33.plot(recov[1:], np.diff(recov), '-o', alpha=0.7, label=country, ms=marker_size)
            # fit ot log:
            dt = 86400 # = np.diff(cases_dates_float)[-1]
            try:
                logfit_cases = np.polyfit(cases_dates_float[-fitpts:], np.log10(cases[-fitpts:]), 1)
                xfit_cases = np.linspace(cases_dates_float[-fitpts] - fitpts_ext*dt, cases_dates_float[-1] + fitpts_ext*dt, 10)
                ax11.plot(xfit_cases, 10**np.poly1d(logfit_cases)(xfit_cases), '--', lw=2, alpha=0.6, color=cc.get_color(), ms=marker_size)
            except:
                print('plot_data(): error logfit cases')
            try:
                logfit_death = np.polyfit(death_dates_float[-fitpts:], np.log10(death[-fitpts:]), 1)
                xfit_death = np.linspace(death_dates_float[-fitpts] - fitpts_ext*dt, death_dates_float[-1] + fitpts_ext*dt, 10)
                ax12.plot(xfit_death, 10**np.poly1d(logfit_death)(xfit_death), '--', lw=2, alpha=0.6, color=cd.get_color(), ms=marker_size)
            except:
                print('plot_data(): error logfit death')
            try:
                logfit_recov = np.polyfit(recov_dates_float[-fitpts:], np.log10(recov[-fitpts:]), 1)
                xfit_recov = np.linspace(recov_dates_float[-fitpts] - fitpts_ext*dt, recov_dates_float[-1] + fitpts_ext*dt, 10)
                ax13.plot(xfit_recov, 10**np.poly1d(logfit_recov)(xfit_recov), '--', lw=2, alpha=0.6, color=cr.get_color(), ms=marker_size)
            except:
                print(f'plot_data(): {country} error logfit recovery')
            
            ax11.semilogy(cases_dates_float[-fitpts:], cases[-fitpts:], 'o', color=cc.get_color(), alpha=0.6, label=country, ms=marker_size)
            ax12.semilogy(death_dates_float[-fitpts:], death[-fitpts:], 'o', color=cd.get_color(), alpha=0.6, label=country, ms=marker_size)
            ax13.semilogy(recov_dates_float[-fitpts:], recov[-fitpts:], 'o', color=cr.get_color(), alpha=0.6, label=country, ms=marker_size)

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
        ax31.set_ylabel('Daily cases'+proc)
        ax32.set_ylabel('Daily deaths'+proc)
        ax33.set_ylabel('Daily recoveries'+proc)
        ax21.set_xlabel('Days')
        ax22.set_xlabel('Days')
        ax23.set_xlabel('Days')
        ax31.set_xlabel('Cumul. cases')
        ax32.set_xlabel('Cumul. death')
        ax33.set_xlabel('Cumul. recov.')
        ax21.legend(fontsize=8,labelspacing=0)
        ax22.legend(fontsize=8,labelspacing=0)
        ax23.legend(fontsize=8,labelspacing=0)
        ax31.legend(fontsize=8,labelspacing=0)
        ax32.legend(fontsize=8,labelspacing=0)
        ax33.legend(fontsize=8,labelspacing=0)
        fig1.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()
        
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime.fromtimestamp(x_val).date()).lstrip('2020'))
        ax11.xaxis.set_major_formatter(formatter)
        ax12.xaxis.set_major_formatter(formatter)
        ax13.xaxis.set_major_formatter(formatter)
        ax21.xaxis.set_major_formatter(formatter)
        ax22.xaxis.set_major_formatter(formatter)
        ax23.xaxis.set_major_formatter(formatter)


