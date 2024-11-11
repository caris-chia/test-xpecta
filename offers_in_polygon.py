from shapely.geometry import Point
from shapely.geometry import Polygon
import pandas as pd

polygon_to_evaluate = Polygon([
    (-74.08155174984176, 4.627973942031079),
    (-74.08498497738083, 4.632080370742741),
    (-74.09030648006637, 4.634475776480623),
    (-74.09356804622848, 4.637384472533626),
    (-74.09528465999801, 4.640635353947642),
    (-74.09940453304489, 4.645426099264879),
    (-74.10730095638473, 4.659627045795844),
    (-74.11210747493942, 4.666641865389938),
    (-74.102666099207, 4.676222969106728),
    (-74.09511299862106, 4.687001554127775),
    (-74.08961983455856, 4.681868915303649),
    (-74.08670159115036, 4.6777627771305035),
    (-74.08155174984176, 4.6731433429054725),
    (-74.07674523128708, 4.67040588603372),
    (-74.07365532650192, 4.667668418477097),
    (-74.07846184505661, 4.6586004809568005),
    (-74.07846184505661, 4.6447417090687235),
    (-74.08000679744919, 4.634989076654115),
    (-74.08000679744919, 4.6303693616762285),
    (-74.080693442957, 4.627802840317588),
    (-74.08223839534958, 4.6283161453339705),
    (-74.08155174984176, 4.627973942031079),
])

# Cargar el archivo en un DataFrame
df = pd.read_csv("./output/offers_deduplicated.csv")

# Por cada registro en el DataFrame, llamar la función is_point_inside_polygon
for index, row in df.iterrows():
    latitude = row['coordinates_lat']
    longitude = row['coordinates_lng']
    coordinate = Point(longitude, latitude)
    in_polygon = polygon_to_evaluate.contains(coordinate)
    df.loc[index, 'in_polygon'] = '1' if in_polygon else '0'

df.to_csv(f"./output/offers_aggregated.csv", index=False)
