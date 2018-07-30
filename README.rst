==============
hypothesis-csv
==============


`hypothesis-csv` is an extension to the `hypothesis` framework. The goal of this framework is to offer a flexible tool
to perform generative-testing/property-based testing for software that accepts CSV files as an input.



Description
===========

`hypothesis-csv` is designed with two main use cases in mind:
    -test software that accepts a wide spectrum of CSV formats and doesn't make
assumptions on the content
    - test software that accepts very specific CSV formats and makes assumption on the content, types and header fields.

Examples
========

.. code-block:: python
    :name: Generate arbitrary, non-empty CSV

    from hypothesis_csv.strategies import csv
    @given(csv=csv())
    def test_my_csv_parse(csv):
        parsed_csv=my_csv_parser(csv)
        assert ...



.. code-block:: python
    :name: Generate CSV of a given size (5 columns x 20 rows)

    from hypothesis_csv.strategies import csv
    @given(csv=csv(lines=20,header=5))
    def test_my_csv_parse(csv):
        parsed_csv=my_csv_parser(csv)
        assert parsed_csv.num_columns == 5
        assert parsed_csv.num_rows == 20



.. code-block:: python
    :name: Generate CSV with a header

    from hypothesis_csv.strategies import csv
    @given(csv=csv(header=["timestamp","val_1","val_2"]))
    def test_my_csv_parse(csv):
        parsed_csv=my_csv_parser(csv)
        assert parsed_csv.num_columns == 3


.. code-block:: python
    :name: Generate CSV with columns of a given type

    from hypothesis_csv.strategies import csv
    @given(csv=csv(columns=[text(),int(),float()]))
    def test_my_csv_parse(csv):
        parsed_csv=my_csv_parser(csv)
        assert parsed_csv.num_columns == 3





TODO and WIP
============

Support multiple dialects (using meza writer)
