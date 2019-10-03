#!/usr/bin/env python3
if __name__ == '__main__':
    import pandas as pd
    import os
    import logging
    import sys
    import glob
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    import requests as req
    from collections import OrderedDict

    # Utilities
    import carto
    import misc

    CARTO_USER = os.getenv('CARTO_WRI_RW_USER')
    WB_DATA = "resourcewatch/"

    def fetch_wb_data(codes_and_names):
        tables = list(codes_and_names.keys())
        for ix, table in enumerate(tables):
            indicators = codes_and_names[table]['indicators']
            value_names = codes_and_names[table]['columns']
            for i in range(len(indicators)):
                indicator = indicators[i]
                value_name = value_names[i]
                # Fetch data
                res = req.get("http://api.worldbank.org/countries/all/indicators/{}?format=json&per_page=10000".format(indicator))
                pages = int(res.json()[0]['pages'])
                #logging.info(res.text)
                json = []
                for page in range(1,pages+1):
                    res = req.get("http://api.worldbank.org/countries/all/indicators/{}?format=json&per_page=10000&page={}".format(indicator,page))
                    json = json + res.json()[1]
                # Format into dataframe, only keep some columns
                #Old way
                #data = pd.io.json.json_normalize(res.json()[1])
                data = pd.io.json.json_normalize(json)
                data = data[["country.value", "date", "value"]]
                data.columns = ["Country", "Year", value_name]
                # Standardize time column for ISO time
                data["Time"] = misc.fix_datetime_UTC(data, dttm_elems={"year_col":"Year"})
            
                # Only keep countries, not larger political bodies
                data = data.iloc[misc.pick_wanted_entities(data["Country"].values)]
            
                # Set index to Country and Year
                data = data.set_index(["Country", "Time","Year"])
                if ix == 0 and i == 0:
                    # Start off the dataframe
                    all_world_bank_data = data
                else:
                    # Continue adding to the dataframe
                    all_world_bank_data = all_world_bank_data.join(data, how="outer")

        # Finished fetching, reset_index
        all_world_bank_data = all_world_bank_data.reset_index()

        # Add ISO3 column - will now only contained desired entities
        all_world_bank_data["ISO3"] = list(map(misc.add_iso, all_world_bank_data["Country"]))
    
        # Drop rows which don't have an ISO3 assigned
        all_world_bank_data = all_world_bank_data.loc[pd.notnull(all_world_bank_data["ISO3"])]
    
        #Add in RW specific countries and ISO codes
        all_world_bank_data["rw_country_name"] = list(map(misc.add_rw_name, all_world_bank_data["ISO3"]))
        all_world_bank_data["rw_country_code"] = list(map(misc.add_rw_code, all_world_bank_data["ISO3"]))

        # Set the index to be everything except the value column. This simplifies dissection later
        all_world_bank_data = all_world_bank_data.set_index(["Country", "ISO3", "Time", "Year", "rw_country_name","rw_country_code"])
        return(all_world_bank_data)

    def main():

        ## World Bank data series codes and names
        # key = WB code: https://datahelpdesk.worldbank.org/knowledgebase/articles/201175-how-does-the-world-bank-code-its-indicators
        # value = [table_name, value_column_name, units]
    
    
        ### WARNINGS
        # For this to work as expected, there must not be any , in the table names
        # And table names cannot be longer than a certain number of characters, equal to
        # Length of: soc_106_proportion_of_seats_held_by_women_in_national_parliamen (63 characters)
        data_codes_and_names = {
            'soc_020_gini' : {
                'indicators': ['SI.POV.GINI'],
                'columns': ['GINI'], 
                'units': ['GINI index (World Bank estimate)']},
            'ene_012_electricity_access': {
                'indicators': ['EG.ELC.ACCS.ZS','EG.ELC.ACCS.RU.ZS','EG.ELC.ACCS.UR.ZS'],
                'columns': ['total','rural','urban'],
                'units': ['% of population', '% of rural population', '% of urban population']},
            'ene_021_se4all_country_indicators':{
                'indicators': ['3.1_RE.CONSUMPTION'],
                'columns': ['rnw_ene_con'],
                'units': ['Renewable energy consumption (TJ)']},
            'soc_101 Renewable energy consumption':{
                'indicators': ['EG.FEC.RNEW.ZS'],
                'columns': ['rnw_ene_con_per'],
                'units': ['% of total final energy consumption']},
            'soc_082_individuals_using_the_internet':{
                'indicators': ['IT.NET.USER.ZS'],
                'columns': ['intnt_use'],
                'units': ['% of population']},
            'soc_103 Household final consumption expenditure per capita':{
                'indicators': ['NE.CON.PRVT.PC.KD'],
                'columns': ['cons_exp'],
                'units': ['constant 2010 US$']},
            'soc_104 Industry value added':{
                'indicators': ['NV.IND.TOTL.KD'],
                'columns': ['ind_val_add'],
                'units': ['constant 2010 US$']},
            'soc_105 Total natural resources rents':{
                'indicators': ['NY.GDP.TOTL.RT.ZS'],
                'columns': ['nat_rsc_rnt'],
                'units': ['% of GDP']},
            'soc_106 Proportion of women in national parliaments':{
                'indicators': ['SG.GEN.PARL.ZS'],
                'columns': ['wmn_prlmnt'],
                'units': ['% of parliamentary seats']},
            'soc_107 Employment to population ratio':{
                'indicators': ['SL.EMP.TOTL.SP.ZS'],
                'columns': ['empl_ratio'],
                'units': ['% employed population, ages 15+']},
            'soc_108 Net migration':{
                'indicators': ['SM.POP.NETM'],
                'columns': ['net_migr'],
                'units': ['number of net in-migrants']},
            'soc_036_life_expectancy_at_birth':{
                'indicators': ['SP.DYN.LE00.IN'],
                'columns': ['life_exp'],
                'units': ['years']},
            'cit_025_urban_population':{
                'indicators': ['SP.URB.TOTL.IN.ZS'],
                'columns': ['urban_pop'],
                'units': ['% of total population']},
            'soc_111 Merchandise imports':{
                'indicators': ['TM.VAL.MRCH.CD.WT'],
                'columns': ['merch_imp'],
                'units': ['current US$']},
            'com_010_gdp_ppp_usd':{
                'indicators': ['NY.GDP.MKTP.CD'],
                'columns': ['gdp'],
                'units': ['current US$']},
            'soc_066_population_below_poverty_line':{
                'indicators':['SI.POV.DDAY'],
                'columns':['poverty'],
                'units':['% of population']},
            'soc_074_employment_in_agriculture':{
                'indicators':['SL.AGR.EMPL.ZS'],
                'columns':['employment'],
                'units':['% of population']},
            'soc_076_country_population':{
                'indicators':['SP.POP.TOTL'],
                'columns':['total population'],
                'units':['people']},
            'soc_081_mortality_rate':{
                'indicators':['SP.DYN.IMRT.IN'],
                'columns':['mortality rate'],
                'units':['deaths per 1000 live births']},
            'soc_029_worldwide_governance_indicators': {
                'indicators': ['GE.EST','RQ.EST','PV.EST','RL.EST','VA.EST','CC.EST'],
                'columns': ['government_effectiveness_data','regulatory_quality_data','political_stability_data','rule_of_law_data','voice_accountability_data','control_of_corruption_data'],
                'units': ['estimate', 'estimate', 'estimate','estimate','estimate','estimate']},
            'soc_084_pop_growth_rate' : {
                'indicators': ['SP.POP.GROW'],
                'columns': ['Growth rate'],
                'units': ['percent']},
            'foo_43_agriculture_value_added' : {
                'indicators': ['NV.AGR.TOTL.ZS'],
                'columns': ['Value added'],
                'units': ['percent of GDP']},
            'com_036_unemployment' : {
                'indicators': ['SL.UEM.TOTL.ZS'],
                'columns': ['unemployment'],
                'units': ['% of total labor force']},
            'ene_012a_electricity_access' : {
                'indicators': ['EG.ELC.ACCS.ZS','EG.ELC.ACCS.UR.ZS','EG.ELC.ACCS.RU.ZS'],
                'columns': ['total','urban','rural'],
                'units': ['% of population','% of urban pop','% of rural pop']},
            'wat_005a_improved_water_access' : {
                'indicators': ['SH.H2O.SMDW.ZS','SH.H2O.SMDW.UR.ZS','SH.H2O.SMDW.RU.ZS'],
                'columns': ['total','urban','rural'],
                'units': ['% of population','% of urban pop','% of rural pop']}  
            }
    
        

        # Write to S3 and Carto the individual data sets
        #for code, info in data_codes_and_names.items():
        for tablename, info in data_codes_and_names.items():
            data_codes_and_names_short = {tablename: info}
            logging.info('Next table to update: {}'.format(data_codes_and_names_short))
            #Creates dataset with all data columns
            all_world_bank_data = fetch_wb_data(data_codes_and_names_short)
            all_world_bank_data = all_world_bank_data.where((pd.notnull(all_world_bank_data)), None)

            # Can't have spaces in Carto table names
            table = tablename.replace(' ', '_').lower()
            valnames = info['columns']
            units = info['units']
            indicators = info['indicators']

            column_order = ['ISO3', 'Country', 'Time', 'Year']
            CARTO_SCHEMA = OrderedDict([
                ('country_code', 'text'),
                ('Country_name', 'text'),
                ('datetime', 'timestamp'),
                ('Year', 'numeric')])

            #Get subset of dataset with
            long_form = all_world_bank_data[valnames]
            long_form = long_form.reset_index()

            #Add data column, unit, and indicator code to CARTO_SCHEMA, column_order, and dataset
            for i in range(len(valnames)):
                if i==0 and len(valnames) == 1  and tablename!='soc_081_mortality_rate':
                    CARTO_SCHEMA.update({'yr_data':'numeric'})
                else:
                    CARTO_SCHEMA.update({valnames[i].replace(' ', '_').lower():'numeric'})
                CARTO_SCHEMA.update({'Unit'+str(i+1):'text'})
                CARTO_SCHEMA.update({'Indicator_code'+str(i+1):'text'})
                long_form[units[i]] = units[i]
                long_form[indicators[i]] = indicators[i]
                column_order.append(valnames[i])
                column_order.append(units[i])
                column_order.append(indicators[i])

            CARTO_SCHEMA.update({"rw_country_name":'text'})
            CARTO_SCHEMA.update({"rw_country_code":'text'})
            column_order = column_order + ["rw_country_name", "rw_country_code"]


            # Enforce order in the data frame
            long_form = long_form[column_order]

            #Remove null values if there is only one data column
            #if len(valnames) == 1:
            #    long_form = long_form[pd.notnull(long_form[valnames[0]])]


            # Write to S3
            misc.write_to_S3(long_form, WB_DATA + "{}_edit.csv.gz".format(table))

            # Write to Carto
            CARTO_TABLE = table


            ### 1. Check if table exists and create table, if it does, drop and replace
            #dest_ids = []
            if not carto.tableExists(CARTO_TABLE):
                logging.info('Table {} does not exist'.format(CARTO_TABLE))
                carto.createTable(CARTO_TABLE, CARTO_SCHEMA)
            else:
                logging.info('Table {} does exist'.format(CARTO_TABLE))
                carto.dropTable(CARTO_TABLE)
                carto.createTable(CARTO_TABLE, CARTO_SCHEMA)

            ### 2. Insert new observations
            # https://stackoverflow.com/questions/19585280/convert-a-row-in-pandas-into-list
            rows = long_form.values.tolist()
            logging.info('Success! The following includes the first ten rows added to Carto')
            logging.info(rows[:10])
            if len(rows):
                carto.blockInsertRows(CARTO_TABLE, CARTO_SCHEMA, rows)

    main()
