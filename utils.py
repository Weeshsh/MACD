import pandas as pd

SIGNAL_OFFSET = 750
ALPHA = 0.75
DPI = 300


def get_data(path: str) -> pd.DataFrame:
    data = fetch_data(path)
    data = calculate_ema(data, 12, "Price", "EMA12")
    data = calculate_ema(data, 26, "Price", "EMA26")

    data["MACD"] = data.EMA12 - data.EMA26

    data = calculate_ema(data, 9, "MACD", "SIGNAL")
    data["CROSS"] = data.MACD >= data.SIGNAL

    for i in range(1, len(data)):
        current = data.CROSS.at[i]
        previous = data.CROSS.at[i - 1]

        data.at[i, "DIRECTION"] = "NONE"

        if current and not previous:
            data.at[i, "DIRECTION"] = "BUY"

        if not current and previous:
            data.at[i, "DIRECTION"] = "SELL"

    data.to_csv("data/processed.csv")

    return data


def fetch_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)

    data = data.replace({",": ""}, regex=True)

    data.Price = pd.to_numeric(data.Price)
    data.Date = pd.to_datetime(data.Date, format="%m/%d/%Y")

    data = data.iloc[::-1].reset_index(drop=True)

    return data[["Date", "Price"]]


def calculate_ema(
    data: pd.DataFrame, n: int, loc_from: str, save_to: str
) -> pd.DataFrame:
    alpha = 2 / (n + 1)
    for i in range(n, len(data)):
        denominator = numerator = 0
        for j in range(0, n + 1):
            p = data.at[i - j, loc_from]
            numerator += p * ((1 - alpha) ** j)
            denominator += (1 - alpha) ** j

        data.at[i, save_to] = numerator / denominator

    return data


def run_macd_simulation(data: pd.DataFrame) -> pd.DataFrame:
    buy_price = 0
    current_holdings = 0
    portfolio_value = 1000 * data.Price.values[0]
    would_be_port_val = portfolio_value
    results = []
    profitable_trades = []
    losing_trades = []

    for transaction in data.itertuples():
        match transaction.DIRECTION:
            case "BUY":
                current_holdings = portfolio_value / transaction.Price
                buy_price = transaction.Price
                would_be_port_val = portfolio_value
            case "SELL":
                if current_holdings:
                    profit = transaction.Price - buy_price
                    transaction_profit = (
                        transaction.Price - buy_price
                    ) * current_holdings
                    portfolio_value += transaction_profit
                    current_holdings = 0
                    if profit > 0:
                        profitable_trades.append(transaction_profit)
                    else:
                        losing_trades.append(transaction_profit)
                would_be_port_val = portfolio_value
            case "NONE":
                if current_holdings:
                    would_be_port_val = (
                        portfolio_value
                        + (transaction.Price - buy_price) * current_holdings
                    )

        results.append({"Date": transaction.Date, "Value": would_be_port_val})
    print("MACD: min max")
    print(min(results, key=lambda x: x["Value"]))
    print(max(results, key=lambda x: x["Value"]))
    print(results[-1])

    total_trades = len(profitable_trades) + len(losing_trades)
    avg_profit = sum(profitable_trades) / len(profitable_trades)
    avg_loss = sum(losing_trades) / len(losing_trades)
    print(
        f"Ile transakcji: {total_trades}; \n\t profit: {len(profitable_trades)}; avg:{avg_profit} \n\t strata: {len(losing_trades)}; avg:{avg_loss}"
    )
    return pd.DataFrame(results)


def run_hold_simulation(data: pd.DataFrame) -> pd.DataFrame:
    res = [
        {"Date": transaction.Date, "Value": 1000 * transaction.Price}
        for transaction in data.itertuples()
    ]
    print("Hold: min max")
    print(min(res, key=lambda x: x["Value"]))
    print(max(res, key=lambda x: x["Value"]))
    print(res[-1])
    return pd.DataFrame(res)
