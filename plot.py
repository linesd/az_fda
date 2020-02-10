import pandas as pd
import matplotlib.pyplot as plt

def plot_ingredients(df, type = 'bar', save_fig=None, path = None):
    """
    Plots the results of the analysis.

    Params
    ------
    df : pandas DataFrame
        results of the analysis

    type : string
        type of plot to show - (bar or line)

    save_fig : bool
        whether to save the figure

    path : string
        path to folder to save figure
    """
    if 'route' in df.columns:
        analysis_name = "route"
        years = list(dict.fromkeys(df['year']))
        x = {}
        for route, frame in df.groupby(by=['route']):
            num_ingredient_per_route = []
            i = 0
            for year in years:
                if year in list(frame['year']):
                    num_ingredient_per_route.append(list(frame['average_number_of_ingredients'])[i])
                    i += 1
                else:
                    num_ingredient_per_route.append(0)
            x[route] = num_ingredient_per_route
    else:
        analysis_name = "generic"
        years = list(dict.fromkeys(df['year']))
        anoi = list(dict.fromkeys(df['average_number_of_ingredients']))
        x = {'Average Number of Ingredients': anoi}

    f = pd.DataFrame(x, index=years)

    if type == "bar":
        ax = f.plot.bar(rot=0)
    elif type == "line":
        ax = f.plot.line(rot=0)
    else:
        raise Exception('Plot only implemented for bar and line type')

    ax.grid(linestyle='--')
    plt.xlabel('Year')
    plt.ylabel('Average number of ingredients')

    if save_fig is not None:
        fname = path + "/" + analysis_name + "_" + type + ".png"
        plt.savefig(fname, dpi=300)
    plt.show()