import numpy as np
import matplotlib.pyplot as plt
import xlrd
import datetime



def covid_analysis_xls(countries=['Italy','France'], download=False, fitpts=10, fitpts_ext=10):
    ''' plot covid19 data from www.ecdc.europa.eu 
    download : download the data before analysis
    countries : list of valid names
    fitpts : numb. of data points (from the end) to use for the fit
    fitpts_ext : points to extend after the end the fit
    '''

    if download:
        import wget, os
        if 'data.xls' in os.listdir():
            os.rename('data.xls', 'data_old.xls')
        wget.download('https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-14_1.xls', './data.xls')

    d_cases_day = {}
    d_deaths_day = {}
    d_cases = {}
    d_deaths = {}
    
    fig = plt.figure('covid_xls cumulative', clear=True)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122, sharex=ax1)

    fig1 = plt.figure('covid_xls per day', clear=True)
    ax11 = fig1.add_subplot(121)
    ax12 = fig1.add_subplot(122, sharex=ax11)
    
    # get data from data.xls:
    book = xlrd.open_workbook('data.xls')
    sheet = book.sheet_by_index(0)
    dates_float = sheet.col_values(0)
    countries_all = sheet.col_values(1)
    newconfcases = sheet.col_values(2)
    newdeaths = sheet.col_values(3)
    cases_all = np.array(list(zip(countries_all, dates_float, newconfcases)))[1:]
    deaths_all = np.array(list(zip(countries_all, dates_float, newdeaths)))[1:]
    
    for country in countries:
        # populate with dates_float, data:
        c = np.array([[float(i[1]), float(i[2])] for i in cases_all if i[0]==country])
        d = np.array([[float(i[1]), float(i[2])] for i in deaths_all if i[0]==country])
        
        # per day: 
        d_cases_day[country] = np.copy(c[::-1])
        d_deaths_day[country] = np.copy(d[::-1])

        # cumulative:
        d_cases[country] = np.copy(c[::-1])
        d_deaths[country] = np.copy(d[::-1])
        d_cases[country][:,1] = np.cumsum(d_cases[country][:,1])
        d_deaths[country][:,1] = np.cumsum(d_deaths[country][:,1])

        # fit of last fitpts:
        xfit0c = d_cases[country][-fitpts:,0]
        xfit0d = d_deaths[country][-fitpts:,0]
        logfit_cases = np.polyfit(xfit0c, np.log10(d_cases[country][-fitpts:,1]), 1)
        logfit_deaths = np.polyfit(xfit0d, np.log10(d_deaths[country][-fitpts:,1]), 1)
        
        # dates as days:
        dates_time_c = [str(datetime.datetime(*xlrd.xldate_as_tuple(a, book.datemode)).date()) for a in d_cases[country][:,0]]
        dates_time_d = [str(datetime.datetime(*xlrd.xldate_as_tuple(a, book.datemode)).date()) for a in d_deaths[country][:,0]]

        # plots: 
        p1, = ax1.semilogy(d_cases[country][:,0], d_cases[country][:,1], '-o', alpha=0.4, label=country)
        p2, = ax2.semilogy(d_deaths[country][:,0], d_deaths[country][:,1], '-o', alpha=0.4, label=country)
        
        xfit1c = np.arange(xfit0c[0], xfit0c[-1] + fitpts_ext)
        xfit1d = np.arange(xfit0d[0], xfit0d[-1] + fitpts_ext)
        ax1.plot(xfit1c, 10**np.poly1d(logfit_cases)(xfit1c), '--', alpha=0.6, color=p1.get_color())
        ax2.plot(xfit1d, 10**np.poly1d(logfit_deaths)(xfit1d), '--', alpha=0.6, color=p2.get_color())
        
        p11, = ax11.semilogy(d_cases_day[country][:,0], d_cases_day[country][:,1], '-o', alpha=0.4, label=country)
        p12, = ax12.semilogy(d_deaths_day[country][:,0], d_deaths_day[country][:,1], '-o', alpha=0.4, label=country)

    
    ax1.legend()
    ax2.legend()
    ax11.legend()
    ax12.legend()
    ax1.set_xlabel('Days')
    ax2.set_xlabel('Days')
    ax1.set_ylabel('Cumulative cases')
    ax2.set_ylabel('Cumulative deaths')
    ax11.set_xlabel('Days')
    ax12.set_xlabel('Days')
    ax11.set_ylabel('Daily cases')
    ax12.set_ylabel('Daily deaths')
    fig.tight_layout()
    fig1.tight_layout()

    from matplotlib.ticker import FuncFormatter
    formatter = FuncFormatter(lambda x_val, tick_pos: str(datetime.datetime(*xlrd.xldate_as_tuple(x_val, book.datemode)).date()).lstrip('2020'))
    ax1.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_formatter(formatter)
    ax11.xaxis.set_major_formatter(formatter)
    ax12.xaxis.set_major_formatter(formatter)


    #return d_cases, d_deaths
    #return dates_time_d


