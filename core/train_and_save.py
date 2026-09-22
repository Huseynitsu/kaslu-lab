from core.dataset_builder import (
    build_dataset,
    save_dataset
)

from core.ml_model import (
    AnammoxMLModel
)

from core.hybrid_model import (
    HybridModel
)

from core.model_manager import (
    save_model
)


def train_and_save():

    print(
        "\nGenerating dataset..."
    )

    df = build_dataset(
        n_samples=3000
    )

    print(
        f"Dataset size: {len(df)}"
    )

    save_dataset(
        df,
        "anammox_dataset.csv"
    )

    print(
        "\nTraining ML model..."
    )

    ml_model = AnammoxMLModel()

    ml_model.train(df)

    print(
        "\nBuilding Hybrid Model..."
    )

    hybrid_model = HybridModel(
        ml_model
    )

    print(
        "\nSaving model..."
    )

    save_model(
        hybrid_model
    )

    print(
        "\nTraining completed."
    )

    return hybrid_model


if __name__ == "__main__":

    train_and_save()