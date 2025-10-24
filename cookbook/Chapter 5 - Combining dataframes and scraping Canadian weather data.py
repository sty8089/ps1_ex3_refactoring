# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (15, 3)
plt.rcParams["font.family"] = "sans-serif"

# %%
# By the end of this chapter, we're going to have downloaded all of Canada's weather data for 2012, and saved it to a CSV. We'll do this by downloading it one month at a time, and then combining all the months together.
# Here's the temperature every hour for 2012!

#weather_2012_final = pd.read_csv("../data/weather_2012.csv", index_col="date_time")
#weather_2012_final["temperature_c"].plot(figsize=(15, 6))
#plt.show()

# TODO: rewrite using Polars
weather_2012_final = pl.read_csv("../data/weather_2012.csv")
weather_2012_final = weather_2012_final.with_columns(
    pl.col("date_time").str.strptime(pl.Datetime, fmt="%Y-%m-%d %H:%M:%S")
)
weather_2012_final = weather_2012_final.set_sorted("date_time")

weather_2012_final.select(["date_time", "temperature_c"]).to_pandas().plot(
    x="date_time", y="temperature_c", figsize=(15, 6)
)
plt.show()

# %%
# Okay, let's start from the beginning.
# We're going to get the data for March 2012, and clean it up
# You can directly download a csv with a URL using Pandas!
# Note, the URL the repo provides is faulty but kindly, someone submitted a PR fixing it. Have a look
# here: https://github.com/jvns/pandas-cookbook/pull/74 and click on "Files changed" and then fix the url.


# This URL has to be fixed first!
#url_template = "http://climate.weather.gc.ca/climateData/bulkdata_e.html?format=csv&stationID=5415&Year={year}&Month={month}&timeframe=1&submit=Download+Data"

#year = 2012
#month = 3
#url_march = url_template.format(month=3, year=2012)
#weather_mar2012 = pd.read_csv(
   # url_march,
    #index_col="Date/Time (LST)",
    #parse_dates=True,
    #encoding="latin1",
    #header=0,
##)
#weather_mar2012.head()

# TODO: rewrite using Polars. Yes, Polars can handle URLs similarly.

url_template = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=5415&Year={year}&Month={month}&timeframe=1&submit=Download+Data"

year = 2012
month = 3

url_march = url_template.format(year=year, month=month)


weather_mar2012 = pl.read_csv(url_march, try_parse_dates=True)
weather_mar2012.head()

# %%
# Let's clean up the data a bit.
# You'll notice in the summary above that there are a few columns which are are either entirely empty or only have a few values in them. Let's get rid of all of those with `dropna`.
# The argument `axis=1` to `dropna` means "drop columns", not rows", and `how='any'` means "drop the column if any value is null".
#weather_mar2012 = weather_mar2012.dropna(axis=1, how="any")
#weather_mar2012[:5]

# This is much better now -- we only have columns with real data.

# TODO: rewrite using Polars
weather_mar2012 = weather_mar2012.select(
    [col for col in weather_mar2012.columns if weather_mar2012[col].null_count() == 0]
)

weather_mar2012.head(5)

# %%
# Let's get rid of columns that we do not need.
# For example, the year, month, day, time columns are redundant (we have Date/Time (LST) column).
# Let's get rid of those. The `axis=1` argument means "Drop columns", like before. The default for operations like `dropna` and `drop` is always to operate on rows.
#weather_mar2012 = weather_mar2012.drop(["Year", "Month", "Day", "Time (LST)"], axis=1)
#weather_mar2012[:5]

# TODO: redo this using polars
weather_mar2012 = weather_mar2012.drop(["Year", "Month", "Day", "Time (LST)"])

weather_mar2012.head(5)


# %%
# When you look at the data frame, you see that some column names have some weird characters in them.
# Let's clean this up, too.
# Let's print the column names first:
#weather_mar2012.columns

# And now rename the columns to make it easier to work with
#weather_mar2012.columns = weather_mar2012.columns.str.replace(
  #  'ï»¿"', ""
#)  # Remove the weird characters at the beginning
#weather_mar2012.columns = weather_mar2012.columns.str.replace(
   # "Â", ""
#)  # Remove the weird characters at the

# TODO: rewrite using Polars
print(weather_mar2012.columns)

cleaned= [
    name.replace('ï»¿"', "").replace("Â", "") for name in weather_mar2012.columns
]

weather_mar2012.columns = cleaned
print(weather_mar2012.columns)

# %%
# Optionally, you can also rename columns more manually for specific cases:
#weather_mar2012 = weather_mar2012.rename(
   # columns={
        #'Longitude (x)"': "Longitude",
       # "Latitude (y)": "Latitude",
       # "Station Name": "Station_Name",
       # "Climate ID": "Climate_ID",
       # "Temp (°C)": "Temperature_C",
       ## "Dew Point Temp (Â°C)": "Dew_Point_Temp_C",
       # "Rel Hum (%)": "Relative_Humidity",
       # "Wind Spd (km/h)": "Wind_Speed_kmh",
       # "Visibility (km)": "Visibility_km",
       # "Stn Press (kPa)": "Station_Pressure_kPa",
       # "Weather": "Weather",
    #}
#)
#weather_mar2012.index.name = "date_time"

# Check the new column names
#print(weather_mar2012.columns)

# Some people also prefer lower case column names.
#weather_mar2012.columns = weather_mar2012.columns.str.lower()
#print(weather_mar2012.columns)

# TODO: redo this using polars
weather_mar2012 = weather_mar2012.rename({
    'Longitude (x)"': "Longitude",
    "Latitude (y)": "Latitude",
    "Station Name": "Station_Name",
    "Climate ID": "Climate_ID",
    "Temp (°C)": "Temperature_C",
    "Dew Point Temp (Â°C)": "Dew_Point_Temp_C",
    "Rel Hum (%)": "Relative_Humidity",
    "Wind Spd (km/h)": "Wind_Speed_kmh",
    "Visibility (km)": "Visibility_km",
    "Stn Press (kPa)": "Station_Pressure_kPa",
    "Weather": "Weather",
})


print(weather_mar2012.columns)

weather_mar2012.columns = [col.lower() for col in weather_mar2012.columns]
print(weather_mar2012.columns)

# %%
# Notice how it goes up to 25° C in the middle there? That was a big deal. It was March, and people were wearing shorts outside.
#weather_mar2012["temperature_c"].plot(figsize=(15, 5))
#plt.show()

# TODO: redo this using polars
weather_mar2012.to_pandas()["temperature_c"].plot(figsize=(15, 5))
plt.show()

# %%
# This one's just for fun -- we've already done this before, using groupby and aggregate! We will learn whether or not it gets colder at night. Well, obviously. But let's do it anyway.
#temperatures = weather_mar2012[["temperature_c"]].copy()
#print(temperatures.head)
##temperatures.loc[:, "Hour"] = weather_mar2012.index.hour
#temperatures.groupby("Hour").aggregate(np.median).plot()
#plt.show()

# So it looks like the time with the highest median temperature is 2pm. Neat.

# TODO: redo this using polars
temperatures = weather_mar2012.select(["date_time", "temperature_c"])


temperatures = temperatures.with_columns(
    pl.col("date_time").dt.hour().alias("Hour")
)


hourly_medians = (
    temperatures.group_by("Hour")
    .agg(pl.col("temperature_c").median())
    .sort("Hour")
)

hourly_medians.to_pandas().plot(x="Hour", y="temperature_c", legend=False)
plt.xlabel("Hour of Day")
plt.ylabel("Median Temperature (°C)")
plt.title("Median Temperature by Hour — March 2012")
plt.show()
# %%
# Okay, so what if we want the data for the whole year? Ideally the API would just let us download that, but I couldn't figure out a way to do that.
# First, let's put our work from above into a function that gets the weather for a given month.


#def clean_data(data):
    #data = data.dropna(axis=1, how="any")
    #data = data.drop(["Year", "Month", "Day", "Time (LST)"], axis=1)
    #data.columns = data.columns.str.replace('ï»¿"', "")
    #data.columns = data.columns.str.replace("Â", "")
    #data = data.rename(
       # columns={
            "Longitude (x)": "Longitude",
            "Latitude (y)": "Latitude",
            "Station Name": "Station_Name",
            "Climate ID": "Climate_ID",
            "Temp (°C)": "Temperature_C",
            "Dew Point Temp (°C)": "Dew_Point_Temp_C",
            "Rel Hum (%)": "Relative_Humidity",
            "Wind Spd (km/h)": "Wind_Speed_kmh",
            "Visibility (km)": "Visibility_km",
            "Stn Press (kPa)": "Station_Pressure_kPa",
            "Weather": "Weather",
        }
    )
   # data.columns = data.columns.str.lower()
    #data.index.name = "date_time"
    #return data


# def download_weather_month(year, month):
   # url_template = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=5415&Year={year}&Month={month}&timeframe=1&submit=Download+Data"
    #url = url_template.format(year=year, month=month)
    #weather_data = pd.read_csv(
       # url, index_col="Date/Time (LST)", parse_dates=True, header=0
   # )
    #weather_data_clean = clean_data(weather_data)
    #return weather_data_clean


# TODO: redefine these functions using polars and your code above
def clean_data_pl(df: pl.DataFrame) -> pl.DataFrame:
    df = df.select([c for c in df.columns if df[c].null_count() == 0])

    drop_cols = [c for c in ["Year", "Month", "Day", "Time (LST)"] if c in df.columns]
    df = df.drop(drop_cols)

  
    cleaned_names = [c.replace('ï»¿"', "").replace("Â", "") for c in df.columns]
    df.columns = cleaned_names

  
    df = df.rename({
        "Longitude (x)": "Longitude",
        "Latitude (y)": "Latitude",
        "Station Name": "Station_Name",
        "Climate ID": "Climate_ID",
        "Temp (°C)": "Temperature_C",
        "Dew Point Temp (°C)": "Dew_Point_Temp_C",
        "Rel Hum (%)": "Relative_Humidity",
        "Wind Spd (km/h)": "Wind_Speed_kmh",
        "Visibility (km)": "Visibility_km",
        "Stn Press (kPa)": "Station_Pressure_kPa",
        "Weather": "Weather",
    })


    df.columns = [c.lower() for c in df.columns]

 
    if "date/time (lst)" in df.columns:
        df = df.with_columns(
            pl.col("date/time (lst)").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M").alias("date_time")
        )
        df = df.drop("date/time (lst)")

    return df


def download_weather_month_pl(year: int, month: int) -> pl.DataFrame:
  
    url_template = (
        "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?"
        "format=csv&stationID=5415&Year={year}&Month={month}&timeframe=1&submit=Download+Data"
    )
    url = url_template.format(year=year, month=month)


    df = pl.read_csv(url, try_parse_dates=True)

  
    df_clean = clean_data_pl(df)
    return df_clean


# %%
#download_weather_month(2012, 1)[:5]
# %%
# Now, let's use a list comprehension to download all our data and then just concatenate these data frames
# This might take a while
#data_by_month = [download_weather_month(2012, i) for i in range(1, 13)]
#weather_2012 = pd.concat(data_by_month)
#weather_2012.head()

# TODO: do the same with polars
download_weather_month_pl(2012, 1).head(5)
data_by_month = [download_weather_month_pl(2012, month) for month in range(1, 13)]
weather_2012 = pl.concat(data_by_month)
weather_2012.head(5)


# %%
# Now, let's save the data.
#weather_2012.to_csv("../data/weather_2012.csv")

# TODO: use polars to save the data.
weather_2012.write_csv("../data/weather_2012.csv")