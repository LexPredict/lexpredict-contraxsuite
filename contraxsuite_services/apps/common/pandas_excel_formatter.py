"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import pandas as pd
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet


class PandasExcelFormatter:
    MAX_ROW_HEIGHT = 10
    MAX_COL_WIDTH = 100

    @classmethod
    def export_to_xlsx(cls,
                       data_frame: pd.DataFrame,
                       sheet_name: str,
                       output_file_path: str) -> None:
        writer = pd.ExcelWriter(path=output_file_path, engine='xlsxwriter',
                                options={'remove_timezone': True})
        for df in [data_frame]:

            # seems that options={'remove_timezone': True} doesn't work and datetime with timezone still give error
            datetime_columns = df.select_dtypes(['datetimetz']).columns
            for dtz_column in datetime_columns:
                df[dtz_column] = df[dtz_column].dt.tz_localize(None)

            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            cls.adjust_columns_width(df, writer.book, worksheet)
            cls.adjust_rows_height(df, writer.book, worksheet)
        writer.save()

    @classmethod
    def adjust_columns_width(cls,
                             df: pd.DataFrame,
                             wb: Workbook,
                             worksheet: Worksheet):
        # wrap_format = wb.add_format({'shrink': True})
        for idx, col in enumerate(df):
            series = df.iloc[:, idx]    # vs df[col] - col may not be unique
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            max_len = min(max_len, cls.MAX_COL_WIDTH)
            worksheet.set_column(idx, idx, max_len)

    @classmethod
    def adjust_rows_height(cls,
                           df: pd.DataFrame,
                           wb: Workbook,
                           worksheet: Worksheet):
        bold_fmt = wb.add_format({'bold': True})
        worksheet.set_row(0, cell_format=bold_fmt)
        for idx, row in df.iterrows():
            height = max([1 + sum([1 for ch in str(c or '') if ch == '\n'])
                          for c in row])
            height = min(height, cls.MAX_ROW_HEIGHT)
            worksheet.set_row(idx + 1, height * worksheet.default_row_height)
