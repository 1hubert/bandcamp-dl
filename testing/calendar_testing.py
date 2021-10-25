import calendar

date = "released December 1, 2010"
date = date[9:]
date_month = list(calendar.month_name).index(date.split(" ")[0])
#date_days = date.split(", ")[0].split(" ")[1]
#if len(date_days) == 1:
#    date_days = "0" + date_days
date_year = date.split(", ")[1]

