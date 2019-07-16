## This file describes the data pre-processing that was done to create the layer "2010 Ratio of Males to Females (# of males per 100 females)" of the dataset "Female & Male Population Densities".

This calculation was done using Google Earth Engine, a free geospatial analysis system by Google. The code itself can be found [here](https://code.earthengine.google.com/34fc95dd936fbdc29f3e623ffdae89af). While the sytem is free you need to sign up with a Google account, which can be done [here](https://earthengine.google.com/). 

The code is shown below:
'''
var female = ee.Image('projects/resource-watch-gee/soc_075_female_male_populations/female_density')
var male = ee.Image('projects/resource-watch-gee/soc_075_female_male_populations/male_density')
Map.addLayer(female)
Map.addLayer(male)
var scale = female.projection().nominalScale().getInfo()

var m_f_ratio = male.divide(female).multiply(100)
var sld = 
  '<RasterSymbolizer>' +
    '<ColorMap type="ramp" extended="false" >' +
      '<ColorMapEntry color="#d73027" quantity="0"  opacity="0" />' +
      '<ColorMapEntry color="#d73027" quantity="80" />' +
      '<ColorMapEntry color="#f46d43" quantity="90" />' +
      '<ColorMapEntry color="#fdae61" quantity="95"  />' +
      '<ColorMapEntry color="#fee090" quantity="100"  />' +
      '<ColorMapEntry color="#e0f3f8" quantity="105"  />' +
      '<ColorMapEntry color="#abd9e9" quantity="110" />' +
      '<ColorMapEntry color="#74add1" quantity="120"  />' +
      '<ColorMapEntry color="#4575b4" quantity="170"  />' +
    '</ColorMap>' +
  '</RasterSymbolizer>';  
  
Map.addLayer(m_f_ratio.sldStyle(sld), {}, 'm_f_ratio_new');
 
Export.image.toAsset({
  image: m_f_ratio,  
  description: 'Male_Female_Ratio',  
  assetId: 'projects/resource-watch-gee/soc_075_female_male_populations/male_female_ratio_density', 
  scale: scale, 
  maxPixels:1e13})
'''
