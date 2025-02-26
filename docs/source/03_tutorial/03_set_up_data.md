# Setting up the data

Kedro uses configuration to make your code reproducible when it has to reference datasets in different locations and / or in different environments. In this section of the tutorial we will describe the following:

* Adding datasets to your `data/` folder, according to [data engineering convention](../06_resources/01_faq.md#what-is-data-engineering-convention)
* Using the Data Catalog as a registry of all data sources available for use by the project `conf/base/catalog.yml`

For further information about the Data Catalog, please see the [User Guide](../04_user_guide/04_data_catalog.md).


## Adding your datasets to `data`

This tutorial will make use of fictional datasets for spaceflight companies shuttling customers to the Moon and back. You will use the data to train a model to predict the price of shuttle hire. However, before you get to train the model, you will need to prepare the data by doing some data engineering, which is the process of preparing data for model building by creating a master table.

The spaceflight tutorial has three files and uses two data formats: `.csv` and `.xlsx`. Download and save the files to the `data/01_raw/` folder of your project directory:

* [reviews.csv](https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/docs/source/03_tutorial/data/reviews.csv)
* [companies.csv](https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/docs/source/03_tutorial/data/companies.csv)
* [shuttles.xlsx](https://github.com/quantumblacklabs/kedro/blob/develop/docs/source/03_tutorial/data/shuttles.xlsx?raw=true)

You can [download the files from GitHub](https://www.quora.com/How-do-I-download-something-from-GitHub) using [cURL](https://curl.haxx.se/download.html) or [Wget](https://www.gnu.org/software/wget/).

An example of downloading [reviews.csv](https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/docs/source/03_tutorial/data/reviews.csv) to your current directory is done by running this in your terminal or command line:

```bash
curl -O https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/docs/source/03_tutorial/data/reviews.csv
```

Or through using Wget:

```bash
wget https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/docs/source/03_tutorial/data/reviews.csv
```


## Reference all datasets

To work with the datasets provided you need to make sure they can be loaded by Kedro.

All Kedro projects have a `conf/base/catalog.yml` file where users register the datasets they use. Registering a dataset is as simple as adding a named entry into the `.yml` file, which includes:

* File location (path)
* Parameters for the given dataset
* Type of data
* Versioning

Kedro supports a number of different data types, such as `csv`, which is implemented by `CSVLocalDataSet`. The full list of supported datasets can be found in the [API documentation](../kedro.io.rst#data-sets).

Let’s start this process by registering the `csv` datasets by copying the following to the end of the `catalog.yml` file:

```yaml
companies:
  type: CSVLocalDataSet
  filepath: data/01_raw/companies.csv

reviews:
  type: CSVLocalDataSet
  filepath: data/01_raw/reviews.csv
```

If you want to check whether Kedro loads the data correctly, open a `kedro ipython` session and run:

```python
context.catalog.load('companies').head()
```

This should show you the first five rows of the dataset. If you want to explore more of it before moving on with the project:

```python
df = context.catalog.load('companies')
```

The entire `companies` dataset is loaded into a `pandas` DataFrame and you can play with it as you wish.

When you have finished, simply close `ipython` session by typing the following:

```python
exit()
```


## Creating custom datasets

Often, real world data is stored in formats that are not supported by Kedro. We will illustrate this with `shuttles.xlsx`. In fact, Kedro has built-in support for Microsoft Excel files, but we will take the opportunity to demonstrate how to use Kedro to implement support for custom data formats.

Let’s create a custom dataset implementation which will allow you to load and save `.xlsx` files.

To keep your code well-structured you should create a Python sub-package called **`kedro_tutorial.io`**. You can do that by running this in your terminal:

```bash
mkdir -p src/kedro_tutorial/io && touch src/kedro_tutorial/io/__init__.py
```

Creating new custom dataset implementations is done by creating a class that extends and implements all methods from `AbstractDataSet`. To implement a class that will allow you to load and save Excel files, you need to create the file `src/kedro_tutorial/io/xls_local.py` and paste the following into it:

```python
"""ExcelLocalDataSet loads and saves data to a local Excel file. The
underlying functionality is supported by pandas, so it supports all
allowed pandas options for loading and saving Excel files.
"""
from os.path import isfile
from typing import Any, Union, Dict

import pandas as pd

from kedro.io import AbstractDataSet

class ExcelLocalDataSet(AbstractDataSet):
    """``ExcelLocalDataSet`` loads and saves data to a local Excel file. The
    underlying functionality is supported by pandas, so it supports all
    allowed pandas options for loading and saving Excel files.

    Example:
    ::
        >>> import pandas as pd
        >>>
        >>> data = pd.DataFrame({'col1': [1, 2], 'col2': [4, 5],
        >>>                      'col3': [5, 6]})
        >>> data_set = ExcelLocalDataSet(filepath="test.xlsx",
        >>>                              load_args={'sheet_name':"Sheet1"},
        >>>                              save_args=None)
        >>> data_set.save(data)
        >>> reloaded = data_set.load()
        >>>
        >>> assert data.equals(reloaded)

    """

    def _describe(self) -> Dict[str, Any]:
        return dict(filepath=self._filepath,
                    engine=self._engine,
                    load_args=self._load_args,
                    save_args=self._save_args)

    def __init__(
        self,
        filepath: str,
        engine: str = "xlsxwriter",
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
    ) -> None:
        """Creates a new instance of ``ExcelLocalDataSet`` pointing to a concrete
        filepath.

        Args:
            engine: The engine used to write to excel files. The default
                          engine is 'xlswriter'.

            filepath: path to an Excel file.

            load_args: Pandas options for loading Excel files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html
                The default_load_arg engine is 'xlrd', all others preserved.

            save_args: Pandas options for saving Excel files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_excel.html
                All defaults are preserved.

        """
        self._filepath = filepath
        default_save_args = {}
        default_load_args = {"engine": "xlrd"}

        self._load_args = {**default_load_args, **load_args} \
            if load_args is not None else default_load_args
        self._save_args = {**default_save_args, **save_args} \
            if save_args is not None else default_save_args
        self._engine = engine

    def _load(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        return pd.read_excel(self._filepath, **self._load_args)

    def _save(self, data: pd.DataFrame) -> None:
        writer = pd.ExcelWriter(self._filepath, engine=self._engine)
        data.to_excel(writer, **self._save_args)
        writer.save()

    def _exists(self) -> bool:
        return isfile(self._filepath)
```

And update the `catalog.yml` file by adding the following:

```yaml
shuttles:
  type: kedro_tutorial.io.xls_local.ExcelLocalDataSet
  filepath: data/01_raw/shuttles.xlsx
```

> *Note:* The `type` specified is `kedro_tutorial.io.xls_local.ExcelLocalDataSet` which points Kedro to use the custom dataset implementation. To use Kedro's internal support for reading Excel datasets, you can simply specify `ExcelLocalDataSet`, which is implemented as in the code above.

A good way to test that everything works as expected is by trying to load the dataset within a new `kedro ipython` session:

```python
context.catalog.load('shuttles').head()
```

### Contributing a custom dataset implementation

Kedro users create many custom dataset implementations while working on real-world projects, and it makes sense that they should be able to share their work with each other. That is why Kedro has a `kedro.contrib` sub-package, where users can add new custom dataset implementations to help others in our community. Sharing your custom datasets implementations is possibly the easiest way to contribute back to Kedro and if you are interested in doing so, you can check out the Kedro contribution guide on the [GitHub repo](https://github.com/quantumblacklabs/kedro).
