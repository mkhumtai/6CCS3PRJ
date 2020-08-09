# Code adapted from Dr. Geoff Boeing's Urban Data Science Course (MIT License):
# https://github.com/gboeing/urban-data-science/blob/master/15-Spatial-Cluster-Analysis/cluster-analysis.ipynb

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning

simplefilter("ignore", category=ConvergenceWarning)


def kmeans(groups):
    """
        Apply kmeans for each quarter iteration
        Iterate through possible number of cluster and choose the one with the highest silhouette value

        Parameters:
            groups (df): A dataframe from table empres

        Returns:
            fin (list): A list containing, Id, Latitude, Longitude and Cluster number of each quarter
            hover (list): A list containing silhouette coefficient and compression data of each quarter

    """
    dfs = [] # Create an empty list of dataframes
    hover = [] # Create an empty list of silhouette value and percentage clustered
    for group in groups:

        X = group.loc[:, ['Id', 'latitude', 'longitude']]

        if len(X) <= 3:
            continue

        coords = group[['latitude', 'longitude']].values
        quarter = group['quarters'].values
        row = group.shape[0]

        maxk = 7 # Set the maximum number of clusters
        if row < 7:
            maxk = row # Change the maximum number of clusters if there are not enough data
        bestSil = -1

        for k in range(2, maxk + 1): # Iterate through the possible number of clusters
            kmeans = KMeans(n_clusters=k, init='k-means++').fit(X[X.columns[1:3]])
            labels = kmeans.labels_
            if (len(coords) != len(np.unique(labels))):
                sil = metrics.silhouette_score(coords, labels)
                if sil > bestSil: # Check for the silhouette value that is closest to 1
                    bestSil = sil
                    X['cluster'] = kmeans.fit_predict(X[X.columns[1:3]])
                    labels = kmeans.predict(X[X.columns[1:3]])  # Labels of each point
                    bestLabels = labels
                    num_clusters = len(set(bestLabels))
                    silhouette = quarter[0] + 'Silhouette coefficient: {:0.03f}'.format(sil)
                    message = ' Clustered {:,} points down to {:,} clusters, for {:.1f}% compression'.format(len(group),
                                                                                                             num_clusters,
                                                                                                             100 * (
                                                                                                                     1 - float(
                                                                                                                 num_clusters) / len(
                                                                                                                 group)))

        X = X[['Id', 'cluster']]
        df = group.merge(X, left_on='Id', right_on='Id')

        dfs.append(df)
        hover.append(silhouette + ', ' + message)

    df = pd.concat(dfs, keys=range(len(dfs)))
    df = df.drop_duplicates()

    return df, hover
