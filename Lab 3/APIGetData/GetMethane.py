import cdsapi

dataset = "cams-global-radiative-forcings"
request = {
    "variable": ["radiative_forcing_of_methane"],
    "forcing_type": "instantaneous",
    "band": [
        "long_wave",
        "short_wave"
    ],
    "sky_type": ["all_sky"],
    "level": ["surface"],
    "version": ["2"],
    "year": [
        "2003", "2004", "2005",
        "2006", "2007", "2008",
        "2009", "2010", "2011",
        "2012", "2013", "2014",
        "2015", "2016", "2017",
        "2018"
    ],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
