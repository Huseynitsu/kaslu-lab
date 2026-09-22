from core.dataset_builder import (
    build_dataset
)

from core.ml_model import (
    AnammoxMLModel
)

from core.hybrid_model import (
    HybridModel
)


def train_pipeline(
    n_samples=3000
):

    print(
        "\nGenerating dataset..."
    )

    df = build_dataset(
        n_samples=n_samples
    )

    print(
        f"Dataset size: {len(df)}"
    )

    print(
        "\nTraining ML model..."
    )

    ml_model = AnammoxMLModel()

    ml_model.train(df)

    print(
        "\nCreating Hybrid Model..."
    )

    hybrid_model = HybridModel(
        ml_model
    )

    print(
        "\nTraining finished."
    )

    return hybrid_model