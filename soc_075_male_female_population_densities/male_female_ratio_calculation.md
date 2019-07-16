## This file describes the data pre-processing that was done to create the layer "2010 Ratio of Males to Females (# of males per 100 females)" of the dataset "Female & Male Population Densities".

This calculation was done using Google Earth Engine, a free geospatial analysis system by Google. The code itself can be found [here](https://code.earthengine.google.com/69705398b91fdcbdad2298f08ada5da4). While the sytem is free you need to sign up with a Google account, which can be done [here](https://earthengine.google.com/). 

The code is shown below:
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
