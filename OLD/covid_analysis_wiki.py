import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import wget, os, sys
import dateutil


# some valid countries names: 
# Mainland_China, Italy, France, United_States, United_Kingdom, Spain, Germany, Netherlands, Sweden 



class Covid_analysis_wiki():
    

    def __init__(self, countries=['Italy','France'], download_wiki=False, download_ntests=True, dotests=False, fitpts=5, fitpts_ext=10, procapite=True, verbose=False, doit=True, UKrmlast=False, rmlast=False, filt_win=7):
        ''' 
        Plot covid data of countries from their wikipedia pages.
        
        countries : list of valid country names (use '_' as in 'United_States', not 'United States')
        download_ntests : use Chromium to download number of tests
        download_wiki : download data from wikipedia pages
        fitpts : number of last point to fit with an exponential
        fitpts_ext : graphical extention of exponential fits beyond the data
        procapite : normalize to country population
        verbose : get debug info
        doit : run it all at __init__

        ex. usage: 
            covid_analysis_wiki.Covid_analysis_wiki(download=True, countries=['Italy','France','United_States'], procapite=True)

        '''

        self.wiki_page = 'https://en.wikipedia.org/w/index.php?title=Template:COVID-19_pandemic_data/'
        self.ntests_github = 'https://github.com/owid/covid-19-data/blob/master/public/data/testing/covid-testing-all-observations.csv'
        self.data_ourworldindata = 'https://covid.ourworldindata.org/data/owid-covid-data.json'
        self.d_data = {}
        self.verbose = verbose
        self.UKrmlast = UKrmlast
        self.rmlast = rmlast
        self.filt_win = filt_win
        
        if doit:
            # get ntests:
            if download_ntests:
                self.ntests_download(mode=2)
            else:
                self.ntests_filename = 'covid-testing-all-observations.csv'
            if dotests:
                self.ntests_make_dict_from_csv(self.ntests_filename)
            # get cases, deaths, recov:
            for country in countries:
                self.d_data[country] = {}
                if download_wiki:
                    self.wiki_download(country)
                self.read_file(country)
                if dotests:
                    self.ntests_make_country_data(country)
                    self.make_casesXntests(country)
            # plot all:
            self.plot_data(fitpts=fitpts, fitpts_ext=fitpts_ext, procapite=procapite)
            if dotests:
                self.plot_data_ntests()



    def population(self,country):
        pop = 1
        if   country == 'Italy':          pop =    60486199
        elif country == 'United_States':  pop =   327200000
        elif country == 'Mainland_China': pop =  1386000000
        elif country == 'Spain':          pop =    46660000
        elif country == 'France':         pop =    66990000
        elif country == 'United_Kingdom': pop =    66440000
        elif country == 'Netherlands':    pop =    17180000
        elif country == 'Germany':        pop =    82790000
        elif country == 'South_Korea':    pop =    51470000
        elif country == 'Brazil':         pop =   209500000
        elif country == 'Russia':         pop =   144500000
        elif country == 'Sweden':         pop =    10230000
        elif country == 'Israel':         pop =     9199700 
        else: print(f'covid_analysis_wiki.population(): no population for {country}, set to 1.')
        return pop


    
    def ntests_download(self, mode='2'):
        ''' mode = 1 : download tests .csv driving Chrome https://ourworldindata.org 
            mode = 2 : from github https://github.com/owid/covid-19-data/blob/master/public/data/testing/covid-testing-all-observations.csv
        '''
        if mode == 1:
            import webbot, time 
            print('covid_analysis_wiki.download_tests(): downloading n.tests using Chromium...')
            # driving Chrome to download:
            driver = webbot.Browser()                              
            driver.go_to('https://ourworldindata.org/covid-testing')
            driver.scrolly(4000)
            driver.click(text='DATA', number=1)
            driver.click(text=self.ntests_filename) 
            timeout = 10
            filesizes = 0
            t0 = time.time()
            # wait until download is done:
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
            # mv downloaded file to here:
            os.replace('/home/francesco/Downloads/' + self.ntests_filename, '/home/francesco/scripts/repositories/covid19_analysis/' + self.ntests_filename)
            print('covid_analysis_wiki.download_tests(): done.')
        elif mode == 2:
            import wget
            wget.download(self.ntests_github)
            self.ntests_filename = 'covid-testing-all-observations.csv'



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



    def ntests_make_country_data(self, country):
        ''' make ntests data for country '''
        d = self.ntests_make_dict_from_csv(self.ntests_filename)
        country_no_ = country.replace('_', ' ')
        if self.verbose: 
            print(f'covid_analysis_wiki.ntests_make_country_data(): {country} {country_no_}')
        self.d_data[country]['ntests_dates'] = [d[k]['Date'] for k in d if d[k]['Entity'].startswith(country_no_)] #and d[k]['Entity'].find('inconsistent') == -1]
        self.d_data[country]['ntests'] = np.array([int(d[k]['Cumulative total tests']) for k in d if d[k]['Entity'].startswith(country_no_)]) # and d[k]['Entity'].find('inconsistent') == -1])
        if country == 'United_States':
            print('covid_analysis_wiki.ntests_make_country_data(): selecting data for United State')
            self.d_data[country]['ntests_dates'] = [d[k]['Date'] for k in d if d[k]['Entity'] ==country_no_]
            self.d_data[country]['ntests'] = np.array([int(d[k]['Cumulative total tests']) for k in d if d[k]['Entity'] == country_no_])
            #self.d_data[country]['ntests_dates'] = [d[k]['Date'] for k in d if d[k]['Entity'].startswith(country_no_) and d[k]['Entity'].find('inconsistent') >= 0]
            #self.d_data[country]['ntests'] = np.array([int(d[k]['Cumulative total tests']) for k in d if d[k]['Entity'].startswith(country_no_) and d[k]['Entity'].find('inconsistent') >= 0])

        self.d_data[country]['ntests_dates_float'] = np.array([dateutil.parser.parse(i).timestamp() for i in self.d_data[country]['ntests_dates']])



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
        if self.verbose: print(f'covid_analysis_wiki.read_file(): old format, found_lines: {found_lines}')
        # format from 200327:
        if found_lines == []:
            found_lines = [line for line in lines if re.match('202', line)]
            data_format = '200327'
        if self.verbose: print(f'covid_analysis_wiki.read_file(): new format, found_lines: {found_lines}')
            
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
        if country == 'United_Kingdom' and self.UKrmlast:
            death_dates = death_dates[:-1]
            death = death[:-1]
        if self.rmlast:
            death = death[:-1]
            recov = recov[:-1]
            cases = cases[:-1]
            death_dates = death_dates[:-1]
            recov_dates = recov_dates[:-1]
            cases_dates = cases_dates[:-1]
        # store:
        self.d_data[country]['death_dates'] = death_dates
        self.d_data[country]['recov_dates'] = recov_dates
        self.d_data[country]['cases_dates'] = cases_dates
        self.d_data[country]['death_dates_float'] = np.array([dateutil.parser.parse(i).timestamp() for i in death_dates])
        self.d_data[country]['recov_dates_float'] = np.array([dateutil.parser.parse(i).timestamp() for i in recov_dates])
        self.d_data[country]['cases_dates_float'] = np.array([dateutil.parser.parse(i).timestamp() for i in cases_dates])
        self.d_data[country]['death'] = death
        self.d_data[country]['recov'] = recov
        self.d_data[country]['cases'] = cases

    

    def make_casesXntests(self, country):
        ''' normalize cases in self.d_data by number of tests, aligning the dates '''
        ntests_d = self.d_data[country]['ntests_dates_float']
        cases_d  = self.d_data[country]['cases_dates_float']
        ntests   = self.d_data[country]['ntests']
        cases    = self.d_data[country]['cases']
        casesXntests = []
        casesXntests_dates_float = []
        casesntests_ntests = []
        casesntests_cases = []
        if ntests != []:
            # align dates and get cases/ntests:
            for i, _cases_d in enumerate(cases_d):
                idx = np.argmin(np.abs(_cases_d - ntests_d))
                if np.abs(ntests_d[idx] - _cases_d) < 86400:  # seconds in 1 day
                    casesntests_cases  = np.append(casesntests_cases, cases[i])
                    casesntests_ntests = np.append(casesntests_ntests, ntests[idx])
                    casesXntests = np.append(casesXntests, cases[i]/ntests[idx]) 
                    casesXntests_dates_float = np.append(casesXntests_dates_float, cases_d[i])
        else:
            print(f'covid_analysis_wiki.make_casesXntests(): no tests found for {country}')
        # store:
        self.d_data[country]['casesXntests'] = casesXntests 
        self.d_data[country]['casesXntests_dates_float'] = casesXntests_dates_float
        self.d_data[country]['casesntests_cases'] = casesntests_cases
        self.d_data[country]['casesntests_ntests'] = casesntests_ntests
        if self.verbose:
            print(f'covid_analysis_wiki.make_casesXntests(): cases: {cases}')
            print(f'covid_analysis_wiki.make_casesXntests(): ntests: {ntests}')
            print(f'covid_analysis_wiki.make_casesXntests(): casesntests_ntests: {casesntests_ntests}')
            print(f'covid_analysis_wiki.make_casesXntests(): casesntests_cases: {casesntests_cases}')



    def plot_data_ntests(self):
        ''' plot data with ntests '''
        fig4 = plt.figure('daily/ntests', clear=True, figsize=(9,5.54))
        ax41 = fig4.add_subplot(221)
        ax42 = fig4.add_subplot(222, sharex=ax41)
        ax43 = fig4.add_subplot(223, sharex=ax41)
        ax44 = fig4.add_subplot(224, sharex=ax41)
        
        for country in d:
            ntests       = d[country]['ntests'] #/pop ?
            casesXntests = d[country]['casesXntests']
            casesntests_cases  = d[country]['casesntests_cases']
            casesntests_ntests = d[country]['casesntests_ntests']
            ntests_dates_float       = self.d_data[country]['ntests_dates_float']
            casesXntests_dates_float = self.d_data[country]['casesXntests_dates_float']
            
            ax41.plot(ntests_dates_float, ntests, '-o', alpha=0.7, label=country if len(ntests) else None, ms=marker_size)
            ax42.plot(casesXntests_dates_float, casesXntests, '-o', alpha=0.7, label=country if len(casesXntests) else None, ms=marker_size)
            try: 
                ax43.plot(ntests_dates_float[1:], np.diff(ntests), '-o', alpha=0.7, label=country if len(casesXntests) else None, ms=marker_size)
                dc, = ax44.plot(casesXntests_dates_float[1:], np.diff(casesntests_cases)/np.diff(casesntests_ntests), '-', alpha=0.7, ms=marker_size, lw=0.1)
                dntests_mn, dntests_st = self.running_stats(np.diff(casesntests_cases)/np.diff(casesntests_ntests), npts=3)
                ax44.plot(casesXntests_dates_float[1:], dntests_mn, '-', alpha=0.7, color=dc.get_color(), label=country if len(casesXntests) else None)
                ax44.fill_between(casesXntests_dates_float[1:], dntests_mn - dntests_st, dntests_mn + dntests_st, color=dc.get_color(), alpha=0.2, lw=0  )
            except:
                print(f'covid_analysis_wiki.plot_data(): {country} casesXntests Error.')
        ax41.set_xlabel('Days')
        ax42.set_xlabel('Days')
        ax43.set_xlabel('Days')
        ax44.set_xlabel('Days')
        ax41.set_ylabel('Tot.tests' + proc)
        ax42.set_ylabel('Tot.cases / Tot.tests' + proc)
        ax43.set_ylabel('Daily tests' + proc)
        ax44.set_ylabel('Daily cases / Daily tests' + proc)
        ax41.legend(fontsize=8,labelspacing=0)
        ax42.legend(fontsize=8,labelspacing=0)
        ax43.legend(fontsize=8,labelspacing=0)
        ax44.legend(fontsize=8,labelspacing=0)
        # make xticklabels as date strings:
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime.fromtimestamp(x_val).date()).lstrip('2020'))
        ax41.xaxis.set_major_formatter(formatter)
        ax42.xaxis.set_major_formatter(formatter)
        fig4.tight_layout()



    def plot_data(self, fitpts=5, fitpts_ext=10, procapite=True):
        d = self.d_data
        savw = self.filt_win # savgol filter win
        savord = 1 # savgol filter polyorder
        marker_size= 3
        fig1 = plt.figure('cumulative', clear=True, figsize=(5,8))
        ax11 = fig1.add_subplot(311)
        ax12 = fig1.add_subplot(312, sharex=ax11)
        ax13 = fig1.add_subplot(313, sharex=ax11)
        fig2 = plt.figure('daily', clear=True, figsize=(5,8))
        ax21 = fig2.add_subplot(311, sharex=ax11)
        ax22 = fig2.add_subplot(312, sharex=ax11)
        ax23 = fig2.add_subplot(313, sharex=ax11)
        fig3 = plt.figure('daily Vs tot', clear=True, figsize=(5,8))
        ax31 = fig3.add_subplot(311)
        ax32 = fig3.add_subplot(312)
        ax33 = fig3.add_subplot(313)

        for country in d:
            print(f'covid_analysis_wiki.plot_data(): plotting {country}')
            pop = self.population(country) if procapite else 1

            death_dates_float        = self.d_data[country]['death_dates_float']
            recov_dates_float        = self.d_data[country]['recov_dates_float']
            cases_dates_float        = self.d_data[country]['cases_dates_float']
            death        = d[country]['death']/pop
            recov        = d[country]['recov']/pop
            cases        = d[country]['cases']/pop
            
            # plots:
            cc, = ax11.plot(cases_dates_float, cases, 'o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            ax11.plot(cases_dates_float, self.savgol_filter(cases, win=savw, polyorder=savord), '-', alpha=0.9, color=cc.get_color(), label=country)
            cd, = ax12.plot(death_dates_float, death, 'o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            ax12.plot(death_dates_float, self.savgol_filter(death, win=savw, polyorder=savord), '-', alpha=0.9, color=cd.get_color(), label=country)
            cr, = ax13.plot(recov_dates_float, recov, 'o', mfc='none', mew=1, alpha=0.7, ms=marker_size)
            try:
                ax13.plot(recov_dates_float, self.savgol_filter(recov, win=savw, polyorder=savord), '-', alpha=0.9, color=cr.get_color(), label=country)
            except:
                pass
            
            p21, = ax21.plot(cases_dates_float[1:], np.diff(cases), 'o', alpha=0.3, ms=marker_size)
            ax21.plot(cases_dates_float[1:], self.savgol_filter(np.diff(cases), win=savw, polyorder=savord), '-', alpha=0.9, color=p21.get_color(), label=country)
            p22, = ax22.plot(death_dates_float[1:], np.diff(death), 'o', alpha=0.3, ms=marker_size)
            ax22.plot(death_dates_float[1:], self.savgol_filter(np.diff(death), win=savw, polyorder=savord), '-', alpha=0.9, color=p22.get_color(), label=country)
            p23, = ax23.plot(recov_dates_float[1:], np.diff(recov), 'o', alpha=0.3, ms=marker_size)
            try:
                ax23.plot(recov_dates_float[1:], self.savgol_filter(np.diff(recov), win=savw, polyorder=savord), '-', alpha=0.9, color=p23.get_color(), label=country)
            except:
                pass

            p31, = ax31.plot(cases[1:], np.diff(cases), 'o', alpha=0.3, ms=marker_size)
            ax31.plot(cases[1:], self.savgol_filter(np.diff(cases), win=savw, polyorder=savord), '-', alpha=0.9, color=p31.get_color(), label=country)
            p32, = ax32.plot(death[1:], np.diff(death), 'o', alpha=0.3, ms=marker_size)
            ax32.plot(death[1:], self.savgol_filter(np.diff(death), win=savw, polyorder=savord), '-', alpha=0.9, color=p32.get_color(), label=country)
            p33, = ax33.plot(recov[1:], np.diff(recov), 'o', alpha=0.3, ms=marker_size)
            try:
                ax33.plot(recov[1:], self.savgol_filter(np.diff(recov), win=savw, polyorder=savord), '-', alpha=0.9, color=p33.get_color(), label=country)
            except:
                pass

            # daily death Vs daily cases:
            fig4 = plt.figure('d.cases Vs d.deaths'+country, clear=True, figsize=(3,2))
            ax41 = fig4.add_subplot(111)
            m = np.min([len(np.diff(cases)), len(np.diff(death))])
            alphas = np.linspace(0.2,1,m)**2
            cols = ([(1,0,0,i) for i in alphas])
            #x = self.running_stats(np.diff(cases), npts=10)[0][-m:]
            #y = self.running_stats(np.diff(death), npts=10)[0][-m:]
            x = self.savgol_filter(np.diff(cases), win=savw, polyorder=savord)[-m:]
            y = self.savgol_filter(np.diff(death), win=savw, polyorder=savord)[-m:]
            for i in range(m-1):
                ax41.plot([x[i],x[i+1]], [y[i],y[i+1]], 'r-', lw=5, alpha=alphas[i])
            ax41.scatter(x, y, label=country, c=cols, alpha=0., edgecolors='none')
            ax41.legend(fontsize=8,labelspacing=0)
            ax41.set_xlabel('Daily cases')
            ax41.set_ylabel('Daily deaths')
            fig4.tight_layout()
            
            # fit ot log:
            dt = 86400 # = np.diff(cases_dates_float)[-1]
            try:
                logfit_cases = np.polyfit(cases_dates_float[-fitpts:], np.log10(cases[-fitpts:]), 1)
                xfit_cases = np.linspace(cases_dates_float[-fitpts] - fitpts_ext*dt, cases_dates_float[-1] + fitpts_ext*dt, 10)
                ax11.plot(xfit_cases, 10**np.poly1d(logfit_cases)(xfit_cases), '--', lw=1, alpha=0.6, color=cc.get_color(), ms=marker_size)
            except:
                print('plot_data(): error logfit cases')
            try:
                logfit_death = np.polyfit(death_dates_float[-fitpts:], np.log10(death[-fitpts:]), 1)
                xfit_death = np.linspace(death_dates_float[-fitpts] - fitpts_ext*dt, death_dates_float[-1] + fitpts_ext*dt, 10)
                ax12.plot(xfit_death, 10**np.poly1d(logfit_death)(xfit_death), '--', lw=1, alpha=0.6, color=cd.get_color(), ms=marker_size)
            except:
                print('plot_data(): error logfit death')
            try:
                logfit_recov = np.polyfit(recov_dates_float[-fitpts:], np.log10(recov[-fitpts:]), 1)
                xfit_recov = np.linspace(recov_dates_float[-fitpts] - fitpts_ext*dt, recov_dates_float[-1] + fitpts_ext*dt, 10)
                ax13.plot(xfit_recov, 10**np.poly1d(logfit_recov)(xfit_recov), '--', lw=1, alpha=0.6, color=cr.get_color(), ms=marker_size)
            except:
                print(f'plot_data(): {country} error logfit recovery')
            
            ax11.plot(cases_dates_float[-fitpts:], cases[-fitpts:], 'o', color=cc.get_color(), alpha=0.6,  ms=marker_size)
            ax12.plot(death_dates_float[-fitpts:], death[-fitpts:], 'o', color=cd.get_color(), alpha=0.6,  ms=marker_size)
            ax13.plot(recov_dates_float[-fitpts:], recov[-fitpts:], 'o', color=cr.get_color(), alpha=0.6,  ms=marker_size)
            
        proc = ' per capita' if procapite else ''
        ax11.set_ylabel('Cumul. cases' + proc)
        ax12.set_ylabel('Cumul. deaths' + proc)
        ax13.set_ylabel('Cumul. recoveries' + proc)
        ax11.set_xlabel('Days')
        ax12.set_xlabel('Days')
        ax13.set_xlabel('Days')
        ax21.set_ylabel('Daily cases' + proc)
        ax22.set_ylabel('Daily deaths' + proc)
        ax23.set_ylabel('Daily recoveries' + proc)
        ax31.set_ylabel('Daily cases' + proc)
        ax32.set_ylabel('Daily deaths' + proc)
        ax33.set_ylabel('Daily recoveries' + proc)
        ax21.set_xlabel('Days')
        ax22.set_xlabel('Days')
        ax23.set_xlabel('Days')
        ax31.set_xlabel('Cumul. cases')
        ax32.set_xlabel('Cumul. death')
        ax33.set_xlabel('Cumul. recov.')
        ax11.legend(fontsize=8,labelspacing=0)
        ax12.legend(fontsize=8,labelspacing=0)
        ax13.legend(fontsize=8,labelspacing=0)
        ax21.legend(fontsize=8,labelspacing=0)
        ax22.legend(fontsize=8,labelspacing=0)
        ax23.legend(fontsize=8,labelspacing=0)
        ax31.legend(fontsize=8,labelspacing=0)
        ax32.legend(fontsize=8,labelspacing=0)
        ax33.legend(fontsize=8,labelspacing=0)
        
        # make xticklabels as date strings:
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime.fromtimestamp(x_val).date()).lstrip('2020'))
        ax11.xaxis.set_major_formatter(formatter)
        ax12.xaxis.set_major_formatter(formatter)
        ax13.xaxis.set_major_formatter(formatter)
        ax21.xaxis.set_major_formatter(formatter)
        ax22.xaxis.set_major_formatter(formatter)
        ax23.xaxis.set_major_formatter(formatter)
        
        fig1.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()

   


    def savgol_filter(self, x, win=5, polyorder=3, plots=0):
        ''' from https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way/26337730#26337730'''
        import scipy.signal as sig
        if polyorder >= win:
            polyorder = win-1
            print('savgol_filter(): bad polyorder fixed to win-1')
        if np.mod(win,2) == 0:
            win = win+1
            print('Warning savgol_filter, win must be odd: forced win = '+str(win))
        y = sig.savgol_filter(x, window_length=win, polyorder=polyorder)
        if plots:
            plt.figure('savgol_filter()')
            plt.clf()
            plt.plot(x, '.')
            plt.plot(y)
        return y


    def running_stats(self, sig, npts=5, plots=0):
        ''' simple running mean std of sig on windows of npts '''
        if npts%2: 
            npts = npts + 1 #np.clip(npts+1, 1, npts+1)
        #d = int(npts/2) #int((npts-1)/2)
        d = int((npts-1)/2)
        sigex = np.concatenate((np.repeat(np.nan, d), sig, np.repeat(np.nan, d)))
        mn = []
        st = []
        #for i in np.arange(len(sig)):
        for i in np.arange(len(sigex)-npts):
            mn = np.append(mn, np.nanmean(sig[i:i+npts]))
            #mn = np.append(mn, np.nanmean(sigex[i:i+npts]))
            st = np.append(st,np.nanstd(sigex[i:i+npts]))
            #st = np.append(st,np.nanstd(sig[i:i+npts]))
        #mn = mn[]
        if plots:
            print(npts)
            print(d)
            print(len(sig))
            print(len(sigex))
            print(len(mn))
            fig = plt.figure('running_stats', clear=1)
            plt.plot(sig, '-o')
            plt.plot(mn, '-')
        return mn, st
