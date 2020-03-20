import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import wget, os
import dateutil


# TODO fix Mainland_China, check other countries


class Covid_analysis_wiki():
    

    def __init__(self, countries=['Italy','France'], download=False, fitpts=5, fitpts_ext=10):
        ''' 
        plot covid data of countries from their wikipedia pages.
        fit the log of the last 'fitpts' points, extend the plot to +- 'fitpts_ext' points

        ex. usage: 
            covid_analysis_wiki.Covid_analysis_wiki(download=1, countries=['Italy','France','United_States'])
        '''
        self.wiki_page = 'https://en.wikipedia.org/w/index.php?title=Template:2019%E2%80%9320_coronavirus_pandemic_data/'
        self.d_data = {}
        
        for country in countries:
            if download:
                self.download(country)
            self.read_file(country)
        self.plot_data(fitpts=fitpts, fitpts_ext=fitpts_ext)


    def download(self, country):
        print(f'covid_analysis_wiki.download(): downloading {country}')
        filename = f'wiki_{country}.txt'
        if filename in os.listdir():
            os.rename(filename, filename+'.old')
        address = self.wiki_page+country+'_medical_cases_chart&action=edit'
        print(f'covid_analysis_wiki.download(): {address}')
        wget.download(address, filename)
        
    
    def read_file(self, country):
        # read country file:
        with open(f'wiki_{country}.txt', 'r') as f:
            lines = f.readlines()
        # get data:
        found_lines = [line for line in lines if re.match('{{Medical cases chart/Row\|202', line)]
        data_matrix = [f.replace('|||','|').split(sep='|')[1:5] for f in found_lines]
        #data_matrix = [f.split(sep='|')[1:5] for f in found_lines]
        #print(data_matrix)

        for i,d in enumerate(data_matrix):
            print('---')
            print(i,d)
            for j,dd in enumerate(d[1:]):
                print(j, dd)
                try:
                    int(dd)
                except:
                    print(data_matrix[i][j+1])
                    data_matrix[i][j+1] = ''
                    print(data_matrix[i])
                    print('-corr')
        print(data_matrix)
        
        #return data_matrix
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

   
    def plot_data(self, fitpts=5, fitpts_ext=10):
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
            death_dates = d[country]['death_dates']
            recov_dates = d[country]['recov_dates']
            cases_dates = d[country]['cases_dates']
            death_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in death_dates])
            recov_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in recov_dates])
            cases_dates_float = np.array([dateutil.parser.parse(i).timestamp() for i in cases_dates])
            death = d[country]['death']
            recov = d[country]['recov']
            cases = d[country]['cases']

            # plots:
            cc, = ax11.semilogy(cases_dates_float, cases, '-o', mfc='none', mew=1, alpha=0.7)
            cd, = ax12.semilogy(death_dates_float, death, '-o', mfc='none', mew=1, alpha=0.7)
            cr, = ax13.semilogy(recov_dates_float, recov, '-o', mfc='none', mew=1, alpha=0.7)
            ax21.plot(cases_dates_float[1:], np.diff(cases), '-o', alpha=0.6, label=country)
            ax22.plot(death_dates_float[1:], np.diff(death), '-o', alpha=0.6, label=country)
            ax23.plot(recov_dates_float[1:], np.diff(recov), '-o', alpha=0.6, label=country)
            
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
                print('plot_data(): error logfit recovery')

            ax11.semilogy(cases_dates_float[-fitpts:], cases[-fitpts:], 'o', color=cc.get_color(), alpha=0.6, label=country)
            ax12.semilogy(death_dates_float[-fitpts:], death[-fitpts:], 'o', color=cd.get_color(), alpha=0.6, label=country)
            ax13.semilogy(recov_dates_float[-fitpts:], recov[-fitpts:], 'o', color=cr.get_color(), alpha=0.6, label=country)


        ax11.set_ylabel('Cumul. cases')
        ax12.set_ylabel('Cumul. deaths')
        ax13.set_ylabel('Cumul. recoveries')
        ax11.set_xlabel('Days')
        ax12.set_xlabel('Days')
        ax13.set_xlabel('Days')
        ax11.legend(fontsize=9)
        ax21.set_ylabel('Daily cases')
        ax22.set_ylabel('Daily deaths')
        ax23.set_ylabel('Daily recoveries')
        ax21.set_xlabel('Days')
        ax22.set_xlabel('Days')
        ax23.set_xlabel('Days')
        ax21.legend(fontsize=9)
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


    #TODOc#
#    d_cases_day = {}
#    d_deaths_day = {}
#    d_cases = {}
#    d_deaths = {}
#    
#    fig = plt.figure('covid_xls cumulative', clear=True)
#    ax1 = fig.add_subplot(121)
#    ax2 = fig.add_subplot(122, sharex=ax1)
#
#    fig1 = plt.figure('covid_xls per day', clear=True)
#    ax11 = fig1.add_subplot(121)
#    ax12 = fig1.add_subplot(122, sharex=ax11)
#    
#    # get data from data.xls:
#    book = xlrd.open_workbook('data.xls')
#    sheet = book.sheet_by_index(0)
#    dates_float = sheet.col_values(0)
#    countries_all = sheet.col_values(1)
#    newconfcases = sheet.col_values(2)
#    newdeaths = sheet.col_values(3)
#    cases_all = np.array(list(zip(countries_all, dates_float, newconfcases)))[1:]
#    deaths_all = np.array(list(zip(countries_all, dates_float, newdeaths)))[1:]
#    
#    for country in countries:
#        # populate with dates_float, data:
#        c = np.array([[float(i[1]), float(i[2])] for i in cases_all if i[0]==country])
#        d = np.array([[float(i[1]), float(i[2])] for i in deaths_all if i[0]==country])
#        
#        # per day: 
#        d_cases_day[country] = np.copy(c[::-1])
#        d_deaths_day[country] = np.copy(d[::-1])
#
#        # cumulative:
#        d_cases[country] = np.copy(c[::-1])
#        d_deaths[country] = np.copy(d[::-1])
#        d_cases[country][:,1] = np.cumsum(d_cases[country][:,1])
#        d_deaths[country][:,1] = np.cumsum(d_deaths[country][:,1])
#
#        # fit of last fitpts:
#        xfit0c = d_cases[country][-fitpts:,0]
#        xfit0d = d_deaths[country][-fitpts:,0]
#        logfit_cases = np.polyfit(xfit0c, np.log10(d_cases[country][-fitpts:,1]), 1)
#        logfit_deaths = np.polyfit(xfit0d, np.log10(d_deaths[country][-fitpts:,1]), 1)
#        
#        # dates as days:
#        dates_time_c = [str(datetime.datetime(*xlrd.xldate_as_tuple(a, book.datemode)).date()) for a in d_cases[country][:,0]]
#        dates_time_d = [str(datetime.datetime(*xlrd.xldate_as_tuple(a, book.datemode)).date()) for a in d_deaths[country][:,0]]
#
#        # plots: 
#        p1, = ax1.semilogy(d_cases[country][:,0], d_cases[country][:,1], '-o', alpha=0.4, label=country)
#        p2, = ax2.semilogy(d_deaths[country][:,0], d_deaths[country][:,1], '-o', alpha=0.4, label=country)
#        
#        xfit1c = np.arange(xfit0c[0], xfit0c[-1] + fitpts_ext)
#        xfit1d = np.arange(xfit0d[0], xfit0d[-1] + fitpts_ext)
#        ax1.plot(xfit1c, 10**np.poly1d(logfit_cases)(xfit1c), '--', alpha=0.6, color=p1.get_color())
#        ax2.plot(xfit1d, 10**np.poly1d(logfit_deaths)(xfit1d), '--', alpha=0.6, color=p2.get_color())
#        
#        p11, = ax11.semilogy(d_cases_day[country][:,0], d_cases_day[country][:,1], '-o', alpha=0.4, label=country)
#        p12, = ax12.semilogy(d_deaths_day[country][:,0], d_deaths_day[country][:,1], '-o', alpha=0.4, label=country)
#
#    
#    ax1.legend()
#    ax2.legend()
#    ax11.legend()
#    ax12.legend()
#    ax1.set_xlabel('Days')
#    ax2.set_xlabel('Days')
#    ax1.set_ylabel('Cumulative cases')
#    ax2.set_ylabel('Cumulative deaths')
#    ax11.set_xlabel('Days')
#    ax12.set_xlabel('Days')
#    ax11.set_ylabel('Daily cases')
#    ax12.set_ylabel('Daily deaths')
#    fig.tight_layout()
#    fig1.tight_layout()
#
#    from matplotlib.ticker import FuncFormatter
#    formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime(*xlrd.xldate_as_tuple(x_val, book.datemode)).date()).lstrip('2020'))
#    ax1.xaxis.set_major_formatter(formatter)
#    ax2.xaxis.set_major_formatter(formatter)
#    ax11.xaxis.set_major_formatter(formatter)
#    ax12.xaxis.set_major_formatter(formatter)
#
#
#    #return d_cases, d_deaths
#    #return dates_time_d
#
#
