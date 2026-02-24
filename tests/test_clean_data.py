import pandas as pd

from mcp_server.scripts.clean_data import clean_price_df


def test_clean_price_df_fills_business_days():
    dates = pd.to_datetime(["2024-01-04", "2024-01-08"])
    df = pd.DataFrame({"Close": [100.0, 110.0]}, index=dates)

    cleaned = clean_price_df(df)

    # 2024-01-05 is a business day and should be filled
    assert len(cleaned) == 3
    assert cleaned.loc["2024-01-05", "Close"] == 100.0
    assert "return_1d" in cleaned.columns
