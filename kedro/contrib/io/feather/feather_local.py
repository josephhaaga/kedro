# Copyright 2018-2019 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.


"""``FeatherLocalDataSet`` is a data set used to load and save
data to local feather files. It uses the ``pandas`` implementation,
Feather is a fast, lightweight, and easy-to-use binary file format for storing data frames.
The underlying functionality is supported by pandas,
so it supports all operations the pandas supports.


Documentation on the Feather features, compatibility
list and known caveats can also be found on their official guide at:

https://github.com/wesm/feather.
"""

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from kedro.io.core import AbstractVersionedDataSet, DataSetError, Version


class FeatherLocalDataSet(AbstractVersionedDataSet):
    """``FeatherLocalDataSet`` loads and saves data to a local feather file. The
    underlying functionality is supported by pandas, so it supports all
    allowed pandas options for loading and saving csv files.

    Example:
    ::

        >>> from kedro.contrib.io.feather import FeatherLocalDataSet
        >>> import pandas as pd
        >>>
        >>> data = pd.DataFrame({'col1': [1, 2], 'col2': [4, 5],
        >>>                      'col3': [5, 6]})
        >>>
        >>> data_set = FeatherLocalDataSet(filepath="test.feather",
        >>>                                load_args=None)
        >>> data_set.save(data)
        >>> reloaded = data_set.load()
        >>>
        >>> assert data.equals(reloaded)

    """

    def __init__(
        self, filepath: str, load_args: Dict[str, Any] = None, version: Version = None
    ) -> None:
        """Creates a new instance of ``FeatherLocalDataSet`` pointing to a concrete
        filepath.

        Args:
            filepath: path to a feather file.
            load_args: feather options for loading feather files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_feather.html#pandas.read_feather
                All defaults are preserved.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.
        """
        super().__init__(Path(filepath), version)
        default_load_args = {}  # type: Dict[str, Any]
        self._load_args = (
            {**default_load_args, **load_args}
            if load_args is not None
            else default_load_args
        )

    def _load(self) -> pd.DataFrame:
        load_path = Path(self._get_load_path())

        return pd.read_feather(load_path, **self._load_args)

    def _save(self, data: pd.DataFrame) -> None:
        save_path = Path(self._get_save_path())
        save_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_feather(str(save_path))

        load_path = Path(self._get_load_path())
        self._check_paths_consistency(load_path.absolute(), save_path.absolute())

    def _exists(self) -> bool:
        try:
            path = self._get_load_path()
        except DataSetError:
            return False
        return Path(path).is_file()

    def _describe(self) -> Dict[str, Any]:
        return dict(
            filepath=self._filepath, load_args=self._load_args, version=self._version
        )
