import sqlite3

import pandas


def main():
    connection = sqlite3.connect("db.sqlite3")
    data_to_load = (
        ("static/data/titles.csv", "reviews_title"),
        ("static/data/users.csv", "users_user"),
        ("static/data/review.csv", "reviews_review"),
        ("static/data/category.csv", "reviews_category"),
        ("static/data/comments.csv", "reviews_comment"),
        ("static/data/genre_title.csv", "reviews_genretitle"),
        ("static/data/genre.csv", "reviews_genre"),
    )

    for path, table in data_to_load:
        try:
            df = pandas.read_csv(
                path,
                sep=",",
                header=0,
            )
            df.rename(
                columns={
                    "category": "category_id",
                    "author": "author_id",
                },
                inplace=True,
            )
            df.columns
            if table == "users_user":
                new_df = df.assign(
                    password="---",
                    is_superuser=False,
                    is_staff=False,
                    is_active=True,
                    date_joined=0,
                    first_name="null",
                    last_name="null",
                    bio="null",
                )
            else:
                new_df = df
            new_df.to_sql(table, connection, if_exists="append", index=False)
            print(f"OK: {path}")
        except Exception as error:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
