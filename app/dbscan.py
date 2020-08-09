# Code adapted from Dr. Geoff Boeing's Urban Data Science Course (MIT License):
# https://github.com/gboeing/urban-data-science/blob/master/15-Spatial-Cluster-Analysis/cluster-analysis.ipynb

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn import metrics

kms_per_radian = 6371.0088

epsilon = 200 / kms_per_radian


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def dbscan(groups):
    """
        Apply dbscan cluster analysis for each quarter iteration

        Parameters:
            groups (df): A dataframe from table empres

        Returns:
            fin (list): A list containing, Id, Latitude, Longitude and Cluster number of each quarter
            hover (list): A list containing silhouette coefficient and compression data of each quarter

    """
    hover = []
    dfs = []

    for group in groups:
        coords = group[['latitude', 'longitude']].values

        db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

        if num_clusters < 2:
            continue

        quarter = group['quarters'].values

        if len(coords) != len(np.unique(cluster_labels)):
            silhouette = quarter[0] + ' Silhouette coefficient: {:0.03f}'.format(
                metrics.silhouette_score(coords, cluster_labels))
            message = ' Clustered {:,} points down to {:,} clusters, for {:.1f}% compression'.format(len(group),
                                                                                                     num_clusters,
                                                                                                     100 * (
                                                                                                             1 - float(
                                                                                                         num_clusters) / len(
                                                                                                         group)))
            hover.append(silhouette + ', ' + message)

        else:
            hover.append(quarter[0] + 'No points clustered, Number of clusters: ' + str(num_clusters))

        centermost_points = clusters.map(get_centermost_point)

        lats, lons = zip(*centermost_points)

        rep_points = pd.DataFrame({'longitude': lons, 'latitude': lats})

        rs = rep_points.apply(
            lambda row: group[(group['latitude'] == row['latitude']) & (group['longitude'] == row['longitude'])].iloc[
                0], axis=1)

        dfs.append(rs)
    df = pd.concat(dfs, keys=range(len(dfs)))

    return df, hover
