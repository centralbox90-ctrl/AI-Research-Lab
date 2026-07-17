from src.indicators.configs import WILLIAMS_CONFIG

from src.indicators.williams import WilliamsIndicator



def main():


    indicator = WilliamsIndicator(
        config=WILLIAMS_CONFIG
    )


    print(
        "Индикатор:",
        indicator.name
    )


    print(
        "Период:",
        indicator.period
    )



if __name__ == "__main__":

    main()