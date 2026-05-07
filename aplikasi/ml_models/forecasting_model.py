import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime, timedelta
from aplikasi import log

class DemandForecastModel:
    def __init__(self):
        self.model = None
        self.product_id = None
        self.residual_std = 0.0
        self.df_train = None

    def _build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['dayofweek']  = df['ds'].dt.dayofweek
        df['dayofmonth'] = df['ds'].dt.day
        df['month']      = df['ds'].dt.month
        df['weekofyear'] = df['ds'].dt.isocalendar().week.astype(int)
        df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)

        for lag in [1, 2, 3, 7]:
            df[f'lag_{lag}'] = df['y'].shift(lag)

        df['rolling_mean_3'] = df['y'].shift(1).rolling(3).mean()
        df['rolling_mean_7'] = df['y'].shift(1).rolling(7).mean()
        df['rolling_std_7']  = df['y'].shift(1).rolling(7).std()

        return df

    def prepare_data(self, sales_data: list) -> pd.DataFrame:
        try:
            df = pd.DataFrame(sales_data)

            if 'date' not in df.columns or 'quantity' not in df.columns:
                raise ValueError("Data harus memiliki kolom 'date' dan 'quantity'")

            df['ds'] = pd.to_datetime(df['date'])
            df['y']  = df['quantity'].astype(float)
            df = df[['ds', 'y']].sort_values('ds').reset_index(drop=True)

            if len(df) < 2:
                raise ValueError("Minimal butuh 2 data point untuk forecasting")

            return df

        except Exception as e:
            log.error(f"Error prepare_data: {str(e)}")
            raise

    def train(self, sales_data: list, product_id: str):
        try:
            self.product_id = product_id
            df = self.prepare_data(sales_data)
            self.df_train = df.copy()

            df_feat = self._build_features(df)
            df_feat = df_feat.dropna().reset_index(drop=True)

            feature_cols = [
                'dayofweek', 'dayofmonth', 'month', 'weekofyear', 'is_weekend',
                'lag_1', 'lag_2', 'lag_3', 'lag_7',
                'rolling_mean_3', 'rolling_mean_7', 'rolling_std_7'
            ]

            X = df_feat[feature_cols]
            y = df_feat['y']

            self.model = lgb.LGBMRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                num_leaves=31,
                min_child_samples=1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
            self.model.fit(X, y)

            y_pred_train = self.model.predict(X)
            self.residual_std = float(np.std(y - y_pred_train))

            log.info(f"LightGBM model trained for product: {product_id}")
            return True

        except Exception as e:
            log.error(f"Error training model: {str(e)}")
            raise

    def predict(self, forecast_days: int) -> dict:
        try:
            if self.model is None:
                raise ValueError("Model belum di-train. Panggil train() terlebih dahulu.")

            feature_cols = [
                'dayofweek', 'dayofmonth', 'month', 'weekofyear', 'is_weekend',
                'lag_1', 'lag_2', 'lag_3', 'lag_7',
                'rolling_mean_3', 'rolling_mean_7', 'rolling_std_7'
            ]

            df_history = self.df_train.copy()
            last_date  = df_history['ds'].max()
            recommendations = []

            for i in range(1, forecast_days + 1):
                future_date = last_date + timedelta(days=i)
                df_ext = pd.concat([
                    df_history,
                    pd.DataFrame({'ds': [future_date], 'y': [np.nan]})
                ], ignore_index=True)

                df_feat = self._build_features(df_ext)
                row = df_feat.iloc[[-1]]

                X_pred = row[feature_cols].fillna(df_history['y'].mean())
                v_predicted = float(self.model.predict(X_pred)[0])
                v_predicted = max(0.0, v_predicted)

                margin = 1.96 * self.residual_std
                v_lower = max(0, int(round(v_predicted - margin)))
                v_upper = max(0, int(round(v_predicted + margin)))
                v_pred_int = int(round(v_predicted))

                recommendations.append({
                    "date": future_date.strftime('%Y-%m-%d'),
                    "predicted_demand": v_pred_int,
                    "lower_bound": v_lower,
                    "upper_bound": v_upper,
                    "stock_needed": int(round(v_predicted * 1.1))
                })

                df_history = pd.concat([
                    df_history,
                    pd.DataFrame({'ds': [future_date], 'y': [v_predicted]})
                ], ignore_index=True)

            v_total_stock = sum(r['stock_needed'] for r in recommendations)

            return {
                "product_id": self.product_id,
                "forecast_period": f"{forecast_days}_days",
                "recommendations": recommendations,
                "total_stock_needed": v_total_stock,
                "confidence_level": "95%",
                "forecast_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            log.error(f"Error predicting: {str(e)}")
            raise

    def calculate_accuracy(self, actual_data: list, predicted_data: list) -> dict:
        try:
            if len(actual_data) != len(predicted_data):
                raise ValueError("Panjang actual dan predicted data harus sama")

            actual    = np.array([d['quantity'] for d in actual_data])
            predicted = np.array([d['predicted_demand'] for d in predicted_data])

            mape     = np.mean(np.abs((actual - predicted) / actual)) * 100
            mae      = np.mean(np.abs(actual - predicted))
            rmse     = np.sqrt(np.mean((actual - predicted) ** 2))
            accuracy = max(0, 100 - mape)

            return {
                "mape": round(mape, 2),
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "accuracy": round(accuracy, 2)
            }

        except Exception as e:
            log.error(f"Error calculating accuracy: {str(e)}")
            raise
