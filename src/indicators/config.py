from dataclasses import dataclass, field



@dataclass
class IndicatorConfig:
    """
    Общая конфигурация индикатора.
    """


    name: str

    parameters: dict = field(
        default_factory=dict
    )


    optimization_space: dict = field(
        default_factory=dict
    )



    def get(self, key, default=None):

        return self.parameters.get(
            key,
            default
        )



    def get_optimization_space(self):

        return self.optimization_space