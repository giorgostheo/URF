# URF
Urban Route Finder - Open source alt to mapbox etc that can find multiple urban routes that are close-to optimal

# Dependencies
This project depends on GeoPandas, Pandas, Numpy etc. A requirements.txt will be released eventually.

# Data
To run this, you need a dataset that corresponds to the street network of the city/area where you want to plan routes. This dataset needs to also provide info regarding the direction of each street (TF,FT,TW etc - as per usual). Lastly, you need a starting and a stoping point for your route. 

# Disclaimer
This is a completelly open-source alt to mapbox-tomtom-google services that do more or less the same thing (a lot better I suppose) but only offer it as a closed source/paid service. Do not expect this to be just as good... (at least for now)

# Example
The following is an example that shows one or multiple (5 in this case) routes from the black point to the red one in Manhattan, NYC. 
![routes](https://user-images.githubusercontent.com/15364873/174436046-86eb416a-9600-4da3-9122-985b6ce28f9c.png)

$ Improvements

- Make it fast(er)
- Add weigts for each road (this will be useful if traffic is also taken into account at some point). 
- Multistop routes
- Routes that take into account road closures (proly the easiest imnprovement rn).

# People
Me, myself and I
