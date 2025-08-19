import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle
import pandas as pd
import utils


def plot_macd(data: pd.DataFrame) -> None:
    plt.figure(figsize=(14, 6))
    plt.xticks(rotation=15)
    plt.plot(data.Date.values, data.MACD.values, label="MACD", alpha=utils.ALPHA)
    plt.plot(data.Date.values, data.SIGNAL.values, label="SIGNAL", alpha=utils.ALPHA)

    buys = data[data.DIRECTION == "BUY"]
    sells = data[data.DIRECTION == "SELL"]
    plt.scatter(buys.Date.values, buys.MACD.values, color="green", marker=4)
    plt.scatter(
        buys.Date.values,
        buys.MACD.values - utils.SIGNAL_OFFSET,
        color="green",
        marker=6,
        label="buy",
    )
    plt.scatter(sells.Date.values + 100, sells.MACD.values, color="red", marker=4)
    plt.scatter(
        sells.Date.values,
        sells.MACD.values + utils.SIGNAL_OFFSET,
        color="red",
        marker=7,
        label="sell",
    )

    plt.legend()
    plt.title("Wykres MACD/SIGNAL dla BTC/USD od 20-06-2022 do 27-02-2025")
    plt.savefig("images/signals_plot.png", dpi=utils.DPI)


def plot_price(data: pd.DataFrame, with_signals: bool = False) -> None:
    save_path = "images/btc_plot"
    buys = data[data.DIRECTION == "BUY"]
    sells = data[data.DIRECTION == "SELL"]

    if with_signals:
        save_path += "_with_signals"

    plt.figure(figsize=(14, 6))
    plt.xticks(rotation=15)
    plt.plot(
        data.Date.values,
        data.Price.values,
        label="price",
        alpha=utils.ALPHA if with_signals else 1,
    )
    plt.gca().yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    if with_signals:
        plt.scatter(buys.Date.values, buys.Price.values, color="green", marker=4)
        plt.scatter(
            buys.Date.values,
            buys.Price.values - utils.SIGNAL_OFFSET * 5,
            color="green",
            marker=6,
            label="buy",
        )
        plt.scatter(sells.Date.values, sells.Price.values, color="red", marker=4)
        plt.scatter(
            sells.Date.values,
            sells.Price.values + utils.SIGNAL_OFFSET * 5,
            color="red",
            marker=7,
            label="sell",
        )
        plt.gca().add_patch(
            Rectangle(
                (
                    buys.Date.values[20] - pd.Timedelta(days=10),
                    buys.Price.values[20] - utils.SIGNAL_OFFSET * 8,
                ),
                buys.Date.values[22] - buys.Date.values[20] + pd.Timedelta(days=10),
                sells.Price.values[21]
                - buys.Price.values[20]
                + utils.SIGNAL_OFFSET * 17,
                fill=False,
                edgecolor="green",
                linewidth=1,
                alpha=0.5,
            )
        )

        plt.gca().add_patch(
            Rectangle(
                (
                    buys.Date.values[9] - pd.Timedelta(days=10),
                    buys.Price.values[9] - utils.SIGNAL_OFFSET * 12,
                ),
                buys.Date.values[12] - buys.Date.values[9] + pd.Timedelta(days=6),
                sells.Price.values[10]
                - buys.Price.values[9]
                + utils.SIGNAL_OFFSET * 24,
                fill=False,
                edgecolor="red",
                linewidth=1,
                alpha=0.5,
            )
        )

    if with_signals:
        plt.legend()

    plt.title("Wykres BTC/USD od 20-06-2022 do 27-02-2025")
    plt.savefig(f"{save_path}.png", dpi=utils.DPI)

    if with_signals:
        # add text labels
        for i in range(len(buys)):
            offset = utils.SIGNAL_OFFSET * 3
            if i < 15:
                offset = utils.SIGNAL_OFFSET
            plt.text(
                buys.Date.values[i],  # - pd.Timedelta(days=1.75),
                buys.Price.values[i] + offset,
                f"${buys.Price.values[i]:,.2f}",
                fontsize=10,
                horizontalalignment="center",
                verticalalignment="center",
            )
            plt.text(
                sells.Date.values[i],  # - pd.Timedelta(days=1.75),
                sells.Price.values[i] - offset,
                f"${sells.Price.values[i]:,.2f}",
                fontsize=10,
                horizontalalignment="center",
                verticalalignment="center",
            )

        # zoom1
        x0 = buys.Date.values[20] - pd.Timedelta(days=2)
        x1 = sells.Date.values[21] + pd.Timedelta(days=2)

        y0 = buys.Price.values[20] - utils.SIGNAL_OFFSET * 8
        y1 = sells.Price.values[21] + utils.SIGNAL_OFFSET * 8

        plt.xlim((x0, x1))
        plt.ylim((y0, y1))

        plt.title("Przyblizenie 1")
        plt.savefig("images/zoomed1.png", dpi=utils.DPI)

        # zoom2
        x0 = buys.Date.values[9] - pd.Timedelta(days=2)
        x1 = sells.Date.values[11] + pd.Timedelta(days=2)

        y0 = buys.Price.values[9] - utils.SIGNAL_OFFSET * 8
        y1 = sells.Price.values[10] + utils.SIGNAL_OFFSET * 8

        plt.xlim((x0, x1))
        plt.ylim((y0, y1))

        plt.title("Przyblizenie 2")
        plt.savefig("images/zoomed2.png", dpi=utils.DPI)


def plot_simulation(strategy: pd.DataFrame, hold: pd.DataFrame) -> None:
    plt.figure(figsize=(14, 6))
    plt.xticks(rotation=15)
    plt.plot(strategy.Date.values, strategy.Value.values, label="MACD", color="red")
    plt.plot(hold.Date.values, hold.Value.values, label="hold", color="blue")

    plt.gca().yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )
    print(f"initial portfolio value: {strategy.Value.values[0]}")
    plt.axhline(y=strategy.Value.values[0], color="grey", linestyle="--", linewidth=1)

    plt.legend()
    plt.title("Porównanie strategii - wartość portfolio")
    plt.savefig("images/compare_strategies.png", dpi=utils.DPI)


def main():
    data = utils.get_data("data/btc_daily.csv")
    plot_price(data)
    plot_price(data, True)
    plot_macd(data)
    plot_simulation(utils.run_macd_simulation(data), utils.run_hold_simulation(data))


if __name__ == "__main__":
    main()
