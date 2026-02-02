import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from category_encoders import CountEncoder, TargetEncoder

class Encoder(BaseEstimator, TransformerMixin):
    def __init__(self,
                 disposition_encod=False, 
                 furnishing_encod=False,
                 district_mode="none",  # "none", "count", "te"       
                 te_smoothing=20, #smoothing parameter for target encoding to avoid overfitting
                 te_min_samples_leaf=30, #min samples to take category average "safe" , if less model use global mean
                 drop_original_district=True):
        self.disposition_encod = disposition_encod
        self.furnishing_encod  = furnishing_encod
        self.district_mode     = district_mode
        self.te_smoothing      = te_smoothing
        self.te_min_samples_leaf = te_min_samples_leaf
        self.drop_original_district = drop_original_district

        self._disp_map = {"1+kk":1,"1+1":2,"2+kk":3,"2+1":4,"3+kk":5,"3+1":6,
                          "4+kk":7,"4+1":8,"5+kk":9,"5+1":10,"other":11}
        self._furn_map = {"not_furnished":1,
                          "partly_furnished":2,
                          "furnished":3}

        self._count = None      
        self._te    = None      

    def fit(self, X, y=None):
        X = pd.DataFrame(X)

        
        if "district" in X.columns and self.district_mode == "count": 
            self._count = CountEncoder(
                cols=["district"],
                handle_unknown=0, 
                handle_missing=0,
                normalize=True     
            ).fit(X[["district"]])

        if "district" in X.columns and self.district_mode == "te":
            if y is None or not np.issubdtype(pd.Series(y).dtype, np.number):
                raise ValueError("district_mode='te' требует числовой y")
            self._te = TargetEncoder(
                smoothing=self.te_smoothing,
                min_samples_leaf=self.te_min_samples_leaf,
                handle_missing="value",
                handle_unknown="value",
            ).fit(X[["district"]], y)

        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()

        if self.disposition_encod and "disposition" in X.columns:
            X["disposition"] = X["disposition"].map(self._disp_map).fillna(-1).astype(float)

        if self.furnishing_encod and "furnishing" in X.columns:
            X["furnishing"] = X["furnishing"].map(self._furn_map).fillna(-1).astype(float)

        if "district" in X.columns and self._count is not None:
            X["district_count"] = self._count.transform(X[["district"]])["district"]
            if self.drop_original_district:
                X.drop(columns=["district"], inplace=True, errors="ignore")

        if "district" in X.columns and self._te is not None:
            X[["district"]] = self._te.transform(X[["district"]])  

        return X