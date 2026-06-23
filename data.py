import matplotlib
import pandas as pd

import api
import db


stats = db.getStats()

itemStats_df = pd.DataFrame(list(stats["itemsFound"].items()), columns=["Item Name", "Quantity"])
