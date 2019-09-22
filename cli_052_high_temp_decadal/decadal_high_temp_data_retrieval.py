import datetime
import urllib

data_dir = '/home/amsnyder/Github/data/'

DATA_URL = 'http://berkeleyearth.lbl.gov/auto/Global/Gridded/Complete_TMAX_LatLong1.nc'

#list of years from start year (1753) until the most recent year
current_year = datetime.datetime.today().year
current_month = datetime.datetime.today().month
YEARS = range(1753, current_year)
MONTHS = range(1, 13)

urllib.request.urlretrieve(DATA_URL, data_dir+DATA_URL.split('/')[-1])