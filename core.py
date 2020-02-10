import pandas as pd
import requests
import json

MAX_QUERY = 99

class QueryFDA():
    """
    Class to query the OpenFDA API.

    Params
    ------
    url: string
        url to query the OpenFDA API
    """
    def __init__(self, url):
        self.url = url
        self.num_records = self._get_total_records()
        self.queries = self._get_num_queries()

    def _get_total_records(self):
        """
        Retrieves the total number of records returned by the query

        Returns
        -------
        : int
            total number of records for the query
        """
        return json.loads(requests.get(self.url).content)['meta']['results']['total']

    def _get_num_queries(self):
        """
        The number of requests needed to retrieve all records (max records per query is 99)

        Returns
        -------
        : dictionary
            how many full requests (99) and partial requests to query
        """
        num_records = self._get_total_records()
        full_query = num_records // MAX_QUERY
        part_query = num_records % MAX_QUERY
        return {'full_query': full_query,
                'part_query': part_query if part_query!=0 else None}

    def _fetch_data(self):
        """
        Fetch the data by querying the OpenFDA API.

        Returns
        -------
        results : list
            list of "results" sections of the query
        """
        data = []
        for q in range(self.queries['full_query']):
            start = q * MAX_QUERY
            end = start + MAX_QUERY
            print("Retrieving {0}-{1} of {2} records".format(start, end, self.num_records))
            _url = "{0}&skip={1}&limit={2}".format(self.url, start, MAX_QUERY)
            response = json.loads(requests.get(_url).content)
            data += response['results']

        if self.queries['part_query'] is not None:
            start = self.num_records - self.queries['part_query']
            end = self.num_records
            print("Retrieving {0}-{1} of {2} records".format(start, end, self.num_records))
            _url = "{0}&skip={1}&limit={2}".format(self.url, start, end)
            response = json.loads(requests.get(_url).content)
            data += response['results']

        return data

class IngredientsAnalysis(QueryFDA):
    """
    Class to transform the queried data into the right form for visualisation.

    Params
    ------
    url : string
        the url for the query
    """
    def __init__(self, url):
        QueryFDA.__init__(self, url)
        self.frame = None

    def extract_ingredient_info(self):
        """
        Get the required entries from the larger query.

        Returns
        -------
        : pandas DataFrame
            a dataframe with the required entries

        """
        data = self._fetch_data()
        table = []
        for d in data:
            year = d['effective_time'][0:4]
            drug_name = d['openfda']['generic_name'][0]
            manufacturer = d['openfda']['manufacturer_name'][0]
            num_ingredients = len(d['spl_product_data_elements'][0].split(","))
            try:
                route = d['openfda']['route'][0]
            except:
                route = None
            table.append([year, drug_name, route, num_ingredients, manufacturer])
        return pd.DataFrame(table, columns=['year', 'drug_name', 'route', 'num_ingredients', 'manufacturer'])

    def _calc_ingredients_pyear(self):
        """
        Calculates the number of ingredients per year of the manufacturers products.

        Returns
        -------
        : pandas DataFrame
            a dataframe with the required data
        """
        table = []
        if self.frame is None:
            self.frame = self.extract_ingredient_info() # get dataframe of ingredient info
        for year, df in self.frame.groupby(by='year'):
            drug_names = df['drug_name'].values
            ave_num_ingredients = df['num_ingredients'].values.mean().round(2)
            # std_dev = v['num_ingredients'].values.std().round(2)
            table.append([year, drug_names, ave_num_ingredients])
        return pd.DataFrame(table, columns=['year', 'drug_names', 'average_number_of_ingredients'])\
                .sort_values(by='year')

    def _calc_ingredients_pyear_proute(self):
        """
        Calculates the number of ingredients per year per route of the manufacturers products.

        Returns
        -------
        : pandas DataFrame
            a dataframe with the required data
        """
        table = []
        if self.frame is None:
            self.frame = self.extract_ingredient_info() # get dataframe of ingredient info
        for (year, route), df in self.frame.groupby(by=['year', 'route']):
            ave_num_ingredients = df['num_ingredients'].values.mean().round(2)
            table.append([year, route, ave_num_ingredients])
        return pd.DataFrame(table, columns=['year', 'route', 'average_number_of_ingredients']) \
            .sort_values(by=['year', 'route'])

    def get_analysis(self, type):
        """
        Returns the results for the required analysis.

        Params
        ------
        type : string
            the analysis type

        Returns
        -------
        : pandas DataFrame
            dataframe with the results of analysis
        """
        if type == 'generic':
            return self._calc_ingredients_pyear()
        elif type == 'route':
            return self._calc_ingredients_pyear_proute()
        else:
            raise Exception('Only "generic" and "route" analysis implemented')