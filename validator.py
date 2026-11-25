import pandas as pd


def validate_prices(df):
    reason = pd.Series("", index=df.index, dtype="string")
    reason.loc[df.duplicated()] = "Точный дубль"

    for column in ["Регулярная цена конкурента", "Акционная цена конкурента"]:
        raw = df[column]
        price = pd.to_numeric(raw, errors="coerce")

        reason.loc[reason.eq("") & raw.isna()] = f"{column} — пустое значение"
        reason.loc[reason.eq("") & price.isna()] = f"{column} — нечисловое значение"

        invalid = price.le(0) | price.eq(float("inf"))
        reason.loc[reason.eq("") & invalid] = f"{column} — некорректное значение"

    passed = reason.eq("")
    clean = df.loc[passed].copy()
    excluded = df.loc[~passed].copy()
    excluded["Причина"] = reason.loc[~passed]

    summary = {
        "Обработано": len(df),
        "Прошло проверку": len(clean),
        "Не прошло проверку": len(excluded),
    }
    by_reason = excluded["Причина"].value_counts()

    return clean, excluded, summary, by_reason
