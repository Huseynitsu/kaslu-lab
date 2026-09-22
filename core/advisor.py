def generate_advice(
    nh4,
    no2,
    ph,
    temperature,
    do,
    biomass,
    srt
):

    advice = []

    # pH
    if ph < 7.0:
        advice.append(
            "Increase pH toward 7.5–8.0 for better Anammox activity."
        )

    elif ph > 8.5:
        advice.append(
            "Decrease pH toward 7.5–8.0."
        )

    # Temperature
    if temperature < 30:
        advice.append(
            "Increase temperature toward 30–35°C."
        )

    elif temperature > 37:
        advice.append(
            "Reduce temperature below 37°C."
        )

    # DO
    if do > 0.8:
        advice.append(
            "Decrease dissolved oxygen below 0.8 mg/L."
        )

    # NO2 ratio
    target_no2 = nh4 * 1.32

    if no2 < target_no2:
        advice.append(
            f"Increase NO2 to approximately {target_no2:.1f} mg/L."
        )

    # Biomass
    if biomass < 500:
        advice.append(
            "Increase Anammox biomass concentration."
        )

    # SRT
    if srt < 15:
        advice.append(
            "Increase SRT above 15 days."
        )

    if len(advice) == 0:

        advice.append(
            "Current operating conditions appear close to optimal."
        )

    return advice