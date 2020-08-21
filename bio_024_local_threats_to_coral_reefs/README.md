## Local Threats to Coral Reefs Dataset Pre-processing
This file describes the data pre-processing that was done to the [Local Threats to Coral Reefs](https://www.wri.org/resources/data-sets/reefs-risk-revisited) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

These data files are provided by the source as shapefiles (along with other data formats) within a single zipped directory. The following variables are shown on Resource Watch:
- 2011 Threat to Coral Reefs from Coastal Development: Estimated threat to coral reefs from coastal development, which reflects: the number, size, population density, and population growth rates of human settlements on the coast; locations of seaports, airports and hotels; and traffic from tourism.
- 2011 Threat to Coral Reefs from Marine Pollution: Estimated threat to coral reefs from marine-based pollution and damage, which reflects: distance from commercial and cruise ports, shipping intensity as measured by a voluntary reporting scheme, and presence of oil infrastructure.
- 2011 Threat to Coral Reefs from Coastal Pollution: Estimated threat to coral reefs from coastal-based pollution, which reflects sediment deposits accumulated throughout watersheds and released at river mouths.
- 2011 Threat to Coral Reefs from Overfishing: Estimated threat to coral reefs from overfishing and destructive fishing, which is based on proxies for demand for fish products and monitoring by field experts. The threat may be adjusted within marine protected areas rated as "effective" or "partially effective".
- 2011 Integrated Local Threat Level for Coral Reefs: Estimated threat to coral reefs from combined local activities in 2011. Local threats include: coastal development; marine-based pollution and damage; watershed-based pollution; overfishing and destructive fishing practices.

Because the data were already provided in a compatible format and projection, very little processing was necessary to display this data on Resource Watch, save for some file corrections (see next paragraph). The main zip file was downloaded from the source. Data for each indicator were stored in a dedicated folder. From each folder, the files associated with the shapefile (`rf_*_poly.*`) were renamed to correspond to the Resource Watch dataset identifier, then zipped together and uploaded to the Carto geospatial data hosting service. Map layers as drawn on Resource Watch then referenced these Carto data tables.

Each of the individual threat shapefiles contained some malformed geometries, which were manually removed from the table. The corresponding numeric identifiers (reflecting natural order of appearance within _original_ shapefile) are enumerated below:
- Coastal Development: 53253, 53402, 53414, 53810, 53845, 54091
- Marine Pollution: 48228, 48237, 48585, 48610, 48827
- Coastal Pollution: 53089, 53177, 53232, 53592, 53621, 53882
- Overfishing: 48540, 48553, 48886, 48913, 49154

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/bio024-try-2).

You can also download the original dataset [from the source website](https://www.wri.org/resources/data-sets/reefs-risk-revisited).

###### Note: This dataset processing was initially executed by [Elise Mazur](https://www.wri.org/profile/elise-mazur), with additional data layers later added by [Peter Kerins](https://www.wri.org/profile/peter-kerins).
