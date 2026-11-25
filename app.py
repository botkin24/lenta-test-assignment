import pandas as pd
import streamlit as st

from validator import validate_prices

st.title("Проверка цен конкурентов")

file = st.file_uploader("Загрузить выгрузку", type=["xlsx"])

# Выбор листа загруженной книги
if file is not None:
    with pd.ExcelFile(file) as workbook:
        sheet_names = workbook.sheet_names

    default_index = sheet_names.index("Данные") if "Данные" in sheet_names else 0
    sheet_name = st.selectbox("Лист с данными", sheet_names, index=default_index)

if st.button("Запустить обработку", disabled=file is None):
    with st.spinner("Идёт обработка"):
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            clean, excluded, summary, by_reason = validate_prices(df)
        except ValueError:
            st.error(f"Не удалось прочитать лист «{sheet_name}». Проверьте файл.")
            st.stop()
        except KeyError as error:
            st.error(f"В файле нет столбца «{error.args[0]}».")
            st.stop()

    st.subheader("Краткая статистика обработки")
    for label, count in summary.items():
        st.write(f"{label} — {count:,}".replace(",", " "))
    if not by_reason.empty:
        st.dataframe(by_reason.rename("Количество строк"))

    # Очищенный набор данных с ценами, которые прошли проверку
    st.subheader("Очищенный набор данных с ценами, которые прошли проверку")
    st.dataframe(clean, hide_index=True)

    st.download_button(
        "Скачать очищенный набор данных (CSV)",
        data=clean.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name="Очищенный набор данных.csv",
        mime="text/csv",
        on_click="ignore",
    )

    # Список исключённых наблюдений с причиной
    st.subheader("Список исключённых наблюдений с причиной")
    columns = ["Причина"] + excluded.columns.drop("Причина").tolist()
    excluded_table = excluded[columns]
    st.dataframe(excluded_table, hide_index=True)

    st.download_button(
        "Скачать список исключённых наблюдений (CSV)",
        data=excluded_table.to_csv(index=False, sep=";", decimal=",").encode(
            "utf-8-sig"
        ),
        file_name="Список исключённых наблюдений.csv",
        mime="text/csv",
        on_click="ignore",
    )
