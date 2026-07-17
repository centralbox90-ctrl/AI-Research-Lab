from src.indicators.configs import WILLIAMS_CONFIG



def main():

    print(
        "Индикатор:",
        WILLIAMS_CONFIG.name
    )


    print(
        "Текущие параметры:"
    )

    print(
        WILLIAMS_CONFIG.parameters
    )


    print(
        "Параметры оптимизации:"
    )

    print(
        WILLIAMS_CONFIG.optimization_space
    )



if __name__ == "__main__":

    main()