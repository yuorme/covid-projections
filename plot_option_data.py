
csv_dtypes = [
        'category','str',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'category','category',
        'float32','float32','float32',
        'float32','float32','float32',
    ]

# data types for the sql table, which includes transformed columns: date, model_date, location_abbr
table_dtypes = [
        'category','datetime64[ns]',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'category','category',
        'float32','float32','float32',
        'float32','float32','float32', 'datetime64[ns]','object'
    ]