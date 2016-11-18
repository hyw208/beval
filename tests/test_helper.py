import pandas as pd
from StringIO import StringIO


CAR_DATA = """Make,Type,MinPrice,MidPrice,MaxPrice,MPGcity,MPGhiway,Airbags,DriveTrain,Cylinders,Engine,HP,RPM,RevMile,Manual,FuelCap,PassCap,Length,Wheelbase,Width,Uturn,RearSeat,LugCap,Weight,Source
Acura,Small,12.9,15.9,18.8,25,31,None,Front,4,1.8,140,6300,2890,1,13.2,5,177,102,68,37,26.5,11,2705,nonUSA
Acura,Midsize,29.2,33.9,38.7,18,25,DriverPass,Front,6,3.2,200,5500,2335,1,18,5,195,115,71,38,30,15,3560,nonUSA
Audi,Compact,25.9,29.1,32.3,20,26,Driver,Front,6,2.8,172,5500,2280,1,16.9,5,180,102,67,37,28,14,3375,nonUSA
Audi,Midsize,30.8,37.7,44.6,19,26,DriverPass,Front,6,2.8,172,5500,2535,1,21.1,6,193,106,70,37,31,17,3405,nonUSA
BMW,Midsize,23.7,30,36.2,22,30,Driver,Rear,4,3.5,208,5700,2545,1,21.1,4,186,109,69,39,27,13,3640,nonUSA
Buick,Midsize,14.2,15.7,17.3,22,31,Driver,Front,4,2.2,110,5200,2565,0,16.4,6,189,105,69,41,28,16,2880,USA
Buick,Large,19.9,20.8,21.7,19,28,Driver,Front,6,3.8,170,4800,1570,0,18,6,200,111,74,42,30.5,17,3470,USA
Buick,Large,22.6,23.7,24.9,16,25,Driver,Rear,6,5.7,180,4000,1320,0,23,6,216,116,78,45,30.5,21,4105,USA
Buick,Midsize,26.3,26.3,26.3,19,27,Driver,Front,6,3.8,170,4800,1690,0,18.8,5,198,108,73,41,26.5,14,3495,USA
Cadillac,Large,33,34.7,36.3,16,25,Driver,Front,8,4.9,200,4100,1510,0,18,6,206,114,73,43,35,18,3620,USA
Cadillac,Midsize,37.5,40.1,42.7,16,25,DriverPass,Front,8,4.6,295,6000,1985,0,20,5,204,111,74,44,31,14,3935,USA
Chevrolet,Compact,8.5,13.4,18.3,25,36,None,Front,4,2.2,110,5200,2380,1,15.2,5,182,101,66,38,25,13,2490,USA
Chevrolet,Compact,11.4,11.4,11.4,25,34,Driver,Front,4,2.2,110,5200,2665,1,15.6,5,184,103,68,39,26,14,2785,USA
Chevrolet,Sporty,13.4,15.1,16.8,19,28,DriverPass,Rear,6,3.4,160,4600,1805,1,15.5,4,193,101,74,43,25,13,3240,USA
Chevrolet,Midsize,13.4,15.9,18.4,21,29,None,Front,4,2.2,110,5200,2595,0,16.5,6,198,108,71,40,28.5,16,3195,USA
Chevrolet,Van,14.7,16.3,18,18,23,None,Front,6,3.8,170,4800,1690,0,20,7,178,110,74,44,30.5,NA,3715,USA
Chevrolet,Van,14.7,16.6,18.6,15,20,None,All,6,4.3,165,4000,1790,0,27,8,194,111,78,42,33.5,NA,4025,USA
Chevrolet,Large,18,18.8,19.6,17,26,Driver,Rear,8,5,170,4200,1350,0,23,6,214,116,77,42,29.5,20,3910,USA
Chevrolet,Sporty,34.6,38,41.5,17,25,Driver,Rear,8,5.7,300,5000,1450,1,20,2,179,96,74,43,NA,NA,3380,USA
Chrylser,Large,18.4,18.4,18.4,20,28,DriverPass,Front,6,3.3,153,5300,1990,0,18,6,203,113,74,40,31,15,3515,USA
Chrysler,Compact,14.5,15.8,17.1,23,28,DriverPass,Front,4,3,141,5000,2090,0,16,6,183,104,68,41,30.5,14,3085,USA
Chrysler,Large,29.5,29.5,29.5,20,26,Driver,Front,6,3.3,147,4800,1785,0,16,6,203,110,69,44,36,17,3570,USA
Dodge,Small,7.9,9.2,10.6,29,33,None,Front,4,1.5,92,6000,3285,1,13.2,5,174,98,66,32,26.5,11,2270,USA
Dodge,Small,8.4,11.3,14.2,23,29,Driver,Front,4,2.2,93,4800,2595,1,14,5,172,97,67,38,26.5,13,2670,USA
Dodge,Compact,11.9,13.3,14.7,22,27,Driver,Front,4,2.5,100,4800,2535,1,16,6,181,104,68,39,30.5,14,2970,USA
Dodge,Van,13.6,19,24.4,17,21,Driver,All,6,3,142,5000,1970,0,20,7,175,112,72,42,26.5,NA,3705,USA
Dodge,Midsize,14.8,15.6,16.4,21,27,Driver,Front,4,2.5,100,4800,2465,0,16,6,192,105,69,42,30.5,16,3080,USA
Dodge,Sporty,18.5,25.8,33.1,18,24,Driver,All,6,3,300,6000,2120,1,19.8,4,180,97,72,40,20,11,3805,USA
Eagle,Small,7.9,12.2,16.5,29,33,None,Front,4,1.5,92,6000,2505,1,13.2,5,174,98,66,36,26.5,11,2295,USA
Eagle,Large,17.5,19.3,21.2,20,28,DriverPass,Front,6,3.5,214,5800,1980,0,18,6,202,113,74,40,30,15,3490,USA
Ford,Small,6.9,7.4,7.9,31,33,None,Front,4,1.3,63,5000,3150,1,10,4,141,90,63,33,26,12,1845,USA
Ford,Small,8.4,10.1,11.9,23,30,None,Front,4,1.8,127,6500,2410,1,13.2,5,171,98,67,36,28,12,2530,USA
Ford,Compact,10.4,11.3,12.2,22,27,None,Front,4,2.3,96,4200,2805,1,15.9,5,177,100,68,39,27.5,13,2690,USA
Ford,Sporty,10.8,15.9,21,22,29,Driver,Rear,4,2.3,105,4600,2285,1,15.4,4,180,101,68,40,24,12,2850,USA
Ford,Sporty,12.8,14,15.2,24,30,Driver,Front,4,2,115,5500,2340,1,15.5,4,179,103,70,38,23,18,2710,USA
Ford,Van,14.5,19.9,25.3,15,20,Driver,All,6,3,145,4800,2080,1,21,7,176,119,72,45,30,NA,3735,USA
Ford,Midsize,15.6,20.2,24.8,21,30,Driver,Front,6,3,140,4800,1885,0,16,5,192,106,71,40,27.5,18,3325,USA
Ford,Large,20.1,20.9,21.7,18,26,Driver,Rear,8,4.6,190,4200,1415,0,20,6,212,114,78,43,30,21,3950,USA
Geo,Small,6.7,8.4,10,46,50,None,Front,3,1,55,5700,3755,1,10.6,4,151,93,63,34,27.5,10,1695,nonUSA
Geo,Sporty,11.5,12.5,13.5,30,36,Driver,Front,4,1.6,90,5400,3250,1,12.4,4,164,97,67,37,24.5,11,2475,nonUSA
Honda,Sporty,17,19.8,22.7,24,31,DriverPass,Front,4,2.3,160,5800,2855,1,15.9,4,175,100,70,39,23.5,8,2865,nonUSA
Honda,Small,8.4,12.1,15.8,42,46,Driver,Front,4,1.5,102,5900,2650,1,11.9,4,173,103,67,36,28,12,2350,nonUSA
Honda,Compact,13.8,17.5,21.2,24,31,DriverPass,Front,4,2.2,140,5600,2610,1,17,4,185,107,67,41,28,14,3040,nonUSA
Hyundai,Small,6.8,8,9.2,29,33,None,Front,4,1.5,81,5500,2710,1,11.9,5,168,94,63,35,26,11,2345,nonUSA
Hyundai,Small,9,10,11,22,29,None,Front,4,1.8,124,6000,2745,1,13.7,5,172,98,66,36,28,12,2620,nonUSA
Hyundai,Sporty,9.1,10,11,26,34,None,Front,4,1.5,92,5550,2540,1,11.9,4,166,94,64,34,23.5,9,2285,nonUSA
Hyundai,Midsize,12.4,13.9,15.3,20,27,None,Front,4,2,128,6000,2335,1,17.2,5,184,104,69,41,31,14,2885,nonUSA
Infiniti,Midsize,45.4,47.9,50.4,17,22,Driver,Rear,8,4.5,278,6000,1955,0,22.5,5,200,113,72,42,29,15,4000,nonUSA
Lexus,Midsize,27.5,28,28.4,18,24,Driver,Front,6,3,185,5200,2325,1,18.5,5,188,103,70,40,27.5,14,3510,nonUSA
Lexus,Midsize,34.7,35.2,35.6,18,23,DriverPass,Rear,6,3,225,6000,2510,1,20.6,4,191,106,71,39,25,9,3515,nonUSA
Lincoln,Midsize,33.3,34.3,35.3,17,26,DriverPass,Front,6,3.8,160,4400,1835,0,18.4,6,205,109,73,42,30,19,3695,USA
Lincoln,Large,34.4,36.1,37.8,18,26,DriverPass,Rear,8,4.6,210,4600,1840,0,20,6,219,117,77,45,31.5,22,4055,USA
Mazda,Small,7.4,8.3,9.1,29,37,None,Front,4,1.6,82,5000,2370,1,13.2,4,164,97,66,34,27,16,2325,nonUSA
Mazda,Small,10.9,11.6,12.3,28,36,None,Front,4,1.8,103,5500,2220,1,14.5,5,172,98,66,36,26.5,13,2440,nonUSA
Mazda,Compact,14.3,16.5,18.7,26,34,Driver,Front,4,2.5,164,5600,2505,1,15.5,5,184,103,69,40,29.5,14,2970,nonUSA
Mazda,Van,16.6,19.1,21.7,18,24,None,All,6,3,155,5000,2240,0,19.6,7,190,110,72,39,27.5,NA,3735,nonUSA
Mazda,Sporty,32.5,32.5,32.5,17,25,Driver,Rear,NA,1.3,255,6500,2325,1,20,2,169,96,69,37,NA,NA,2895,nonUSA
Mercedes-Benz,Compact,29,31.9,34.9,20,29,Driver,Rear,4,2.3,130,5100,2425,1,14.5,5,175,105,67,34,26,12,2920,nonUSA
Mercedes-Benz,Midsize,43.8,61.9,80,19,25,DriverPass,Rear,6,3.2,217,5500,2220,0,18.5,5,187,110,69,37,27,15,3525,nonUSA
Mercury,Sporty,13.3,14.1,15,23,26,Driver,Front,4,1.6,100,5750,2475,1,11.1,4,166,95,65,36,19,6,2450,USA
Mercury,Midsize,14.9,14.9,14.9,19,26,None,Rear,6,3.8,140,3800,1730,0,18,5,199,113,73,38,28,15,3610,USA
Mitsubishi,Small,7.7,10.3,12.9,29,33,None,Front,4,1.5,92,6000,2505,1,13.2,5,172,98,67,36,26,11,2295,nonUSA
Mitsubishi,Midsize,22.4,26.1,29.9,18,24,Driver,Front,6,3,202,6000,2210,0,19,5,190,107,70,43,27.5,14,3730,nonUSA
Nissan,Small,8.7,11.8,14.9,29,33,Driver,Front,4,1.6,110,6000,2435,1,13.2,5,170,96,66,33,26,12,2545,nonUSA
Nissan,Compact,13,15.7,18.3,24,30,Driver,Front,4,2.4,150,5600,2130,1,15.9,5,181,103,67,40,28.5,14,3050,nonUSA
Nissan,Van,16.7,19.1,21.5,17,23,None,Front,6,3,151,4800,2065,0,20,7,190,112,74,41,27,NA,4100,nonUSA
Nissan,Midsize,21,21.5,22,21,26,Driver,Front,6,3,160,5200,2045,0,18.5,5,188,104,69,41,28.5,14,3200,nonUSA
Oldsmobile,Compact,13,13.5,14,24,31,None,Front,4,2.3,155,6000,2380,0,15.2,5,188,103,67,39,28,14,2910,USA
Oldsmobile,Midsize,14.2,16.3,18.4,23,31,Driver,Front,4,2.2,110,5200,2565,0,16.5,5,190,105,70,42,28,16,2890,USA
Oldsmobile,Van,19.5,19.5,19.5,18,23,None,Front,6,3.8,170,4800,1690,0,20,7,194,110,74,44,30.5,NA,3715,USA
Oldsmobile,Large,19.5,20.7,21.9,19,28,Driver,Front,6,3.8,170,4800,1570,0,18,6,201,111,74,42,31.5,17,3470,USA
Plymouth,Sporty,11.4,14.4,17.4,23,30,None,All,4,1.8,92,5000,2360,1,15.9,4,173,97,67,39,24.5,8,2640,USA
Pontiac,Small,8.2,9,9.9,31,41,None,Front,4,1.6,74,5600,3130,1,13.2,4,177,99,66,35,25.5,17,2350,USA
Pontiac,Compact,9.4,11.1,12.8,23,31,None,Front,4,2,110,5200,2665,1,15.2,5,181,101,66,39,25,13,2575,USA
Pontiac,Sporty,14,17.7,21.4,19,28,DriverPass,Rear,6,3.4,160,4600,1805,1,15.5,4,196,101,75,43,25,13,3240,USA
Pontiac,Midsize,15.4,18.5,21.6,19,27,None,Front,6,3.4,200,5000,1890,1,16.5,5,195,108,72,41,28.5,16,3450,USA
Pontiac,Large,19.4,24.4,29.4,19,28,DriverPass,Front,6,3.8,170,4800,1565,0,18,6,177,111,74,43,30.5,18,3495,USA
Saab,Compact,20.3,28.7,37.1,20,26,Driver,Front,4,2.1,140,6000,2910,1,18,5,184,99,67,37,26.5,14,2775,nonUSA
Saturn,Small,9.2,11.1,12.9,28,38,Driver,Front,4,1.9,85,5000,2145,1,12.8,5,176,102,68,40,26.5,12,2495,USA
Subaru,Small,7.3,8.4,9.5,33,37,None,All,3,1.2,73,5600,2875,1,9.2,4,146,90,60,32,23.5,10,2045,nonUSA
Subaru,Small,10.5,10.9,11.3,25,30,None,All,4,1.8,90,5200,3375,1,15.9,5,175,97,65,35,27.5,15,2490,nonUSA
Subaru,Compact,16.3,19.5,22.7,23,30,Driver,All,4,2.2,130,5600,2330,1,15.9,5,179,102,67,37,27,14,3085,nonUSA
Suzuki,Small,7.3,8.6,10,39,43,None,Front,3,1.3,70,6000,3360,1,10.6,4,161,93,63,34,27.5,10,1965,nonUSA
Toyota,Small,7.8,9.8,11.8,32,37,Driver,Front,4,1.5,82,5200,3505,1,11.9,5,162,94,65,36,24,11,2055,nonUSA
Toyota,Sporty,14.2,18.4,22.6,25,32,Driver,Front,4,2.2,135,5400,2405,1,15.9,4,174,99,69,39,23,13,2950,nonUSA
Toyota,Midsize,15.2,18.2,21.2,22,29,Driver,Front,4,2.2,130,5400,2340,1,18.5,5,188,103,70,38,28.5,15,3030,nonUSA
Toyota,Van,18.9,22.7,26.6,18,22,Driver,All,4,2.4,138,5000,2515,1,19.8,7,187,113,71,41,35,NA,3785,nonUSA
Volkswagen,Small,8.7,9.1,9.5,25,33,None,Front,4,1.8,81,5500,2550,1,12.4,4,163,93,63,34,26,10,2240,nonUSA
Volkswagen,Van,16.6,19.7,22.7,17,21,None,Front,5,2.5,109,4500,2915,1,21.1,7,187,115,72,38,34,NA,3960,nonUSA
Volkswagen,Compact,17.6,20,22.4,21,30,None,Front,4,2,134,5800,2685,1,18.5,5,180,103,67,35,31.5,14,2985,nonUSA
Volkswagen,Sporty,22.9,23.3,23.7,18,25,None,Front,6,2.8,178,5800,2385,1,18.5,4,159,97,66,36,26,15,2810,nonUSA
Volvo,Compact,21.8,22.7,23.5,21,28,Driver,Rear,4,2.3,114,5400,2215,1,15.8,5,190,104,67,37,29.5,14,2985,nonUSA
Volvo,Midsize,24.8,26.7,28.5,20,28,DriverPass,Front,5,2.4,168,6200,2310,1,19.3,5,184,105,69,38,30,15,3245,nonUSA
"""


class CompareError(object):

    def __init__(self, error):
        self._error = error

    def __cmp__(self, other):
        raise self._error


class Car(object):

    def __init__(self, dims):
        self._data = {k: v for k, v in zip(CAR_DIMENSIONS, dims)}
        self._access_errors = {}
        self._compare_errors = {}

    def __enter__(self):
        self.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def __getattr__(self, item):
        if item in self._access_errors:
            raise self._access_errors[item]

        elif item in self._compare_errors:
            return self._compare_errors[item]

        elif item in self._data:
            return self._data[item]

        else:
            raise AttributeError("cannot find dimension '%s'" % item)

    def set_access_error(self, item, err):
        """ raise specified error when accessing item """
        self._access_errors[item] = err

    def set_compare_error(self, item, err):
        self._compare_errors[item] = err

    def clear(self):
        self._access_errors = {}
        self._compare_errors = {}

    def toDict(self):
        return self._data


CAR_DF = pd.read_csv(StringIO(CAR_DATA), sep=",")


CAR_DIMENSIONS = [col.lower() for col in CAR_DF.columns]


CARS = [Car(row) for i, row in CAR_DF.iterrows()]

acura_small = CARS[0]
acura_midsize = CARS[1]
chevrolet_compact_e = CARS[11]
chevrolet_compact_c = CARS[12]