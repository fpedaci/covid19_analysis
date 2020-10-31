import numpy as np
import matplotlib.pyplot as plt
import datetime
import wget
import dateutil
import json
import os
from matplotlib.ticker import FuncFormatter



class Covid_analysis_OWID():
    ''' data from ourwolrdindata '''

    def __init__(self, countries=['ITA','FRA','USA'], filter_win=7, filter_ord=1, procapite=False, download=True):
        ''' 
        Covid Analysis from www.ourwolrdindata.org 
        
        countries : list of country names, 3 letters (run get_country_names() to have the list) 
        filter_win : window datapoint to smooth [7]
        filter_ord : polynome order for the fit [1]
        download : download the latest data

        ex:
            covid_analysis_owid.Covid_analysis_OWID(countries=['USA','ITA','FRA'], download=1, filter_win=7)
        '''
        self.OWID_address = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json'
        self.local_file = 'OWID_data.json'
        self.procapite = procapite
        if download:
            self.download()
        self.read()
        self.init_fig()
        for country in countries:
            self.plot_country(country, filter_win=filter_win, filter_ord=filter_ord)


    def download(self):
        if os.path.exists(self.local_file):
            os.remove(self.local_file)
            print('Covid_analysis_OWID: removed old local file.')
        print('Covid_analysis_OWID: downloading new file...')
        wget.download(self.OWID_address, self.local_file) 


    def read(self):
        print('Covid_analysis_OWID: reading...')
        with open('OWID_data.json') as f:
            self.d = json.load(f)


    def get_country_names(self):
        if not hasattr(self, 'd'):
            raise RuntimeError('missing data from read()')
        for k in self.d:
            name = self.d[k]['location']
            print(f'{k} :\t{name}')


    def init_fig(self):
        print('Covid_analysis_OWID: init plots...')
        self.fig1 = plt.figure('Daily', clear=True)
        self.ax11 = self.fig1.add_subplot(221)
        self.ax12 = self.fig1.add_subplot(222, sharex=self.ax11)
        self.ax13 = self.fig1.add_subplot(223, sharex=self.ax11)
        self.ax14 = self.fig1.add_subplot(224, sharex=self.ax11)
        self.ax11.set_xlabel('Day')
        self.ax12.set_xlabel('Day')
        self.ax13.set_xlabel('Day')
        self.ax14.set_xlabel('Day')
        if self.procapite:
            self.ax11.set_ylabel('Daily Cases pro capite')
            self.ax12.set_ylabel('Daily Tests pro capite')
            self.ax13.set_ylabel('Daily Deaths pro capite')
        else:
            self.ax11.set_ylabel('Daily Cases')
            self.ax12.set_ylabel('Daily Tests')
            self.ax13.set_ylabel('Daily Deaths')
        self.ax14.set_ylabel('Daily Cases / Tests')
        self.fig2 = plt.figure('Total', clear=True)
        self.ax21 = self.fig2.add_subplot(211, sharex=self.ax11)
        self.ax22 = self.fig2.add_subplot(212, sharex=self.ax11)
        self.ax21.set_xlabel('Day')
        self.ax22.set_xlabel('Day')
        self.ax21.set_ylabel('Total Cases')
        self.ax22.set_ylabel('Total Deaths')


    def linfit_log(self, x, y, a, b):
        pfit = np.polyfit(x[a:b], np.log10(y[a:b]), 1)
        xfit = np.linspace(x[a], x[-1] + np.diff(x)[-1]*50, 50)
        yfit = 10**np.poly1d(pfit)(xfit)
        return xfit, yfit


    def plot_country(self, country, filter_win=7, filter_ord=1):
        print(f'Covid_analysis_OWID: processing {country}')
        co = self.d[country]
        # timestamps:
        tstamps = np.array([dateutil.parser.parse(i['date']).timestamp() if 'date' in i else np.nan             for i in co['data']])
        # cases:
        new_cases = np.array([i['new_cases'] if 'new_cases' in i else np.nan                                    for i in co['data']])
        new_cases_sf = savgol_filter(new_cases, win=filter_win, polyorder=filter_ord)
        new_cases_sf = np.clip(new_cases_sf, 0, None)
        new_cases_sf = zeros2nan(new_cases_sf)
        new_cases_sm = np.array([i['new_cases_smoothed'] if 'new_cases_smoothed' in i else np.nan               for i in co['data']])
        new_cases_pc = np.array([i['new_cases_per_million']/1e6 if 'new_cases_per_million' in i else np.nan     for i in co['data']])
        new_cases_pc_sf = savgol_filter(new_cases_pc, win=filter_win, polyorder=filter_ord)
        new_cases_pc_sf = np.clip(new_cases_pc_sf, 0, None)
        new_cases_pc_sf = zeros2nan(new_cases_pc_sf)
        total_cases = np.array([i['total_cases'] if 'total_cases' in i else np.nan                              for i in co['data']])
        total_cases_xfit, total_cases_yfit = self.linfit_log(tstamps, total_cases, -7, -1)
        total_cases_xfit_1, total_cases_yfit_1 = self.linfit_log(tstamps, total_cases, -14, -7)
        total_cases_xfit_2, total_cases_yfit_2 = self.linfit_log(tstamps, total_cases, -21, -14)
        # deaths:
        new_deaths = np.array([i['new_deaths'] if 'new_deaths' in i else np.nan                                 for i in co['data']])
        new_deaths_sf = savgol_filter(new_deaths, win=filter_win, polyorder=filter_ord)
        new_deaths_sf = np.clip(new_deaths_sf, 0, None)
        new_deaths_sf = zeros2nan(new_deaths_sf)
        new_deaths_sm = np.array([i['new_deaths_smoothed'] if 'new_deaths_smoothed' in i else np.nan            for i in co['data']])
        new_deaths_pc = np.array([i['new_deaths_per_million']/1e6 if 'new_deaths_per_million' in i else np.nan  for i in co['data']])
        new_deaths_pc_sf = savgol_filter(new_deaths_pc, win=filter_win, polyorder=filter_ord)
        new_deaths_pc_sf = np.clip(new_deaths_pc_sf, 0, None)
        new_deaths_pc_sf = zeros2nan(new_deaths_pc_sf)
        total_deaths = np.array([i['total_deaths'] if 'total_deaths' in i else np.nan                           for i in co['data']])
        # tests:
        new_tests_pc = np.array([i['new_tests_per_thousand']/1e3 if 'new_tests_per_thousand' in i else np.nan   for i in co['data']])
        new_tests_pc_sf = savgol_filter(nan2neig(new_tests_pc)[0], win=filter_win, polyorder=filter_ord)
        new_tests_pc_sf = np.clip(new_tests_pc_sf, 0, None)
        new_tests_pc_sf = zeros2nan(new_tests_pc_sf)
        new_tests = np.array([i['new_tests'] if 'new_tests' in i else np.nan                                    for i in co['data']])
        new_tests_sf = savgol_filter(nan2neig(new_tests)[0], win=filter_win, polyorder=filter_ord)
        new_tests_sf = np.clip(new_tests_sf, 0, None)
        new_tests_sf = zeros2nan(new_tests_sf)
        tests_absent = np.all(np.isnan(new_tests))
        if tests_absent: 
            new_tests = np.array([i['new_tests_smoothed'] if 'new_tests_smoothed' in i else np.nan               for i in co['data']])
            new_tests_pc = np.array([i['new_tests_smoothed_per_thousand']/1e3 if 'new_tests_smoothed_per_thousand' in i else np.nan for i in co['data']])
            new_tests_sf = new_tests
            new_tests_pc_sf = new_tests_pc
            tests_absent = np.all(np.isnan(new_tests))
            print(f'Covid_analysis_OWID: no tests found for {country}. new_tests_smoothed: {not tests_absent}')
        # cases normalized by tests:
        new_cases_tests = new_cases/new_tests
        new_cases_tests_neig, new_cases_tests_neig_idx = nan2neig(new_cases_tests)
        #new_cases_tests_sf = savgol_filter(new_cases_tests_neig, win=filter_win, polyorder=filter_ord)
        new_cases_tests_sf = new_cases_sf/new_tests_sf
        new_cases_tests_sf = np.clip(new_cases_tests_sf, 0, None)
        new_cases_tests_sf = zeros2nan(new_cases_tests_sf)
        new_cases_tests_sf = np.delete(new_cases_tests_sf, new_cases_tests_neig_idx)
        new_cases_tests_tstamps = np.delete(tstamps, new_cases_tests_neig_idx)
        new_cases_tests = zeros2nan(new_cases_tests)

        ### Plots:
        if self.procapite:
            p1, = self.ax11.semilogy(tstamps, new_cases_pc, 'o', ms=3, alpha=0.2)
            self.ax11.semilogy(tstamps, new_cases_pc_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
            self.ax13.semilogy(tstamps, new_deaths_pc, 'o', ms=3, alpha=0.2, color=p1.get_color())
            self.ax13.semilogy(tstamps, new_deaths_pc_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
            self.ax12.semilogy(tstamps, new_tests_pc, 'o', ms=3, alpha=0.2, color=p1.get_color())
            self.ax12.semilogy(tstamps, new_tests_pc_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
        else:
            p1, = self.ax11.semilogy(tstamps, new_cases, 'o', ms=3, alpha=0.2)
            self.ax11.semilogy(tstamps, new_cases_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
            self.ax13.semilogy(tstamps, new_deaths, 'o', ms=3, alpha=0.2, color=p1.get_color())
            self.ax13.semilogy(tstamps, new_deaths_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
            self.ax12.semilogy(tstamps, new_tests, 'o', ms=3, alpha=0.2, color=p1.get_color())
            self.ax12.semilogy(tstamps, new_tests_sf, '-', lw=2, alpha=0.9, color=p1.get_color(), label=country)
        self.ax11.legend(fontsize=8, labelspacing=0)
        self.ax12.legend(fontsize=8, labelspacing=0)
        self.ax13.legend(fontsize=8, labelspacing=0)
        if not tests_absent:
            self.ax14.semilogy(tstamps, new_cases_tests, 'o', ms=3, alpha=0.2, color=p1.get_color())
            self.ax14.semilogy(new_cases_tests_tstamps, new_cases_tests_sf, '-', alpha=0.9, lw=2, color=p1.get_color(), label=country)
            self.ax14.legend(fontsize=8, labelspacing=0)
        # total cases plots: 
        self.ax21.semilogy(tstamps, total_cases , '.', ms=6, alpha=0.7, color=p1.get_color(), label=country)
        self.ax22.plot(tstamps, total_deaths, '.', ms=6, alpha=0.4, color=p1.get_color(), label=country)
        self.ax21.plot(total_cases_xfit, total_cases_yfit, '-', lw=1, alpha=1, color=p1.get_color())
        self.ax21.plot(total_cases_xfit_1, total_cases_yfit_1, '-', lw=1, alpha=0.4, color=p1.get_color())
        self.ax21.plot(total_cases_xfit_2, total_cases_yfit_2, '-', lw=1, alpha=0.2, color=p1.get_color())
        self.ax21.legend(fontsize=8, labelspacing=0)
        self.ax22.legend(fontsize=8, labelspacing=0)
        
        # make xticklabels as date strings:
        formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime.fromtimestamp(x_val).date()).lstrip('2020-'))
        self.ax11.xaxis.set_major_formatter(formatter)
        self.fig1.tight_layout()



def nan2neig(x, start=0):
    ''' replaces np.nan with neighbor value, starting at x[0]=start, giving indexes where values changed '''
    xx = np.copy(x)
    if np.isnan(xx[0]):
        xx[0] = start
    idx = []
    for i in range(1, len(xx)):
        if np.isnan(xx[i]):
            xx[i] = xx[i-1]
            idx.append(i)
    return xx, idx



def zeros2nan(x):
    xx = np.copy(x)
    xx[np.nonzero(xx==0)[0]] = np.nan
    return xx



def savgol_filter(x, win=7, polyorder=3, plots=False):
    ''' from https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way/26337730#26337730'''
    import scipy.signal as sig
    if polyorder >= win:
        polyorder = win-1
        print(f'savgol_filter(): Warning, bad polyorder fixed to win-1 = {polyorder}')
    if np.mod(win,2) == 0:
        win = win+1
        print(f'savgol_filter(): Warning, win must be odd, forced win = {win}')
    y = sig.savgol_filter(x, window_length=win, polyorder=polyorder, mode='interp')
    if plots:
        plt.figure('savgol_filter()')
        plt.clf()
        plt.plot(x, '.')
        plt.plot(y)
    return y

