## Female & Male Population Densities Dataset Pre-processing
This file describes the data pre-processing that was done to [the Gridded Population of the World (GPW), v4: Basic Demographic Characteristics, v4.10 (2010)](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-basic-demographic-characteristics-rev11) for [display on Resource Watch](https://resourcewatch.org/data/explore/soc075-Broad-Age-Groups).

{Describe how the original data came from the source.}
The original data contains two layers, male population density and female population density in people per square kilometer.

To create the layer "Number of females per 100 males", we divide the female population density by the male population density and then multiply by 100.

This calculation was done using Google Earth Engine, a free geospatial analysis system by Google. While the sytem is free you need to sign up with a Google account, which can be done [here](https://earthengine.google.com/). 

And you can run the code we used to preprocess this layer in Google Earth Engine here [here](https://code.earthengine.google.com/69705398b91fdcbdad2298f08ada5da4), and the code is also copied below.
```
var female = ee.Image('projects/resource-watch-gee/soc_075_female_male_populations/female_density')
var male = ee.Image('projects/resource-watch-gee/soc_075_female_male_populations/male_density')

var scale = female.projection().nominalScale().getInfo()

var m_f_ratio = male.divide(female).multiply(100)

Export.image.toAsset({
  image: m_f_ratio,  
  description: 'Male_Female_Ratio',  
  assetId: 'projects/resource-watch-gee/soc_075_female_male_populations/male_female_ratio_density', 
  scale: scale, 
  maxPixels:1e13})
```

You can view the processed {Resource Watch public title} dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download original dataset [from the source website](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-basic-demographic-characteristics-rev11/data-download).

###### Note: This dataset processing was done by [Kristine Lister](https://www.wri.org/profile/kristine-lister), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
