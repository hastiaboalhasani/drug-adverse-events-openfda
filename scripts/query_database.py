import pandas as pd
from database_connection import get_engine


def run_queries():
    engine = get_engine()

    queries = {
        "Total number of records": """
            SELECT COUNT(*) AS total_records
            FROM adverse_events;
        """,

        "Serious vs non-serious reports": """
            SELECT serious, COUNT(*) AS count
            FROM adverse_events
            GROUP BY serious;
        """,

        "Top 10 query drugs by number of reports": """
            SELECT query_drug, COUNT(*) AS report_count
            FROM adverse_events
            GROUP BY query_drug
            ORDER BY report_count DESC
            LIMIT 10;
        """,

        "Top 10 countries": """
            SELECT country, COUNT(*) AS report_count
            FROM adverse_events
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY report_count DESC
            LIMIT 10;
        """,

        "Average number of reactions by seriousness": """
            SELECT serious, AVG(num_reactions) AS avg_reactions
            FROM adverse_events
            GROUP BY serious;
        """
    }

    for title, query in queries.items():
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)

        result = pd.read_sql(query, engine)
        print(result)


if __name__ == "__main__":
    run_queries()
